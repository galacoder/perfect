# BusinessX Canada Lead Nurture Campaign

Automated email nurture sequence for leads who complete the BusinessX assessment.

## Campaign Overview

This campaign manages the entire lead journey from signup to conversion:

1. **Signup** - Capture lead information from website form
2. **Assessment** - Process completed assessments and classify segment
3. **Email Sequence** - Send 5-email nurture sequence with personalized content

## Flows

- `signup_handler.py` - Handle new signup submissions
- `assessment_handler.py` - Process assessments and trigger email sequence
- `email_sequence.py` - 5-email nurture sequence with wait times

## Tasks

- `notion_operations.py` - Notion database CRUD operations
- `resend_operations.py` - Email delivery via Resend API
- `routing.py` - Segment classification (CRITICAL/URGENT/OPTIMIZE)
- `template_operations.py` - Dynamic template fetching from Notion

## Integrations

- **Notion**: Contact database, email templates
- **Resend**: Email delivery service
- **Discord**: Hot lead notifications (CRITICAL segment)

## Diagrams

See `diagrams/` for ASCII workflow documentation:
- `CAMPAIGN_OVERVIEW.txt` - High-level campaign architecture
- `SIGNUP_HANDLER.txt` - Signup flow task breakdown
- `ASSESSMENT_HANDLER.txt` - Assessment flow with segment logic
- `EMAIL_SEQUENCE.txt` - 5-email sequence with wait times

## Testing

Run tests for this campaign:
```bash
# From project root
pytest campaigns/businessx_canada_lead_nurture/tests/

# Run specific test module
pytest campaigns/businessx_canada_lead_nurture/tests/test_signup_handler.py
```

## Development

### Local Testing
```bash
# Set testing mode for faster email sequence (minutes instead of days)
export TESTING_MODE=true

# Run webhook server
python server.py

# Test signup webhook
curl -X POST http://localhost:8000/webhook/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User","business_name":"Test Corp"}'

# Test assessment webhook
curl -X POST http://localhost:8000/webhook/assessment \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","red_systems":2,"orange_systems":1}'
```

### Deployment

This campaign is deployed to Prefect Cloud. See `/DEPLOYMENT.md` for details.

## Segment Classification

Leads are classified into 3 segments based on assessment results:

- **CRITICAL** (red_systems >= 2): Immediate attention needed → Discord alert
- **URGENT** (red_systems == 1 OR orange_systems >= 2): Action needed soon
- **OPTIMIZE** (all others): Growth opportunities

Each segment receives personalized email content (Email 2 and Email 5 variants).

## Environment Variables

Required environment variables:
- `NOTION_TOKEN` - Notion integration token
- `NOTION_CONTACTS_DB_ID` - Contacts database ID
- `NOTION_TEMPLATES_DB_ID` - Email templates database ID
- `RESEND_API_KEY` - Resend API key
- `DISCORD_WEBHOOK_URL` - Discord webhook for hot leads
- `TESTING_MODE` - Set to "true" for faster wait times (optional, defaults to false)
