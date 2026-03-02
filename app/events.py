from flask import Blueprint, current_app, jsonify, render_template

from .models import serialize_event

events_bp = Blueprint("events", __name__)


@events_bp.route("/")
def index():
    """Serve the UI."""
    return render_template("index.html")


@events_bp.route("/events", methods=["GET"])
def get_events():
    """
    Return the latest GitHub events from MongoDB.
    The UI calls this endpoint every 15 seconds.
    """
    collection = current_app.db["events"]
    # Return the 50 most recent events, newest first
    docs = list(collection.find().sort("timestamp", -1).limit(50))
    events = [serialize_event(doc) for doc in docs]
    return jsonify(events), 200


@events_bp.route("/debug", methods=["GET"])
def debug():
    """Debug endpoint to check MongoDB connection and data."""
    try:
        collection = current_app.db["events"]
        count = collection.count_documents({})
        sample = list(collection.find().sort("_id", -1).limit(3))
        return jsonify({
            "status": "ok",
            "total_events": count,
            "latest_3": [serialize_event(doc) for doc in sample]
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
