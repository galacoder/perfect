# Christmas Campaign - Kestra Webhook Endpoints

**Last Updated**: 2025-11-30
**Status**: Production Ready (No FastAPI proxy needed)
**Decision**: Direct Kestra webhooks (simpler architecture)

---

## Architecture Decision: No FastAPI Proxy

**Why no FastAPI proxy?**

1. **Simpler**: Fewer moving parts, less to maintain
2. **Faster**: Direct webhook calls, no proxy overhead
3. **More reliable**: One less service to fail
4. **Kestra native**: Use Kestra's built-in webhook system

**Original FastAPI server (`server.py`)**: Used for Prefect, but not needed for Kestra.

---

## Kestra Webhook URLs

### Local Development

```bash
# Base URL
KESTRA_BASE_URL=http://localhost:8080

# Webhook endpoints
POST http://localhost:8080/api/v1/executions/webhook/christmas/handlers/signup-handler/signup-webhook-key
POST http://localhost:8080/api/v1/executions/webhook/christmas/handlers/assessment-handler/assessment-webhook-key
POST http://localhost:8080/api/v1/executions/webhook/christmas/handlers/noshow-recovery-handler/noshow-webhook-key
POST http://localhost:8080/api/v1/executions/webhook/christmas/handlers/postcall-maybe-handler/postcall-webhook-key
POST http://localhost:8080/api/v1/executions/webhook/christmas/handlers/onboarding-handler/onboarding-webhook-key
```

### Production (Homelab - Traefik Domain)

**Traefik Domain**: `kestra.galatek.dev` (configured via Dokploy deployment)

```bash
# Base URL (production)
KESTRA_BASE_URL=https://kestra.galatek.dev

# Webhook endpoints (christmas namespace)
POST https://kestra.galatek.dev/api/v1/executions/webhook/christmas/signup-handler/christmas-signup-webhook
POST https://kestra.galatek.dev/api/v1/executions/webhook/christmas/assessment-handler/christmas-assessment-webhook
POST https://kestra.galatek.dev/api/v1/executions/webhook/christmas/noshow-recovery-handler/calendly-noshow-webhook
POST https://kestra.galatek.dev/api/v1/executions/webhook/christmas/postcall-maybe-handler/postcall-maybe-webhook
POST https://kestra.galatek.dev/api/v1/executions/webhook/christmas/onboarding-handler/onboarding-start-webhook
```

**Note**: All flows use `namespace: christmas` (not `christmas.campaign`) to match webhook URLs.

---

## Webhook Endpoint Reference

### 1. Signup Handler (Tracking Only)

**URL**: `/api/v1/executions/webhook/christmas/handlers/signup-handler/signup-webhook-key`

**Purpose**: Track signup, create Notion contact (NO EMAILS SENT)

**Payload**:
```json
{
  "email": "customer@example.com",
  "first_name": "Sarah",
  "business_name": "Sarah's Salon"
}
```

**Response**:
```json
{
  "id": "execution_id_here",
  "state": "CREATED"
}
```

**Website Must Do**: Send signup confirmation email directly

---

### 2. Assessment Handler (Emails #2-5 Only)

**URL**: `/api/v1/executions/webhook/christmas/handlers/assessment-handler/assessment-webhook-key`

**Purpose**: Schedule follow-up emails #2-5 after website sends Email #1

**Payload**:
```json
{
  "email": "customer@example.com",
  "first_name": "Sarah",
  "business_name": "Sarah's Salon",
  "red_systems": 2,
  "orange_systems": 1,
  "yellow_systems": 2,
  "green_systems": 3,
  "weakest_system_1": "GPS",
  "weakest_system_2": "Money",
  "revenue_leak_total": 14700,
  "email_1_sent_at": "2025-12-01T10:30:00Z",
  "email_1_status": "sent"
}
```

**CRITICAL Fields**:
- `email_1_sent_at` - ISO 8601 timestamp when website sent Email #1
- `email_1_status` - Must be "sent"

**Website Must Do**: Send Email #1 BEFORE calling this webhook

---

### 3. No-Show Recovery Handler

**URL**: `/api/v1/executions/webhook/christmas/handlers/noshow-recovery-handler/noshow-webhook-key`

**Purpose**: Send 3-email recovery sequence after missed call

**Payload**:
```json
{
  "email": "customer@example.com",
  "first_name": "Sarah",
  "calendly_event_id": "evt_123abc",
  "scheduled_time": "2025-12-10T14:00:00Z"
}
```

**Kestra Sends**: All 3 emails (5min, 24h, 48h)

---

### 4. Post-Call Maybe Handler

