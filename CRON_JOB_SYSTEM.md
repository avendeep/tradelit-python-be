# Cron Job System Documentation

## Overview

The TradeLit API includes a scalable cron job system that automatically fetches option chain data from Upstox and stores it in MongoDB. The system is built using APScheduler and is designed to be easily extensible for future tasks.

## Architecture

### Components

1. **Scheduler Service** (`app/services/scheduler.py`)
   - Manages the APScheduler instance
   - Provides methods to add, remove, pause, and resume jobs
   - Centralized task registration

2. **Tasks Directory** (`app/services/tasks/`)
   - Contains individual task modules
   - Each task is a separate file for better organization
   - Currently includes: `fetch_option_chain.py`

3. **Database Models** (`app/models/trading.py`)
   - `OptionChainSnapshotModel`: Stores option chain data snapshots

## Current Tasks

### 1. Fetch Option Chain Data

**Task ID**: `fetch_option_chain`  
**Schedule**: Every minute  
**Function**: `fetch_option_chain_task()` in `app/services/tasks/fetch_option_chain.py`

#### What it does

1. Checks if Upstox authentication token is valid
2. Fetches all active instruments from the watchlist in MongoDB
3. For each instrument:
   - Fetches option chain data from Upstox API
   - Stores snapshot in `option_chain_snapshots` collection
   - Timestamp is stored without seconds (only hour and minute)

#### Database Collections Used

- **Input**: `instrument_watchlist` (reads active instruments)
- **Output**: `option_chain_snapshots` (stores fetched data)

## Configuration

### Timezone

The scheduler is configured to use **Asia/Kolkata (IST)** timezone.

### Market Hours (Optional)

To run tasks only during market hours, uncomment the `hour` parameter in `scheduler.py`:

```python
self.add_job(
    func=fetch_option_chain_task,
    job_id="fetch_option_chain",
    name="Fetch Option Chain Data",
    trigger="cron",
    minute="*",
    hour="9-15",  # Uncomment this line to run only 9 AM - 3 PM
)
```

## Adding New Tasks

### Step 1: Create Task File

Create a new file in `app/services/tasks/` directory:

```python
# app/services/tasks/your_new_task.py

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


async def your_new_task():
    """
    Description of what your task does
    """
    try:
        logger.info("🔄 Starting your new task...")
        
        # Your task logic here
        
        logger.info("✅ Your new task completed successfully")
    
    except Exception as e:
        logger.error(f"❌ Error in your_new_task: {str(e)}")
```

### Step 2: Register Task in Scheduler

Add your task to the `register_tasks()` method in `app/services/scheduler.py`:

```python
def register_tasks(self):
    """Register all scheduled tasks"""
    from app.services.tasks.fetch_option_chain import fetch_option_chain_task
    from app.services.tasks.your_new_task import your_new_task  # Import your task
    
    # Existing tasks...
    
    # Add your new task
    self.add_job(
        func=your_new_task,
        job_id="your_task_id",
        name="Your Task Name",
        trigger="cron",
        minute="*/5",  # Every 5 minutes
        hour="9-17",   # Optional: specific hours
    )
```

### Cron Schedule Examples

```python
# Every minute
minute="*"

# Every 5 minutes
minute="*/5"

# Every hour at minute 30
minute="30"

# Every day at 9:30 AM
hour="9", minute="30"

# Every Monday at 9:00 AM
day_of_week="mon", hour="9", minute="0"

# Market hours only (9 AM - 3 PM)
hour="9-15"

# Multiple specific times
hour="9,12,15", minute="0"
```

## Data Storage Format

### Option Chain Snapshot

```json
{
  "_id": "ObjectId",
  "instrument_key": "NSE_INDEX|Nifty 50",
  "expiry_date": "2024-03-28",
  "timestamp": "2024-03-20T10:15:00",  // No seconds
  "data": {
    // Complete option chain data from Upstox API
    "status": "success",
    "data": [...]
  },
  "created_at": "2024-03-20T10:15:23.456Z"
}
```

## Monitoring and Logging

The scheduler uses Python's logging module. All task executions are logged with the following levels:

- **INFO**: Normal execution, task start/completion
- **WARNING**: Non-critical issues (e.g., invalid token, no watchlist entries)
- **ERROR**: Task failures and exceptions

### Log Output Example

```
✅ Scheduler initialized
✅ Scheduler started
✅ Added scheduled job: Fetch Option Chain Data (ID: fetch_option_chain)
✅ All scheduled tasks registered
🔄 Starting option chain fetch task...
📋 Found 2 active watchlist entries
📊 Fetching option chain for NSE_INDEX|Nifty 50 (Expiry: 2024-03-28)
✅ Saved option chain snapshot for NSE_INDEX|Nifty 50
✅ Option chain fetch task completed. Success: 2, Errors: 0
```

## Scheduler Management

### Programmatic Control

You can control the scheduler programmatically:

```python
from app.services.scheduler import scheduler_service

# Pause a specific job
scheduler_service.pause_job("fetch_option_chain")

# Resume a paused job
scheduler_service.resume_job("fetch_option_chain")

# Remove a job
scheduler_service.remove_job("fetch_option_chain")

# Get all jobs
jobs = scheduler_service.get_jobs()
```

## Error Handling

The system includes comprehensive error handling:

1. **Authentication Checks**: Tasks verify Upstox token validity before execution
2. **Database Errors**: Individual task failures don't crash the scheduler
3. **Graceful Degradation**: If one instrument fails, others continue processing
4. **Logging**: All errors are logged with context for debugging

## Performance Considerations

### Job Defaults

- **Coalesce**: Missed runs are combined into one (prevents backlog)
- **Max Instances**: Only one instance of each job runs at a time
- **Misfire Grace Time**: 30 seconds grace period for missed jobs

### Database Indexes

Consider adding indexes for better query performance:

```javascript
// In MongoDB shell
db.option_chain_snapshots.createIndex({ "instrument_key": 1, "timestamp": -1 })
db.option_chain_snapshots.createIndex({ "expiry_date": 1, "timestamp": -1 })
```

## Testing

To test a task manually without waiting for schedule:

```python
import asyncio
from app.services.tasks.fetch_option_chain import fetch_option_chain_task

# Run task immediately
asyncio.run(fetch_option_chain_task())
```

## Dependencies

- **APScheduler**: 3.10.4 - Job scheduling library
- **Motor**: Async MongoDB driver
- **Upstox Python SDK**: For API access

## Troubleshooting

### Task Not Running

1. Check if scheduler is started in main.py lifespan
2. Verify task is registered in `register_tasks()`
3. Check logs for errors
4. Ensure Upstox token is valid

### Database Connection Issues

1. Verify MongoDB is running
2. Check connection string in settings
3. Ensure database is initialized in lifespan

### API Rate Limits

If you hit Upstox API rate limits:

1. Reduce task frequency
2. Implement rate limiting in task logic
3. Add delays between API calls

## Future Enhancements

Potential improvements for the cron job system:

1. **Admin API Endpoints**: Add REST API to manage scheduler (pause/resume jobs)
2. **Job History**: Store execution history in database
3. **Alerting**: Send notifications on task failures
4. **Metrics**: Track success rates and execution times
5. **Conditional Execution**: Run tasks based on market status
6. **Retry Logic**: Automatic retry on failure with exponential backoff
7. **Job Priority**: Priority queue for critical tasks

## Support

For issues or questions:

- Check application logs
- Review task implementation
- Verify database collections and data
- Ensure all dependencies are installed
