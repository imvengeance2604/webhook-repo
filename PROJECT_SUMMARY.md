# GitHub Webhook Monitoring System - Complete Implementation

## Project Overview

A complete GitHub webhook monitoring system that captures and displays PUSH, PULL_REQUEST, and MERGE events from source repositories in real-time.

**Architecture:**
- Flask backend receiving GitHub webhooks
- Local MongoDB for event storage
- Real-time dashboard with 15-second polling
- Event deduplication and formatting
- HMAC-SHA256 webhook signature validation

---

## Repository Structure

### webhook-repo (Receiver & Dashboard)
```
webhook-repo/
├── app/
│   ├── __init__.py          # Flask factory, MongoDB initialization
│   ├── config.py            # Environment configuration management
│   ├── webhook.py           # GitHub webhook receiver & parser
│   ├── events.py            # Event API endpoints
│   └── models.py            # Event serialization & building
├── static/
│   ├── css/style.css        # GitHub-themed dashboard styling
│   └── js/app.js            # Real-time polling & event rendering
├── templates/
│   └── index.html           # Dashboard UI
├── run.py                   # Flask application entry point
├── .env                     # Local environment configuration (local MongoDB)
├── .env.example             # Configuration template
├── .gitignore               # Git exclusions
├── README.md                # Setup & API documentation
├── SETUP_LOCAL_MONGODB.md   # MongoDB installation guide
├── MIGRATION_GUIDE.md       # Atlas to Local migration docs
└── requirements.txt         # Python dependencies
```

### action-repo (Event Source)
```
action-repo/
├── main branch              # Pushes trigger PUSH events
├── feature branch           # Merge triggers MERGE event
├── .github/workflows/       # (Optional) CI/CD workflows
├── README.md                # Setup instructions
└── test.txt, feature.txt    # Test files for triggering events
```

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Backend | Flask | 3.1.3 |
| Database | MongoDB | 7.2.0 (Community) |
| Database Driver | PyMongo | 4.16.0 |
| Frontend | HTML/CSS/JavaScript | ES6+ |
| Environment | Python | 3.11.9 |
| Public Tunnel | ngrok | 3.36.1 |
| Version Control | Git | 2.40+ |

---

## Key Features

### 1. GitHub Webhook Receiver
- ✅ HMAC-SHA256 signature validation
- ✅ Automatic GitHub IP whitelisting support
- ✅ Handles PUSH, PULL_REQUEST, and MERGE events
- ✅ Robust error handling

### 2. Event Processing
- ✅ PUSH detection (direct commits + merge commits)
- ✅ PULL_REQUEST capture (open/reopen/synchronize)
- ✅ MERGE detection via regex pattern matching
- ✅ Branch extraction from commit refs
- ✅ ISO-8601 timestamp parsing

### 3. Event Storage
- ✅ MongoDB document schema for structured storage
- ✅ 50 most recent events retrieval
- ✅ Event deduplication by timestamp + type
- ✅ ObjectID to string serialization

### 4. Real-Time Dashboard
- ✅ 15-second polling with countdown timer
- ✅ Live status indicator (green/red)
- ✅ Event statistics (total, PUSH, PR, MERGE)
- ✅ Color-coded event badges
- ✅ Dark GitHub-inspired theme
- ✅ XSS prevention via HTML escaping

### 5. Webhook Events

**PUSH Event:**
```json
{
  "type": "PUSH",
  "actor": "username",
  "repository": "repo-name",
  "branch": "main",
  "message": "User username pushed to main in repo-name",
  "timestamp": "2026-03-02T19:15:30Z"
}
```

**PULL_REQUEST Event:**
```json
{
  "type": "PULL_REQUEST",
  "actor": "username",
  "action": "opened",
  "pr_number": 42,
  "repository": "repo-name",
  "message": "User username opened pull request #42 in repo-name",
  "timestamp": "2026-03-02T19:16:45Z"
}
```

**MERGE Event:**
```json
{
  "type": "MERGE",
  "actor": "username",
  "repository": "repo-name",
  "message": "User username merged into main in repo-name",
  "timestamp": "2026-03-02T19:17:20Z"
}
```

---

## Setup & Deployment

### Quick Start (Local Development)

1. **Install MongoDB:**
   ```powershell
   # Download from https://www.mongodb.com/try/download/community
   # Run installer, create C:\mongodb\data and C:\mongodb\logs
   & 'C:\Program Files\MongoDB\Server\7.2\bin\mongod.exe' --dbpath 'C:\mongodb\data'
   ```

2. **Clone webhook-repo:**
   ```powershell
   git clone https://github.com/imvengeance2604/webhook-repo.git
   cd webhook-repo
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```powershell
   copy .env.example .env
   # .env already configured for local MongoDB
   ```

4. **Start Flask:**
   ```powershell
   python run.py
   # Server runs on http://127.0.0.1:5000
   ```

5. **Configure GitHub webhook:**
   - Repository Settings → Webhooks → Add webhook
   - Payload URL: `https://your-tunnel-url.ngrok.io/webhook`
   - Content type: `application/json`
   - Events: Push events, Pull requests
   - Secret: Set in `.env` GITHUB_SECRET

6. **Access Dashboard:**
   - Open http://127.0.0.1:5000 in browser
   - Watch events appear in real-time

### Production Deployment

See `README.md` for detailed production deployment options:
- Gunicorn + Nginx
- Docker containerization
- Cloud platforms (Heroku, AWS, Azure)

---

## API Endpoints

### POST /webhook
Receives GitHub webhook payloads
- **Authentication:** HMAC-SHA256 signature validation
- **Returns:** 200 OK on success
- **Events Handled:** PUSH, PULL_REQUEST, MERGE

