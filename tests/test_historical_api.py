import urllib.request
import json

BASE_URL = "http://localhost:8000/api/v1/analysis"

def test_historical_api():
    print("🚀 Testing Historical Candle API Integration...")
    
    # 1. Set Config
    print("1️⃣ Setting Configuration...")
    data = {
        "instrument_key": "NSE_INDEX|Nifty 50",
        "date": "2025-11-29",
        "unit": "minute",
        "interval": "15"
    }
    req = urllib.request.Request(
        f"{BASE_URL}/config",
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print("✅ Config set successfully")
            else:
                print(f"❌ Config set failed: {response.status}")
                return
    except Exception as e:
        print(f"❌ Config set failed: {e}")
        return

    # 2. Call Delta API
    print("2️⃣ Calling POST /eod/delta...")
    print("   (Check server logs for the Historical Candle URL)")
    req = urllib.request.Request(
        f"{BASE_URL}/eod/delta",
        data=b"",
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                res_body = json.loads(response.read().decode('utf-8'))
                print(f"✅ API call successful!")
                print(f"   Daily Cumulative Delta: {res_body.get('daily_cumulative_delta')}")
            else:
                print(f"❌ API call failed with status {response.status}")
    except urllib.error.HTTPError as e:
        print(f"⚠️ API returned error: {e.code} - {e.reason}")
        error_body = e.read().decode('utf-8')
        print(f"   Error Body: {error_body}")
        print("   Check if Upstox token is valid and data exists for the date")
    except Exception as e:
        print(f"❌ API call failed: {e}")

if __name__ == "__main__":
    test_historical_api()
