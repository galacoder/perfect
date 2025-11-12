# BusOS Email Sequence - Prefect Migration

Automated email nurture sequence system built with Prefect v3, replacing the original n8n workflow.

## Overview

This system sends a 5-email nurture sequence to contacts who complete the BusOS assessment, with segment-based content routing (CRITICAL/URGENT/OPTIMIZE).

### Key Features

- ✅ **Dynamic Email Templates**: Edit templates in Notion without code deployment
- ✅ **Segment-Based Routing**: Automatic classification and content personalization
- ✅ **Testing Mode**: Fast validation (1-4min waits) vs Production (24-48hr waits)
- ✅ **Webhook Integration**: FastAPI server for frontend integration
- ✅ **Comprehensive Testing**: 93 unit tests + integration tests
- ✅ **Discord Notifications**: Alert for hot leads (CRITICAL segment)
- ✅ **Production Ready**: Deployment guides for server, Docker, Prefect Cloud

## Quick Start

### 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Seed Email Templates

```bash
python scripts/seed_templates.py
```

### 4. Run Tests

```bash
# Dry-run validation (no API calls)
python test_flows_dry_run.py

# Integration tests (mocked APIs)
python test_integration_e2e.py --mode mock
```

### 5. Start Webhook Server

```bash
uvicorn server:app --reload
```

Server runs at `http://localhost:8000`

### 6. Test Webhooks

```bash
# Health check
curl http://localhost:8000/health

# Signup webhook
curl -X POST http://localhost:8000/webhook/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test","first_name":"Test","business_name":"Test Co"}'

# Assessment webhook
curl -X POST http://localhost:8000/webhook/assessment \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","red_systems":2,"orange_systems":1}'
```

## Architecture

```
Frontend
   ↓
FastAPI Webhooks (/webhook/signup, /webhook/assessment)
   ↓
Prefect Flows (signup_handler, assessment_handler, email_sequence)
   ↓
Notion Database (Contacts, Templates) + Resend API (Email Delivery)
```

## Project Structure

```
perfect/
├── flows/                    # Prefect flows
│   ├── __init__.py
│   ├── signup_handler.py    # Handle new signups
│   ├── assessment_handler.py # Handle assessments
│   ├── email_sequence.py    # 5-email sequence
│   └── deploy.py            # Prefect deployment config
├── tasks/                    # Prefect tasks
│   ├── __init__.py
│   ├── notion_operations.py # Notion CRUD
│   ├── resend_operations.py # Email sending
│   ├── routing.py           # Segment classification
│   └── template_operations.py # Dynamic template fetching
├── config/                   # Configuration
│   └── email_templates.py   # Static templates (fallback)
├── tests/                    # Unit tests (93 tests)
│   ├── test_notion_operations.py
│   ├── test_resend_operations.py
│   ├── test_routing.py
│   └── test_template_operations.py
├── scripts/                  # Utility scripts
│   └── seed_templates.py    # Seed Notion templates
├── server.py                 # FastAPI webhook server
├── test_flows_dry_run.py    # Dry-run validation
├── test_integration_e2e.py  # Integration tests
├── requirements.txt          # Python dependencies
├── DEPLOYMENT.md             # Deployment guide
├── .env                      # Environment config (gitignored)
└── .gitignore
```

## Email Sequence

### Email Flow

1. **Email #1**: Assessment invitation (Universal)
   - Wait: 24h (prod) / 1min (test)

2. **Email #2**: Results (Segment-specific)
   - 2A: CRITICAL (2+ red systems)
   - 2B: URGENT (1 red OR 2+ orange)
   - 2C: OPTIMIZE (all green/yellow)
   - Wait: 48h (prod) / 2min (test)

3. **Email #3**: BusOS Framework (Universal)
   - Wait: 48h (prod) / 3min (test)

4. **Email #4**: Christmas Special (Universal)
   - Wait: 48h (prod) / 4min (test)

5. **Email #5**: Final push (Segment-specific)
   - 5A: CRITICAL
   - 5B: URGENT
   - 5C: OPTIMIZE

### Segment Classification

| Segment | Condition | Urgency |
|---------|-----------|---------|
| CRITICAL | 2+ red systems | Immediate action needed |
| URGENT | 1 red OR 2+ orange | Attention needed soon |
| OPTIMIZE | 0-1 red, 0-1 orange | Growth opportunities |

## Testing

### Unit Tests (93 tests)

```bash
pytest tests/ -v
```

Coverage:
- Notion operations (12 tests)
- Resend operations (17 tests)
- Routing logic (40+ tests)
- Template operations (24 tests)

