# Trading Bot - OI Analysis Bot

## Overview

The Trading Bot is an automated system that analyzes Open Interest (OI) changes for option strikes around the ATM (At The Money) strike price. It runs every minute and provides trading signals based on OI movement patterns.

## Features

✅ **Automatic OI Analysis** - Analyzes OI changes every minute for active bots
✅ **ATM Detection** - Automatically identifies the ATM strike based on spot price
✅ **Multi-Strike Analysis** - Analyzes 3 strikes above and below ATM (7 total strikes)
✅ **Historical Comparison** - Compares current OI with data from 10 minutes ago (configurable)
✅ **Trading Signals** - Generates BULLISH, BEARISH, or NEUTRAL signals
✅ **PCR Calculation** - Calculates Put-Call Ratio based on OI
✅ **Complete Logging** - Stores all analysis results in database
✅ **API Control** - Start, stop, and monitor bots via REST API

## How It Works

### 1. Bot Activation

When you activate a bot, you specify:

- **Instrument Key**: The underlying symbol (e.g., `NSE_INDEX|Nifty 50`)
- **Expiry Date**: The option expiry date (e.g., `2024-03-28`)
- **Lookback Minutes**: How many minutes back to compare OI (default: 10)

### 2. Scheduled Analysis

Every minute, the bot:

1. Identifies the current ATM strike based on spot price
2. Selects 3 strikes above and 3 strikes below ATM (7 total)
3. Fetches current OI data from the latest snapshot
4. Fetches historical OI data from 10 minutes ago
5. Calculates OI changes for both calls and puts
6. Generates trading signal based on OI patterns
7. Logs results to database

### 3. Signal Generation

The bot generates signals based on OI change patterns:

- **BULLISH**: Put OI increases significantly more than Call OI
  - Indicates put writers are confident (selling puts)
  - Market sentiment is bullish
  
- **BEARISH**: Call OI increases significantly more than Put OI
  - Indicates call writers are confident (selling calls)
  - Market sentiment is bearish
  
- **NEUTRAL**: OI changes are balanced or insignificant
  - No clear directional bias

## API Endpoints

### 1. Activate Bot

**Endpoint:** `POST /api/v1/trading-bot/activate`

Activates a trading bot for the specified instrument.

**Request Body:**

```json
{
  "instrument_key": "NSE_INDEX|Nifty 50",
  "expiry_date": "2024-03-28",
  "lookback_minutes": 10
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Trading bot activated successfully",
  "data": {
    "bot_id": "oi_bot_NSE_INDEX_Nifty_50_2024-03-28",
    "is_active": true,
    "instrument_key": "NSE_INDEX|Nifty 50",
    "expiry_date": "2024-03-28",
    "lookback_minutes": 10,
    "activated_at": "2024-03-20T10:30:00.000000"
  }
}
```

### 2. Deactivate Bot

**Endpoint:** `POST /api/v1/trading-bot/deactivate/{bot_id}`

Deactivates an active trading bot.

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/trading-bot/deactivate/oi_bot_NSE_INDEX_Nifty_50_2024-03-28"
```

**Response:**

```json
{
  "status": "success",
  "message": "Trading bot deactivated successfully",
  "data": {
    "bot_id": "oi_bot_NSE_INDEX_Nifty_50_2024-03-28",
    "is_active": false
  }
}
```

### 3. Get Bot Status

**Endpoint:** `GET /api/v1/trading-bot/status/{bot_id}`

Retrieves the current status and configuration of a bot.

**Response:**

```json
{
  "bot_id": "oi_bot_NSE_INDEX_Nifty_50_2024-03-28",
  "is_active": true,
  "instrument_key": "NSE_INDEX|Nifty 50",
  "expiry_date": "2024-03-28",
  "lookback_minutes": 10,
  "activated_at": "2024-03-20T10:30:00",
  "last_analysis_at": "2024-03-20T10:45:00",
  "total_analyses": 15
}
```

### 4. List Active Bots

**Endpoint:** `GET /api/v1/trading-bot/list`

Lists all currently active trading bots.

**Response:**

```json
{
  "status": "success",
  "message": "Found 2 active bots",
  "data": {
    "active_bots": [
      {
        "bot_id": "oi_bot_NSE_INDEX_Nifty_50_2024-03-28",
        "is_active": true,
        "instrument_key": "NSE_INDEX|Nifty 50",
        "expiry_date": "2024-03-28"
      },
      {
        "bot_id": "oi_bot_NSE_INDEX_Bank_Nifty_2024-03-28",
        "is_active": true,
        "instrument_key": "NSE_INDEX|Bank Nifty",
        "expiry_date": "2024-03-28"
      }
    ],
    "count": 2
  }
}
```

### 5. Trigger Manual Analysis

**Endpoint:** `POST /api/v1/trading-bot/analyze/{bot_id}`

Manually triggers an immediate OI analysis without waiting for the scheduled task.

**Response:**

```json
{
  "timestamp": "2024-03-20T10:45:00",
  "instrument_key": "NSE_INDEX|Nifty 50",
  "expiry_date": "2024-03-28",
  "atm_strike": 22000,
  "spot_price": 22050.75,
  "strikes_analyzed": [
    {
      "strike_price": 21850,
      "call_oi_current": 1500000,
      "call_oi_previous": 1450000,
      "call_oi_change": 50000,
      "call_oi_change_percent": 3.45,
      "put_oi_current": 800000,
      "put_oi_previous": 780000,
      "put_oi_change": 20000,
      "put_oi_change_percent": 2.56
    },
    // ... more strikes
  ],
  "analysis_period_minutes": 10,
  "total_call_oi_change": 150000,
  "total_put_oi_change": 250000,
  "pcr_oi": 0.85,
  "signal": "BULLISH"
}
```

## Usage Examples

### Using cURL

#### Activate a bot for Nifty 50

```bash
curl -X POST "http://localhost:8000/api/v1/trading-bot/activate" \
  -H "Content-Type: application/json" \
  -d '{
    "instrument_key": "NSE_INDEX|Nifty 50",
    "expiry_date": "2024-03-28",
    "lookback_minutes": 10
  }'
