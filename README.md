# webhook-repo

Flask-based GitHub webhook receiver that listens to `action-repo` events,
stores them in MongoDB, and surfaces them in a clean UI that auto-refreshes
every 15 seconds.

---

## Project Structure

```
webhook-repo/
├── app/
│   ├── __init__.py      # Flask app factory
│   ├── config.py        # Configuration (reads .env)
│   ├── models.py        # Schema builder & serialisation helpers
│   ├── webhook.py       # POST /webhook  – receives GitHub events
│   └── events.py        # GET  /events   – serves events to UI
│                        # GET  /         – serves the HTML UI
├── templates/
│   └── index.html       # Single-page UI
├── static/
│   ├── css/style.css
│   └── js/app.js        # Polling logic (every 15 s)
├── run.py               # Entry point
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Setup

### 1. Clone & create a virtual environment
```bash
git clone https://github.com/<you>/webhook-repo.git
cd webhook-repo
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env and fill in your MONGO_URI and (optionally) GITHUB_SECRET
```

### 4. Run the server
```bash
python run.py
# Server starts on http://localhost:5000
```

---

## Exposing to GitHub with ngrok (for local development)

GitHub webhooks need a public URL. Use [ngrok](https://ngrok.com):

```bash
ngrok http 5000
```

Copy the `https://xxxx.ngrok-free.app` URL.

---

## Registering the Webhook on `action-repo`

1. Go to your `action-repo` on GitHub → **Settings → Webhooks → Add webhook**
2. **Payload URL**: `https://xxxx.ngrok-free.app/webhook`
3. **Content type**: `application/json`
4. **Secret**: paste the value you put in `GITHUB_SECRET` (optional but recommended)
5. **Which events?** → select **individual events**:
   - ✅ Pushes
   - ✅ Pull requests
6. Click **Add webhook**

---

## MongoDB Schema

| Field        | Type              | Details                                      |
|-------------|-------------------|----------------------------------------------|
| `_id`        | ObjectID          | MongoDB default                              |
| `request_id` | string            | Git commit hash (PUSH/MERGE) or PR number    |
| `author`     | string            | GitHub username                              |
| `action`     | string (enum)     | `"PUSH"` · `"PULL_REQUEST"` · `"MERGE"`     |
| `from_branch`| string            | Source branch                                |
| `to_branch`  | string            | Target branch                                |
| `timestamp`  | string (datetime) | UTC ISO-8601 – `"YYYY-MM-DDTHH:MM:SSZ"`     |

---

## API Endpoints

| Method | Path       | Description                           |
|--------|------------|---------------------------------------|
| POST   | `/webhook` | Receives raw GitHub webhook payloads  |
| GET    | `/events`  | Returns latest 50 events as JSON      |
| GET    | `/`        | Serves the UI                         |

---

## UI Display Formats

| Action         | Format                                                                 |
|----------------|------------------------------------------------------------------------|
| PUSH           | `"Author" pushed to "branch" on 1st April 2021 - 9:30 PM UTC`        |
| PULL_REQUEST   | `"Author" submitted a pull request from "A" to "B" on …`             |
| MERGE          | `"Author" merged branch "A" to "B" on …`                             |

---

## Production deployment

```bash
gunicorn -w 2 -b 0.0.0.0:5000 "app:create_app()"
```
