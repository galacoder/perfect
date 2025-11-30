# Task: Deploy Kestra with Dokploy + E2E Tests

**Task ID**: 1130-deploy-kestra-dokploy-e2e-tests
**Domain**: CODING
**Started**: 2025-11-30T10:00:00Z
**Status**: AWAITING_APPROVAL

## State Files
- **feature_list.json** - Source of truth (JSON)
- **tests.json** - Test tracking (JSON)
- **PLAN.md** - Human-readable plan
- **DISCOVERY.md** - Exploration findings

## Phase Checklist
- [x] EXPLORE - Discovery complete
- [x] PLAN - Implementation plan created
- [ ] CODE - Implementation (via /execute-coding)
- [ ] COMMIT - Validation and packaging

## Task Summary

### Part 1: Repository Extraction (NEW)
Extract Kestra to standalone repository:
- Create /Users/sangle/Dev/action/projects/kestra-automation/
- Preserve git commit history from task 1129
- Extract all flows, tests, docker-compose files
- Update documentation for standalone structure

### Part 2: Dokploy Deployment
Deploy Kestra to kestra.galatek.dev using Dokploy with:
- PostgreSQL database
- SSL/HTTPS via Let's Encrypt
- All secrets configured
- Health monitoring
- 13 flows deployed

### Part 3: E2E Tests (5 Features from Task 1129)
Complete pending E2E test features:
- **4.4**: Assessment handler E2E (Emails #2-5)
- **4.5**: All handler flows E2E
- **4.7**: Puppeteer - Assessment funnel
- **4.8**: Puppeteer - Signup handler (tracking only)
- **4.9**: Puppeteer - Secondary funnels

## Key Decisions

### Email Responsibility Split
| Component | Sends |
|-----------|-------|
| Website | Signup email, Email #1 of 5-day sequence |
| Kestra | Emails #2-5 of 5-day, ALL secondary sequences |

### Browser Automation
- **Primary**: Puppeteer MCP (mcp__puppeteer__*)
- **Alternative**: playwright-skill

### Test Email
- **MANDATORY**: lengobaosang@gmail.com

## Waves Overview

| Wave | Name | Features | Status |
|------|------|----------|--------|
| 0 | Repository Extraction | 6 | Pending |
| 1 | Dokploy Deployment | 5 | Pending |
| 2 | E2E Test Infrastructure | 4 | Pending |
| 3 | Handler Flow E2E Tests | 3 | Pending |
| 4 | Puppeteer Sales Funnel Tests | 5 | Pending |

**Total**: 23 features across 5 waves

## Progress Log
- 2025-11-30T10:00:00Z - Task initialized via /start-coding
- 2025-11-30T10:15:00Z - EXPLORE phase complete
- 2025-11-30T10:30:00Z - PLAN phase complete
- 2025-11-30T10:30:00Z - Awaiting user approval

## Related Tasks
- **Task 1129**: Port Prefect to Kestra (81.48% complete)
  - This task completes remaining 5 E2E features

## Files to Create

### Deployment
- docker-compose.kestra.dokploy.yml

### Tests
- tests/kestra/e2e/conftest.py
- tests/kestra/e2e/kestra_helpers.py
- tests/kestra/e2e/notion_helpers.py
- tests/kestra/e2e/test_dokploy_compose.py
- tests/kestra/e2e/test_deployment_health.py
- tests/kestra/e2e/test_webhook_accessibility.py
- tests/kestra/e2e/test_kestra_helpers.py
- tests/kestra/e2e/test_notion_helpers.py
- tests/kestra/e2e/test_assessment_e2e.py
- tests/kestra/e2e/test_all_handlers_e2e.py
- tests/kestra/e2e/test_email_split_verification.py
- tests/kestra/e2e/test_puppeteer_assessment_funnel.py
- tests/kestra/e2e/test_puppeteer_signup_funnel.py
- tests/kestra/e2e/test_puppeteer_secondary_funnels.py

## Commands

```bash
# Run deployment tests
pytest tests/kestra/e2e/test_deployment_health.py -v

# Run all E2E tests
pytest tests/kestra/e2e/ -v

# Run Puppeteer tests only
pytest tests/kestra/e2e/test_puppeteer_*.py -v
```

## Next Steps

1. Review plan and approve
2. Run `/execute-coding` to begin implementation
3. Wave 1 deploys Kestra (must complete first)
4. Waves 2-4 implement E2E tests
5. Run `/verify-coding` for final validation
