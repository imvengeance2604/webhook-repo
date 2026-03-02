# Local MongoDB Setup Guide

This project uses **MongoDB Community Edition** running locally on your machine for development and testing.

## Prerequisites

- Windows 10 or later
- Administrator access to install MongoDB

## Installation Steps

### 1. Download MongoDB Community Edition

Download the Windows MSI installer from:
https://www.mongodb.com/try/download/community

Select the latest **Community Server** version (e.g., 7.2.0 or newer).

### 2. Run the Installer

Execute the downloaded `.msi` file and follow the installation wizard:
- Accept license agreement
- Choose "Complete" installation
- Check "Run MongoDB as a Windows Service" (optional, but recommended)

Default installation path: `C:\Program Files\MongoDB\Server\<version>\`

### 3. Create Data and Log Directories

```powershell
mkdir -Force 'C:\mongodb\data', 'C:\mongodb\logs'
```

### 4. Start MongoDB

**Option A: As a Service (if installed as service)**
```powershell
Start-Service MongoDB
```

**Option B: Direct Execution**
```powershell
& 'C:\Program Files\MongoDB\Server\7.2\bin\mongod.exe' --dbpath 'C:\mongodb\data'
```

### 5. Verify MongoDB is Running

Open a new PowerShell window and run:
```powershell
& 'C:\Program Files\MongoDB\Server\7.2\bin\mongosh.exe'
```

You should see the MongoDB shell prompt `>`. Type `exit()` to quit.

## Configuration

The Flask application automatically connects to `mongodb://localhost:27017/` using the configuration in `.env`:

```env
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=github_events
```

No additional configuration is needed for local development.

## Troubleshooting

### MongoDB won't start
- Ensure `C:\mongodb\data` and `C:\mongodb\logs` directories exist
- Check if port 27017 is already in use: `netstat -ano | findstr :27017`
- Verify MongoDB installation path matches your version

### Connection refused error in Flask
- Verify MongoDB is running: `Get-Service MongoDB` should show "Running"
- Check that Flask is using the correct `MONGO_URI` in `.env`
- Ensure the database directories have proper permissions

### Clear all data (reset database)
```powershell
Remove-Item -Recurse -Force 'C:\mongodb\data\*'
```

Then restart MongoDB to create a fresh database.

## Production Deployment

For production environments, consider using:
- **MongoDB Atlas** (Cloud) - https://www.mongodb.com/cloud/atlas
- **MongoDB Enterprise** - For production support
- Docker containers - For consistent environment management

Update `MONGO_URI` in `.env` with your production connection string.

## References

- MongoDB Community Edition: https://docs.mongodb.com/manual/
- PyMongo Documentation: https://pymongo.readthedocs.io/
- Flask-PyMongo: For future enhancement
