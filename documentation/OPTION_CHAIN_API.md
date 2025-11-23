# Upstox Option Chain API Integration

## Overview

The Upstox Option Chain API integration allows you to fetch complete put/call option chain data for various underlying symbols including indices and stocks.

## Features

✅ **Complete Option Chain Data** - Strike prices, call/put options, market data
✅ **Option Greeks** - Delta, Gamma, Vega, Theta, Implied Volatility
✅ **Market Data** - LTP, Volume, Open Interest, Bid/Ask prices
✅ **Authentication Required** - Uses stored Upstox access token
✅ **Multiple Instruments** - Supports NSE Index, NSE Equity, BSE
✅ **Type-Safe** - Pydantic schemas for request/response validation

## API Endpoints

### 1. Get Option Chain (GET)

**Endpoint:** `GET /api/v1/option-chain`

**Query Parameters:**

- `instrument_key` (required) - Key of underlying symbol
- `expiry_date` (required) - Expiry date in YYYY-MM-DD format

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/v1/option-chain?instrument_key=NSE_INDEX|Nifty%2050&expiry_date=2024-03-28" \
  -H "accept: application/json"
```

**Example Response:**

```json
{
  "status": "success",
  "data": [
    {
      "strike_price": 21500,
      "expiry": "2024-03-28",
      "underlying_spot_price": 21850.50,
      "underlying_key": "NSE_INDEX|Nifty 50",
      "call_options": {
        "instrument_key": "NSE_FO|38088",
        "market_data": {
          "ltp": 385.50,
          "close_price": 380.00,
          "volume": 1250000,
          "oi": 2500000,
          "bid_price": 384.00,
          "bid_qty": 50,
          "ask_price": 386.00,
          "ask_qty": 75,
          "prev_oi": 2450000
        },
        "option_greeks": {
          "delta": 0.65,
          "gamma": 0.0012,
          "theta": -15.5,
          "vega": 8.2,
          "iv": 18.5
        }
      },
      "put_options": {
        "instrument_key": "NSE_FO|38089",
        "market_data": {
          "ltp": 35.25,
          "volume": 980000,
          "oi": 1800000
        },
        "option_greeks": {
          "delta": -0.35,
          "gamma": 0.0012,
          "theta": -12.3,
          "vega": 7.8,
          "iv": 16.2
        }
      }
    }
  ]
}
```

### 2. Get Option Chain (POST)

**Endpoint:** `POST /api/v1/option-chain`

**Request Body:**

```json
{
  "instrument_key": "NSE_INDEX|Nifty 50",
  "expiry_date": "2024-03-28"
}
```

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/option-chain" \
  -H "Content-Type: application/json" \
  -d '{
    "instrument_key": "NSE_INDEX|Nifty 50",
    "expiry_date": "2024-03-28"
  }'
```

### 3. Get Popular Instruments

**Endpoint:** `GET /api/v1/option-chain/instruments`

Returns a list of commonly traded instruments for quick access.

**Example Response:**

```json
{
  "status": "success",
  "data": {
    "indices": [
      {
        "name": "Nifty 50",
        "instrument_key": "NSE_INDEX|Nifty 50",
        "exchange": "NSE"
      },
      {
        "name": "Bank Nifty",
        "instrument_key": "NSE_INDEX|Bank Nifty",
        "exchange": "NSE"
      }
    ],
    "stocks": [
      {
        "name": "Reliance Industries",
        "instrument_key": "NSE_EQ|RELIANCE",
        "exchange": "NSE"
      }
    ]
  }
}
```

## Supported Instruments

### Indices

- **Nifty 50**: `NSE_INDEX|Nifty 50`
- **Bank Nifty**: `NSE_INDEX|Bank Nifty`
- **Fin Nifty**: `NSE_INDEX|Nifty Fin Service`
- **Sensex**: `BSE_INDEX|Sensex`

### Stocks (Examples)

- **Reliance**: `NSE_EQ|RELIANCE`
- **TCS**: `NSE_EQ|TCS`
- **HDFC Bank**: `NSE_EQ|HDFCBANK`
- **Infosys**: `NSE_EQ|INFY`

## Usage Examples

### Using Swagger UI

1. Start the server: `uvicorn main:app --reload`
2. Go to: <http://localhost:8000/docs>
3. Find "Option Chain" section
4. Try `GET /api/v1/option-chain`
5. Enter parameters:
   - `instrument_key`: `NSE_INDEX|Nifty 50`
   - `expiry_date`: `2024-03-28`
6. Click "Execute"

### Using Python

