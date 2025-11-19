# Upstox Authentication Integration Guide

This guide explains how to set up and use Upstox authentication in the TradeLit application.

## Overview

The Upstox integration implements OAuth 2.0 authentication flow following the official Upstox API documentation. It allows users to:

- Authenticate with Upstox
- Get access tokens for API calls
- Access user profile information
- Make authenticated API requests

## Setup

### 1. Get Upstox API Credentials

1. Go to [Upstox Developer Portal](https://upstox.com/developer/apps)
2. Create a new app or use an existing one
3. Note down your:
   - API Key (client_id)
   - API Secret (client_secret)
   - Redirect URI (must match exactly)

### 2. Configure Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```env
UPSTOX_API_KEY=your_api_key_here
UPSTOX_API_SECRET=your_api_secret_here
UPSTOX_REDIRECT_URI=http://localhost:8000/api/v1/upstox/callback
```

**Important:** The redirect URI in your `.env` file MUST exactly match the redirect URI configured in your Upstox app settings.

## Authentication Flow

### Step 1: Get Login URL

**Endpoint:** `GET /api/v1/upstox/login`

Request:

```bash
curl http://localhost:8000/api/v1/upstox/login
```

Response:

```json
{
  "login_url": "https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id=xxx&redirect_uri=xxx&state=xxx",
  "state": "random_state_token"
}
```

**Usage:** Redirect the user to the `login_url` in their browser.

### Step 2: User Authentication

The user will:

1. Be redirected to Upstox login page
2. Enter their credentials
3. Complete 2FA (SMS OTP or TOTP)
4. Authorize your application
5. Be redirected back to your callback URL with an authorization code

### Step 3: Exchange Code for Token

After successful login, Upstox redirects to your callback URL:

```
http://localhost:8000/api/v1/upstox/callback?code=abc123&state=xyz
```

The callback endpoint automatically exchanges the code for an access token.

**Alternative:** You can also manually exchange the code using:

**Endpoint:** `POST /api/v1/upstox/token`

Request:

```bash
curl -X POST http://localhost:8000/api/v1/upstox/token \
  -H "Content-Type: application/json" \
  -d '{"code": "authorization_code_here"}'
```

Response:

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "expires_in": 86400,
  "token_type": "Bearer",
  "expires_at": "2025-11-20T15:30:00"
}
```

## Available Endpoints

### 1. Get Login URL

```
GET /api/v1/upstox/login
```

Generates the OAuth login URL.

### 2. OAuth Callback

```
GET /api/v1/upstox/callback?code=xxx&state=xxx
```

Receives the authorization code and exchanges it for an access token.

### 3. Generate Token (Alternative)

```
POST /api/v1/upstox/token
Body: {"code": "authorization_code"}
```

Manually exchange authorization code for access token.

### 4. Get Authentication Status

```
GET /api/v1/upstox/status
```

Check if user is authenticated and token validity.

Response:

```json
{
  "is_authenticated": true,
  "token_valid": true,
  "expires_at": "2025-11-20T15:30:00",
  "user_profile": {
    "user_id": "ABC123",
    "user_name": "John Doe",
    "email": "john@example.com",
    "user_type": "individual",
    "broker": "UPSTOX"
  }
}
```

### 5. Get User Profile

```
GET /api/v1/upstox/profile
```

Get authenticated user's profile information.

### 6. Logout

```
POST /api/v1/upstox/logout
```

Revoke access token and clear session.

## Using the Access Token

Once authenticated, the access token is stored in memory by the `UpstoxService`. You can use it to make API calls:

```python
from app.services.upstox_service import upstox_service

# Get API client
api_client = upstox_service.get_api_client()

if api_client:
    # Use the client to make API calls
    # Example: Get holdings, positions, etc.
    pass
```

## Testing the Integration

1. Start the application:

```bash
uvicorn main:app --reload
```

2. Visit the API docs:

```
http://localhost:8000/docs
```

3. Try the authentication flow:
   - Call `/api/v1/upstox/login` to get the login URL
   - Open the URL in a browser
   - Complete the login process
   - Check `/api/v1/upstox/status` to verify authentication

## Important Notes

### Security Considerations

1. **State Parameter:** Used for CSRF protection. Store and verify it in production.
2. **HTTPS Required:** In production, use HTTPS for all OAuth flows.
3. **Token Storage:** Currently tokens are stored in memory. Implement persistent storage for production.
4. **API Secret:** Never expose your API secret in client-side code.

### Token Management

- Access tokens are valid for 24 hours (86400 seconds)
- Tokens are automatically validated before API calls
- Extended tokens (1 year validity) are available for specific read-only APIs

### Error Handling

Common errors:

- **Invalid Credentials:** Check that your API key, secret, and redirect URI match exactly
- **Invalid Code:** Authorization codes are single-use only
- **Expired Token:** Tokens expire after 24 hours, user needs to re-authenticate

## Next Steps

1. **Implement Token Persistence:** Store tokens in database for multi-session support
2. **Add State Verification:** Verify state parameter in callback for CSRF protection
3. **Implement Token Refresh:** Add logic to handle token expiration gracefully
4. **Add Upstox API Features:** Implement trading functions (orders, positions, holdings)
5. **WebSocket Integration:** Add real-time market data streaming

## Resources

- [Upstox API Documentation](https://upstox.com/developer/api-documentation/)
- [Upstox Python SDK](https://github.com/upstox/upstox-python)
- [OAuth 2.0 Specification](https://oauth.net/2/)

## Support

For issues related to:

- Upstox API: Visit [Upstox API Community](https://community.upstox.com/c/developer-api/15)
- This integration: Check the code comments or create an issue