### GET /events
Retrieves recent events
- **Returns:** JSON array of up to 50 events (most recent first)
- **Response:** `[{type, actor, message, timestamp, ...}, ...]`

### GET /
Serves dashboard UI
- **Returns:** HTML page with CSS and JavaScript
- **Real-time:** Updates via JavaScript polling every 15 seconds

---

## MongoDB Schema

### Events Collection
```javascript
{
  "_id": ObjectId(),
  "type": "PUSH|PULL_REQUEST|MERGE",
  "actor": "github_username",
  "repository": "repo_name",
  "branch": "branch_name",
  "action": "opened|synchronize|etc",  // PR only
  "pr_number": 42,                     // PR only
  "message": "Formatted event message",
  "timestamp": "2026-03-02T19:15:30Z"
}
```

---

## Environment Configuration

### .env File
```env
# Flask session key
SECRET_KEY=your-flask-secret-key

# MongoDB connection (LOCAL)
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=github_events

# GitHub webhook secret (optional, for signature validation)
GITHUB_SECRET=
```

---

## Migration from MongoDB Atlas

This project was originally using MongoDB Atlas cloud database but migrated to local MongoDB for development.

**Reasons for Migration:**
- SSL/TLS handshake failures
- Simplified development setup
- Faster event processing
- No authentication overhead

**What Changed:**
- Connection string only (no code changes)
- Configuration files updated
- Added documentation

See `MIGRATION_GUIDE.md` for detailed information.

---

## Testing & Verification

### Manual Testing

1. **Test PUSH event:**
   ```powershell
   cd action-repo
   echo "test" >> file.txt
   git add file.txt
   git commit -m "Test push"
   git push origin main
   ```

2. **Test MERGE event:**
   ```powershell
   git checkout main
   git merge feature -m "Test merge"
   git push origin main
   ```

3. **Verify in Dashboard:**
   - Check http://127.0.0.1:5000
   - Events should appear within 15 seconds
   - Status indicator should be green (Live)

### Webhook Testing

Use provided test commands in `ONE_LINER_COMMANDS.md` to quickly test all event types.

---

## Project Files Summary

### Configuration
- `.env` - Local environment configuration
- `.env.example` - Configuration template
- `.gitignore` - Git exclusions (*.env, __pycache__)
- `requirements.txt` - Python dependencies

### Documentation
- `README.md` - Complete setup & usage guide
- `SETUP_LOCAL_MONGODB.md` - MongoDB installation guide
- `MIGRATION_GUIDE.md` - Atlas to Local migration
- `TESTING_GUIDE.md` - Step-by-step testing procedures
- `ONE_LINER_COMMANDS.md` - Quick test commands

### Backend Code (app/)
- `__init__.py` - Flask factory, MongoDB client
- `config.py` - Configuration management
- `webhook.py` - GitHub webhook handler (213 lines)
- `events.py` - API endpoints
- `models.py` - Event serialization

### Frontend Code
- `static/js/app.js` - Real-time polling (190+ lines)
- `static/css/style.css` - Dark GitHub theme
- `templates/index.html` - Dashboard UI
- `run.py` - Application entry point

### Test Files
- `test.txt` - Push event test file
- `feature.txt` - Merge event test file

---

## Deployment Checklist

- [ ] MongoDB installed and running
- [ ] Flask dependencies installed
- [ ] `.env` file configured with GitHub secret
- [ ] ngrok tunnel established for public access
- [ ] GitHub webhook configured with tunnel URL
- [ ] Dashboard accessible at http://127.0.0.1:5000
- [ ] Test PUSH event triggers in dashboard
- [ ] Test MERGE event triggers in dashboard
- [ ] All event types displaying correctly
- [ ] No MongoDB connection errors

---

## Troubleshooting

### "Connection refused" from Flask
```powershell
# Check MongoDB is running
Get-Service MongoDB
Start-Service MongoDB
```

### Dashboard shows "Error" status
```powershell
# Check Flask terminal for error messages
# Common causes:
# 1. MongoDB not running
# 2. Wrong MONGO_URI in .env
# 3. Invalid GITHUB_SECRET
```

### Webhook not triggering
- Verify tunnel URL in GitHub webhook settings
- Check webhook delivery logs in GitHub
- Ensure GITHUB_SECRET matches (if set)
- Verify Flask is running on correct port

### Events not appearing in dashboard
- Refresh browser (F5)
- Check Flask logs for webhook receipt
- Verify event type is PUSH, PULL_REQUEST, or MERGE
- Check MongoDB is storing events (mongosh)

---

## Future Enhancements

- [ ] Event filtering by repository, actor, type
- [ ] Event search and pagination
- [ ] WebSocket support for true real-time updates
- [ ] Event export (CSV, JSON)
- [ ] Multiple repository monitoring
- [ ] Email/Slack notifications
- [ ] User authentication for sensitive webhooks
- [ ] Event analytics and statistics
- [ ] Automatic event retention policies

---

## License

Open source - Free to use and modify

---

## Version Information

- **Project Version:** 1.0.0
- **Python Version:** 3.11.9
- **Flask Version:** 3.1.3
- **MongoDB Version:** 7.2.0 Community
- **Last Updated:** March 2, 2026

---

## Support

For issues or questions:
1. Check `README.md` for common solutions
2. Review `MIGRATION_GUIDE.md` for MongoDB setup
3. See `TESTING_GUIDE.md` for verification steps
4. Check Flask terminal logs for error messages

---

**✅ Project Complete & Ready for Use**

All features implemented, tested, and documented. Local MongoDB fully configured. Ready for webhook event monitoring!
