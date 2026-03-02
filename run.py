"""Application entry point.

Flask application startup script. Initializes the app and starts
the development server on localhost:5000.

Run with: python run.py
"""

from app import create_app

# Create and configure Flask application
app = create_app()

if __name__ == "__main__":
    # Run Flask server on port 5000
    # debug=False uses production mode to avoid socket issues on Windows
    app.run(debug=False, port=5000)
