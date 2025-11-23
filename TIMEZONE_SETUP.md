# Timezone Setup - Indian Standard Time (IST)

## Overview

The entire TradeLit application is configured to use **Indian Standard Time (IST)** - `Asia/Kolkata` timezone. All datetime operations, cron jobs, scheduled tasks, and database timestamps strictly follow IST.

## Key Components

### 1. **Timezone Configuration** (`app/core/config.py`)

- **Timezone**: `Asia/Kolkata` (IST - UTC+5:30)
- **Library**: `pytz` for timezone support

#### Utility Methods

```python
from app.core.config import settings

# Get current time in IST (timezone-aware)
current_time = settings.now()

# Get current time in IST (naive datetime)
current_time_naive = settings.now_naive()

# Get timezone object
tz = settings.get_timezone()
```

### 2. **Scheduler Configuration** (`app/services/scheduler.py`)

The APScheduler is configured with IST timezone:

```python
self.scheduler = AsyncIOScheduler(
    timezone="Asia/Kolkata",  # All cron jobs run in IST
    job_defaults={
        "coalesce": True,
        "max_instances": 1,
        "misfire_grace_time": 30,
    },
)
```

### 3. **Cron Jobs & Scheduled Tasks**

All cron jobs automatically use IST timezone:

- **Option Chain Fetch Task**: Runs every minute (IST)
- **Trading Bot Analysis Task**: Runs every minute (IST)
- Market hours: 9 AM to 3 PM IST (when enabled)

Example cron configuration:

```python
self.add_job(
    func=fetch_option_chain_task,
    job_id="fetch_option_chain",
    name="Fetch Option Chain Data",
    trigger="cron",
    minute="*",  # Every minute
    hour="9-15",  # 9 AM to 3 PM IST (market hours)
)
```

### 4. **Datetime Operations**

All datetime operations in the application use IST:

#### ✅ **Correct Usage** (IST)

```python
from app.core.config import settings

# Creating timestamps
timestamp = settings.now_naive()
created_at = settings.now_naive()
updated_at = settings.now_naive()

# Time calculations
target_time = settings.now_naive() - timedelta(minutes=10)
```

#### ❌ **AVOID** (UTC/Ambiguous)

```python
# Don't use these - they are UTC-based or system timezone
datetime.now()           # System timezone (could be UTC or local)
datetime.utcnow()        # UTC timezone
datetime.today()         # System timezone
```

## Modified Files

### Core Files

1. **`app/core/config.py`**
   - Added `TIMEZONE = "Asia/Kolkata"`
   - Added utility methods: `get_timezone()`, `now()`, `now_naive()`
   - Added `pytz` import

2. **`requirements.txt`**
   - Added `pytz==2024.1` dependency

### Service Files

3. **`app/services/scheduler.py`**
   - Already configured with `timezone="Asia/Kolkata"`

4. **`app/services/tasks/fetch_option_chain.py`**
   - Updated to use `settings.now_naive()` for timestamps
   - IST-based snapshot timestamps

5. **`app/services/trading_bot.py`**
   - All datetime operations use `settings.now_naive()`
   - Bot activation, analysis, and logging timestamps in IST
   - Historical snapshot calculations in IST

6. **`app/services/upstox_service.py`**
   - Token expiry calculations in IST
   - Token save/update timestamps in IST
   - Token validation uses IST

7. **`app/services/trading.py`**
   - Trade, strategy, and portfolio timestamps in IST

### API Endpoint Files

8. **`app/api/v1/endpoints/option_chain.py`**
   - Watchlist creation/update timestamps in IST

### Security Files

9. **`app/core/security.py`**
   - JWT token expiry calculations in IST

## Benefits

1. **Consistency**: All timestamps across the application are in IST
2. **NSE Trading**: Aligns with NSE India trading hours (9 AM - 3:30 PM IST)
3. **Cron Jobs**: Scheduled tasks run exactly when expected in IST
4. **Data Integrity**: All database records have consistent timezone
5. **Analysis**: Time-based analysis (OI changes, etc.) uses correct local time
6. **No Confusion**: Developers don't need to convert UTC ↔ IST manually

## Installation

Install required dependency:

```bash
pip install pytz==2024.1
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## Usage Examples

### Example 1: Creating a Timestamp

```python
from app.core.config import settings

# Current time in IST (naive)
now = settings.now_naive()
print(f"Current IST time: {now}")
# Output: Current IST time: 2024-03-20 14:30:00
```

### Example 2: Time Calculations

```python
from app.core.config import settings
from datetime import timedelta

# 10 minutes ago in IST
ten_min_ago = settings.now_naive() - timedelta(minutes=10)

# 1 hour from now in IST
one_hour_later = settings.now_naive() + timedelta(hours=1)
```

### Example 3: Cron Job for Market Hours

```python
# Run every 5 minutes during market hours (9 AM - 3 PM IST)
scheduler_service.add_job(
    func=my_task,
    job_id="market_task",
    name="Market Hours Task",
    trigger="cron",
    minute="*/5",    # Every 5 minutes
    hour="9-15",     # 9 AM to 3 PM IST
)
```

### Example 4: Database Timestamp

```python
from app.core.config import settings

# Creating a database record with IST timestamp
trade_data = {
    "symbol": "NIFTY",
    "quantity": 100,
    "timestamp": settings.now_naive(),
    "created_at": settings.now_naive(),
}
```

## Testing

To verify IST timezone is working:

```python
from app.core.config import settings
from datetime import datetime
import pytz

# Check configuration
print(f"Configured Timezone: {settings.TIMEZONE}")
print(f"Current IST Time: {settings.now_naive()}")
print(f"Current IST Time (aware): {settings.now()}")

# Verify scheduler timezone
from app.services.scheduler import scheduler_service
scheduler_service.start()
print(f"Scheduler Timezone: {scheduler_service.scheduler.timezone}")
```

## Migration Notes

If you have existing data with UTC timestamps:

1. The new system uses IST for all new records
2. Existing UTC timestamps in database remain unchanged
3. Consider adding a migration script if timestamp consistency is critical
4. All new records will automatically use IST

## Important Reminders

1. **Always use** `settings.now_naive()` or `settings.now()` for current time
2. **Never use** `datetime.now()`, `datetime.utcnow()`, or `datetime.today()` directly
3. **Cron jobs** automatically use IST timezone (no additional configuration needed)
4. **Market hours** (9 AM - 3 PM IST) are correctly aligned
5. **All scheduled tasks** run according to IST

## Support

For any timezone-related issues or questions, refer to:

- `app/core/config.py` - Timezone configuration
- `app/services/scheduler.py` - Scheduler setup
- This document - Complete reference

---

**Last Updated**: November 22, 2025  
**Timezone**: Asia/Kolkata (IST, UTC+5:30)  
**Status**: ✅ Fully Implemented
