"""Application configuration management.

Loads environment variables from .env file and provides Flask configuration
for database connection, secrets, and GitHub webhook validation.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Flask application configuration class.
    
    Reads settings from environment variables with sensible defaults.
    Configure these in .env file for deployment.
    """
    # Flask session encryption key
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key")
    
    # MongoDB Atlas connection string
    # Format: mongodb+srv://username:password@cluster.mongodb.net/
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
    
    # MongoDB database name for storing events
    MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "github_events")
    
    # GitHub webhook secret for HMAC signature validation
    # Should match the secret configured in GitHub webhook settings
    GITHUB_SECRET = os.environ.get("GITHUB_SECRET", "")
