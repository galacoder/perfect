## Environment Variables

### Required

```bash
NOTION_TOKEN=ntn_xxxxx                  # Notion integration token
NOTION_CONTACTS_DB_ID=xxxxx             # Contacts database ID
NOTION_TEMPLATES_DB_ID=xxxxx            # Email templates database ID
RESEND_API_KEY=re_xxxxx                 # Resend API key
```

### Optional

```bash
TESTING_MODE=false                      # true = fast waits (minutes), false = prod waits (days)
DISCORD_WEBHOOK_URL=https://...         # Discord webhook for CRITICAL segment alerts
API_HOST=0.0.0.0                        # FastAPI server host
API_PORT=8000                           # FastAPI server port
```

**Configuration location**: `.env` file (gitignored)

