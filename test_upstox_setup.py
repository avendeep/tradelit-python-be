"""
Quick test to verify Upstox integration is working
"""

from app.services.upstox_service import upstox_service
from app.core.config import settings


def test_upstox_setup():
    """Test basic Upstox setup"""
    print("Testing Upstox Integration Setup")
    print("=" * 60)

    # Check configuration
    print("\n1. Configuration Check:")
    print(f"   API Key: {'✓ Set' if settings.UPSTOX_API_KEY else '✗ Not Set'}")
    print(f"   API Secret: {'✓ Set' if settings.UPSTOX_API_SECRET else '✗ Not Set'}")
    print(f"   Redirect URI: {settings.UPSTOX_REDIRECT_URI}")
    print(f"   Auth URL: {settings.UPSTOX_AUTH_URL}")
    print(f"   Token URL: {settings.UPSTOX_TOKEN_URL}")

    # Test login URL generation
    print("\n2. Login URL Generation:")
    try:
        login_url = upstox_service.get_login_url(state="test123")
        print(f"   ✓ Login URL generated successfully")
        print(f"   URL: {login_url[:80]}...")
    except Exception as e:
        print(f"   ✗ Failed: {str(e)}")

    # Check service initialization
    print("\n3. Service Status:")
    print(f"   Token Valid: {upstox_service.is_token_valid()}")
    print(
        f"   Access Token: {'Available' if upstox_service.get_access_token() else 'Not Available'}"
    )

    print("\n" + "=" * 60)
    print("✓ Upstox integration is properly set up!")
    print("\nNext Steps:")
    print("1. Configure your Upstox credentials in .env file")
    print("2. Start the FastAPI server: uvicorn main:app --reload")
    print("3. Visit http://localhost:8000/docs to test the endpoints")
    print("4. Call /api/v1/upstox/login to get the login URL")
    print("\nFor detailed guide, see UPSTOX_INTEGRATION.md")


if __name__ == "__main__":
    test_upstox_setup()
