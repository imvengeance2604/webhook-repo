from datetime import datetime, timezone
from bson import ObjectId


def serialize_event(event: dict) -> dict:
    """Convert MongoDB document to JSON-serialisable dict."""
    event["_id"] = str(event["_id"])
    return event


def build_event(
    request_id: str,
    author: str,
    action: str,
    from_branch: str,
    to_branch: str,
    timestamp: datetime | None = None,
) -> dict:
    """
    Build a GitHub event document matching the required schema:
    {
        request_id : string  (commit hash or PR id)
        author     : string
        action     : string  ENUM["PUSH", "PULL_REQUEST", "MERGE"]
        from_branch: string
        to_branch  : string
        timestamp  : string  (datetime UTC)
    }
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    return {
        "request_id": request_id,
        "author": author,
        "action": action,
        "from_branch": from_branch,
        "to_branch": to_branch,
        "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
