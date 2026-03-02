"""REST API endpoints for the event dashboard.

Provides HTTP routes for serving the UI and retrieving stored GitHub events
from the MongoDB database.
"""

from flask import Blueprint, current_app, jsonify, render_template

from .models import serialize_event

events_bp = Blueprint("events", __name__)


@events_bp.route("/")
def index():
    """Serve the main dashboard HTML page.
    
    Returns:
        HTML: index.html template with embedded JavaScript for polling
    """
    return render_template("index.html")


@events_bp.route("/events", methods=["GET"])
def get_events():
    """Retrieve recent GitHub events from MongoDB.
    
    Returns the 50 most recent events from the database, sorted by
    timestamp in descending order (newest first).
    
    Returns:
        JSON: Array of event documents with fields:
        - _id: MongoDB ObjectID as string
        - request_id: Commit hash or PR number
        - author: GitHub username
        - action: PUSH, PULL_REQUEST, or MERGE
        - from_branch: Source branch
        - to_branch: Destination branch
        - timestamp: ISO-8601 UTC timestamp
    """
    # Query MongoDB for recent events, sorted newest first
    collection = current_app.db["events"]
    docs = list(collection.find().sort("timestamp", -1).limit(50))
    
    # Convert ObjectIDs to strings for JSON serialization
    events = [serialize_event(doc) for doc in docs]
    
    return jsonify(events), 200
