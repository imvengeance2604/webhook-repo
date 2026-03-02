"""GitHub webhook receiver module.

Handles incoming GitHub webhook events for push and pull request actions,
validates webhook signatures, and stores events in MongoDB.
"""

import hashlib
import hmac
import re
from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request

from .models import build_event

webhook_bp = Blueprint("webhook", __name__)


def verify_github_signature(payload_bytes: bytes, sig_header: str) -> bool:
    """Verify GitHub webhook HMAC-SHA256 signature.
    
    GitHub signs webhook payloads using a secret key. This function validates
    that the incoming webhook is legitimate by comparing the provided signature
    against the expected signature calculated from the payload and secret.
    
    Args:
        payload_bytes: Raw request body bytes (before JSON parsing)
        sig_header: X-Hub-Signature-256 header value from GitHub request
        
    Returns:
        bool: True if signature is valid or no secret is configured, False otherwise
    """
    secret = current_app.config.get("GITHUB_SECRET", "")
    if not secret:
        # No secret configured, accept all webhooks
        return True

    # Validate header format
    if not sig_header or not sig_header.startswith("sha256="):
        return False

    # Calculate expected signature from payload
    expected = hmac.new(
        secret.encode(), payload_bytes, hashlib.sha256
    ).hexdigest()
    
    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(f"sha256={expected}", sig_header)


def parse_iso_timestamp(ts_str: str = None) -> datetime:
    """Parse ISO-8601 UTC timestamp string from GitHub webhook payload.
    
    GitHub provides timestamps in ISO-8601 format with 'Z' suffix (e.g.,
    "2026-03-02T14:35:00Z"). This function safely parses such strings and
    handles missing or malformed timestamps gracefully.
    
    Args:
        ts_str: Timestamp string in format "YYYY-MM-DDTHH:MM:SSZ" or None
        
    Returns:
        datetime: Parsed UTC datetime object with timezone info, or current UTC time if parsing fails
    """
    if ts_str:
        try:
            # Replace 'Z' suffix with '+00:00' for fromisoformat compatibility
            return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            # Fall through to return current time
            pass
    # Return current UTC time as fallback
    return datetime.now(timezone.utc)


@webhook_bp.route("/webhook", methods=["POST"])
def github_webhook():
    """GitHub webhook endpoint for handling push and pull request events.
    
    This endpoint receives webhook payloads from GitHub when repository events occur:
    - PUSH: Direct commits or merge commits to a branch
    - PULL_REQUEST: Pull request created, opened, or merged
    - MERGE: Detected from merge commits or merged pull requests
    
    Processing flow:
    1. Validate webhook signature using HMAC-SHA256
    2. Determine event type from X-GitHub-Event header
    3. Extract relevant fields based on event type
    4. Build event document and store in MongoDB
    
    Returns:
        JSON response with status and optional event data:
        - 201: Event stored successfully with event details
        - 403: Webhook signature validation failed
        - 200: Event ignored (not tracked event type, branch deletion, etc.)
    """
    # Get raw bytes for signature verification
    payload_bytes = request.get_data()
    sig = request.headers.get("X-Hub-Signature-256", "")
    
    # Validate GitHub webhook signature
    if not verify_github_signature(payload_bytes, sig):
        return jsonify({"error": "Invalid signature"}), 403

    # Parse webhook event type and JSON payload
    github_event = request.headers.get("X-GitHub-Event", "")
    payload = request.get_json(force=True) or {}

    event_doc = None

    # Handle push events (includes direct commits and merge commits)
    if github_event == "push":
        # Ignore branch deletion events
        if payload.get("deleted"):
            return jsonify({"status": "ignored"}), 200

        # Extract branch name from ref (format: refs/heads/branch-name)
        ref = payload.get("ref", "")
        to_branch = ref.split("/")[-1] if "/" in ref else ref
        
        # Get author from pusher object or fallback to sender
        author = (
            payload.get("pusher", {}).get("name")
            or payload.get("sender", {}).get("login", "unknown")
        )
        
        # Extract commit details from head_commit
        head_commit = payload.get("head_commit") or {}
        request_id = head_commit.get("id", payload.get("after", ""))
        timestamp = parse_iso_timestamp(head_commit.get("timestamp"))
        commit_message = head_commit.get("message", "")
        
        # Detect merge commits by checking commit message for "Merge branch" pattern
        if commit_message.startswith("Merge"):
            # For merge commits, extract source branch from message
            # Pattern: "Merge branch 'feature' into main"
            from_branch = payload.get("before", "")
            match = re.search(r"Merge branch ['\"](.+?)['\"]", commit_message)
            if match:
                from_branch = match.group(1)

            event_doc = build_event(
                request_id=request_id,
                author=author,
                action="MERGE",
                from_branch=from_branch,
                to_branch=to_branch,
                timestamp=timestamp,
            )
        else:
            # Regular direct push (non-merge commit)
            event_doc = build_event(
                request_id=request_id,
                author=author,
                action="PUSH",
                from_branch=to_branch,
                to_branch=to_branch,
                timestamp=timestamp,
            )

    # Handle pull request events
    elif github_event == "pull_request":
        pr = payload.get("pull_request", {})
        pr_action = payload.get("action", "")

        # Map GitHub PR actions to our event types
        if pr_action == "closed" and pr.get("merged"):
            # Closed PR that was merged
            action = "MERGE"
        elif pr_action in ("opened", "reopened", "synchronize"):
            # PR created, reopened, or updated
            action = "PULL_REQUEST"
        else:
            # Other PR actions (assigned, labeled, etc.) - ignore
            return jsonify({"status": "ignored"}), 200

        # Extract PR metadata
        author = (
            pr.get("user", {}).get("login")
            or payload.get("sender", {}).get("login", "unknown")
        )
        from_branch = pr.get("head", {}).get("ref", "")
        to_branch = pr.get("base", {}).get("ref", "")
        request_id = str(pr.get("number", ""))
        
        # Use merged_at timestamp for merged PRs, created_at for new PRs
        timestamp_field = (
            pr.get("merged_at") if action == "MERGE" else pr.get("created_at")
        )
        timestamp = parse_iso_timestamp(timestamp_field)

        event_doc = build_event(
            request_id=request_id,
            author=author,
            action=action,
            from_branch=from_branch,
            to_branch=to_branch,
            timestamp=timestamp,
        )

    else:
        # Unknown or untracked event type - ignore
        return jsonify({"status": "ignored"}), 200

    # Store event in MongoDB if it was successfully parsed
    if event_doc:
        current_app.db["events"].insert_one(event_doc)
        # Remove MongoDB ObjectID from response
        event_doc.pop("_id", None)
        return jsonify({"status": "ok", "event": event_doc}), 201

    # Fallback for unparseable events
    return jsonify({"status": "ignored"}), 200
