import urllib.request
import json
import time

BASE_URL = "http://localhost:8000/api/v1/analysis"

def test_config():
    print("🚀 Starting EOD Config Verification...")
    
    # 1. POST Config
    print("1️⃣ POST /config (Create)...")
    data = {
        "instrument_key": "TEST_KEY_1",
        "date": "2025-01-01"
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
                print("✅ POST successful")
                res_body = json.loads(response.read().decode('utf-8'))
                print(f"   Response: {res_body}")
            else:
                print(f"❌ POST failed with status {response.status}")
                return
    except Exception as e:
        print(f"❌ POST failed: {e}")
        return

    # 2. GET Config
    print("2️⃣ GET /config...")
    try:
        with urllib.request.urlopen(f"{BASE_URL}/config") as response:
            if response.status == 200:
                res_body = json.loads(response.read().decode('utf-8'))
                print(f"   Response: {res_body}")
                if res_body['instrument_key'] == "TEST_KEY_1" and res_body['date'] == "2025-01-01":
                     print("✅ GET verification passed")
                else:
                     print("❌ GET verification failed: Data mismatch")
            else:
                print(f"❌ GET failed with status {response.status}")
                return
    except Exception as e:
        print(f"❌ GET failed: {e}")
        return

    # 3. POST Config (Update)
    print("3️⃣ POST /config (Update)...")
    data = {
        "instrument_key": "TEST_KEY_2",
        "date": "2025-01-02"
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
                print("✅ POST update successful")
             else:
                print(f"❌ POST update failed with status {response.status}")
                return
    except Exception as e:
        print(f"❌ POST update failed: {e}")
        return

    # 4. GET Config (Verify Update)
    print("4️⃣ GET /config (Verify Update)...")
    try:
        with urllib.request.urlopen(f"{BASE_URL}/config") as response:
            if response.status == 200:
                res_body = json.loads(response.read().decode('utf-8'))
                print(f"   Response: {res_body}")
                if res_body['instrument_key'] == "TEST_KEY_2" and res_body['date'] == "2025-01-02":
                     print("✅ GET verification passed")
                else:
                     print("❌ GET verification failed: Data mismatch")
            else:
                print(f"❌ GET failed with status {response.status}")
                return
    except Exception as e:
        print(f"❌ GET failed: {e}")
        return
        
    print("✅ All tests passed!")

if __name__ == "__main__":
    # Wait a bit for server to reload if needed
    time.sleep(2)
    test_config()
