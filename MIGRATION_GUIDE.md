# Migration: MongoDB Atlas to Local MongoDB

This guide documents the migration from MongoDB Atlas (cloud) to local MongoDB Community Edition.

## Why This Migration?

**Previous Setup (MongoDB Atlas):**
- Cloud-hosted MongoDB with SSL/TLS encryption
- Advantages: Managed service, automatic backups, accessible from anywhere
- Issues encountered: SSL/TLS handshake failures, connection timeouts

**Current Setup (Local MongoDB):**
- Self-hosted MongoDB running locally
- Advantages: No SSL overhead, faster development, full control
- Use case: Development, testing, and webhook event logging

## What Changed

### Configuration Files

**Before:**
```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?tlsAllowInvalidCertificates=true&ssl=true
```

**After:**
```env
MONGO_URI=mongodb://localhost:27017/
```

### Environment Setup

1. **No authentication needed** for local development
2. **No SSL/TLS certificates** required
3. **Simpler connection string** - just host:port

### Code Changes

**None required!** The application code remains unchanged:
- `pymongo` library works identically with both local and cloud MongoDB
- Connection string format is the only difference
- All database operations (insert, find, update) work the same way

## Migration Steps

1. Install MongoDB Community Edition locally (see `SETUP_LOCAL_MONGODB.md`)
2. Update `.env` with new local connection string
3. Start MongoDB service
4. Restart Flask application
5. Verify connection by checking dashboard status

## Data Migration

If you need to migrate data from MongoDB Atlas to local MongoDB:

```powershell
# Export data from Atlas (requires mongodump)
mongodump --uri "mongodb+srv://..." --out ./atlas_backup

# Import to local MongoDB
mongorestore ./atlas_backup
```

Note: The current implementation starts fresh without existing data.

## Reverting to MongoDB Atlas

If you need to switch back:

1. Update `.env` with Atlas connection string:
   ```env
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
   ```

2. Restart Flask application
3. No code changes needed

## Performance Comparison

| Aspect | MongoDB Atlas | Local MongoDB |
|--------|---------------|---------------|
| Setup Time | ~5 minutes | ~2 minutes |
| Network Latency | High (cloud) | None (local) |
| SSL Overhead | Yes | No |
| Development Speed | Medium | Fast |
| Accessibility | Anywhere | Local only |
| Cost | Paid (after free tier) | Free |

## Production Recommendations

For production deployment:
1. Use MongoDB Atlas or managed MongoDB service
2. Configure proper SSL/TLS certificates
3. Implement authentication and authorization
4. Enable backup and recovery
5. Monitor performance and security

Update production `.env` accordingly:
```env
MONGO_URI=mongodb+srv://prod_user:prod_pass@prod-cluster.mongodb.net/?retryWrites=true&w=majority
```

## Troubleshooting

**Issue:** Flask shows "Connection refused"
- Ensure MongoDB is running: `Get-Service MongoDB`
- Check port 27017: `netstat -ano | findstr :27017`

**Issue:** Previous Atlas events not showing
- Local MongoDB is a fresh database
- Historical data from Atlas is not automatically migrated
- This is by design for testing environments

**Issue:** Need to go back to Atlas
- Just update `.env` and restart Flask
- No database migration needed
- Application handles both seamlessly

## Summary

✅ **Completed:**
- Local MongoDB installation and configuration
- Updated Flask configuration files
- Tested webhook event capture
- Documentation for future reference

🎯 **Result:**
- Faster development cycle
- No SSL/TLS connection issues
- Cleaner setup process
- Full local control for testing
