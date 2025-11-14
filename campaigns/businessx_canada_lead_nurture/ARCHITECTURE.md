# BusinessX Canada Lead Nurture - Architecture

## System Overview

This campaign implements a webhook-driven email nurture sequence with intelligent segment classification.

## Flow Architecture

### 1. Entry Points (FastAPI Webhooks)

**POST /webhook/signup**
- Triggered by: Website form submission
- Payload: `{email, name, first_name, business_name}`
- Handler: `signup_handler_flow`
- Action: Create or update contact in Notion

**POST /webhook/assessment**
- Triggered by: Assessment completion
- Payload: `{email, red_systems, orange_systems, yellow_systems, green_systems, assessment_score}`
- Handler: `assessment_handler_flow`
- Action: Classify segment, update Notion, trigger email sequence

### 2. Flow Relationships

```
Website Form
    │
    ├──► Signup Flow ──► Notion (Contact Created)
    │
    └──► Assessment Flow ──┬──► Notion (Segment Updated)
                           │
                           ├──► Discord (if CRITICAL)
                           │
                           └──► Email Sequence Flow ──► Resend API
```

### 3. Data Flow

**Signup Flow**:
1. Receive form data (email, name, business_name)
2. Search Notion for existing contact by email
3. If found: Update contact properties
4. If not found: Create new contact
5. Return contact page_id

**Assessment Flow**:
1. Receive assessment data (email, system counts)
2. Find contact in Notion (error if not found)
3. Classify segment based on red/orange system counts:
   - `red_systems >= 2` → CRITICAL
   - `red_systems == 1 OR orange_systems >= 2` → URGENT
   - Otherwise → OPTIMIZE
4. Update contact in Notion with assessment data and segment
5. If segment == CRITICAL: Send Discord notification
6. Trigger email sequence flow with (email, segment, contact_id)

**Email Sequence Flow**:
1. Fetch email templates from Notion (or use static fallbacks)
2. Send Email 1 (universal)
3. Wait 24 hours (or 1 min in test mode)
4. Send Email 2 (segment-specific: 2A/2B/2C)
5. Wait 48 hours (or 2 min in test mode)
6. Send Email 3 (universal)
7. Wait 48 hours (or 3 min in test mode)
8. Send Email 4 (universal)
9. Wait 48 hours (or 4 min in test mode)
10. Send Email 5 (segment-specific: 5A/5B/5C)
11. Mark sequence as completed in Notion

### 4. Task Organization

**Notion Operations** (`notion_operations.py`):
- `search_contact_by_email(email)` - Query contacts database
- `create_contact(properties)` - Create new contact page
- `update_contact(page_id, properties)` - Update existing contact
- `fetch_template(template_name)` - Get email template from Notion

**Resend Operations** (`resend_operations.py`):
- `send_email(to, subject, html)` - Send email via Resend API

**Routing** (`routing.py`):
- `classify_segment(red, orange, yellow, green)` - Determine segment classification

**Template Operations** (`template_operations.py`):
- `render_template(template, contact_data)` - Replace placeholders with contact info

### 5. Error Handling

**Retry Strategy**:
- Notion API calls: 3 retries with 60-second delay
- Resend API calls: 3 retries with 30-second delay
- Discord webhook: 2 retries with 30-second delay

**Failure Modes**:
- **Contact not found** (Assessment): Return 404 error
- **Template fetch failure**: Fallback to static template in `config/`
- **Email send failure**: Retry 3×, then log for manual follow-up
- **Discord failure**: Log but don't block email sequence
- **Notion update failure**: Log but don't block sequence

### 6. Testing Modes

**Production Mode** (`TESTING_MODE=false` or unset):
- Email wait times: 24h → 48h → 48h → 48h (7 days total)
- Full retry delays
- Production logging

**Testing Mode** (`TESTING_MODE=true`):
- Email wait times: 1min → 2min → 3min → 4min (~10 minutes total)
- Same retry strategy (for reliability testing)
- Verbose logging

### 7. Deployment Architecture

**Prefect Cloud Deployment**:
- Flows deployed as separate Prefect deployments
- Webhook server runs on separate process (FastAPI)
- Flows triggered via `deployment.run()` from webhook handlers
- Environment variables injected via Prefect Cloud secrets

**Local Development**:
- Run `python server.py` for webhook server
- Flows execute locally when triggered
- Use `.env` file for environment variables

### 8. Security Considerations

**Webhook Security**:
- No authentication currently (assumes internal network or proxy auth)
- TODO: Add webhook signature verification

**Data Protection**:
- Email addresses stored in Notion (encrypted at rest)
- API keys stored as environment variables
- No PII logged to stdout

**Rate Limiting**:
- Notion API: Built-in retry with exponential backoff
- Resend API: Respects rate limits
- No custom rate limiting on webhooks (FastAPI default)

### 9. Monitoring

**Success Metrics**:
- Contact creation rate (signup flow)
- Assessment completion rate
- Email delivery success rate
- Segment distribution (CRITICAL/URGENT/OPTIMIZE)

**Logs to Monitor**:
- Notion API errors (rate limits, database not found)
- Resend API errors (bounces, invalid emails)
- Discord webhook failures (hot leads missed)
- Template fallback usage (Notion template fetch failures)

**Alerting**:
- Discord notifications for CRITICAL segment leads
- TODO: Add Sentry for exception tracking
- TODO: Add Datadog/Grafana for metrics

### 10. Future Enhancements

**Planned**:
- [ ] A/B testing for email subject lines
- [ ] Dynamic wait times based on engagement
- [ ] Lead scoring based on email opens/clicks
- [ ] SMS notifications for CRITICAL segment
- [ ] Calendar booking integration

**Under Consideration**:
- [ ] Multi-language support
- [ ] Email preference center
- [ ] Unsubscribe handling
- [ ] GDPR compliance enhancements
