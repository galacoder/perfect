# Task: Port Prefect Christmas Automation to Kestra

**Task ID**: 1129-port-prefect-to-kestra
**Domain**: CODING
**Started**: 2025-11-29
**Status**: AWAITING_APPROVAL

---

## State Files

| File | Purpose | Format |
|------|---------|--------|
| **feature_list.json** | Source of truth - features, waves, progress | JSON |
| **tests.json** | Test tracking - suites, cases, results | JSON |
| **PLAN.md** | Human-readable implementation plan | Markdown |
| **DISCOVERY.md** | Exploration findings and analysis | Markdown |
| **CHECKPOINT_SUMMARY.md** | Approval checkpoint summary | Markdown |

---

## Phase Checklist

- [x] EXPLORE - Discovery complete
- [x] PLAN - Implementation plan created
- [ ] CODE - Implementation (via /execute-coding)
- [ ] COMMIT - Validation and packaging

---

## CRITICAL ARCHITECTURAL DECISION

### Website/Kestra Email Responsibility Split (2025-11-29)

**Decision**: Website sends signup email + Email #1 of 5-day sequence. Kestra handles Emails #2-5 and ALL emails for secondary sequences.

**Email Responsibility Matrix**:

| Sequence | Emails | Sent By |
|----------|--------|---------|
| Signup confirmation | 1 email | Website |
| 5-Day Nurture | Email #1 | Website |
| 5-Day Nurture | Emails #2-5 | Kestra |
| No-Show Recovery | All 3 emails | Kestra |
| Post-Call Maybe | All 3 emails | Kestra |
| Onboarding | All 3 emails | Kestra |

**Webhook Payload Requirement**:
```json
{
  "email": "user@example.com",
  "red_systems": 2,
  "orange_systems": 1,
  "email_1_sent_at": "2025-11-29T10:30:00Z",
  "email_1_status": "sent"
}
```

