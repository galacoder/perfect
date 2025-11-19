# 🎯 Final Deployment Checklist - Christmas Campaign

**Status**: Ready for Production Deployment
**Date**: 2025-11-19
**Architecture**: Prefect CLI (Simplified - No FastAPI/Nginx/Webhook subdomain)

---

## ✅ Completed (Local Development)

### Wave 1: Foundation ✅
- [x] Webhook endpoint created (`POST /webhook/christmas-signup`)
- [x] Email Sequence DB operations implemented
- [x] Signup handler flow created with full logic
- [x] Unit tests written (12 tests)
- [x] Committed to git

### Wave 2: Email Scheduling ✅
- [x] Send email flow updated with Email Sequence DB tracking
- [x] Prefect deployment script created
- [x] Signup handler schedules 7 emails via Deployment
- [x] TESTING_MODE support (fast/production delays)
- [x] Idempotency checks implemented
- [x] Committed to git

### Wave 3: Cal.com Integration ✅
- [x] Cal.com webhook endpoint created (`POST /webhook/calcom-booking`)
- [x] Pre-call prep flow implemented (3 reminder emails)
- [x] Notion meeting tracking integration
- [x] Dry-run tests passing (5 test suites)
- [x] Manual testing script created
- [x] Committed to git

### Wave 4: Sales Funnel Integration ✅
- [x] Replaced Resend with Prefect webhook in assessment page
- [x] Frontend integration complete (businessName + webhook call)
- [x] E2E test script created
- [x] Testing guide created
- [x] Production deployment guide created
- [x] Committed to git

### Local Deployment ✅
- [x] Prefect server running locally
- [x] Work pool created (`default-pool`)
- [x] Flow deployed via Prefect CLI
- [x] Worker started and executing flows
- [x] API endpoint tested successfully (HTTP 201)
- [x] Flow execution verified
- [x] Complete documentation created (2,100+ lines)

---

## 🚀 Production Deployment Tasks

### Pre-Deployment Preparation

- [ ] **1. Verify Server Access**
  - [ ] SSH access to prefect.galatek.dev
  - [ ] Sudo privileges for systemd service creation
  - [ ] Git access to clone/pull latest code

- [ ] **2. Environment Setup**
  - [ ] Python 3.11+ installed
  - [ ] Prefect CLI installed (`pip install prefect`)
  - [ ] PostgreSQL running (if using Prefect Server with DB)
  - [ ] Project code synced to server

- [ ] **3. Credentials Ready**
  - [ ] NOTION_TOKEN
  - [ ] NOTION_EMAIL_SEQUENCE_DB_ID
  - [ ] NOTION_BUSINESSX_DB_ID
  - [ ] RESEND_API_KEY
  - [ ] RESEND_FROM_EMAIL
  - [ ] All credentials added to `.env` file on server

### Deployment Execution

- [ ] **4. SSH to Production Server**
  ```bash
  ssh your-username@galatek.dev
  cd /path/to/perfect
  ```

- [ ] **5. Run Deployment Script**
  ```bash
  chmod +x campaigns/christmas_campaign/scripts/deploy_to_production.sh
  ./campaigns/christmas_campaign/scripts/deploy_to_production.sh
  ```

  **OR Manual Steps**:

  - [ ] 5.1. Set PYTHONPATH
    ```bash
    export PYTHONPATH=/path/to/perfect
    ```

  - [ ] 5.2. Create work pool
    ```bash
    prefect work-pool create default-pool --type process
    ```

  - [ ] 5.3. Deploy flow
    ```bash
    prefect deploy \
      campaigns/christmas_campaign/flows/signup_handler.py:signup_handler_flow \
      --name christmas-signup-handler \
      --pool default-pool \
      --tag christmas \
      --tag christmas-2025 \
      --tag email-nurture \
      --description "Christmas Campaign signup handler" \
      --version 1.0.0
    ```

  - [ ] 5.4. Save deployment ID
    ```bash
    prefect deployment ls | grep christmas-signup-handler
    ```

