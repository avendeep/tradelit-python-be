# Quick Start Guide - Testing the Cron Job

## Prerequisites

1. MongoDB is running
2. Upstox authentication token is valid
3. Dependencies are installed

## Step-by-Step Testing

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install `apscheduler==3.10.4` and all other dependencies.

### 2. Start the Server

```bash
cd c:\Users\prade\Desktop\TradeLit\tradeLit_app
uvicorn main:app --reload
```

**Expected Output:**

```
🚀 Starting TradeLit API...
✅ Connected to MongoDB: tradeLit
✅ Loaded valid Upstox token from database (expires: ...)
✅ Scheduler initialized
✅ Scheduler started
✅ Added scheduled job: Fetch Option Chain Data (ID: fetch_option_chain)
✅ All scheduled tasks registered
⏰ Scheduler started with all tasks registered
INFO:     Application startup complete.
```

### 3. Add Instruments to Watchlist

Use the API to add instruments that you want to track:

```bash
# Using curl
curl -X POST "http://localhost:8000/api/v1/option-chain/watchlist" \
  -H "Content-Type: application/json" \
  -d '{
    "instrument_key": "NSE_INDEX|Nifty 50",
    "expiry_date": "2024-12-26"
  }'

# Or using Python requests
import requests

response = requests.post(
    "http://localhost:8000/api/v1/option-chain/watchlist",
    json={
        "instrument_key": "NSE_INDEX|Nifty 50",
        "expiry_date": "2024-12-26"
    }
)
print(response.json())
```

### 4. Watch the Logs

Within 1 minute, you should see the cron job start executing:

```
INFO:     🔄 Starting option chain fetch task...
INFO:     📋 Found 1 active watchlist entries
INFO:     📊 Fetching option chain for NSE_INDEX|Nifty 50 (Expiry: 2024-12-26)
INFO:     ✅ Saved option chain snapshot for NSE_INDEX|Nifty 50
INFO:     ✅ Option chain fetch task completed. Success: 1, Errors: 0
```

### 5. Verify Data in MongoDB

Check that data is being stored:

```javascript
// In MongoDB shell or MongoDB Compass
use tradeLit

// Check watchlist entries
db.instrument_watchlist.find().pretty()

// Check option chain snapshots
db.option_chain_snapshots.find().sort({timestamp: -1}).limit(5).pretty()

// Count total snapshots
db.option_chain_snapshots.countDocuments()

// Check latest snapshot
db.option_chain_snapshots.findOne({}, {sort: {timestamp: -1}})
```

### 6. View Watchlist via API

```bash
# Get all watchlist entries
curl "http://localhost:8000/api/v1/option-chain/watchlist"

# Get only active entries
curl "http://localhost:8000/api/v1/option-chain/watchlist?is_active=true"
```

## Troubleshooting

### Problem: No logs about cron job execution

**Solution:**

1. Check if scheduler started in startup logs
2. Verify task is registered
3. Wait a full minute (runs every minute on the minute)

### Problem: "Upstox token is not valid"

**Solution:**

1. Login via `/api/v1/upstox/login`
2. Complete OAuth flow
3. Restart the server to load new token

### Problem: "No active watchlist entries found"

**Solution:**

1. Add at least one instrument via POST `/api/v1/option-chain/watchlist`
2. Ensure `is_active` is `true`

### Problem: Import errors

**Solution:**

```bash
pip install --upgrade -r requirements.txt
```

## Testing Individual Task Manually

If you want to test the task without waiting for the schedule:

```python
# Create test script: test_cron_task.py
import asyncio
import sys
sys.path.insert(0, '.')

async def test_task():
    from app.db.mongodb import MongoDB
    from app.services.upstox_service import upstox_service
    from app.services.tasks.fetch_option_chain import fetch_option_chain_task
    
    # Connect to database
    await MongoDB.connect_db()
    
    # Load token
    await upstox_service.load_token_from_db()
    
    # Run task
    await fetch_option_chain_task()
    
    # Cleanup
    await MongoDB.close_db()

if __name__ == "__main__":
    asyncio.run(test_task())
```

Run it:

```bash
python test_cron_task.py
```

## Monitoring Tips

### Check Scheduler Status

The scheduler info is printed at startup. Look for:

- ✅ Scheduler initialized
- ✅ Scheduler started
- ✅ Added scheduled job: Fetch Option Chain Data

### Enable Debug Logging

In your code, set logging level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Query Recent Snapshots

```javascript
// Get snapshots from last hour
db.option_chain_snapshots.find({
  timestamp: {
    $gte: new Date(Date.now() - 60*60*1000)
  }
}).sort({timestamp: -1})

// Group by instrument to see count per instrument
db.option_chain_snapshots.aggregate([
  {
    $group: {
      _id: "$instrument_key",
      count: { $sum: 1 },
      latest: { $max: "$timestamp" }
    }
  }
])
```

## Common Expiry Dates

For testing, use upcoming expiry dates:

- **Weekly expiries**: Usually every Thursday
- **Monthly expiries**: Last Thursday of each month
- **Check Upstox API** for valid expiry dates

Example format: `YYYY-MM-DD` (e.g., `2024-12-26`)

## Success Indicators

✅ Server starts without errors  
✅ Scheduler logs show task registration  
✅ Task executes every minute (check logs)  
✅ Data appears in MongoDB `option_chain_snapshots`  
✅ Timestamps have no seconds (e.g., `2024-03-20T10:15:00`)  

## Next Steps

1. **Monitor for a few minutes** to ensure continuous execution
2. **Check MongoDB** for accumulated snapshots
3. **Add more instruments** to watchlist
4. **Configure market hours** if needed (uncomment `hour="9-15"` in scheduler.py)
5. **Build analytics** on top of stored data

## Support

If you encounter issues:

1. Check all logs carefully
2. Verify MongoDB connection
3. Ensure Upstox token is valid
4. Review `CRON_JOB_SYSTEM.md` for detailed documentation
