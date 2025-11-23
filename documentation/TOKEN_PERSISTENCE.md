# Token Persistence Implementation

## Overview

The Upstox authentication system now includes **persistent token storage** in MongoDB. Access tokens survive server restarts and are automatically loaded on startup.

## How It Works

### 1. **Token Storage**

When a user successfully authenticates via `/api/v1/upstox/callback` or `/api/v1/upstox/token`:

- The access token is stored in memory (as before)
- **NEW:** The token is also saved to MongoDB in the `upstox_tokens` collection
- Document structure:

  ```json
  {
    "_id": "upstox_token",
    "access_token": "eyJ0eXAiOiJKV1QiLCJr...",
    "token_type": "Bearer",
    "expires_in": 86400,
    "expires_at": "2025-11-20T17:55:27.192142",
    "updated_at": "2025-11-19T17:55:27.192142"
  }
  ```

### 2. **Token Loading on Startup**

When the FastAPI application starts:

- MongoDB connection is established
- **NEW:** `upstox_service.load_token_from_db()` is called automatically
- If a valid token exists in the database, it's loaded into memory
- The service checks if the token is still valid (not expired)
- Console messages indicate whether a token was loaded

### 3. **Token Deletion on Logout**

When a user logs out via `/api/v1/upstox/logout`:

- The token is cleared from memory (as before)
- **NEW:** The token is also deleted from MongoDB
- This ensures complete cleanup

## Database Schema

### Collection: `upstox_tokens`

| Field | Type | Description |
|-------|------|-------------|
| `_id` | String | Fixed value: "upstox_token" (single document) |
| `access_token` | String | The JWT access token from Upstox |
| `token_type` | String | Token type (usually "Bearer") |
| `expires_in` | Integer | Token validity duration in seconds |
| `expires_at` | String (ISO) | ISO format timestamp when token expires |
| `updated_at` | String (ISO) | When the token was last updated |

## Code Changes

### Files Modified

1. **`app/services/upstox_service.py`**
   - Added `load_token_from_db()` - Load token on startup
   - Added `save_token_to_db()` - Save token after authentication
   - Added `delete_token_from_db()` - Delete token on logout
   - Modified `generate_access_token()` - Now saves to DB automatically

2. **`main.py`**
   - Modified `lifespan()` - Now calls `load_token_from_db()` on startup

3. **`app/api/v1/endpoints/upstox.py`**
   - Modified `upstox_logout()` - Now deletes token from DB

### Files Created

4. **`app/models/upstox.py`**
   - Added `UpstoxTokenModel` - Pydantic model for token document

5. **`test_token_persistence.py`**
   - Test script to verify persistence functionality

## Usage

### Automatic Behavior (No Code Changes Required)

1. **User authenticates:**

   ```bash
   GET /api/v1/upstox/login
   # User completes OAuth flow
   GET /api/v1/upstox/callback?code=abc123
   ```

   → Token is automatically saved to MongoDB

2. **Server restarts:**

   ```bash
   uvicorn main:app --reload
   ```

   → Token is automatically loaded from MongoDB
   → User remains authenticated (if token hasn't expired)

3. **User logs out:**

   ```bash
   POST /api/v1/upstox/logout
   ```

   → Token is removed from memory and MongoDB

### Testing Persistence

Run the test script:

```bash
python test_token_persistence.py
```

This will:

- Connect to MongoDB
- Check current token status
- Attempt to load token from database
- Display token information if found

### Checking Logs

When the server starts, look for these messages:

**If token found and valid:**

```
✅ Loaded valid Upstox token from database (expires: 2025-11-20 17:55:27.192142)
```

**If token expired:**

```
⚠️  Token loaded from database but has expired
```

**If no token:**

```
ℹ️  No Upstox token found in database
```

## Benefits

✅ **Persistent Sessions** - Users don't need to re-authenticate after server restarts
✅ **24-Hour Validity** - Tokens are valid for 24 hours (Upstox default)
✅ **Automatic Management** - No manual intervention required
✅ **Clean Logout** - Complete cleanup on logout
✅ **Startup Validation** - Expired tokens are detected and cleared automatically

## MongoDB Operations

### View stored token

```javascript
// In MongoDB shell or Compass
db.upstox_tokens.findOne({_id: "upstox_token"})
```

### Manually delete token

```javascript
db.upstox_tokens.deleteOne({_id: "upstox_token"})
```

### Check expiry

```javascript
db.upstox_tokens.findOne(
  {_id: "upstox_token"},
  {expires_at: 1, updated_at: 1}
)
```

## Important Notes

1. **Single User System**: Currently stores only one token (single-user design)
   - For multi-user: Add user_id field and modify the `_id` strategy

2. **Token Expiry**:
   - Upstox tokens expire after 24 hours
   - System automatically detects expired tokens on startup
   - Users need to re-authenticate after expiry

3. **Security**:
   - Tokens are sensitive - ensure MongoDB is properly secured
   - Consider encrypting tokens at rest for production
   - Use proper MongoDB authentication

4. **Error Handling**:
   - If MongoDB is down, tokens fall back to memory-only mode
   - Server continues to function even if persistence fails

## Future Enhancements

- [ ] Add token refresh logic before expiry
- [ ] Support multiple users with user_id mapping
- [ ] Encrypt tokens at rest
- [ ] Add token expiry notifications
- [ ] Implement extended token support (1-year validity)
- [ ] Add token usage analytics

## Troubleshooting

### Token not persisting

- Check MongoDB connection
- Verify write permissions on `upstox_tokens` collection
- Check logs for error messages

### Token not loading on startup

- Ensure MongoDB is running before starting the app
- Check token hasn't expired
- Verify collection name is correct

### Token expired after restart

- Upstox tokens are only valid for 24 hours
- User needs to re-authenticate
- This is expected behavior