- [ ] **6. Start Worker Service**
  - [ ] Create systemd service file
  - [ ] Enable service: `sudo systemctl enable prefect-worker`
  - [ ] Start service: `sudo systemctl start prefect-worker`
  - [ ] Verify: `sudo systemctl status prefect-worker`

- [ ] **7. Test Production Endpoint**
  ```bash
  curl -X POST https://prefect.galatek.dev/api/deployments/{DEPLOYMENT_ID}/create_flow_run \
    -H "Content-Type: application/json" \
    -d '{"name":"test","parameters":{"email":"test@example.com",...}}'
  ```

  **Expected**: HTTP 201 Created

### Post-Deployment Validation

- [ ] **8. Verify in Prefect UI**
  - [ ] Open https://prefect.galatek.dev/
  - [ ] Check "Deployments" → christmas-signup-handler exists
  - [ ] Check "Flow Runs" → test run completed successfully
  - [ ] Check "Workers" → worker active and healthy

- [ ] **9. Verify Notion Integration**
  - [ ] Check Email Sequence DB for test record
  - [ ] Verify segment classification (CRITICAL/URGENT/OPTIMIZE)
  - [ ] Verify all fields populated correctly
  - [ ] Check BusinessX Canada DB updated (if applicable)

- [ ] **10. Verify Email Delivery**
  - [ ] Check Resend dashboard for sent email
  - [ ] Verify email received in inbox
  - [ ] Verify email content matches template
  - [ ] Check "Email 1 Sent" timestamp in Notion

### Website Integration

- [ ] **11. Update Website Environment Variables**

  **Vercel Dashboard**:
  - [ ] Add `PREFECT_API_URL=https://prefect.galatek.dev/api`
  - [ ] Add `CHRISTMAS_DEPLOYMENT_ID={deployment-id-from-step-5}`

  **OR Vercel CLI**:
  ```bash
  vercel env add PREFECT_API_URL production
  vercel env add CHRISTMAS_DEPLOYMENT_ID production
  ```

- [ ] **12. Deploy Website Updates**
  ```bash
  git add .
  git commit -m "feat: integrate Prefect production deployment"
  git push origin main
  ```

  **OR**:
  ```bash
  vercel --prod
  ```

- [ ] **13. Test Website Form Submission**
  - [ ] Go to Christmas assessment page
  - [ ] Complete assessment form
  - [ ] Submit form
  - [ ] Verify: "Success" message shown
  - [ ] Verify: Flow run created in Prefect UI
  - [ ] Verify: Notion record created
  - [ ] Verify: Email sent within 1 minute (TESTING_MODE=true)

### End-to-End Testing

- [ ] **14. Test CRITICAL Segment**
  - [ ] Submit form with red_systems >= 2
  - [ ] Verify segment = "CRITICAL" in Notion
  - [ ] Verify email sent with CRITICAL template

- [ ] **15. Test URGENT Segment**
  - [ ] Submit form with red_systems = 1 OR orange_systems >= 2
  - [ ] Verify segment = "URGENT" in Notion
  - [ ] Verify email sent with URGENT template

- [ ] **16. Test OPTIMIZE Segment**
  - [ ] Submit form with all systems mostly green/yellow
  - [ ] Verify segment = "OPTIMIZE" in Notion
  - [ ] Verify email sent with OPTIMIZE template

- [ ] **17. Test Idempotency**
  - [ ] Submit same email address twice
  - [ ] Verify: Only ONE sequence created
  - [ ] Verify: Second submission prevented
  - [ ] Verify: Only ONE email sent

### Monitoring Setup

- [ ] **18. Create Health Check Script**
  ```bash
  # Script created at: scripts/health_check.sh
  chmod +x scripts/health_check.sh
  ./scripts/health_check.sh
  ```

- [ ] **19. Setup Log Monitoring**
  - [ ] Worker logs: `sudo journalctl -u prefect-worker -f`
  - [ ] Prefect server logs (if applicable)
  - [ ] Application logs

