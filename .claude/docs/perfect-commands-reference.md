## Common Tasks

### Run Webhook Server

```bash
# Development (auto-reload)
uvicorn server:app --reload

# Production
uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Test Webhooks

```bash
# Health check
curl http://localhost:8000/health

# Signup
curl -X POST http://localhost:8000/webhook/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User","business_name":"Test Corp"}'

# Assessment
curl -X POST http://localhost:8000/webhook/assessment \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","red_systems":2,"orange_systems":1}'
```

### Seed Email Templates

```bash
python scripts/seed_templates.py
```

This creates 8 email templates in Notion:
- `email_1` (universal)
- `email_2a_critical`, `email_2b_urgent`, `email_2c_optimize`
- `email_3` (universal)
- `email_4` (universal)
- `email_5a_critical`, `email_5b_urgent`, `email_5c_optimize`

### Run Full Test Suite

```bash
# All validation steps
python test_flows_dry_run.py && \
python test_integration_e2e.py --mode mock && \
pytest campaigns/businessx_canada_lead_nurture/tests/ -v
```
