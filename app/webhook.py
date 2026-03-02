import hashlib
import hmac
import json
from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request

from .models import build_event

webhook_bp = Blueprint("webhook", __name__)

ALLOWED_ACTIONS = {"PUSH", "PULL_REQUEST", "MERGE"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _verify_signature(payload_bytes: bytes, sig_header: str) -> bool:
    """Validate GitHub HMAC-SHA256 webhook signature (optional but recommended)."""
    secret = current_app.config.get("GITHUB_SECRET", "")
    if not secret:
        return True  # skip verification if no secret is configured

    if not sig_header or not sig_header.startswith("sha256="):
        return False

    expected = hmac.new(
        secret.encode(), payload_bytes, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", sig_header)


def _parse_timestamp(ts_str: str | None) -> datetime:
    """Parse ISO-8601 timestamp from GitHub; fall back to UTC now."""
    if ts_str:
        try:
            # GitHub sends timestamps like "2021-04-01T09:30:00Z"
            return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Webhook endpoint
# ---------------------------------------------------------------------------

@webhook_bp.route("/webhook", methods=["POST"])
def github_webhook():
    # ── 1. Signature verification ──────────────────────────────────────────
    payload_bytes = request.get_data()
    sig = request.headers.get("X-Hub-Signature-256", "")
    if not _verify_signature(payload_bytes, sig):
        return jsonify({"error": "Invalid signature"}), 403

    # ── 2. Determine event type ────────────────────────────────────────────
    github_event = request.headers.get("X-GitHub-Event", "")
    payload = request.get_json(force=True) or {}

    event_doc = None

    # ── PUSH ────────────────────────────────────────────────────────────────
    if github_event == "push":
        # Ignore branch-delete pushes (ref is gone)
        if payload.get("deleted"):
            return jsonify({"status": "ignored", "reason": "branch deleted"}), 200

        ref = payload.get("ref", "")          # e.g. "refs/heads/main"
        to_branch = ref.split("/")[-1]
        author = (
            payload.get("pusher", {}).get("name")
            or payload.get("sender", {}).get("login", "unknown")
        )
        head_commit = payload.get("head_commit") or {}
        request_id = head_commit.get("id", payload.get("after", ""))
        timestamp = _parse_timestamp(head_commit.get("timestamp"))

        # Detect merge-via-push: head commit message starts with "Merge"
        commit_message = head_commit.get("message", "")
        if commit_message.startswith("Merge"):
            before_ref = payload.get("before", "")
            from_branch = before_ref  # best-effort; GitHub merges may not expose source branch
            # Try to parse "Merge branch 'X' into Y" pattern
            import re
            m = re.search(r"Merge branch ['\"](.+?)['\"]", commit_message)
            if m:
                from_branch = m.group(1)

            event_doc = build_event(
                request_id=request_id,
                author=author,
                action="MERGE",
                from_branch=from_branch,
                to_branch=to_branch,
                timestamp=timestamp,
            )
        else:
            event_doc = build_event(
                request_id=request_id,
                author=author,
                action="PUSH",
                from_branch=to_branch,   # same branch for push
                to_branch=to_branch,
                timestamp=timestamp,
            )

    # ── PULL REQUEST ─────────────────────────────────────────────────────────
    elif github_event == "pull_request":
        pr = payload.get("pull_request", {})
        pr_action = payload.get("action", "")

        # Map GitHub PR actions to our schema actions
        if pr_action == "closed" and pr.get("merged"):
            action = "MERGE"
        elif pr_action in ("opened", "reopened", "synchronize"):
            action = "PULL_REQUEST"
        else:
            return jsonify({"status": "ignored", "reason": f"pr action '{pr_action}' not tracked"}), 200

        author = (
            pr.get("user", {}).get("login")
            or payload.get("sender", {}).get("login", "unknown")
        )
        from_branch = pr.get("head", {}).get("ref", "")
        to_branch = pr.get("base", {}).get("ref", "")
        request_id = str(pr.get("number", ""))
        timestamp = _parse_timestamp(
            pr.get("merged_at") if action == "MERGE" else pr.get("created_at")
        )

        event_doc = build_event(
            request_id=request_id,
            author=author,
            action=action,
            from_branch=from_branch,
            to_branch=to_branch,
            timestamp=timestamp,
        )

    else:
        return jsonify({"status": "ignored", "reason": f"event '{github_event}' not tracked"}), 200

    # ── 3. Persist to MongoDB ──────────────────────────────────────────────
    if event_doc:
        current_app.db["events"].insert_one(event_doc)
        # Remove ObjectId before returning (not JSON-serialisable)
        event_doc.pop("_id", None)
        return jsonify({"status": "ok", "event": event_doc}), 201

    return jsonify({"status": "ignored"}), 200