- [ ] **20. Setup Alerting (Optional)**
  - [ ] Email alerts for failed flow runs
  - [ ] Discord/Slack webhook for CRITICAL segment
  - [ ] Daily health check reports

### Production Timing Switch

- [ ] **21. Monitor for 24-48 Hours (TESTING_MODE=true)**
  - [ ] Check all flow runs complete successfully
  - [ ] Verify email delivery rates acceptable
  - [ ] Verify Notion tracking accurate
  - [ ] Verify no errors in logs

- [ ] **22. Switch to Production Timing**
  ```bash
  # Edit .env on server
  TESTING_MODE=false

  # Restart worker
  sudo systemctl restart prefect-worker
  ```

  **Production Delays**:
  - Email 1: 0 hours (immediate)
  - Email 2: 24 hours
  - Email 3: 72 hours (3 days)
  - Email 4: 120 hours (5 days)
  - Email 5: 168 hours (7 days)
  - Email 6: 216 hours (9 days)
  - Email 7: 264 hours (11 days)

---

## 📊 Success Metrics

After deployment, track these metrics:

### Week 1
- [ ] Total signups processed: ___
- [ ] Flow runs succeeded: ___
- [ ] Flow runs failed: ___
- [ ] Email delivery rate: ___%
- [ ] Idempotency checks triggered: ___

### Segment Distribution
- [ ] CRITICAL: ___ (___%)
- [ ] URGENT: ___ (___%)
- [ ] OPTIMIZE: ___ (___%)

### Email Performance (Track in Resend)
- [ ] Email 1 sent: ___
- [ ] Email 2 sent: ___
- [ ] Email 3 sent: ___
- [ ] Email 4 sent: ___
- [ ] Email 5 sent: ___
- [ ] Email 6 sent: ___
- [ ] Email 7 sent: ___

### Issues Encountered
- [ ] Document any issues: ___________________
- [ ] Resolution steps: ___________________

---

## 🆘 Rollback Procedure

If critical issues occur:

1. **Stop Worker**
   ```bash
   sudo systemctl stop prefect-worker
   ```

2. **Delete Deployment**
   ```bash
   prefect deployment delete christmas-signup-handler/christmas-signup-handler
   ```

3. **Revert Website Changes**
   ```bash
   # Remove environment variables from Vercel
   vercel env rm CHRISTMAS_DEPLOYMENT_ID production
   ```

4. **Restore Previous Webhook** (if applicable)
   - Revert `assessment/complete.ts` to previous version
   - Redeploy website

---

## 📚 Reference Documentation

- **Production Deployment Execution**: `PRODUCTION_DEPLOYMENT_EXECUTION.md`
- **Production Deployment Info**: `PRODUCTION_DEPLOYMENT_INFO.md`
- **Deployment Success Summary**: `DEPLOYMENT_SUCCESS_SUMMARY.md`
- **Simplified Architecture Decision**: `SIMPLIFIED_ARCHITECTURE_DECISION.md`
- **Deployment Guide**: `DEPLOYMENT_GUIDE_SIMPLIFIED.md`

---

## 🎉 Deployment Complete Criteria

All tasks above must be checked ✅ before declaring production deployment complete:

- [ ] All "Production Deployment Tasks" completed
- [ ] All "Post-Deployment Validation" passed
- [ ] All "Website Integration" verified
- [ ] All "End-to-End Testing" scenarios passed
- [ ] Monitoring setup and running
- [ ] 24-48 hour validation period completed
- [ ] Switched to production timing
- [ ] No critical issues in first week

---

**Status**: ⏳ Pending Production Deployment
**Blocker**: SSH access to prefect.galatek.dev required
**Ready**: All code, tests, and documentation complete
**Time Estimate**: 15-20 minutes on production server

---

**Once deployment is complete, update this file and commit:**

```bash
git add campaigns/christmas_campaign/FINAL_DEPLOYMENT_CHECKLIST.md
git commit -m "docs(christmas): mark production deployment complete"
git push origin main
```
