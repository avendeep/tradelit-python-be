# Upstox Integration - Quick Start

## ✅ Integration Complete

The Upstox Python SDK has been successfully integrated with your TradeLit application. The OAuth 2.0 authentication flow is fully implemented.

## 📁 Files Created/Modified

### New Files

1. **`app/services/upstox_service.py`** - Core Upstox authentication service
2. **`app/schemas/upstox.py`** - Pydantic schemas for Upstox data models
3. **`app/api/v1/endpoints/upstox.py`** - FastAPI endpoints for authentication
4. **`test_upstox_setup.py`** - Setup verification script
5. **`test_upstox_auth.py`** - Authentication flow test script
6. **`UPSTOX_INTEGRATION.md`** - Comprehensive integration guide

### Modified Files

1. **`app/core/config.py`** - Added Upstox configuration settings
2. **`app/api/v1/router.py`** - Registered Upstox endpoints
3. **`requirements.txt`** - Added `requests` library
4. **`.env`** - Added Upstox credentials placeholders

## 🚀 Quick Setup

### 1. Get Upstox API Credentials

1. Visit [Upstox Developer Portal](https://upstox.com/developer/apps)
2. Create a new app or use existing one
3. Note your **API Key** and **API Secret**
4. Set redirect URI to: `http://localhost:8000/api/v1/upstox/callback`

### 2. Configure Environment Variables

Edit `.env` file and add your credentials:

```env
UPSTOX_API_KEY=your_actual_api_key_here
UPSTOX_API_SECRET=your_actual_api_secret_here
UPSTOX_REDIRECT_URI=http://localhost:8000/api/v1/upstox/callback
```

### 3. Start the Application

```bash
cd tradeLit_app
uvicorn main:app --reload
```

### 4. Test the Integration

Visit: <http://localhost:8000/docs>

You'll see new Upstox endpoints under "Upstox Authentication" section.

## 🔐 Authentication Flow

### Method 1: Using Swagger UI (Recommended for Testing)

1. Go to <http://localhost:8000/docs>
2. Expand **"Upstox Authentication"** section
3. Try **GET /api/v1/upstox/login**
   - Click "Try it out" → "Execute"
   - Copy the `login_url` from response
4. Open the login URL in browser
5. Complete Upstox login (username, password, OTP)
6. After redirect, copy the `code` from callback URL
7. Use **POST /api/v1/upstox/token** with the code
8. Check authentication status with **GET /api/v1/upstox/status**

### Method 2: Using cURL

```bash
# Step 1: Get login URL
curl http://localhost:8000/api/v1/upstox/login

# Step 2: Open the login_url in browser and complete authentication
# You'll be redirected to callback with code parameter

# Step 3: Exchange code for token
curl -X POST http://localhost:8000/api/v1/upstox/token \
  -H "Content-Type: application/json" \
  -d '{"code": "YOUR_AUTH_CODE_HERE"}'

# Step 4: Check status
curl http://localhost:8000/api/v1/upstox/status

# Step 5: Get user profile
curl http://localhost:8000/api/v1/upstox/profile
```

### Method 3: Using Python Test Script

```bash
python test_upstox_auth.py
```

This script will:

- Generate login URL
- Open browser for authentication
- Prompt for authorization code
- Exchange code for access token
- Fetch user profile

## 📡 Available API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/upstox/login` | Generate OAuth login URL |
| GET | `/api/v1/upstox/callback` | OAuth callback (auto-exchanges code) |
| POST | `/api/v1/upstox/token` | Manually exchange code for token |
| GET | `/api/v1/upstox/status` | Check authentication status |
| GET | `/api/v1/upstox/profile` | Get user profile (requires auth) |
| POST | `/api/v1/upstox/logout` | Logout and revoke token |

## 🔑 Key Features Implemented

✅ **OAuth 2.0 Flow** - Complete authentication implementation
✅ **Token Management** - Automatic token validation and expiry tracking
✅ **User Profile** - Fetch authenticated user information
✅ **State Parameter** - CSRF protection support
✅ **Error Handling** - Comprehensive error messages
✅ **Type Safety** - Pydantic schemas for data validation
✅ **API Client** - Pre-configured upstox_client integration

## 📚 Usage in Your Code

```python
from app.services.upstox_service import upstox_service

# Generate login URL
login_url = upstox_service.get_login_url(state="optional_state")

# Exchange code for token (after OAuth callback)
token_data = await upstox_service.generate_access_token(auth_code)

# Check if authenticated
if upstox_service.is_token_valid():
    # Get API client for making Upstox API calls
    api_client = upstox_service.get_api_client()
    
    # Get user profile
    profile = await upstox_service.get_user_profile()
```

## ⚠️ Important Notes

1. **Redirect URI Must Match**: The redirect URI in your `.env` must exactly match the one configured in your Upstox app settings.

2. **Authorization Code is Single-Use**: Each auth code can only be used once. If token generation fails, you need to login again.

3. **Token Validity**: Access tokens are valid for 24 hours (86400 seconds).

4. **In-Memory Storage**: Currently tokens are stored in memory. For production, implement database storage.

5. **HTTPS Required**: In production, use HTTPS for all OAuth flows.

## 🐛 Troubleshooting

### Error: "Invalid Credentials"

- Check that `UPSTOX_API_KEY` and `UPSTOX_API_SECRET` are correct
- Verify `UPSTOX_REDIRECT_URI` matches exactly with Upstox app settings

### Error: "Invalid or expired code"

- Authorization codes can only be used once
- Get a new code by going through the login flow again

### Error: "ModuleNotFoundError: upstox_client"

- Run: `pip install upstox-python-sdk`
- Verify installation: `pip list | grep upstox`

## 📖 Next Steps

1. **Test Authentication**: Use Swagger UI to test the complete flow
2. **Implement Trading Features**: Add order placement, positions, holdings
3. **Add WebSocket**: Implement real-time market data streaming
4. **Database Integration**: Store tokens in MongoDB for persistence
5. **Frontend Integration**: Build UI for seamless authentication

## 📄 Documentation

- **Comprehensive Guide**: `UPSTOX_INTEGRATION.md`
- **Upstox API Docs**: <https://upstox.com/developer/api-documentation/>
- **Upstox Python SDK**: <https://github.com/upstox/upstox-python>

## 🎉 You're All Set

The Upstox integration is ready to use. Start the server and try the authentication flow!

```bash
uvicorn main:app --reload
```

Then visit: <http://localhost:8000/docs>
