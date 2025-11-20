#!/usr/bin/env python3
"""
Setup Prefect Secret Blocks for Christmas Campaign

This script creates Secret blocks in Prefect for storing sensitive environment variables.
These blocks can be referenced in deployments and flows.

Usage:
    python scripts/setup_secrets.py

Environment variables required:
    - NOTION_TOKEN
    - NOTION_CONTACTS_DB_ID
    - NOTION_TEMPLATES_DB_ID
    - NOTION_EMAIL_SEQUENCE_DB_ID
    - RESEND_API_KEY
    - DISCORD_WEBHOOK_URL (optional)
    - PREFECT_API_URL (for remote deployment)
"""

import os
import sys
from prefect.blocks.system import Secret


def create_secret_block(name: str, env_var: str, required: bool = True):
    """
    Create a Prefect Secret block from an environment variable.

    Args:
        name: Name of the secret block (e.g., "notion-token")
        env_var: Environment variable name (e.g., "NOTION_TOKEN")
        required: Whether this secret is required
    """
    value = os.getenv(env_var)

    if not value:
        if required:
            print(f"❌ Error: {env_var} environment variable not set")
            return False
        else:
            print(f"⏭️  Skipping optional secret: {name} (${env_var} not set)")
            return True

    try:
        # Check if block already exists
        try:
            existing = Secret.load(name)
            print(f"ℹ️  Secret block '{name}' already exists, updating...")
            # Delete old block
            existing.delete()
        except:
            pass

        # Create new secret block
        secret = Secret(value=value)
        secret.save(name, overwrite=True)
        print(f"✅ Created secret block: {name} (from ${env_var})")
        return True

    except Exception as e:
        print(f"❌ Failed to create secret block '{name}': {e}")
        return False


def main():
    """Create all required secret blocks."""

    print("🔐 Setting up Prefect Secret Blocks for Christmas Campaign\n")

    # Check PREFECT_API_URL
    api_url = os.getenv("PREFECT_API_URL")
    if api_url:
        print(f"📡 Deploying to: {api_url}\n")
    else:
        print(f"📡 Deploying to: Local Prefect instance\n")

    # Required secrets
    required_secrets = [
        ("notion-token", "NOTION_TOKEN"),
        ("notion-email-templates-db-id", "NOTION_EMAIL_TEMPLATES_DB_ID"),
        ("notion-email-sequence-db-id", "NOTION_EMAIL_SEQUENCE_DB_ID"),
        ("resend-api-key", "RESEND_API_KEY"),
    ]

    # Optional secrets
    optional_secrets = [
        ("discord-webhook-url", "DISCORD_WEBHOOK_URL"),
    ]

    success = True

    print("Creating required secrets:")
    for name, env_var in required_secrets:
        if not create_secret_block(name, env_var, required=True):
            success = False

    print("\nCreating optional secrets:")
    for name, env_var in optional_secrets:
        create_secret_block(name, env_var, required=False)

    if success:
        print("\n✅ All required secret blocks created successfully!")
        print("\nYou can now reference these in your flows:")
        print("```python")
        print("from prefect.blocks.system import Secret")
        print("")
        print("notion_token = Secret.load('notion-token').get()")
        print("resend_key = Secret.load('resend-api-key').get()")
        print("```")
        print("\nOr in prefect.yaml job_variables:")
        print("```yaml")
        print("job_variables:")
        print("  env:")
        print("    NOTION_TOKEN: \"{{ prefect.blocks.secret.notion-token }}\"")
        print("    RESEND_API_KEY: \"{{ prefect.blocks.secret.resend-api-key }}\"")
        print("```")
        return 0
    else:
        print("\n❌ Some required secrets failed to create")
        print("\nMake sure you have set all required environment variables:")
        for name, env_var in required_secrets:
            status = "✅" if os.getenv(env_var) else "❌"
            print(f"  {status} {env_var}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
