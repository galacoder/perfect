# Plan: Deploy FastAPI Webhook Server via Coolify

**Task ID**: 1128-deploy-fastapi-coolify
**Domain**: CODING (Infrastructure/Deployment)
**Source**: feature_list.json

---

## Overview

Deploy the existing FastAPI webhook server (`server.py`) to Coolify PaaS platform. Docker configuration already exists; primary work is Coolify deployment, DNS, and SSL configuration.

**Key Insight**: 95% of infrastructure is already complete. This is a low-complexity deployment task.

---

## Wave 1: Docker Cleanup
**Objective**: Create .dockerignore and verify Docker configuration
**Status**: Pending
**Estimated Time**: 30 minutes

### Tasks

- [ ] 1.1: Create .dockerignore file
  - Exclude: `.git/`, `__pycache__/`, `.env`, `.venv/`, `tests/`, `.claude/`, `*.pyc`, `.pytest_cache/`
  - Reduces image size and improves security

- [ ] 1.2: Verify Dockerfile.webhook configuration
  - Confirm Python 3.11-slim base
  - Confirm health check endpoint
  - Confirm non-root user
  - Confirm uvicorn workers

- [ ] 1.3: Verify docker-compose.coolify.yml
  - Confirm service names
  - Confirm networking
  - Confirm Coolify magic variables

### Success Criteria
- [ ] .dockerignore exists with appropriate exclusions
- [ ] Docker image builds successfully
- [ ] Image size is reasonable (<500MB)

---

## Wave 2: Coolify Deployment
**Objective**: Deploy webhook server to Coolify using docker-compose.coolify.yml
**Status**: Pending
**Estimated Time**: 60 minutes

### Tasks

- [ ] 2.1: Push latest code to GitHub
  - Ensure .dockerignore is committed
  - Verify docker-compose.coolify.yml is in main branch

- [ ] 2.2: Create Coolify project for perfect-webhook
  - Use `coolify-integration` skill
  - Create new project named "Perfect Marketing Automation"

- [ ] 2.3: Configure Coolify Docker Compose deployment
  - Add Docker Compose resource
  - Point to `galacoder/perfect` repository
  - Specify `docker-compose.coolify.yml`
  - Branch: `main`

- [ ] 2.4: Configure environment variables in Coolify
  - `PREFECT_API_URL=https://prefect.galatek.dev/api`
  - `TESTING_MODE=false`
  - (Optional) `GITHUB_ACCESS_TOKEN` for private repo

- [ ] 2.5: Deploy to Coolify
  - Trigger deployment
  - Monitor build logs
  - Verify container starts healthy

### Success Criteria
- [ ] Both containers (webhook + worker) running
- [ ] Health checks passing
- [ ] No errors in container logs

---

## Wave 3: DNS and SSL Configuration
**Objective**: Configure domain and verify SSL certificate
**Status**: Pending
**Estimated Time**: 30 minutes

### Tasks

- [ ] 3.1: Configure domain in Coolify
  - Choose domain:
    - Option A: `api.sangletech.com`
    - Option B: `webhooks.galatek.dev`
    - Option C: `perfect-webhook.galatek.dev`
  - Set in Coolify service settings

- [ ] 3.2: Configure DNS A/CNAME record
  - Add DNS record at domain registrar
  - Point to Coolify server IP
  - Wait for DNS propagation (5-15 minutes)

- [ ] 3.3: Verify SSL certificate
  - Coolify/Traefik auto-provisions Let's Encrypt
  - Verify HTTPS works
  - Check certificate validity

### Success Criteria
- [ ] Domain resolves to Coolify server
- [ ] HTTPS works without certificate warnings
- [ ] SSL certificate is valid and trusted

---

## Wave 4: Testing and Verification
**Objective**: Test health endpoint, webhook endpoints, and Prefect flow triggers
**Status**: Pending
**Estimated Time**: 60 minutes

### Tasks

- [ ] 4.1: Test health endpoint
  ```bash
  curl -s https://DOMAIN/health | jq
  ```
  Expected:
  ```json
  {
    "status": "healthy",
    "timestamp": "...",
    "environment": {...}
  }
  ```

- [ ] 4.2: Test christmas-signup webhook
  ```bash
  curl -X POST https://DOMAIN/webhook/christmas-signup \
    -H "Content-Type: application/json" \
    -d '{
      "email": "lengobaosang@gmail.com",
      "first_name": "Test",
      "assessment_score": 52,
      "red_systems": 2,
      "orange_systems": 1
    }'
  ```
  Expected: 202 Accepted

- [ ] 4.3: Verify Prefect flow triggered
  - Open https://prefect.galatek.dev
  - Check for new flow run
  - Verify flow completed successfully

- [ ] 4.4: Update STATUS.md with webhook deployment info
  - Add webhook URL to documentation
  - Update status to reflect deployment

- [ ] 4.5: Update WEBSITE_INTEGRATION.md with production URL
  - Replace localhost URLs with production domain
  - Add example curl commands

### Success Criteria
- [ ] Health endpoint returns 200 OK
- [ ] Webhook returns 202 Accepted
- [ ] Prefect flow run visible in dashboard
- [ ] Documentation updated with production URLs

---

## Risk Mitigation

### Environment Variables
**Risk**: server.py startup validation may fail without env vars
**Mitigation**: The flows use Secret blocks, but startup check uses env vars. May need to either:
- Set env vars in Coolify for validation only
- Modify server.py to skip validation when Secret blocks available

### Network Connectivity
**Risk**: Webhook container cannot reach Prefect API
**Mitigation**: Verify `PREFECT_API_URL` is set and accessible from container

### DNS Propagation
**Risk**: DNS changes take time to propagate
**Mitigation**: Use `dig` or online DNS checkers to verify propagation

---

## Dependencies

### External Services
| Service | URL | Required For |
|---------|-----|--------------|
| Coolify | https://coolify.galatek.dev | Deployment |
| Prefect | https://prefect.galatek.dev/api | Flow orchestration |
| GitHub | https://github.com/galacoder/perfect | Source code |

### Skills Required
- `coolify-integration` - For Coolify API operations

---

## Post-Deployment Checklist

- [ ] Health endpoint accessible via HTTPS
- [ ] All 8 webhook endpoints responding
- [ ] Prefect flows triggering successfully
- [ ] Container health checks passing
- [ ] Documentation updated
- [ ] Website team notified of production URL
