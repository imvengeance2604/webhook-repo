# webhook-repo

Receives GitHub webhooks and stores events in MongoDB.

## Setup

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your MongoDB connection string:
```
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGO_DB_NAME=github_events
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
