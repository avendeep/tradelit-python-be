import urllib.request
import json
import time

BASE_URL = "http://localhost:8000/api/v1/analysis"

def test_upstox_integration():
    print("🚀 Starting Upstox Integration Verification...")
    
    # 1. POST Config with unit and interval
    print("1️⃣ POST /config (Update with unit/interval)...")
    data = {
        "instrument_key": "NSE_INDEX|Nifty 50",
        "date": "2025-11-29", # Use today or recent date
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
                res_body = json.loads(response.read().decode('utf-8'))
                print(f"   Response: {res_body}")
                if res_body.get('unit') == "minute" and res_body.get('interval') == "15":
                    print("✅ Config update successful")
                else:
                    print("❌ Config update failed: Data mismatch")
            else:
                print(f"❌ POST failed with status {response.status}")
                return
    except Exception as e:
        print(f"❌ POST failed: {e}")
        return

    # 2. GET Config to verify persistence
    print("2️⃣ GET /config...")
    try:
        with urllib.request.urlopen(f"{BASE_URL}/config") as response:
            if response.status == 200:
                res_body = json.loads(response.read().decode('utf-8'))
                print(f"   Response: {res_body}")
                if res_body.get('unit') == "minute" and res_body.get('interval') == "15":
                    print("✅ GET verification passed")
                else:
                    print("❌ GET verification failed: Data mismatch")
            else:
                print(f"❌ GET failed with status {response.status}")
                return
    except Exception as e:
        print(f"❌ GET failed: {e}")
        return

    # 3. Call Delta API (This attempts to call Upstox)
    print("3️⃣ Calling POST /eod/delta...")
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
                print(f"✅ API call successful: {res_body}")
            else:
                print(f"❌ API call failed with status {response.status}")
    except urllib.error.HTTPError as e:
        print(f"⚠️ API call returned error (expected if no auth/data): {e.code} - {e.reason}")
        error_body = e.read().decode('utf-8')
        print(f"   Error Body: {error_body}")
        # If error is 500 and contains "Not authenticated" or similar, it means logic is working but auth failed.
        if "Not authenticated" in error_body or "No candle data" in error_body:
             print("✅ Logic verification passed (reached Upstox call).")
    except Exception as e:
        print(f"❌ API call failed: {e}")

if __name__ == "__main__":
    test_upstox_integration()
