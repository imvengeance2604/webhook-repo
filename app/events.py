from flask import Blueprint, current_app, jsonify, render_template

from .models import serialize_event

events_bp = Blueprint("events", __name__)


@events_bp.route("/")
def index():
    return render_template("index.html")


@events_bp.route("/events", methods=["GET"])
def get_events():
    collection = current_app.db["events"]
    docs = list(collection.find().sort("timestamp", -1).limit(50))
    events = [serialize_event(doc) for doc in docs]
    return jsonify(events), 200
