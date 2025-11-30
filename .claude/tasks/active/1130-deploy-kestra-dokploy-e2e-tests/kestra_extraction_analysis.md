# Kestra Repository Extraction Analysis

**Generated**: 2025-11-30
**Task**: 1130-deploy-kestra-dokploy-e2e-tests
**Feature**: 0.1 - Analyze git commits for Kestra-related changes

---

## Git Commit Analysis

### Total Commits Found
- **17 commits** related to Kestra work (task 1129)

### Key Commits (newest to oldest)

```
a8ea55d chore(task-1129): update progress - Features 4.1 & 4.2 complete (81.48%)
32d1639 feat(wave4): Feature 4.1 complete - webhook endpoint documentation (no proxy needed)
8582796 feat(wave4): Feature 4.3 complete - production docker-compose for homelab
637444d feat(wave4): Feature 4.6 complete - comprehensive Kestra documentation
fea613d feat(3.6): email analytics logging - integrated into send-email flow
1bcfcf2 feat(3.5): assessment handler - 5-day sequence Emails #2-5 ONLY (Email #1 from website)
c8609cc feat(3.4): onboarding handler - 3-email welcome sequence with payment validation
bb3db94 feat(3.3): post-call maybe handler - 3-email sequence ALL from Kestra
884b7fc feat(3.2): noshow recovery handler - 3-email sequence ALL from Kestra
e766f7f feat(wave2): complete Feature 2.8 - comprehensive tests for Notion Sequence Tracker
4067ac9 feat(2.1): implement routing logic for Kestra (25 tests passing)
471ed91 feat(1.4): set up Kestra flow directory structure with README and handlers directory
36a9218 feat(1.3): implement Kestra health check flow with secret verification
31d8d27 test: add failing tests for Kestra health check flow (Feature 1.3)
e38951d feat(1.2): configure Kestra secrets with .env.kestra.example and .gitignore
a130e5c test: add failing tests for Kestra secrets configuration (Feature 1.2)
d212b12 feat(1.1): implement Docker Compose for Kestra + PostgreSQL
```

---

## File Paths to Extract

### Kestra Flows (13 YAML files)
```
kestra/flows/christmas/health-check.yml
kestra/flows/christmas/send-email.yml
kestra/flows/christmas/schedule-email-sequence.yml
kestra/flows/christmas/handlers/signup-handler.yml
kestra/flows/christmas/handlers/assessment-handler.yml
kestra/flows/christmas/handlers/noshow-recovery-handler.yml
kestra/flows/christmas/handlers/postcall-maybe-handler.yml
kestra/flows/christmas/handlers/onboarding-handler.yml
kestra/flows/christmas/tasks/notion_search_contact.yml
kestra/flows/christmas/tasks/notion_create_sequence.yml
kestra/flows/christmas/tasks/notion_fetch_template.yml
kestra/flows/christmas/tasks/notion_update_sequence_tracker.yml
kestra/flows/christmas/tasks/resend_send_email.yml
```

### Kestra Library Code
```
kestra/flows/christmas/lib/routing.py
kestra/flows/christmas/handlers/.gitkeep
```

### Documentation
```
kestra/README.md
campaigns/christmas_campaign/DEPLOYMENT_KESTRA.md
campaigns/christmas_campaign/KESTRA_MIGRATION.md
campaigns/christmas_campaign/WEBSITE_INTEGRATION_KESTRA.md
```

### Docker Compose Files
```
docker-compose.kestra.yml
docker-compose.kestra.prod.yml
```

### Test Files (18 Python files)
```
tests/kestra/test_analytics_task.py
tests/kestra/test_assessment_handler_flow.py
tests/kestra/test_health_flow.py
tests/kestra/test_noshow_handler_flow.py
tests/kestra/test_notion_sequence_tracker.py
tests/kestra/test_onboarding_handler_flow.py
tests/kestra/test_postcall_handler_flow.py
tests/kestra/test_production_compose.py
tests/kestra/test_secrets.py
... (18 total)
```

---

## Extraction Strategy

### Approach: Git Filter-Branch with Subdirectory Filter

**Recommended command**:
```bash
git filter-branch --subdirectory-filter kestra --prune-empty -- --all
```

**Alternative: Git Subtree Split** (preserves more history):
```bash
git subtree split --prefix=kestra -b kestra-extraction
```

### Paths to Include in Extraction
1. `kestra/` directory (all flows, lib, README)
2. `tests/kestra/` directory (all test files)
3. `docker-compose.kestra.yml`
4. `docker-compose.kestra.prod.yml`
5. `campaigns/christmas_campaign/DEPLOYMENT_KESTRA.md`
6. `campaigns/christmas_campaign/KESTRA_MIGRATION.md`
7. `campaigns/christmas_campaign/WEBSITE_INTEGRATION_KESTRA.md`

### Paths to EXCLUDE
- `.claude/` (task metadata)
- `campaigns/` (except Kestra docs)
- `flows/` (Prefect flows)
- `tasks/` (Prefect tasks)
- `server.py` (FastAPI server)
- All other non-Kestra files

---

## Target Repository Structure

```
kestra-automation/
├── README.md                          # From kestra/README.md
├── docker-compose.yml                 # From docker-compose.kestra.prod.yml
├── docker-compose.dev.yml             # From docker-compose.kestra.yml
├── .gitignore
├── .env.example
├── docs/
│   ├── DEPLOYMENT.md                  # From campaigns/.../DEPLOYMENT_KESTRA.md
│   ├── MIGRATION.md                   # From campaigns/.../KESTRA_MIGRATION.md
│   └── WEBSITE_INTEGRATION.md         # From campaigns/.../WEBSITE_INTEGRATION_KESTRA.md
├── flows/
│   └── christmas/
│       ├── health-check.yml
│       ├── send-email.yml
│       ├── schedule-email-sequence.yml
│       ├── lib/
│       │   └── routing.py
│       ├── handlers/
│       │   ├── signup-handler.yml
│       │   ├── assessment-handler.yml
│       │   ├── noshow-recovery-handler.yml
│       │   ├── postcall-maybe-handler.yml
│       │   └── onboarding-handler.yml
│       └── tasks/
│           ├── notion_search_contact.yml
│           ├── notion_create_sequence.yml
│           ├── notion_fetch_template.yml
│           ├── notion_update_sequence_tracker.yml
│           └── resend_send_email.yml
└── tests/
    ├── test_analytics_task.py
    ├── test_assessment_handler_flow.py
    ├── test_health_flow.py
    ├── test_noshow_handler_flow.py
    ├── test_notion_sequence_tracker.py
    ├── test_onboarding_handler_flow.py
    ├── test_postcall_handler_flow.py
    ├── test_production_compose.py
    ├── test_secrets.py
    └── ... (18 total test files)
```

---

## Validation Checklist (for Feature 0.6)

- [ ] All 13 YAML flows exist in flows/christmas/
- [ ] All 18 test files copied from tests/kestra/
- [ ] Git log shows 17 Kestra-related commits with preserved messages
- [ ] Docker compose files valid YAML
- [ ] No broken file references in flows
- [ ] README.md updated with standalone repository context
- [ ] Documentation paths updated (no references to "perfect" repo)
- [ ] .gitignore includes .env and kestra data directories
- [ ] .env.example with all required secrets documented

---

## Notes

- Total commits to preserve: **17**
- Total YAML flows: **13**
- Total test files: **18**
- Estimated repository size: ~50KB (text files only)
- Git history size: TBD (depends on extraction method)
