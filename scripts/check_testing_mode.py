"""
Check TESTING_MODE Secret block value from Prefect server.
"""
import asyncio
import os
from prefect.blocks.system import Secret

# Set Prefect API URL to production server
os.environ["PREFECT_API_URL"] = "https://prefect.galatek.dev/api"

async def check_testing_mode():
    """Check testing-mode Secret block value."""
    try:
        testing_mode_secret = await Secret.aload("testing-mode")
        value = testing_mode_secret.get()

        print(f"TESTING_MODE Secret Block Value: {value}")
        print(f"Type: {type(value)}")

        if value == "true" or value is True:
            print("✅ TESTING_MODE is enabled (1-minute intervals)")
        else:
            print(f"⚠️  TESTING_MODE is disabled or unexpected value: {value}")

        return value

    except Exception as e:
        print(f"❌ Error loading testing-mode Secret block: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(check_testing_mode())