**Why This Matters**:
- Prevents duplicate emails (website + Kestra both sending Email #1)
- Ensures proper sequencing (Email #2 timing based on Email #1 send time)
- Simplifies Kestra flows (less email sending logic)
- Signup handler becomes tracking-only (no email responsibility)

---

## Progress Summary

| Wave | Name | Features | Status |
|------|------|----------|--------|
| 1 | Foundation | 4 | COMPLETE |
| 2 | Core Flow Migration | 8 | COMPLETE |
| 3 | Handler Flows Migration | 6 | COMPLETE |
| 4 | Website Integration & Deployment | 14 | In Progress |
| **Total** | | **32** | **81.25% complete** |

### Wave 4 Feature Status
| Feature | Status | Notes |
|---------|--------|-------|
| 4.1-4.6 | Complete | Documentation and infrastructure |
| 4.7-4.10 | blocked_external_dependency | Requires frontend webhook integration |
| 4.11 | Complete | 13/15 tests passing (2 fail due to 4.14 bug) |
| 4.12 | Complete | 10/10 tests passing |
| 4.13 | Pending | Traefik domain configuration |
| 4.14 | Pending | Bug fix: Notion property name |

---

## Task Description

Port the current Prefect Christmas automation (flows + webhook server) to Kestra self-hosted automation tool:

1. **Local Deployment**: Deploy Kestra via Docker Compose on local machine
2. **Flow Migration**: Port all Christmas campaign flows from Prefect to Kestra
3. **Webhook Server**: Migrate FastAPI webhook server to work with Kestra
4. **Testing**: Verify end-to-end functionality locally
5. **Production Deployment**: Deploy to homelab production server
6. **Website Integration**: Update sangletech-tailwindcss website for new webhooks

---

## Scope

**Prefect Components to Port**:
- 5 Christmas campaign flows (signup, assessment, noshow, postcall, onboarding, send_email)
- FastAPI webhook server (server.py)
- Notion integration tasks (12+ functions)
- Resend email tasks (4 functions)
- Routing/classification logic
- Secret management (8 Prefect blocks -> Kestra secrets)

**New Kestra Setup**:
- Docker Compose deployment (dev + production)
- 6 Flow definitions (YAML-based) - signup (tracking only), assessment (Emails #2-5), noshow, postcall, onboarding, send_email
- Webhook triggers for 5 handlers
- Base64-encoded secret management
- Email scheduling via subflows with scheduleDate

**Notion Template Integration**:
- Fetch email templates dynamically from Notion Templates database
- Support all sequences: 5-day nurture, no-show recovery, post-call maybe, onboarding
- Fallback to static templates if Notion fetch fails
- Personalization variable substitution (first_name, business_name, segment)

**Puppeteer E2E Sales Funnel Testing**:
- End-to-end browser automation using Puppeteer MCP
- Test complete user journey: website form -> webhook -> Kestra -> email scheduling
- Test all funnels (christmas-signup tracking, christmas-assessment, calendly-noshow, postcall-maybe, onboarding-start)
- Verify Notion sequence tracker updates
- Validate TESTING_MODE vs production delays
- Use mandatory test email: lengobaosang@gmail.com

**Website Updates**:
- Update webhook URLs in sangletech-tailwindcss funnel
- Test integration with new Kestra endpoints
- Document webhook payload requirements including email_1_sent_at

---

## Key Decisions Made

### 1. Webhook Architecture
**Decision**: Use Kestra native webhooks
**Rationale**: Simplifies architecture, removes FastAPI dependency for webhooks

### 2. Email Scheduling
**Decision**: Use Subflow with scheduleDate property, calculate from email_1_sent_at
**Rationale**: More robust than Pause task, matches Prefect behavior, ensures proper sequencing

### 3. Python Code
**Decision**: Use HTTP tasks for APIs, inline Python for business logic
**Rationale**: Cleaner separation, easier testing

### 4. Secret Management
**Decision**: Base64-encoded environment variables with SECRET_ prefix
**Rationale**: Kestra standard for open-source version

### 5. Email Responsibility Split (NEW 2025-11-29)
**Decision**: Website sends signup email + Email #1, Kestra sends Emails #2-5 and secondary sequences
**Rationale**: Prevents duplicate emails, ensures proper sequencing based on Email #1 timestamp

---

## Risk Register

| Risk | Severity | Status | Mitigation |
|------|----------|--------|------------|
| Kestra secret + webhook CPU issue | High | Open | Test thoroughly, use ENV vars if needed |
| Website integration URL changes | High | Open | Coordinate with frontend team |
| Email scheduling differences | Medium | Mitigated | Use email_1_sent_at for timing |
| No direct Python imports | Medium | Mitigated | HTTP tasks + inline scripts |
| Duplicate Email #1 | High | Mitigated | Webhook payload validation |
| Missing email_1_sent_at | Medium | Mitigated | Default to webhook time with warning |

---

## Progress Log

| Timestamp | Action |
|-----------|--------|
| 2025-11-29 10:00 | Task initialized via /start-coding |
| 2025-11-29 10:15 | EXPLORE phase complete - analyzed 5 flows, 3 task modules |
| 2025-11-29 10:30 | Kestra research complete - webhooks, secrets, subflows |
| 2025-11-29 10:45 | PLAN phase complete - 4 waves, 20 features |
| 2025-11-29 10:45 | Status changed to AWAITING_APPROVAL |
| 2025-11-29 11:00 | Added 3 features: Notion templates (2.6), Puppeteer E2E signup (4.7), secondary funnels (4.8) |
| 2025-11-29 12:00 | **CRITICAL ARCHITECTURAL CHANGE**: Website/Kestra email split. Modified 6 features, added 3 new. Total: 26 features, 34 hours. |
| 2025-11-29 14:00 | **CRITICAL REQUIREMENT**: Notion Database Updates Per Email. Modified 6 features (2.2, 2.4, 3.2, 3.3, 3.4, 3.5), added 1 new (2.8). Total: 27 features, 36 hours. |

---

## Changes Summary (2025-11-29 12:00)

### Features Modified
| Feature | Change |
|---------|--------|
| **2.5** | Email scheduling calculates delays from email_1_sent_at, skips Email #1 |
| **3.1** | Signup handler now TRACKING ONLY (no email sending) |
| **3.6** | Analytics task includes sent_by field (website vs Kestra) |
| **4.4** | Renamed to assessment E2E, mocks website Email #1 |
| **4.6** | Elevated to HIGH priority, includes responsibility matrix |
| **4.7** | Updated to test website/Kestra email split |

### Features Added
| Feature | Description | Wave |
|---------|-------------|------|
| **2.7** | Webhook payload validator with email_1_sent_at support | 2 |
| **3.5** | Assessment handler for 5-day sequence (Emails #2-5 only) | 3 |
| **4.8** | Puppeteer E2E for signup (tracking only verification) | 4 |
| **4.9** | Puppeteer E2E for secondary funnels (renumbered from old 4.8) | 4 |

### Impact
- **Previous Features**: 23
- **New Features**: 26 (+3)
- **Previous Estimate**: 30 hours
- **New Estimate**: 34 hours (+4)

---

## Changes Summary (2025-11-29 14:00)

### CRITICAL REQUIREMENT: Notion Database Updates Per Email

For EVERY email sent by Kestra, the system MUST update Notion databases to track delivery status.

### Features Modified
| Feature | Change |
|---------|--------|
| **2.2** | Added `update_sequence_tracker_per_email` function to Notion HTTP tasks |
| **2.4** | send_email_flow now includes Notion Sequence Tracker update after each send |
| **3.2** | noshow_recovery_handler updated with per-email Notion tracking (3 emails) |
| **3.3** | postcall_maybe_handler updated with per-email Notion tracking (3 emails) |
| **3.4** | onboarding_handler updated with per-email Notion tracking (3 emails) |
| **3.5** | assessment_handler updated with per-email Notion tracking (Emails #2-5) |

### Features Added
| Feature | Description | Wave |
|---------|-------------|------|
| **2.8** | Dedicated Notion Sequence Tracker update task | 2 |

### Error Handling Strategy
- Email delivery is PRIMARY - MUST succeed
- Notion tracking is SECONDARY - log failures but don't block
- Notion update failures return success to not interrupt email flow

### Databases Updated
1. **Notion Sequence Tracker** - email_number, sent_at, status, resend_id, sent_by
2. **Notion Contact Database** - last_email_sent timestamp

### Impact
- **Previous Features**: 26
- **New Features**: 27 (+1)
- **Previous Estimate**: 34 hours
- **New Estimate**: 36 hours (+2)

---

## Changes Summary (2025-11-30 20:00)

### E2E Testing Enhancement via /add-tasks-coding

Comprehensive E2E tests added for Kestra sales funnel flows using Puppeteer MCP.

### Features Added
| Feature | Description | Wave | Priority |
|---------|-------------|------|----------|
| **4.10** | Puppeteer E2E: Complete Sales Funnel Integration (Signup -> Assessment -> Email Sequence) | 4 | HIGH |
| **4.11** | E2E Test: Webhook-to-Kestra Flow Integration Verification | 4 | HIGH |
| **4.12** | E2E Test: Notion Email Sequence Tracker Verification | 4 | MEDIUM |

### Key Test Coverage Added
- **Complete User Journey**: Website signup -> assessment -> webhook -> Kestra -> email sequence -> Notion tracking
- **Webhook Integration**: All 5 webhook endpoints tested programmatically
- **Notion Tracking**: Sequence Tracker database updates verified at each step
- **Puppeteer MCP Integration**: Browser automation for form filling, screenshots, network inspection

### Mandatory Test Email
All E2E tests MUST use: `lengobaosang@gmail.com` (per CLAUDE.md requirements)

### Impact
- **Previous Features**: 27
- **New Features**: 30 (+3)
- **Previous Estimate**: 36 hours
- **New Estimate**: 42 hours (+6)
- **Test Cases Added**: 54

---

## Changes Summary (2025-11-30 23:30)

### Bug Fix and External Dependency Documentation via /add-tasks-coding

Identified and documented critical blockers for Puppeteer E2E tests.

### Feature Added
| Feature | Description | Wave | Priority |
|---------|-------------|------|----------|
| **4.14** | Fix signup-handler Notion property name: 'email' to 'Email' | 4 | HIGH |

### Features Modified (Marked as blocked_external_dependency)
| Feature | Change |
|---------|--------|
| **4.7** | Blocked - requires frontend (sangletech-tailwindcss) webhook integration |
| **4.8** | Blocked - requires frontend (sangletech-tailwindcss) webhook integration |
| **4.9** | Blocked - depends on 4.7 |
| **4.10** | Blocked - depends on 4.7 and 4.8 |

### External Dependency Documentation

**Blocker Type**: Frontend webhook integration missing

**Repository**: sangletech-tailwindcss

**Required Work**: Frontend must POST assessment/signup data to Kestra webhooks after form submission

**Root Cause**:
- Assessment completion is PURELY FRONTEND - calculates scores in JavaScript but sends NO data to backend
- No webhook calls detected during form submissions
- Kestra flows are ready but never get triggered

**Workaround**: Direct API webhook testing (Feature 4.11) works - bypass browser automation

**Bug Fix (Feature 4.14)**:
- signup-handler.yml uses lowercase 'email' but Notion expects 'Email' (capitalized)
- Causes 2 test failures in Feature 4.11 (currently 13/15 passing)
- After fix, Feature 4.11 should show 15/15 passing

### Impact
- **Previous Features**: 31
- **New Features**: 32 (+1)
- **Completed Features**: 26
- **Blocked Features**: 4 (4.7-4.10 require frontend work)
- **Pending Features**: 2 (4.13 Traefik domain, 4.14 bug fix)
- **Completion**: 81.25% (26/32 features)

---

## Commands Reference

```bash
# Continue with execution
/execute-coding

# Add new tasks mid-execution
/add-tasks-coding

# Verify completion
/verify-coding

# Resume interrupted work
/continue-coding
```

---

## Files Created

```
.claude/tasks/active/1129-port-prefect-to-kestra/
  feature_list.json    <- SOURCE OF TRUTH
  tests.json           <- Test tracking
  TASK_CONTEXT.md      <- This file
  DISCOVERY.md         <- Exploration findings
  PLAN.md              <- Human-readable plan
  CHECKPOINT_SUMMARY.md <- Approval summary
```
