# webhook-repo

Flask backend application that receives GitHub webhook events and displays them in a real-time dashboard.

## Features

- **GitHub Webhook Receiver**: Validates and processes PUSH, PULL_REQUEST, and MERGE events
- **MongoDB Storage**: Persists events with metadata
- **REST API**: JSON endpoint for retrieving stored events
- **Real-time Dashboard**: Web UI that polls for new events every 15 seconds
- **Secure**: HMAC-SHA256 signature validation

## Setup

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your MongoDB connection string and GitHub secret:

```
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority
MONGO_DB_NAME=github_events
GITHUB_SECRET=your-webhook-secret
```

## Run

```bash
python run.py
```

Server runs on `http://localhost:5000`

## Endpoints

- `POST /webhook` - Receives GitHub webhook payloads
- `GET /events` - Returns stored events as JSON
- `GET /` - UI dashboard
