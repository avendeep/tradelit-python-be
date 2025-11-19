"""
Example script demonstrating Upstox authentication flow
"""

import asyncio
import webbrowser
from app.services.upstox_service import upstox_service


async def test_upstox_auth():
    """Test the Upstox authentication flow"""

    print("=" * 60)
    print("Upstox Authentication Test")
    print("=" * 60)

    # Step 1: Get login URL
    print("\n[Step 1] Generating login URL...")
    login_url = upstox_service.get_login_url(state="test_state_123")
    print(f"Login URL: {login_url}\n")

    # Open browser for user to login
    print("[Step 2] Opening browser for authentication...")
    print("Please complete the login in your browser.")
    print("After login, you'll be redirected to the callback URL.")
    webbrowser.open(login_url)

    # In a real application, the callback endpoint would handle this
    print("\n[Step 3] Waiting for authorization code...")
    print("After successful login, you'll receive a code in the callback URL.")
    print(
        "Example: http://localhost:8000/api/v1/upstox/callback?code=ABC123&state=test_state_123"
    )

    # User would paste the code here
    auth_code = input("\nEnter the authorization code from the callback URL: ")

    if not auth_code:
        print("No code provided. Exiting.")
        return

    # Step 2: Exchange code for token
    print(f"\n[Step 4] Exchanging code for access token...")
    try:
        token_data = await upstox_service.generate_access_token(auth_code)
        print("\n✓ Authentication successful!")
        print(f"Access Token: {token_data['access_token'][:20]}...")
        print(f"Expires In: {token_data['expires_in']} seconds")
        print(f"Expires At: {token_data['expires_at']}")

        # Step 3: Get user profile
        print("\n[Step 5] Fetching user profile...")
        profile = await upstox_service.get_user_profile()

        if profile:
            print("\n✓ User Profile:")
            print(f"  User ID: {profile.get('data', {}).get('user_id', 'N/A')}")
            print(f"  Name: {profile.get('data', {}).get('user_name', 'N/A')}")
            print(f"  Email: {profile.get('data', {}).get('email', 'N/A')}")
            print(f"  Broker: {profile.get('data', {}).get('broker', 'N/A')}")
        else:
            print("✗ Failed to fetch user profile")

        # Check authentication status
        print("\n[Step 6] Checking authentication status...")
        is_valid = upstox_service.is_token_valid()
        print(f"Token Valid: {is_valid}")

    except Exception as e:
        print(f"\n✗ Authentication failed: {str(e)}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    print(
        "\n⚠️  Important: Make sure you have configured your Upstox credentials in .env file"
    )
    print("   - UPSTOX_API_KEY")
    print("   - UPSTOX_API_SECRET")
    print("   - UPSTOX_REDIRECT_URI\n")

    input("Press Enter to continue...")

    asyncio.run(test_upstox_auth())
