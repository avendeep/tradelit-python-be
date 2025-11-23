# Option Chain API - Quick Reference

## Endpoints

### Get Option Chain

```
GET /api/v1/option-chain?instrument_key={key}&expiry_date={date}
POST /api/v1/option-chain
GET /api/v1/option-chain/instruments
```

## Popular Instruments

| Name | Instrument Key | Exchange |
|------|---------------|----------|
| Nifty 50 | `NSE_INDEX\|Nifty 50` | NSE |
| Bank Nifty | `NSE_INDEX\|Bank Nifty` | NSE |
| Fin Nifty | `NSE_INDEX\|Nifty Fin Service` | NSE |
| Reliance | `NSE_EQ\|RELIANCE` | NSE |
| TCS | `NSE_EQ\|TCS` | NSE |
| HDFC Bank | `NSE_EQ\|HDFCBANK` | NSE |

## Quick Examples

### cURL - Nifty 50

```bash
curl "http://localhost:8000/api/v1/option-chain?instrument_key=NSE_INDEX%7CNifty%2050&expiry_date=2024-03-28"
```

### cURL - Bank Nifty

```bash
curl "http://localhost:8000/api/v1/option-chain?instrument_key=NSE_INDEX%7CBank%20Nifty&expiry_date=2024-03-28"
```

### Python

```python
from app.services.upstox_service import upstox_service

option_chain = await upstox_service.get_option_chain(
    instrument_key="NSE_INDEX|Nifty 50",
    expiry_date="2024-03-28"
)
```

## Response Structure

```json
{
  "status": "success",
  "data": [
    {
      "strike_price": 21500,
      "expiry": "2024-03-28",
      "underlying_spot_price": 21850.50,
      "call_options": {
        "market_data": {
          "ltp": 385.50,
          "volume": 1250000,
          "oi": 2500000
        },
        "option_greeks": {
          "delta": 0.65,
          "iv": 18.5
        }
      },
      "put_options": { ... }
    }
  ]
}
```

## Testing

```bash
python test_option_chain.py
```

## Documentation

- Full API Docs: <http://localhost:8000/docs>
- Complete Guide: [OPTION_CHAIN_API.md](OPTION_CHAIN_API.md)
