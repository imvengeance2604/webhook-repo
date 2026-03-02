"""Event model and serialization functions.

Provides functions for building GitHub event documents and serializing
MongoDB documents for JSON response.
"""

from datetime import datetime, timezone


def serialize_event(event: dict) -> dict:
    """Convert MongoDB document to JSON-serializable format.
    
    MongoDB ObjectIDs cannot be directly serialized to JSON. This function
    converts the _id field to a string representation.
    
    Args:
        event: MongoDB document dict with _id field
        
    Returns:
        dict: Event document with _id converted to string
    """
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
    """Build a properly formatted event document for MongoDB storage.
    
    Constructs a document containing all metadata about a GitHub event
    (push, pull request, or merge) with ISO-8601 formatted timestamp.
    
    Args:
        request_id: Unique identifier for the event (commit hash or PR number)
        author: GitHub username of the person who triggered the event
        action: Event type (PUSH, PULL_REQUEST, or MERGE)
        from_branch: Source branch name
        to_branch: Destination branch name
        timestamp: Event timestamp as datetime object (defaults to current UTC time)
        
    Returns:
        dict: Event document with fields: request_id, author, action, 
              from_branch, to_branch, timestamp (ISO-8601 UTC string)
    """
    # Use current UTC time if timestamp not provided
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    # Build and return event document with ISO-8601 formatted timestamp
    return {
        "request_id": request_id,
        "author": author,
        "action": action,
        "from_branch": from_branch,
        "to_branch": to_branch,
        # Format: "2026-03-02T14:35:00Z"
        "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