```

#### Check bot status

```bash
curl "http://localhost:8000/api/v1/trading-bot/status/oi_bot_NSE_INDEX_Nifty_50_2024-03-28"
```

#### Trigger manual analysis

```bash
curl -X POST "http://localhost:8000/api/v1/trading-bot/analyze/oi_bot_NSE_INDEX_Nifty_50_2024-03-28"
```

#### Deactivate bot

```bash
curl -X POST "http://localhost:8000/api/v1/trading-bot/deactivate/oi_bot_NSE_INDEX_Nifty_50_2024-03-28"
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Activate bot
response = requests.post(
    f"{BASE_URL}/trading-bot/activate",
    json={
        "instrument_key": "NSE_INDEX|Nifty 50",
        "expiry_date": "2024-03-28",
        "lookback_minutes": 10
    }
)
bot_data = response.json()
bot_id = bot_data["data"]["bot_id"]
print(f"Bot activated: {bot_id}")

# Check status
response = requests.get(f"{BASE_URL}/trading-bot/status/{bot_id}")
status = response.json()
print(f"Bot is active: {status['is_active']}")
print(f"Total analyses: {status['total_analyses']}")

# Trigger manual analysis
response = requests.post(f"{BASE_URL}/trading-bot/analyze/{bot_id}")
analysis = response.json()
print(f"Signal: {analysis['signal']}")
print(f"ATM Strike: {analysis['atm_strike']}")
print(f"Call OI Change: {analysis['total_call_oi_change']:+,}")
print(f"Put OI Change: {analysis['total_put_oi_change']:+,}")

# Deactivate bot
response = requests.post(f"{BASE_URL}/trading-bot/deactivate/{bot_id}")
print("Bot deactivated")
```

## Data Structure

### Strike OI Analysis

Each strike includes:

- **strike_price**: Strike price value
- **call_oi_current**: Current call OI
- **call_oi_previous**: Call OI 10 minutes ago
- **call_oi_change**: Change in call OI (absolute)
- **call_oi_change_percent**: Percentage change in call OI
- **put_oi_current**: Current put OI
- **put_oi_previous**: Put OI 10 minutes ago
- **put_oi_change**: Change in put OI (absolute)
- **put_oi_change_percent**: Percentage change in put OI

### Analysis Result

Complete analysis includes:

- **timestamp**: Time of analysis
- **instrument_key**: Instrument analyzed
- **expiry_date**: Option expiry date
- **atm_strike**: Identified ATM strike
- **spot_price**: Current spot price
- **strikes_analyzed**: List of strike analyses (7 strikes)
- **analysis_period_minutes**: Lookback period
- **total_call_oi_change**: Sum of all call OI changes
- **total_put_oi_change**: Sum of all put OI changes
- **pcr_oi**: Put-Call Ratio (Put OI / Call OI)
- **signal**: Trading signal (BULLISH/BEARISH/NEUTRAL)

## Database Collections

### 1. `trading_bots`

Stores bot configurations and state.

**Fields:**

- `bot_id`: Unique identifier
- `is_active`: Active status
- `instrument_key`: Instrument
- `expiry_date`: Expiry date
- `lookback_minutes`: Analysis period
- `activated_at`: Activation timestamp
- `last_analysis_at`: Last analysis timestamp
- `total_analyses`: Count of analyses

### 2. `oi_analysis_logs`

Stores all analysis results for historical reference.

**Fields:**

- `bot_id`: Bot that ran the analysis
- `instrument_key`: Instrument analyzed
- `expiry_date`: Expiry date
- `timestamp`: Analysis timestamp
- `atm_strike`: ATM strike at time
- `spot_price`: Spot price at time
- `analysis_result`: Complete analysis data

## Configuration

### Lookback Period

The `lookback_minutes` parameter determines how far back to compare OI data:

- **Default**: 10 minutes
- **Range**: 1-60 minutes
- **Recommendation**: 10 minutes for intraday, 30 minutes for swing trading

### Signal Threshold

The bot uses a threshold to determine signal strength:

- **Current**: 50,000 contracts difference
- **Configurable**: Can be adjusted in `trading_bot.py` service
- **Recommendation**: Adjust based on instrument liquidity

## Prerequisites

### 1. Upstox Authentication

- Bot requires valid Upstox access token
- Ensure you're authenticated via `/api/v1/upstox/login`

### 2. Watchlist Entry

- Add instrument to watchlist before activating bot
- Option chain data must be available in snapshots

### 3. Historical Data

- Requires at least 10 minutes of historical snapshots
- Bot will skip analysis if insufficient data

## Monitoring

### Server Logs

The bot provides detailed logging:

```
🤖 Starting trading bot analysis task...
📋 Found 1 active trading bot(s)
🔍 Analyzing bot: oi_bot_NSE_INDEX_Nifty_50_2024-03-28 (NSE_INDEX|Nifty 50)
📊 ATM Strike: 22000, Spot Price: 22050.75
✅ OI Analysis complete for oi_bot_NSE_INDEX_Nifty_50_2024-03-28 | Signal: BULLISH | Call OI Change: +150,000 | Put OI Change: +250,000 | PCR: 0.85
```

### Database Queries

Query analysis logs:

```python
from app.db.mongodb import MongoDB

