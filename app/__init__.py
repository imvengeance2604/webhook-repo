"""Flask application factory and initialization.

Creates the Flask application instance, configures MongoDB connection,
and registers API blueprints for webhook and event endpoints.
"""

from flask import Flask
from pymongo import MongoClient
from .config import Config


def create_app():
    """Initialize and configure the Flask application.
    
    Creates a Flask app instance with the following setup:
    - Loads configuration from environment variables via Config class
    - Establishes MongoDB Atlas connection
    - Registers blueprints for webhook receiver and event API endpoints
    
    Returns:
        Flask: Configured Flask application instance with MongoDB connection
    """
    # Create Flask app with template and static folder paths
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    
    # Load configuration from Config class (reads .env file)
    app.config.from_object(Config)

    # Initialize MongoDB connection
    client = MongoClient(app.config["MONGO_URI"])
    app.db = client[app.config["MONGO_DB_NAME"]]

    # Import and register blueprints for API routes
    from .webhook import webhook_bp
    from .events import events_bp

    app.register_blueprint(webhook_bp)
    app.register_blueprint(events_bp)

    return app