### Dry-Run Validation

```bash
python test_flows_dry_run.py
```

Tests flow structure without API calls.

### Integration Tests

```bash
# Mocked APIs (recommended)
python test_integration_e2e.py --mode mock

# Real APIs (caution: creates records)
python test_integration_e2e.py --mode real
```

## Deployment

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for complete guide.

### Quick Deploy Options

**Local Development**:
```bash
uvicorn server:app --reload
```

**Production Server**:
```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
```

**Docker**:
```bash
docker-compose up -d
```

**Prefect Cloud**:
```bash
python flows/deploy.py
prefect agent start -q default
```

## Environment Variables

### Required

```bash
NOTION_TOKEN=ntn_xxxxx
NOTION_CONTACTS_DB_ID=xxxxx
NOTION_TEMPLATES_DB_ID=xxxxx
RESEND_API_KEY=re_xxxxx
```

### Optional

```bash
TESTING_MODE=false              # true = fast waits, false = production waits
DISCORD_WEBHOOK_URL=https://... # Hot lead notifications
API_HOST=0.0.0.0               # Server host
API_PORT=8000                   # Server port
```

## API Endpoints

### GET /health

Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-12T10:30:00Z",
  "environment": {
    "testing_mode": false,
    "notion_configured": true,
    "resend_configured": true
  }
}
```

### POST /webhook/signup

Handle new user signups.

**Request**:
```json
{
  "email": "john@example.com",
  "name": "John Doe",
  "first_name": "John",
  "business_name": "John's Salon"
}
```

**Response**:
```json
{
  "status": "accepted",
  "message": "Signup received and being processed",
  "email": "john@example.com",
  "timestamp": "2025-11-12T10:30:00Z"
}
```

### POST /webhook/assessment

Handle completed assessments and trigger email sequence.

**Request**:
```json
{
  "email": "john@example.com",
  "red_systems": 2,
  "orange_systems": 1,
  "yellow_systems": 2,
  "green_systems": 3,
  "assessment_score": 65
}
```

**Response**:
```json
{
  "status": "accepted",
  "message": "Assessment received and email sequence will begin shortly",
  "email": "john@example.com",
  "segment": "CRITICAL",
  "timestamp": "2025-11-12T10:30:00Z"
}
```

## Dynamic Email Templates

Templates are stored in Notion Templates DB and can be edited without code deployment.

### Template Variables

Use these placeholders in Subject or HTML Body:

- `{{first_name}}` - Contact's first name
- `{{business_name}}` - Contact's business name
- `{{email}}` - Contact's email address

### Template Schema

| Field | Type | Description |
|-------|------|-------------|
| Template Name | Title | Unique ID (e.g., "email_1") |
| Subject | Rich Text | Email subject line |
| HTML Body | Rich Text | Email HTML content |
| Active | Checkbox | Whether template is published |
| Last Modified | Timestamp | Automatic tracking |

### Editing Templates

1. Open Notion Templates Database
2. Find template to edit (e.g., "email_2a_critical")
3. Edit Subject or HTML Body
4. Changes take effect immediately
5. Deactivate by unchecking Active checkbox

## Migration from n8n

This system replaces the original n8n workflow with:

| n8n Component | Prefect Replacement |
|---------------|---------------------|
| 7 PostgreSQL nodes | `tasks/notion_operations.py` (4 functions) |
| 9 Resend nodes | `tasks/resend_operations.py` (3 functions) |
| 4 Wait nodes | `time.sleep()` with configurable durations |
| 2 Switch nodes | `tasks/routing.py` segment classification |
| 2 Webhook triggers | FastAPI `/webhook/signup` & `/webhook/assessment` |

**Benefits**:
- ✅ Version controlled (Git)
- ✅ Testable (93 unit tests)
- ✅ Dynamic templates (edit in Notion)
- ✅ Type-safe (Pydantic validation)
- ✅ Production-ready (deployment guides)

## Support

**Issues**: GitHub Issues

**Email**: sang@sanglescalinglabs.com

**Documentation**: See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment details

## License

Proprietary - Sang Le Scaling Labs

---

## Quick Commands Reference

```bash
# Install
pip install -r requirements.txt

# Seed templates
python scripts/seed_templates.py

# Test
python test_flows_dry_run.py
python test_integration_e2e.py --mode mock
pytest tests/ -v

# Run server
uvicorn server:app --reload

# Deploy
python flows/deploy.py
```

🎉 **Ready to deploy your automated email sequence!**
