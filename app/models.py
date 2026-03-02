from datetime import datetime, timezone


def serialize_event(event: dict) -> dict:
    event["_id"] = str(event["_id"])
    return event


def build_event(
    request_id: str,
    author: str,
    action: str,
    from_branch: str,
    to_branch: str,
    timestamp: datetime = None,
) -> dict:
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
