# IST Timezone - Quick Reference Card

## 🇮🇳 Timezone: Asia/Kolkata (IST - UTC+5:30)

### ✅ Correct Usage

```python
from app.core.config import settings

# Get current IST time (naive)
now = settings.now_naive()

# Get current IST time (timezone-aware)  
now_aware = settings.now()

# Time calculations
ten_min_ago = settings.now_naive() - timedelta(minutes=10)
tomorrow = settings.now_naive() + timedelta(days=1)

# Database timestamps
record = {
    "created_at": settings.now_naive(),
    "updated_at": settings.now_naive(),
}
```

### ❌ NEVER Use These

```python
# ❌ These are UTC or system timezone
datetime.now()           # System timezone
datetime.utcnow()        # UTC timezone  
datetime.today()         # System timezone
```

## ⏰ Cron Job Examples

```python
from app.services.scheduler import scheduler_service

# Every minute (IST)
scheduler_service.add_job(
    func=my_task,
    job_id="task_id",
    trigger="cron",
    minute="*"
)

# Every 5 minutes during market hours (9 AM - 3 PM IST)
scheduler_service.add_job(
    func=market_task,
    job_id="market_task",
    trigger="cron",
    minute="*/5",
    hour="9-15"
)

# Every day at 9:15 AM IST
scheduler_service.add_job(
    func=daily_task,
    job_id="daily_task",
    trigger="cron",
    hour=9,
    minute=15
)
```

## 🔍 Quick Verification

```bash
# Install dependency
pip install pytz==2024.1

# Run verification
python verify_timezone.py

# Check in Python
from app.core.config import settings
print(settings.TIMEZONE)          # Asia/Kolkata
print(settings.now_naive())       # Current IST time
```

## 📚 Full Documentation

- **Complete Guide**: `TIMEZONE_SETUP.md`
- **Change Summary**: `IST_TIMEZONE_CHANGES.md`
- **Verification Script**: `verify_timezone.py`

## 🎯 Remember

1. Always use `settings.now_naive()` for timestamps
2. Cron jobs automatically use IST
3. All DB timestamps are in IST
4. Market hours: 9 AM - 3 PM IST (hour="9-15")