collection = MongoDB.get_collection("oi_analysis_logs")

# Get latest analysis for a bot
latest = await collection.find_one(
    {"bot_id": "oi_bot_NSE_INDEX_Nifty_50_2024-03-28"},
    sort=[("timestamp", -1)]
)

# Get all analyses in last hour
from datetime import datetime, timedelta
one_hour_ago = datetime.utcnow() - timedelta(hours=1)
recent = await collection.find(
    {"timestamp": {"$gte": one_hour_ago}}
).to_list(length=None)
```

## Best Practices

### 1. Market Hours

- Run bots during market hours (9:15 AM - 3:30 PM IST)
- Uncomment `hour="9-15"` in scheduler for market hours only

### 2. Instrument Selection

- Focus on liquid instruments (Nifty, Bank Nifty)
- Ensure sufficient OI in strikes around ATM

### 3. Signal Interpretation

- Use signals as indicators, not absolute rules
- Combine with other technical analysis
- Consider market context and news

### 4. Bot Management

- Deactivate bots for expired contracts
- Monitor bot performance regularly
- Adjust lookback period based on results

## Troubleshooting

### Bot Not Analyzing

**Possible causes:**

1. Bot is not active - Check status endpoint
2. Insufficient historical data - Wait 10+ minutes after activation
3. No watchlist entry - Add instrument to watchlist
4. Upstox token expired - Re-authenticate

### No Signal Generated

**Possible causes:**

1. Insufficient OI changes (below threshold)
2. Balanced call/put OI increases
3. This is expected during low volatility periods

### Incorrect ATM Strike

**Possible causes:**

1. Spot price not available in data
2. Missing strikes in option chain
3. Data quality issues from Upstox API

## Future Enhancements

- [ ] Multiple trading strategies (not just OI-based)
- [ ] Configurable signal thresholds via API
- [ ] Real-time notifications (email, webhook)
- [ ] Backtesting framework
- [ ] Performance metrics and analytics
- [ ] Machine learning for signal generation
- [ ] Multi-timeframe analysis

## Files Created

### Schemas

- `app/schemas/trading_bot.py` - Pydantic schemas for requests/responses

### Models

- `app/models/trading.py` - Added TradingBotModel, OIAnalysisLogModel

### Services

- `app/services/trading_bot.py` - Core bot logic and OI analysis

### Endpoints

- `app/api/v1/endpoints/trading_bot.py` - REST API endpoints

### Tasks

- `app/services/tasks/trading_bot_analysis.py` - Scheduled analysis task

### Documentation

- `TRADING_BOT.md` - This file

## Support

For issues or questions:

1. Check server logs for detailed error messages
2. Verify bot status via API
3. Ensure all prerequisites are met
4. Check option chain data availability

## Resources

- **API Documentation**: <http://localhost:8000/docs>
- **Option Chain API**: See `OPTION_CHAIN_API.md`
- **Scheduler System**: See `CRON_JOB_SYSTEM.md`
- **Upstox Integration**: See `UPSTOX_INTEGRATION.md`
