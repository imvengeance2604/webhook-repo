import hashlib
import hmac
import json
from datetime import datetime, timezone
import re

from flask import Blueprint, current_app, jsonify, request

from .models import build_event

webhook_bp = Blueprint("webhook", __name__)


def verify_signature(payload_bytes: bytes, sig_header: str) -> bool:
    secret = current_app.config.get("GITHUB_SECRET", "")
    if not secret:
        return True

    if not sig_header or not sig_header.startswith("sha256="):
        return False

    expected = hmac.new(
        secret.encode(), payload_bytes, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", sig_header)


def parse_timestamp(ts_str: str = None) -> datetime:
    if ts_str:
        try:
            return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(timezone.utc)


@webhook_bp.route("/webhook", methods=["POST"])
def github_webhook():
    payload_bytes = request.get_data()
    sig = request.headers.get("X-Hub-Signature-256", "")
    if not verify_signature(payload_bytes, sig):
        return jsonify({"error": "Invalid signature"}), 403

    github_event = request.headers.get("X-GitHub-Event", "")
    payload = request.get_json(force=True) or {}

    event_doc = None

    if github_event == "push":
        if payload.get("deleted"):
            return jsonify({"status": "ignored"}), 200

        ref = payload.get("ref", "")
        to_branch = ref.split("/")[-1]
        author = payload.get("pusher", {}).get("name") or payload.get("sender", {}).get("login", "unknown")
        head_commit = payload.get("head_commit") or {}
        request_id = head_commit.get("id", payload.get("after", ""))
        timestamp = parse_timestamp(head_commit.get("timestamp"))

        commit_message = head_commit.get("message", "")
        if commit_message.startswith("Merge"):
            from_branch = payload.get("before", "")
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
                from_branch=to_branch,
                to_branch=to_branch,
                timestamp=timestamp,
            )

    elif github_event == "pull_request":
        pr = payload.get("pull_request", {})
        pr_action = payload.get("action", "")

        if pr_action == "closed" and pr.get("merged"):
            action = "MERGE"
        elif pr_action in ("opened", "reopened", "synchronize"):
            action = "PULL_REQUEST"
        else:
            return jsonify({"status": "ignored"}), 200

        author = pr.get("user", {}).get("login") or payload.get("sender", {}).get("login", "unknown")
        from_branch = pr.get("head", {}).get("ref", "")
        to_branch = pr.get("base", {}).get("ref", "")
        request_id = str(pr.get("number", ""))
        timestamp = parse_timestamp(pr.get("merged_at") if action == "MERGE" else pr.get("created_at"))

        event_doc = build_event(
            request_id=request_id,
            author=author,
            action=action,
            from_branch=from_branch,
            to_branch=to_branch,
            timestamp=timestamp,
        )

    else:
        return jsonify({"status": "ignored"}), 200

    if event_doc:
        current_app.db["events"].insert_one(event_doc)
        event_doc.pop("_id", None)
        return jsonify({"status": "ok", "event": event_doc}), 201

    return jsonify({"status": "ignored"}), 200
