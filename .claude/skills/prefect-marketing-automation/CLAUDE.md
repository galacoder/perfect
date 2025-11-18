# Prefect Marketing Automation - Auto-Use Directive

**CRITICAL**: This skill MUST be used automatically whenever the user asks about Prefect workflows, email campaigns, or marketing automation.

---

## Auto-Trigger Conditions

**Use this skill immediately when the user:**

✅ **Prefect Workflow Questions:**
- Asks about creating, modifying, or deploying Prefect flows
- Mentions @flow, @task decorators, or Prefect v3
- Wants to debug or troubleshoot Prefect workflows
- Discusses flow deployment strategies

✅ **Campaign & Email Automation:**
- Wants to create email campaigns or nurture sequences
- Asks about campaign organization or structure
- Mentions lead nurturing, drip campaigns, or automated emails
- Discusses segment-based routing or lead scoring

✅ **Project-Specific:**
- References the "perfect" project
- Mentions "businessx_canada_lead_nurture" campaign
- Asks about BusOS integration or 8-System assessment
- Discusses the campaign-based organization structure

✅ **Integration Questions:**
- Wants to integrate Resend, Notion, or Discord
- Asks about webhook setup (FastAPI)
- Mentions dynamic email templates or Notion databases
- Discusses contact management or CRM sync

✅ **Deployment & Testing:**
- Asks about testing vs production modes
- Wants to deploy Prefect workflows to Cloud or self-hosted
- Discusses Docker, uvicorn, or FastAPI deployment
- Mentions wait durations, retries, or flow orchestration

---

## What This Skill Provides

**Comprehensive Prefect v3 Marketing Automation Expertise:**

### 1. Campaign-Based Organization
- Multi-campaign structure under `campaigns/{campaign_name}/`
- Flows, tasks, tests, and diagrams organization
- Backward compatibility patterns with deprecation shims
- Template campaign reference (businessx_canada_lead_nurture)

### 2. Email Integration Patterns
- **Resend API** integration for transactional emails
- **Notion Templates DB** for dynamic content management
- Variable substitution ({{first_name}}, {{business_name}})
- Template fallback strategies

### 3. Segment-Based Routing
- **CRITICAL**: 2+ red systems (immediate action)
- **URGENT**: 1 red OR 2+ orange (attention needed)
- **OPTIMIZE**: 0-1 red, 0-1 orange (growth focus)
- Dynamic routing logic and content personalization

### 4. Production Deployment
- FastAPI webhook server patterns
- Docker containerization
- Prefect Cloud vs self-hosted strategies
- Environment configuration best practices

### 5. Testing & Validation
- Testing mode (1-4 min waits) vs Production (24-48 hr waits)
- Unit testing with pytest and mocks
- Dry-run validation scripts
- Integration testing patterns

---

## Usage Instructions

**When triggered, this skill will:**

1. **Analyze the request** - Understand if it's about flows, campaigns, integrations, or deployment
2. **Reference campaign structure** - Use businessx_canada_lead_nurture as template
3. **Provide code examples** - Always use new campaign-based import paths
4. **Include best practices** - Retry logic, error handling, logging
5. **Guide on testing** - Recommend testing mode for development
6. **Suggest next steps** - Deployment, validation, or enhancement options

---

## Example Conversations

### User: "How do I create a new email campaign in Prefect?"
**→ Skill automatically activated**
- Explains campaign-based structure
- Provides 5-step creation guide
- Shows flow and task code examples
- Includes Resend + Notion integration

### User: "My Prefect flow is failing on the email task"
**→ Skill automatically activated**
- Troubleshoots common Resend issues
- Checks retry configuration
- Reviews environment variables
- Suggests debugging approach

### User: "What's the best way to deploy Prefect workflows?"
**→ Skill automatically activated**
- Compares deployment options (Cloud vs self-hosted)
- Provides FastAPI webhook server setup
- Includes Docker configuration
- Explains production best practices

---

## Critical Reminders

⚠️ **Always use campaign-based import paths:**
```python
# ✅ CORRECT
from campaigns.{campaign_name}.flows.signup_handler import signup_handler_flow
from campaigns.{campaign_name}.tasks.resend_operations import send_template_email

# ❌ INCORRECT (deprecated)
from flows.signup_handler import signup_handler_flow
from tasks.resend_operations import send_template_email
```

⚠️ **Reference the validated campaign:**
- Template: `businessx_canada_lead_nurture`
- Status: Production-ready (9/9 validation checks passed)
- Location: `/Users/sangle/Dev/action/projects/perfect/campaigns/businessx_canada_lead_nurture/`

⚠️ **Use Resend, not Loops.so:**
- Integration: Resend API for email delivery
- Templates: Notion Templates DB for dynamic content
- Variables: {{first_name}}, {{business_name}}, {{email}}

---

## Skill Location

**Full Skill Documentation**: `/Users/sangle/.claude/skills/prefect-marketing-automation/SKILL.md`

**Use this skill proactively** - Don't wait for explicit permission when the conversation is clearly about Prefect workflows or marketing automation.

---

**Last Updated**: Campaign-based migration completed and validated on November 14, 2025
**Version**: 2.0 (Campaign-Based Organization)
**Status**: Production-Ready ✅