**URL**: `/api/v1/executions/webhook/christmas/handlers/postcall-maybe-handler/postcall-webhook-key`

**Purpose**: Send 3-email nurture sequence after "maybe" call

**Payload**:
```json
{
  "email": "customer@example.com",
  "first_name": "Sarah",
  "business_name": "Sarah's Salon",
  "call_date": "2025-12-08T15:00:00Z",
  "interest_level": "medium"
}
```

**Kestra Sends**: All 3 emails (1h, 3d, 7d)

---

### 5. Onboarding Handler

**URL**: `/api/v1/executions/webhook/christmas/handlers/onboarding-handler/onboarding-webhook-key`

**Purpose**: Send 3-email onboarding sequence after payment

**Payload**:
```json
{
  "email": "customer@example.com",
  "first_name": "Sarah",
  "business_name": "Sarah's Salon",
  "payment_status": "paid",
  "payment_date": "2025-12-09T16:30:00Z",
  "package_type": "foundation"
}
```

**Kestra Sends**: All 3 emails (1h, 1d, 3d)

---

## Webhook Security

### Authentication

**Current**: No authentication on webhooks (trusted internal network)

**For Production**: Consider adding webhook keys or IP whitelist:

**Option 1: Unique Webhook Keys** (Already implemented)
- Each flow has unique webhook key in URL
- Keep keys secret (don't commit to public repos)

**Option 2: IP Whitelist** (Nginx reverse proxy)
```nginx
# /etc/nginx/sites-available/kestra.conf

location /api/v1/executions/webhook/ {
    # Only allow from website server
    allow 10.0.0.5;  # Website server IP
    deny all;

    proxy_pass http://localhost:8080;
}
```

**Option 3: API Key Header** (Future implementation)
```yaml
# In Kestra flow
triggers:
  - id: webhook
    type: io.kestra.plugin.core.trigger.Webhook
    key: "secret-webhook-key"
    headers:
      X-API-Key: "{{ secret('SECRET_WEBHOOK_API_KEY') }}"
```

---

## Testing Webhooks

### Local Testing (curl)

```bash
# Test signup handler
curl -X POST http://localhost:8080/api/v1/executions/webhook/christmas/handlers/signup-handler/signup-webhook-key \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lengobaosang@gmail.com",
    "first_name": "Test",
    "business_name": "Test Corp"
  }'

# Test assessment handler (with email_1_sent_at)
EMAIL_1_SENT_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

curl -X POST http://localhost:8080/api/v1/executions/webhook/christmas/handlers/assessment-handler/assessment-webhook-key \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"lengobaosang@gmail.com\",
    \"first_name\": \"Test\",
    \"business_name\": \"Test Corp\",
    \"red_systems\": 2,
    \"orange_systems\": 1,
    \"yellow_systems\": 2,
    \"green_systems\": 3,
    \"weakest_system_1\": \"GPS\",
    \"revenue_leak_total\": 14700,
    \"email_1_sent_at\": \"$EMAIL_1_SENT_AT\",
    \"email_1_status\": \"sent\"
  }"
```

### JavaScript Testing (Website)

```javascript
async function testKestreaWebhook() {
  const response = await fetch(
    'http://localhost:8080/api/v1/executions/webhook/christmas/handlers/signup-handler/signup-webhook-key',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'lengobaosang@gmail.com',
        first_name: 'Test',
        business_name: 'Test Corp'
      })
    }
  );

  const result = await response.json();
  console.log('Webhook triggered:', result.id);
}
```

---

## Environment Variables for Website

Add these to your Next.js website:

```bash
# .env (local development)
KESTRA_BASE_URL=http://localhost:8080
KESTRA_WEBHOOK_SIGNUP=http://localhost:8080/api/v1/executions/webhook/christmas/handlers/signup-handler/signup-webhook-key
KESTRA_WEBHOOK_ASSESSMENT=http://localhost:8080/api/v1/executions/webhook/christmas/handlers/assessment-handler/assessment-webhook-key
KESTRA_WEBHOOK_NOSHOW=http://localhost:8080/api/v1/executions/webhook/christmas/handlers/noshow-recovery-handler/noshow-webhook-key
KESTRA_WEBHOOK_POSTCALL=http://localhost:8080/api/v1/executions/webhook/christmas/handlers/postcall-maybe-handler/postcall-webhook-key
KESTRA_WEBHOOK_ONBOARDING=http://localhost:8080/api/v1/executions/webhook/christmas/handlers/onboarding-handler/onboarding-webhook-key
```

```bash
# .env.production (Vercel)
KESTRA_BASE_URL=https://kestra.homelab.local
KESTRA_WEBHOOK_SIGNUP=https://kestra.homelab.local/api/v1/executions/webhook/christmas/handlers/signup-handler/signup-webhook-key
KESTRA_WEBHOOK_ASSESSMENT=https://kestra.homelab.local/api/v1/executions/webhook/christmas/handlers/assessment-handler/assessment-webhook-key
# ... (same pattern for other webhooks)
```

---

## Monitoring Webhook Executions

### Kestra UI

**URL**: http://localhost:8080 (local) or https://kestra.homelab.local (production)

**Navigate to**: Executions tab

**Filter by**: Flow name (e.g., `christmas-assessment-handler`)

### Kestra API

```bash
# List recent executions
curl http://localhost:8080/api/v1/executions | jq '.results[] | {id, flowId, state}'

# Get execution details
curl http://localhost:8080/api/v1/executions/{execution-id}

# Get execution logs
curl http://localhost:8080/api/v1/executions/{execution-id}/logs | jq '.[]'
```

---

## Troubleshooting

### Issue 1: 404 Not Found

**Cause**: Flow not deployed or wrong webhook URL

**Fix**:
```bash
# List all flows
curl http://localhost:8080/api/v1/flows | jq '.[] | {id, namespace}'

# Verify flow exists
curl http://localhost:8080/api/v1/flows/christmas.handlers/signup-handler
```

### Issue 2: Webhook succeeds but flow doesn't run

**Cause**: Trigger condition not met or flow errors

**Fix**:
```bash
# Check execution logs
curl http://localhost:8080/api/v1/executions?flowId=christmas.handlers.signup-handler | jq '.results[0].id'

# View logs
curl http://localhost:8080/api/v1/executions/{execution-id}/logs
```

### Issue 3: CORS errors from website

**Cause**: Browser blocking cross-origin requests

**Fix**: Add CORS headers in Nginx reverse proxy:
```nginx
location /api/v1/executions/webhook/ {
    # Add CORS headers
    add_header Access-Control-Allow-Origin "https://sangletech.com" always;
    add_header Access-Control-Allow-Methods "POST, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Content-Type" always;

    if ($request_method = OPTIONS) {
        return 204;
    }

    proxy_pass http://localhost:8080;
}
```

---

## Migration from Prefect FastAPI

**Old Prefect Architecture**:
```
Website → FastAPI (server.py) → Prefect API → Prefect Worker
```

**New Kestra Architecture**:
```
Website → Kestra Webhook (direct) → Kestra Executor
```

**Benefits**:
- ✅ Fewer components (no FastAPI server needed)
- ✅ Faster response (direct webhook, no proxy)
- ✅ Simpler deployment (only Docker Compose, no uvicorn/gunicorn)
- ✅ Built-in webhook auth (via unique keys)

**Migration Checklist**:
- [ ] Update website webhook URLs (Prefect → Kestra)
- [ ] Remove FastAPI server deployment (no longer needed)
- [ ] Test all webhook endpoints
- [ ] Verify Kestra executions triggered
- [ ] Check email delivery
- [ ] Monitor for errors

---

## FAQ

### Q: Why not use FastAPI proxy?

**A**: Simpler architecture. Kestra's native webhooks are reliable and feature-complete. No need for extra proxy layer.

### Q: Can I still use server.py for other purposes?

**A**: Yes! Keep it for non-Kestra tasks (health checks, other integrations). But for Christmas Campaign, use Kestra webhooks directly.

### Q: How do I secure webhooks?

**A**:
1. Use unique webhook keys (already implemented)
2. Keep keys secret (don't commit to public repos)
3. Optional: IP whitelist in reverse proxy
4. Optional: VPN for internal network only

### Q: What if Kestra is down?

**A**: Website should handle webhook failures gracefully (log error, don't block user). Retry logic can be added in website code.

---

## Summary

**TLDR**: Website calls Kestra webhooks directly. No FastAPI proxy needed.

**Key Points**:
1. Simpler architecture (fewer components)
2. Faster (no proxy overhead)
3. More reliable (one less service to fail)
4. Use unique webhook keys for security
5. Monitor in Kestra UI

**Documentation**:
- Full integration guide: `WEBSITE_INTEGRATION_KESTRA.md`
- Deployment guide: `DEPLOYMENT_KESTRA.md`
- Architecture: `ARCHITECTURE.md`

---

**Last Updated**: 2025-11-30
**Contact**: sang@sanglescalinglabs.com
**Kestra UI**: http://localhost:8080 (local) or https://kestra.homelab.local (production)
