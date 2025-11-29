# Discovery: Deploy FastAPI Webhook Server via Coolify

**Task ID**: 1128-deploy-fastapi-coolify
**Domain**: CODING (Infrastructure/Deployment)
**Date**: 2025-11-28

---

## Executive Summary

**EXCELLENT NEWS**: The infrastructure is 95% complete. Docker configuration files already exist and are production-ready. The main task is to deploy to Coolify and configure DNS/SSL.

---

## Key Findings

### 1. Docker Infrastructure (COMPLETE)

All required Docker files exist and are well-configured:

| File | Status | Description |
|------|--------|-------------|
| `Dockerfile.webhook` | COMPLETE | FastAPI server, Python 3.11, uvicorn, health check |
| `Dockerfile.prefect` | COMPLETE | Prefect worker, git support, connects to prefect.galatek.dev |
| `docker-compose.coolify.yml` | COMPLETE | Both services configured, networking, volumes |

**Dockerfile.webhook highlights**:
- Python 3.11-slim base image
- Non-root user for security
- Health check at `/health` endpoint
- Exposes port 8000
- 2 uvicorn workers

**docker-compose.coolify.yml highlights**:
- Two services: `perfect-worker` (Prefect) and `perfect-webhook` (FastAPI)
- Coolify magic variable for FQDN: `SERVICE_FQDN_PERFECT_WEBHOOK_8000`
- Health checks configured
- Bridge networking
- Persistent volume for Prefect data

### 2. FastAPI Server (COMPLETE)

**File**: `server.py` (990 lines)

**Endpoints**:
| Endpoint | Method | Description | Flow Triggered |
|----------|--------|-------------|----------------|
| `/health` | GET | Health check | - |
| `/webhook/signup` | POST | BusOS signup | signup_handler_flow |
| `/webhook/assessment` | POST | Assessment completion | assessment_handler_flow |
| `/webhook/christmas-signup` | POST | Christmas campaign | christmas signup_handler_flow |
| `/webhook/calcom-booking` | POST | Cal.com booking | precall_prep_flow |
| `/webhook/calendly-noshow` | POST | No-show recovery | noshow_recovery_handler_flow |
| `/webhook/postcall-maybe` | POST | Post-call maybe | postcall_maybe_handler_flow |
| `/webhook/onboarding-start` | POST | Onboarding start | onboarding_handler_flow |

**Key Features**:
- CORS middleware enabled
- Pydantic request validation
- Background task execution (non-blocking)
- Logging configured
- Discord notifications for CRITICAL segment

### 3. Dependencies (COMPLETE)

**requirements.txt**:
```
prefect==3.4.1
notion-client==2.2.1
resend==2.19.0
httpx==0.27.2
python-dotenv==1.0.1
fastapi==0.115.6
uvicorn[standard]==0.34.0
pydantic[email]==2.10.4
pytest==8.3.4
pytest-mock==3.14.0
pytest-cov==6.0.0
```

### 4. Secret Management (COMPLETE)

**Prefect Secret Blocks** (7 blocks on production):
| Block Name | Purpose |
|------------|---------|
| `notion-token` | Notion API token |
| `notion-email-templates-db-id` | Email templates DB |
| `notion-email-sequence-db-id` | Sequence tracking DB |
| `notion-businessx-db-id` | BusinessX contacts DB |
| `notion-customer-projects-db-id` | Customer portal DB |
| `notion-email-analytics-db-id` | Analytics DB |
| `resend-api-key` | Resend email API |

**Note**: The webhook server itself may still use environment variables for the Prefect flows to load from Secret blocks. The startup check in `server.py` validates env vars, but the actual flows use Secret blocks.

### 5. Git Repository (COMPLETE)

- **Repository**: https://github.com/galacoder/perfect.git
- **Branch**: main
- **Remote**: origin

### 6. Prefect Deployments (COMPLETE)

5 deployments configured in `prefect.yaml`:
1. `christmas-signup-handler`
2. `christmas-send-email`
3. `christmas-noshow-recovery-handler`
4. `christmas-postcall-maybe-handler`
5. `christmas-onboarding-handler`

All use git-based pull from GitHub.

---

## What's Missing

### 1. No .dockerignore File

Currently copies entire directory into Docker image. Should exclude:
- `.git/`
- `__pycache__/`
- `.env`
- `.venv/`
- `*.pyc`
- `.pytest_cache/`
- `.claude/`
- `tests/` (for production image)

### 2. Coolify Deployment Not Done

The `docker-compose.coolify.yml` exists but:
- Not yet deployed to Coolify
- No domain configured
- No SSL certificate

### 3. Environment Variable Clarification

The `server.py` startup checks for env vars, but flows use Secret blocks. Need to clarify:
- Does FastAPI server need env vars? (For startup validation only)
- Or can we modify to skip validation since flows use Secret blocks?

---

## Architecture Overview

```
                    INTERNET
                        |
                        v
                 [Coolify/Traefik]
                   (SSL, Domain)
                        |
                        v
        +---------------+---------------+
        |                               |
        v                               v
[perfect-webhook]               [perfect-worker]
   FastAPI:8000                  Prefect Worker
        |                               |
        |   Background Task             |
        +-----------> Prefect API <-----+
                          |
                          v
                 [prefect.galatek.dev]
                          |
              +-----------+-----------+
              |           |           |
              v           v           v
         [Notion]    [Resend]   [Discord]
```

**Data Flow**:
1. Website sends POST to `/webhook/christmas-signup`
2. FastAPI validates request, returns 202 Accepted
3. Background task imports and runs Prefect flow
4. Prefect flow loads credentials from Secret blocks
5. Flow schedules email sequence via Prefect API
6. Prefect worker picks up scheduled runs

---

## Risks and Considerations

### Low Risk
- Docker files already tested and production-ready
- Prefect Secret blocks already configured
- Git-based deployment working

### Medium Risk
- Environment variable validation in server.py startup
  - May need to adjust for production where Secret blocks handle credentials

### High Risk
- None identified

---

## Recommendations

1. **Create .dockerignore** to reduce image size and security
2. **Deploy to Coolify** using existing docker-compose.coolify.yml
3. **Configure domain** (suggest: `api.sangletech.com` or `webhooks.galatek.dev`)
4. **Test health endpoint** after deployment
5. **Update server.py** to handle Secret blocks vs env vars gracefully
6. **Document deployment** in campaigns/christmas_campaign/STATUS.md

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `.dockerignore` | CREATE | Exclude unnecessary files from Docker image |
| `server.py` | MODIFY (optional) | Graceful handling when env vars not set |
| `docker-compose.coolify.yml` | VERIFY | May need domain tweaks |
| `campaigns/christmas_campaign/STATUS.md` | UPDATE | Document webhook deployment |

---

## Estimated Effort

| Phase | Hours | Notes |
|-------|-------|-------|
| Wave 1: Docker cleanup | 0.5 | Create .dockerignore |
| Wave 2: Coolify deployment | 1.0 | Deploy via Coolify UI |
| Wave 3: DNS/SSL config | 0.5 | Configure domain, verify SSL |
| Wave 4: Testing | 1.0 | Health check, webhook tests |
| **Total** | **3.0** | |

---

## Conclusion

This is a low-complexity deployment task. The heavy lifting (Docker configuration, Prefect setup, Secret blocks) is already complete. The remaining work is:

1. Create `.dockerignore` (5 minutes)
2. Deploy to Coolify (30 minutes)
3. Configure DNS (15 minutes)
4. Test and verify (30 minutes)

**Ready for PLAN phase.**
