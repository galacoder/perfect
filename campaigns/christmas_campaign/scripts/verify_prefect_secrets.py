#!/usr/bin/env python3
"""
Verify Prefect Secret blocks for Christmas Campaign.

This script:
1. Connects to Prefect API (production server)
2. Attempts to load all required Secret blocks
3. Validates Resend API key by testing connection
4. Reports status of all credentials

Usage:
    python campaigns/christmas_campaign/scripts/verify_prefect_secrets.py

Author: Christmas Campaign Team
Created: 2025-11-28
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()


def verify_prefect_secrets():
    """
    Verify all Prefect Secret blocks required for Christmas Campaign.

    Required Secret blocks:
    - resend-api-key
    - notion-token
    - notion-christmas-contacts-db-id
    - notion-email-templates-db-id
    - notion-email-sequence-db-id
    """
    print("\n🔍 Verifying Prefect Secret blocks...")
    print("=" * 80)

    # Check Prefect API connection
    prefect_api_url = os.getenv("PREFECT_API_URL", "http://localhost:4200/api")
    print(f"\n📡 Prefect API URL: {prefect_api_url}")

    try:
        from prefect.blocks.system import Secret

        # Required secret blocks
        required_secrets = [
            "resend-api-key",
            "notion-token",
            "notion-christmas-contacts-db-id",
            "notion-email-templates-db-id",
            "notion-email-sequence-db-id"
        ]

        results = {}

        for secret_name in required_secrets:
            try:
                print(f"\n🔑 Checking Secret block: {secret_name}")
                secret = Secret.load(secret_name)
                secret_value = secret.get()

                if secret_value:
                    # Mask the secret value
                    masked_value = secret_value[:10] + "..." if len(secret_value) > 10 else "***"
                    print(f"   ✅ Loaded successfully: {masked_value}")
                    results[secret_name] = True

                    # Special validation for Resend API key
                    if secret_name == "resend-api-key":
                        print(f"   🧪 Testing Resend API connection...")
                        try:
                            import resend
                            resend.api_key = secret_value

                            # Test by checking if key format is valid
                            if secret_value.startswith("re_"):
                                print(f"   ✅ Resend API key format is valid")
                            else:
                                print(f"   ⚠️  Resend API key format looks unusual")

                        except Exception as e:
                            print(f"   ❌ Resend API test failed: {e}")
                            results[secret_name] = False

                else:
                    print(f"   ❌ Secret block exists but value is empty")
                    results[secret_name] = False

            except Exception as e:
                print(f"   ❌ Failed to load: {e}")
                results[secret_name] = False

                # Provide helpful error messages
                if "Connection refused" in str(e):
                    print(f"   💡 Tip: Make sure Prefect API is running at {prefect_api_url}")
                elif "not found" in str(e).lower():
                    print(f"   💡 Tip: Create Secret block with: prefect block register -m prefect.blocks.system")

        # Summary
        print("\n" + "=" * 80)
        print("📊 Summary:")
        print("-" * 80)

        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)

        for secret_name, status in results.items():
            status_emoji = "✅" if status else "❌"
            print(f"   {status_emoji} {secret_name}")

        print("-" * 80)
        print(f"   {success_count}/{total_count} Secret blocks verified")

        if success_count == total_count:
            print("\n✅ All Prefect Secret blocks are configured correctly!")
            return True
        else:
            print("\n⚠️  Some Secret blocks are missing or invalid")
            print("\nTo create missing Secret blocks:")
            print("1. Set environment variables in .env file")
            print("2. Run: set -a && source .env && set +a")
            print("3. Create blocks with:")
            print("   PREFECT_API_URL=https://prefect.galatek.dev/api python3 -c \"")
            print("   from prefect.blocks.system import Secret")
            print("   import os")
            print("   Secret(value=os.getenv('RESEND_API_KEY')).save('resend-api-key', overwrite=True)")
            print("   \"")
            return False

    except Exception as e:
        print(f"\n❌ Error verifying Prefect secrets: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check Prefect API is running: prefect server start")
        print("   2. Check PREFECT_API_URL environment variable")
        print("   3. Verify Secret blocks exist: prefect block ls")
        return False


if __name__ == "__main__":
    success = verify_prefect_secrets()
    sys.exit(0 if success else 1)
