# Christmas Campaign - Secrets Setup Guide

This guide shows you how to securely add your API tokens and credentials to Prefect using Secret Blocks.

## Why Use Prefect Secret Blocks?

✅ **Secure**: Encrypted storage in Prefect
✅ **Centralized**: Manage secrets in one place
✅ **Scalable**: Works across all deployments
✅ **Git-safe**: No credentials in your code or repo

---

## Step 1: Load Your Environment Variables

First, make sure your `.env` file has all required values:

```bash
cd /Users/sangle/Dev/action/projects/perfect

# Check your .env file
cat .env
```

**Required variables:**
- `NOTION_TOKEN` - Your Notion integration token
- `NOTION_CONTACTS_DB_ID` - Notion Contacts database ID
- `NOTION_TEMPLATES_DB_ID` - Notion Templates database ID
- `NOTION_EMAIL_SEQUENCE_DB_ID` - Notion Email Sequence database ID
- `RESEND_API_KEY` - Resend API key for sending emails

**Optional variables:**
- `DISCORD_WEBHOOK_URL` - Discord webhook for hot lead alerts
- `TESTING_MODE` - `true` for fast waits, `false` for production timing

---

## Step 2: Create Secret Blocks

### Option A: Using the Setup Script (Recommended)

```bash
cd /Users/sangle/Dev/action/projects/perfect

# Load environment variables from .env
export $(cat .env | grep -v '^#' | xargs)

# Create secret blocks on production Prefect server
PREFECT_API_URL=https://prefect.galatek.dev/api python3 scripts/setup_secrets.py
```

**What this does:**
1. Reads your environment variables
2. Creates encrypted Secret blocks in Prefect
3. Names them: `notion-token`, `resend-api-key`, etc.
4. Stores them on your production Prefect server

### Option B: Manual Creation (Alternative)

If you prefer to create secrets manually:

```python
# Run this on a machine with access to your Prefect server
import os
from prefect.blocks.system import Secret

# Set Prefect API URL
os.environ["PREFECT_API_URL"] = "https://prefect.galatek.dev/api"

# Create each secret
Secret(value=os.environ["NOTION_TOKEN"]).save("notion-token")
Secret(value=os.environ["NOTION_CONTACTS_DB_ID"]).save("notion-contacts-db-id")
Secret(value=os.environ["NOTION_TEMPLATES_DB_ID"]).save("notion-templates-db-id")
Secret(value=os.environ["NOTION_EMAIL_SEQUENCE_DB_ID"]).save("notion-email-sequence-db-id")
Secret(value=os.environ["RESEND_API_KEY"]).save("resend-api-key")

# Optional
if "DISCORD_WEBHOOK_URL" in os.environ:
    Secret(value=os.environ["DISCORD_WEBHOOK_URL"]).save("discord-webhook-url")
```

---

## Step 3: Verify Secret Blocks Were Created

```bash
# List all secret blocks
PREFECT_API_URL=https://prefect.galatek.dev/api prefect block ls --filter block_type.slug=secret

# Inspect a specific secret (shows metadata, not the value)
PREFECT_API_URL=https://prefect.galatek.dev/api prefect block inspect secret/notion-token
```

---

## Step 4: Update Flows to Use Secrets

Your flows should load secrets like this:

```python
from prefect.blocks.system import Secret
from prefect import task, flow

@task
def get_notion_client():
    """Get Notion client with token from Prefect Secret block."""
    notion_token = Secret.load("notion-token").get()
    # Use notion_token...

@flow
def my_flow():
    client = get_notion_client()
    # ...
```

**Current Status**: Christmas campaign flows already use environment variables. We need to update them to use Secret blocks.

---

## Step 5: Update Christmas Campaign Flows (Todo)

We need to update these files to use Prefect Secret blocks instead of `os.getenv()`:

**Files to update:**
1. `campaigns/christmas_campaign/tasks/notion_operations.py`
   - Change: `os.getenv("NOTION_TOKEN")`
   - To: `Secret.load("notion-token").get()`

2. `campaigns/christmas_campaign/tasks/resend_operations.py`
   - Change: `os.getenv("RESEND_API_KEY")`
   - To: `Secret.load("resend-api-key").get()`

3. `campaigns/christmas_campaign/flows/signup_handler.py`
   - Update Notion client initialization

---

## Alternative: Use Environment Variables (Simpler for Now)

If you want to get things working quickly **without** Secret blocks, you can set environment variables on the production worker directly:

### On Production Server

```bash
ssh sangle@galatek.dev

# Add to ~/.bashrc or worker's environment
cat >> ~/.bashrc <<'EOF'

# Prefect Christmas Campaign Secrets
export NOTION_TOKEN="ntn_xxxxx"
export NOTION_CONTACTS_DB_ID="xxxxx"
export NOTION_TEMPLATES_DB_ID="xxxxx"
export NOTION_EMAIL_SEQUENCE_DB_ID="xxxxx"
export RESEND_API_KEY="re_xxxxx"
export TESTING_MODE="true"
EOF

# Reload
source ~/.bashrc

# Restart worker
sudo systemctl restart prefect-worker
# OR if running manually: prefect worker start --pool default
```

**Pros:**
- ✅ Quick and simple
- ✅ Works immediately
- ✅ No code changes needed

**Cons:**
- ❌ Secrets stored in plaintext on server
- ❌ Need to SSH to update
- ❌ Not using Prefect's security features

---

## Recommended Approach

**For now (getting it working):**
1. Use environment variables on the production server (simpler)
2. Test that flows work end-to-end

**Later (production hardening):**
1. Migrate to Prefect Secret blocks
2. Update flow code to load from blocks
3. Remove environment variables from server

---

## Testing After Setup

Once secrets are configured (either method):

```bash
# Trigger a test flow run
PREFECT_API_URL=https://prefect.galatek.dev/api prefect deployment run \
  christmas-signup-handler/christmas-signup-handler \
  --param email="secret-test@example.com" \
  --param first_name="SecretTest" \
  --param business_name="Testing Secrets" \
  --param assessment_score=80 \
  --param red_systems=1 \
  --param orange_systems=1 \
  --param yellow_systems=0 \
  --param green_systems=0

# Check logs
PREFECT_API_URL=https://prefect.galatek.dev/api prefect flow-run logs <flow-run-id>
```

**Expected**: No more "API token is invalid" errors - flow should create Notion records and schedule emails successfully!

---

## Troubleshooting

### "API token is invalid"
- ❌ Worker doesn't have access to secrets
- ✅ Solution: Set environment variables on production server OR create Secret blocks and update code

### "Secret block not found"
- ❌ Secret blocks not created
- ✅ Solution: Run `scripts/setup_secrets.py` again

### "ModuleNotFoundError"
- ❌ Code not on production server
- ✅ Solution: Already fixed! Git-based deployment pulls code automatically

---

## Summary

**Quick Path** (Recommended for now):
1. SSH to production: `ssh sangle@galatek.dev`
2. Add environment variables to `~/.bashrc`
3. Restart worker
4. Test flows

**Production Path** (Do later):
1. Run `scripts/setup_secrets.py` to create Secret blocks
2. Update flow code to use `Secret.load()`
3. Test and verify
4. Remove environment variables from server

Choose the path that gets you running fastest, then migrate to Secret blocks when ready for production hardening!
