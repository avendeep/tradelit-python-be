# Trading Bot Quick Reference

## Quick Start

### 1. Start the server

```bash
cd tradeLit_app
uvicorn main:app --reload
```

### 2. Activate a bot (via Swagger UI)

1. Go to <http://localhost:8000/docs>
2. Find `POST /api/v1/trading-bot/activate`
3. Click "Try it out"
4. Use this request body:

```json
{
  "instrument_key": "NSE_INDEX|Nifty 50",
  "expiry_date": "2024-03-28",
  "lookback_minutes": 10
}
```

5. Click "Execute"

### 3. Check bot status

```bash
curl "http://localhost:8000/api/v1/trading-bot/list"
```

## Key Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/trading-bot/activate` | Start a bot |
| POST | `/api/v1/trading-bot/deactivate/{bot_id}` | Stop a bot |
| GET | `/api/v1/trading-bot/status/{bot_id}` | Check bot status |
| GET | `/api/v1/trading-bot/list` | List all active bots |
| POST | `/api/v1/trading-bot/analyze/{bot_id}` | Manual analysis |

## What the Bot Does

1. **Identifies ATM Strike** - Finds strike closest to spot price
2. **Selects 7 Strikes** - 3 above ATM, ATM, 3 below ATM
3. **Fetches Current OI** - Gets latest open interest data
4. **Fetches Historical OI** - Gets OI from 10 minutes ago
5. **Calculates Changes** - Computes OI delta for each strike
6. **Generates Signal** - Returns BULLISH/BEARISH/NEUTRAL

## Signal Logic

- **BULLISH** = Put OI ↑ significantly more than Call OI ↑
  - Put writers are confident (selling puts)
  
- **BEARISH** = Call OI ↑ significantly more than Put OI ↑
  - Call writers are confident (selling calls)
  
- **NEUTRAL** = Balanced or small changes

## Example Analysis Output

```json
{
  "signal": "BULLISH",
  "atm_strike": 22000,
  "spot_price": 22050.75,
  "total_call_oi_change": 150000,
  "total_put_oi_change": 250000,
  "pcr_oi": 0.85,
  "strikes_analyzed": [
    {
      "strike_price": 21850,
      "call_oi_change": 50000,
      "put_oi_change": 20000
    }
    // ... 6 more strikes
  ]
}
```

## Prerequisites

- ✅ Upstox authenticated (`/api/v1/upstox/login`)
- ✅ Instrument in watchlist
- ✅ At least 10 minutes of option chain snapshots
- ✅ MongoDB running
- ✅ Server running with scheduler

## Bot ID Format

`oi_bot_{instrument}_{expiry_date}`

Example: `oi_bot_NSE_INDEX_Nifty_50_2024-03-28`

## Common Commands

### Activate Nifty Bot

```bash
curl -X POST "http://localhost:8000/api/v1/trading-bot/activate" \
  -H "Content-Type: application/json" \
  -d '{
    "instrument_key": "NSE_INDEX|Nifty 50",
    "expiry_date": "2024-03-28"
  }'
```

### Activate Bank Nifty Bot

```bash
curl -X POST "http://localhost:8000/api/v1/trading-bot/activate" \
  -H "Content-Type: application/json" \
  -d '{
    "instrument_key": "NSE_INDEX|Bank Nifty",
    "expiry_date": "2024-03-28"
  }'
```

### List Active Bots

```bash
curl "http://localhost:8000/api/v1/trading-bot/list"
```

### Manual Analysis

```bash
curl -X POST "http://localhost:8000/api/v1/trading-bot/analyze/{bot_id}"
```

### Deactivate Bot

```bash
curl -X POST "http://localhost:8000/api/v1/trading-bot/deactivate/{bot_id}"
```

## Monitoring

### Check Server Logs

Look for these log messages:

- `🤖 Starting trading bot analysis task...`
- `📋 Found X active trading bot(s)`
- `🔍 Analyzing bot: ...`
- `✅ OI Analysis complete | Signal: BULLISH`

### Query Database

```python
from app.db.mongodb import MongoDB

# Get all analysis logs
collection = MongoDB.get_collection("oi_analysis_logs")
logs = await collection.find().sort("timestamp", -1).limit(10).to_list(10)

# Get active bots
bots_collection = MongoDB.get_collection("trading_bots")
active_bots = await bots_collection.find({"is_active": True}).to_list(None)
```

## Troubleshooting

### Bot not analyzing?

1. Check if bot is active: `GET /api/v1/trading-bot/status/{bot_id}`
2. Check scheduler logs in terminal
3. Verify Upstox token: `GET /api/v1/upstox/status`
4. Ensure 10+ minutes of snapshots exist

### No signal or NEUTRAL?

- Normal behavior when OI changes are small
- Indicates low volatility or balanced activity

### Wrong ATM strike?

- Check if spot price is available in data
- Verify option chain data quality

## Configuration

### Adjust Lookback Period

Change `lookback_minutes` when activating (1-60 minutes)

### Adjust Signal Threshold

Edit `trading_bot.py` → `_generate_signal()` method
Current threshold: 50,000 contracts

### Run Only During Market Hours

Edit `scheduler.py` → uncomment `hour="9-15"`

## Architecture

```
User Request
    ↓
API Endpoint (/api/v1/trading-bot/*)
    ↓
TradingBotService (business logic)
    ↓
MongoDB (bot config, snapshots, logs)
    ↓
Scheduler Task (every minute)
    ↓
Analysis Results → Database + Logs
```

## Files

- **Schemas**: `app/schemas/trading_bot.py`
- **Models**: `app/models/trading.py`
- **Service**: `app/services/trading_bot.py`
- **Endpoints**: `app/api/v1/endpoints/trading_bot.py`
- **Task**: `app/services/tasks/trading_bot_analysis.py`
- **Docs**: `TRADING_BOT.md` (full guide)

## Next Steps

1. Activate a bot for current expiry
2. Wait 10+ minutes for historical data
3. Check analysis logs in database
4. Monitor signals in server logs
5. Use signals as part of trading strategy

For detailed documentation, see `TRADING_BOT.md`
