# Task: Deploy FastAPI Webhook Server via Coolify

**Task ID**: 1128-deploy-fastapi-coolify
**Domain**: CODING (Infrastructure/Deployment)
**Started**: 2025-11-28
**Status**: AWAITING_APPROVAL

---

## State Files
- **feature_list.json** - Source of truth (JSON)
- **tests.json** - Verification test tracking (JSON)
- **PLAN.md** - Human-readable plan
- **DISCOVERY.md** - Exploration findings

---

## Phase Checklist
- [x] EXPLORE - Discovery complete
- [x] PLAN - Implementation plan created
- [ ] CODE - Implementation (via /execute)
- [ ] COMMIT - Validation and packaging

---

## Task Summary

Deploy the existing FastAPI webhook server to Coolify PaaS platform.

**Key Discovery**: Docker infrastructure is 95% complete:
- `Dockerfile.webhook` exists and is production-ready
- `Dockerfile.prefect` exists for Prefect worker
- `docker-compose.coolify.yml` exists with both services configured

**Remaining Work**:
1. Create `.dockerignore` (cleanup)
2. Deploy to Coolify (main task)
3. Configure DNS and SSL
4. Test and verify

---

## Quick Stats

| Metric | Value |
|--------|-------|
| Total Features | 15 |
| Total Waves | 4 |
| Estimated Hours | 3 |
| TDD Required | No (infrastructure task) |
| Skills Required | coolify-integration |

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `.dockerignore` | CREATE |
| `docker-compose.coolify.yml` | VERIFY |
| `campaigns/christmas_campaign/STATUS.md` | UPDATE |
| `campaigns/christmas_campaign/WEBSITE_INTEGRATION.md` | UPDATE |

---

## Existing Infrastructure

**Docker Files**:
- `Dockerfile.webhook` - FastAPI server
- `Dockerfile.prefect` - Prefect worker
- `docker-compose.coolify.yml` - Both services

**Prefect Deployments** (5 total):
- christmas-signup-handler
- christmas-send-email
- christmas-noshow-recovery-handler
- christmas-postcall-maybe-handler
- christmas-onboarding-handler

**Secret Blocks** (7 total):
- notion-token
- notion-email-templates-db-id
- notion-email-sequence-db-id
- notion-businessx-db-id
- notion-customer-projects-db-id
- notion-email-analytics-db-id
- resend-api-key

---

## Context

This task deploys the FastAPI webhook server (`server.py`) to Coolify to handle:
- `/webhook/christmas-signup` -> christmas_campaign signup_handler_flow
- `/webhook/calendly-noshow` -> christmas_campaign noshow_recovery_handler_flow
- `/webhook/postcall-maybe` -> christmas_campaign postcall_maybe_handler_flow
- `/webhook/onboarding-start` -> christmas_campaign onboarding_handler_flow
- `/webhook/calcom-booking` -> precall_prep_flow

**Why**: Prefect self-hosted does NOT support inbound webhooks (Cloud-only feature).
FastAPI is the officially-recommended pattern for self-hosted Prefect webhook handling.

---

## Progress Log

| Timestamp | Action |
|-----------|--------|
| 2025-11-28 22:00 | Task created, invoking Initializer Agent |
| 2025-11-28 22:30 | EXPLORE phase complete - Docker infrastructure discovered |
| 2025-11-28 22:30 | PLAN phase complete - 4 waves, 15 features |
| 2025-11-28 22:30 | Status: AWAITING_APPROVAL |

---

## Next Steps

1. Review DISCOVERY.md for exploration findings
2. Review PLAN.md for detailed implementation waves
3. If approved, run `/execute` to begin implementation
4. Use `coolify-integration` skill for Coolify API operations
