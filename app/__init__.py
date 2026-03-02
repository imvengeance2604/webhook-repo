from flask import Flask
from pymongo import MongoClient
from .config import Config


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(Config)

    # MongoDB connection
    client = MongoClient(app.config["MONGO_URI"])
    app.db = client[app.config["MONGO_DB_NAME"]]

    # Register blueprints
    from .webhook import webhook_bp
    from .events import events_bp

    app.register_blueprint(webhook_bp)
    app.register_blueprint(events_bp)

    return app