```python
from app.services.upstox_service import upstox_service

# Fetch option chain
option_chain = await upstox_service.get_option_chain(
    instrument_key="NSE_INDEX|Nifty 50",
    expiry_date="2024-03-28"
)

# Access data
for strike in option_chain['data']:
    print(f"Strike: {strike['strike_price']}")
    
    # Call option data
    call = strike['call_options']
    if call:
        print(f"  Call LTP: {call['market_data']['ltp']}")
        print(f"  Call OI: {call['market_data']['oi']}")
    
    # Put option data
    put = strike['put_options']
    if put:
        print(f"  Put LTP: {put['market_data']['ltp']}")
        print(f"  Put OI: {put['market_data']['oi']}")
```

### Using cURL

```bash
# Get Nifty 50 option chain
curl "http://localhost:8000/api/v1/option-chain?instrument_key=NSE_INDEX%7CNifty%2050&expiry_date=2024-03-28"

# Get Bank Nifty option chain
curl "http://localhost:8000/api/v1/option-chain?instrument_key=NSE_INDEX%7CBank%20Nifty&expiry_date=2024-03-28"

# Get popular instruments
curl "http://localhost:8000/api/v1/option-chain/instruments"
```

## Data Structure

### Market Data Fields

- `ltp` - Last Traded Price
- `close_price` - Previous day closing price
- `volume` - Trading volume
- `oi` - Open Interest
- `bid_price` / `bid_qty` - Best bid price and quantity
- `ask_price` / `ask_qty` - Best ask price and quantity
- `prev_oi` - Previous Open Interest

### Option Greeks

- `delta` - Rate of change of option price with respect to underlying price
- `gamma` - Rate of change of delta
- `theta` - Time decay of option
- `vega` - Sensitivity to volatility
- `iv` - Implied Volatility

## Testing

Run the test script:

```bash
python test_option_chain.py
```

This will:

- Authenticate with Upstox
- Fetch Nifty 50 option chain
- Fetch Bank Nifty option chain
- Display sample data

## Important Notes

### Authentication

- **Required**: You must be authenticated with Upstox
- The API uses the stored access token from MongoDB
- Token must be valid (not expired)
- If not authenticated, you'll get a 401 error

### Expiry Dates

- Format: `YYYY-MM-DD`
- Must be a valid option expiry date
- Weekly expiries: Typically Thursday for Nifty/Bank Nifty
- Monthly expiries: Last Thursday of the month
- Invalid dates will return empty data or error

### Exchange Support

- ✅ **NSE**: Index and Equity options supported
- ✅ **BSE**: Index options supported
- ❌ **MCX**: Option chains not currently available

### Rate Limits

- Follow Upstox API rate limits
- Recommended: Cache results for a few seconds
- Avoid excessive polling

## Error Handling

### 401 Unauthorized

```json
{
  "detail": "Not authenticated. Please login first."
}
```

**Solution**: Authenticate via `/api/v1/upstox/login`

### 400 Bad Request

```json
{
  "detail": "Invalid request: ..."
}
```

**Solution**: Check instrument_key format and expiry_date

### 500 Internal Server Error

```json
{
  "detail": "Failed to fetch option chain: ..."
}
```

**Solution**: Check Upstox API status, verify parameters

## Code Structure

### Files Created/Modified

1. **`app/schemas/option_chain.py`** - Pydantic schemas
   - `OptionChainRequest` - Request validation
   - `OptionChainResponse` - Response structure
   - `OptionData`, `MarketData`, `OptionGreeks` - Data models

2. **`app/services/upstox_service.py`** - Service method
   - `get_option_chain()` - Fetch option chain from Upstox API

3. **`app/api/v1/endpoints/option_chain.py`** - API endpoints
   - `GET /option-chain` - Fetch option chain
   - `POST /option-chain` - Alternative POST method
   - `GET /option-chain/instruments` - Popular instruments

4. **`app/api/v1/router.py`** - Router registration
   - Added option_chain router

5. **`test_option_chain.py`** - Test script

## Next Steps

- [ ] Add caching layer for option chain data
- [ ] Implement WebSocket for real-time updates
- [ ] Add filtering options (strike range, OI threshold)
- [ ] Store historical option chain data
- [ ] Add analytics (PCR ratio, max pain, etc.)
- [ ] Support for option strategies

## Resources

- **Upstox API Docs**: <https://upstox.com/developer/api-documentation/get-pc-option-chain>
- **API Documentation**: <http://localhost:8000/docs> (when server is running)
- **Test Script**: `python test_option_chain.py`

## Support

For issues:

1. Check authentication status: `GET /api/v1/upstox/status`
2. Verify instrument_key format
3. Confirm expiry_date is valid
4. Check Upstox API status
5. Review server logs for detailed errors
