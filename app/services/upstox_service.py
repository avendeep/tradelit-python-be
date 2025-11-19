"""
Upstox authentication and API service
Implements OAuth 2.0 authentication flow for Upstox API
"""

import upstox_client
from typing import Optional, Dict, Any
from urllib.parse import urlencode
import requests
from datetime import datetime, timedelta

from app.core.config import settings
from app.db.mongodb import MongoDB


class UpstoxService:
    """Service for Upstox authentication and API operations"""

    def __init__(self):
        self.api_key = settings.UPSTOX_API_KEY
        self.api_secret = settings.UPSTOX_API_SECRET
        self.redirect_uri = settings.UPSTOX_REDIRECT_URI
        self.auth_url = settings.UPSTOX_AUTH_URL
        self.token_url = settings.UPSTOX_TOKEN_URL
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        self._collection_name = "upstox_tokens"

    async def load_token_from_db(self) -> bool:
        """
        Load access token from database on startup

        Returns:
            True if token was loaded and is valid, False otherwise
        """
        try:
            collection = MongoDB.get_collection(self._collection_name)
            token_doc = await collection.find_one({"_id": "upstox_token"})

            if token_doc:
                self._access_token = token_doc.get("access_token")
                expires_at_str = token_doc.get("expires_at")

                # Parse datetime string
                if isinstance(expires_at_str, str):
                    self._token_expiry = datetime.fromisoformat(expires_at_str)
                elif isinstance(expires_at_str, datetime):
                    self._token_expiry = expires_at_str

                # Check if token is still valid
                if self.is_token_valid():
                    print(
                        f"✅ Loaded valid Upstox token from database (expires: {self._token_expiry})"
                    )
                    return True
                else:
                    print("⚠️  Token loaded from database but has expired")
                    self._access_token = None
                    self._token_expiry = None
                    return False
            else:
                print("ℹ️  No Upstox token found in database")
                return False

        except Exception as e:
            print(f"❌ Error loading token from database: {str(e)}")
            return False

    async def save_token_to_db(self, token_data: Dict[str, Any]) -> bool:
        """
        Save access token to database for persistence

        Args:
            token_data: Token data including access_token, expires_in, etc.

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            collection = MongoDB.get_collection(self._collection_name)

            # Prepare document
            token_doc = {
                "_id": "upstox_token",
                "access_token": token_data["access_token"],
                "token_type": token_data.get("token_type", "Bearer"),
                "expires_in": token_data["expires_in"],
                "expires_at": token_data["expires_at"],
                "updated_at": datetime.now().isoformat(),
            }

            # Upsert (update or insert)
            await collection.replace_one(
                {"_id": "upstox_token"}, token_doc, upsert=True
            )

            print(
                f"✅ Saved Upstox token to database (expires: {token_data['expires_at']})"
            )
            return True

        except Exception as e:
            print(f"❌ Error saving token to database: {str(e)}")
            return False

    def get_login_url(self, state: Optional[str] = None) -> str:
        """
        Generate the Upstox OAuth login URL

        Args:
            state: Optional state parameter for CSRF protection

        Returns:
            Complete login URL for redirect
        """
        params = {
            "response_type": "code",
            "client_id": self.api_key,
            "redirect_uri": self.redirect_uri,
        }

        if state:
            params["state"] = state

        login_url = f"{self.auth_url}?{urlencode(params, safe=':/')}"
        return login_url

    async def generate_access_token(self, auth_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token

        Args:
            auth_code: Authorization code received from callback

        Returns:
            Token response with access_token and metadata

        Raises:
            Exception: If token generation fails
        """
        payload = {
            "code": auth_code,
            "client_id": self.api_key,
            "client_secret": self.api_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }

        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        try:
            response = requests.post(
                self.token_url, data=payload, headers=headers, timeout=30
            )
            response.raise_for_status()

            token_data = response.json()

            # Store access token and calculate expiry
            self._access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 86400)  # Default 24 hours
            self._token_expiry = datetime.now() + timedelta(seconds=expires_in)

            result = {
                "access_token": self._access_token,
                "expires_in": expires_in,
                "token_type": token_data.get("token_type", "Bearer"),
                "expires_at": self._token_expiry.isoformat(),
            }

            # Save token to database for persistence
            await self.save_token_to_db(result)

            return result

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to generate access token: {str(e)}")

    def is_token_valid(self) -> bool:
        """Check if the current access token is still valid"""
        if not self._access_token or not self._token_expiry:
            return False
        return datetime.now() < self._token_expiry

    def get_access_token(self) -> Optional[str]:
        """Get the current access token if valid"""
        if self.is_token_valid():
            return self._access_token
        return None

    def get_api_client(self) -> Optional[upstox_client.ApiClient]:
        """
        Get configured Upstox API client with authentication

        Returns:
            Configured ApiClient instance or None if no valid token
        """
        if not self.is_token_valid():
            return None

        configuration = upstox_client.Configuration()
        configuration.access_token = self._access_token

        return upstox_client.ApiClient(configuration)

    async def get_user_profile(self) -> Optional[Dict[str, Any]]:
        """
        Get user profile information using the current access token

        Returns:
            User profile data or None if token is invalid
        """
        api_client = self.get_api_client()
        if not api_client:
            return None

        try:
            api_instance = upstox_client.UserApi(api_client)
            api_response = api_instance.get_profile(api_version="2.0")
            return api_response.to_dict() if api_response else None
        except Exception as e:
            print(f"Error fetching user profile: {str(e)}")
            return None

    def revoke_token(self):
        """Revoke the current access token"""
        self._access_token = None
        self._token_expiry = None

    async def delete_token_from_db(self) -> bool:
        """
        Delete access token from database

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            collection = MongoDB.get_collection(self._collection_name)
            await collection.delete_one({"_id": "upstox_token"})
            print("✅ Deleted Upstox token from database")
            return True
        except Exception as e:
            print(f"❌ Error deleting token from database: {str(e)}")
            return False

    async def get_option_chain(
        self, instrument_key: str, expiry_date: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get put/call option chain for an underlying symbol

        Args:
            instrument_key: Key of underlying symbol (e.g., 'NSE_INDEX|Nifty 50')
            expiry_date: Expiry date in YYYY-MM-DD format

        Returns:
            Option chain data or None if request fails

        Raises:
            Exception: If not authenticated or request fails
        """
        if not self.is_token_valid():
            raise Exception("Not authenticated. Please login first.")

        url = "https://api.upstox.com/v2/option/chain"

        params = {
            "instrument_key": instrument_key,
            "expiry_date": expiry_date,
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self._access_token}",
        }

        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching option chain: {str(e)}")
            if hasattr(e.response, "text"):
                print(f"Response: {e.response.text}")
            raise Exception(f"Failed to fetch option chain: {str(e)}")


# Singleton instance
upstox_service = UpstoxService()
