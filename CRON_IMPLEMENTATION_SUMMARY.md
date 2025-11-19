# Cron Job Implementation Summary

## ✅ What Was Implemented

A scalable, production-ready cron job system that:

1. **Fetches option chain data every minute** from Upstox API
2. **Stores data in MongoDB** with timestamps (hour and minute only, no seconds)
3. **Reads instrument keys from watchlist** in the database
4. **Starts automatically** when the server starts
5. **Easy to extend** for future tasks

## 📁 Files Created/Modified

### New Files Created

1. `app/services/scheduler.py` - Main scheduler service with APScheduler
2. `app/services/tasks/__init__.py` - Tasks module initialization
3. `app/services/tasks/fetch_option_chain.py` - Option chain fetch task
4. `CRON_JOB_SYSTEM.md` - Complete documentation

### Modified Files

1. `requirements.txt` - Added `apscheduler==3.10.4`
2. `main.py` - Integrated scheduler lifecycle
3. `app/models/trading.py` - Added `OptionChainSnapshotModel`

## 🏗️ Architecture

```
TradeLit API
├── Scheduler Service (scheduler.py)
│   ├── Start/Stop scheduler
│   ├── Register tasks
│   └── Manage jobs
│
└── Tasks (services/tasks/)
    └── fetch_option_chain.py
        ├── Read from: instrument_watchlist (MongoDB)
        ├── Fetch: Option chain from Upstox API
        └── Store in: option_chain_snapshots (MongoDB)
```

## 🎯 Key Features

### Scalable Design

- **Modular**: Each task is in its own file
- **Centralized Registration**: All tasks registered in one place
- **Easy to Add New Tasks**: Just create a file and register it

### Robust Error Handling

- Token validation before API calls
- Individual error handling per instrument
- Comprehensive logging
- Graceful degradation

### Smart Configuration

- IST timezone support
- Market hours filtering (optional)
- Configurable schedules
- Prevents duplicate runs

## 📊 Data Flow

```
1. Timer triggers (every minute)
   ↓
2. Check Upstox token validity
   ↓
3. Query MongoDB for active watchlist entries
   ↓
4. For each instrument:
   - Fetch option chain from Upstox API
   - Create timestamp (hour:minute only)
   - Store snapshot in MongoDB
   ↓
5. Log results (success/error counts)
```

## 🚀 Usage

### Start the Server

```bash
uvicorn main:app --reload
```

The scheduler will:

- Start automatically
- Register all tasks
- Begin execution based on schedule

### Add an Instrument to Watchlist

```bash
POST /api/v1/option-chain/watchlist
{
  "instrument_key": "NSE_INDEX|Nifty 50",
  "expiry_date": "2024-03-28"
}
```

The cron job will automatically fetch data for this instrument every minute.

## 📝 Database Schema

### Collection: `option_chain_snapshots`

```json
{
  "_id": "ObjectId",
  "instrument_key": "NSE_INDEX|Nifty 50",
  "expiry_date": "2024-03-28",
  "timestamp": "2024-03-20T10:15:00",  // No seconds!
  "data": { /* complete option chain data */ },
  "created_at": "2024-03-20T10:15:23.456Z"
}
```

### Collection: `instrument_watchlist` (existing)

```json
{
  "_id": "ObjectId",
  "instrument_key": "NSE_INDEX|Nifty 50",
  "expiry_date": "2024-03-28",
  "is_active": true,
  "created_at": "...",
  "updated_at": "..."
}
```

## 🔧 Adding New Tasks (Simple!)

### Step 1: Create Task File

```python
# app/services/tasks/my_new_task.py
async def my_new_task():
    logger.info("🔄 Running my new task...")
    # Your logic here
    logger.info("✅ Task completed")
```

### Step 2: Register in Scheduler

```python
# In app/services/scheduler.py → register_tasks()
from app.services.tasks.my_new_task import my_new_task

self.add_job(
    func=my_new_task,
    job_id="my_task",
    name="My New Task",
    trigger="cron",
    minute="*/5",  # Every 5 minutes
)
```

Done! The task will run automatically.

## 📅 Schedule Examples

```python
# Every minute
minute="*"

# Every 5 minutes
minute="*/5"

# Every hour at :30
minute="30"

# Market hours only (9 AM - 3 PM)
hour="9-15", minute="*"

# Daily at 9:30 AM
hour="9", minute="30"

# Weekdays only
day_of_week="mon-fri"
```

## 🎛️ Configuration Options

### In scheduler.py

- **Timezone**: `Asia/Kolkata` (IST)
- **Coalesce**: Prevents job backlog
- **Max Instances**: One job at a time
- **Misfire Grace**: 30 seconds

### Market Hours Filter

Uncomment this line in `register_tasks()`:

```python
hour="9-15",  # Only run during market hours
```

## 🔍 Monitoring

### Logs Show

- Task execution start/completion
- Number of instruments processed
- Success/error counts
- Detailed error messages

### Example Log Output

```
✅ Scheduler started
✅ Added scheduled job: Fetch Option Chain Data
🔄 Starting option chain fetch task...
📋 Found 2 active watchlist entries
📊 Fetching option chain for NSE_INDEX|Nifty 50
✅ Saved option chain snapshot for NSE_INDEX|Nifty 50
✅ Task completed. Success: 2, Errors: 0
```

## 🛡️ Security & Reliability

- ✅ Token validation before API calls
- ✅ Database connection checks
- ✅ Per-instrument error isolation
- ✅ Graceful shutdown on server stop
- ✅ Prevents duplicate job execution
- ✅ Comprehensive error logging

## 📦 Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Start the server**: `uvicorn main:app --reload`
3. **Add instruments to watchlist**: Use POST `/api/v1/option-chain/watchlist`
4. **Monitor logs**: Watch for task execution

## 🎉 Benefits

1. **Automatic Data Collection**: No manual intervention needed
2. **Historical Data**: Build a database of option chain snapshots
3. **Scalable**: Easy to add more tasks
4. **Maintainable**: Clean, modular code
5. **Production-Ready**: Error handling, logging, graceful shutdown

## 🔄 Future Enhancements (Ready to Add)

- Admin API to pause/resume jobs
- Job execution history tracking
- Email/Slack notifications on errors
- Multiple instrument fetch in parallel
- Retry logic with exponential backoff
- Market status check before execution
- Performance metrics and monitoring
