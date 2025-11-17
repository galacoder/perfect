# Next Steps: Christmas Campaign Deployment & Testing

**Status**: Wave 1+2 Complete ✅ - Ready for Deployment Testing
**Updated**: 2025-11-16 23:35
**Estimated Time to First Email**: 3-4 hours

---

## 📋 Quick Summary

You've completed the foundation and core 7-email nurture sequence implementation:
- ✅ 2,714 lines of production code
- ✅ 38/38 tests passing
- ✅ Complete Prefect deployment architecture
- ✅ Production credentials configured

**What's Next**: Deploy to Prefect Server → Create email templates → Test end-to-end

---

## 🚀 Phase 1: Deploy to Prefect Server (30 minutes)

### Step 1.1: Start Prefect Server

**In a new terminal window**, start Prefect Server:

```bash
cd /Users/sangle/Dev/action/projects/perfect
prefect server start
```

This will:
- Start the Prefect API server on http://127.0.0.1:4200
- Open the Prefect UI in your browser
- Keep running in the background (leave this terminal open)

**Expected Output**:
```
 ___ ___ ___ ___ ___ ___ _____
| _ \ _ \ __| __| __/ __|_   _|
|  _/   / _|| _|| _| (__  | |
|_| |_|_\___|_| |___\___| |_|

Configure Prefect to communicate with the server with:

    prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api

View the API reference documentation at http://127.0.0.1:4200/docs

Check out the dashboard at http://127.0.0.1:4200
```

**Verify**: Open http://127.0.0.1:4200 in your browser - you should see the Prefect UI.

---

### Step 1.2: Deploy All Flows

**In a second terminal**, deploy the Christmas Campaign flows:

```bash
cd /Users/sangle/Dev/action/projects/perfect
python campaigns/christmas_campaign/deployments/deploy_all.py
```

**What This Does**:
- Creates 7 email sender deployments (christmas-email-1 through christmas-email-7)
- Creates 1 orchestrator deployment (christmas-email-sequence-orchestrator)
- Outputs deployment IDs that you'll need for .env

**Expected Output**:
```
================================================================================
Christmas Campaign - Prefect Deployment
================================================================================

✅ Connected to Prefect Server: http://127.0.0.1:4200/api

🚀 Deploying 7 email sender flows...

📧 Deploying christmas-email-1...
✅ Deployed christmas-email-1: <deployment-id-1>

📧 Deploying christmas-email-2...
✅ Deployed christmas-email-2: <deployment-id-2>

[... 5 more emails ...]

🚀 Deploying email sequence orchestrator flow...
✅ Deployed orchestrator: <orchestrator-id>

================================================================================
✅ Deployment Complete!
================================================================================

📋 Copy these deployment IDs to your .env file:

DEPLOYMENT_ID_CHRISTMAS_EMAIL_1=<uuid-1>
DEPLOYMENT_ID_CHRISTMAS_EMAIL_2=<uuid-2>
DEPLOYMENT_ID_CHRISTMAS_EMAIL_3=<uuid-3>
DEPLOYMENT_ID_CHRISTMAS_EMAIL_4=<uuid-4>
DEPLOYMENT_ID_CHRISTMAS_EMAIL_5=<uuid-5>
DEPLOYMENT_ID_CHRISTMAS_EMAIL_6=<uuid-6>
DEPLOYMENT_ID_CHRISTMAS_EMAIL_7=<uuid-7>
DEPLOYMENT_ID_CHRISTMAS_ORCHESTRATOR=<uuid-8>

================================================================================
📝 Next Steps:
================================================================================
1. Update .env file with the deployment IDs above
2. Test the orchestrator flow
3. Trigger via webhook
```

---

### Step 1.3: Update .env with Deployment IDs

**Copy the deployment IDs** from the script output and add them to your `.env` file:

```bash
# Open .env in your editor
nano /Users/sangle/Dev/action/projects/perfect/.env

# Add these lines (replace <uuid> with actual IDs from script output):
DEPLOYMENT_ID_CHRISTMAS_EMAIL_1=<uuid-1>
DEPLOYMENT_ID_CHRISTMAS_EMAIL_2=<uuid-2>
DEPLOYMENT_ID_CHRISTMAS_EMAIL_3=<uuid-3>
DEPLOYMENT_ID_CHRISTMAS_EMAIL_4=<uuid-4>
DEPLOYMENT_ID_CHRISTMAS_EMAIL_5=<uuid-5>
DEPLOYMENT_ID_CHRISTMAS_EMAIL_6=<uuid-6>
DEPLOYMENT_ID_CHRISTMAS_EMAIL_7=<uuid-7>
DEPLOYMENT_ID_CHRISTMAS_ORCHESTRATOR=<uuid-8>

# Save and exit (Ctrl+X, then Y, then Enter)
```

**Verify in Prefect UI**:
- Go to http://127.0.0.1:4200/deployments
- You should see 8 deployments listed
- Each should show status "Ready"

---

## 🧪 Phase 2: Test in Testing Mode (30 minutes)

### Step 2.1: Enable Testing Mode

Update `.env` to use fast delays (minutes instead of hours):

```bash
# In .env, update this line:
TESTING_MODE=true
```

This changes email delays from 24-48 hours (production) to 2-7 minutes (testing).

---

### Step 2.2: Test Orchestrator Flow Locally

Run a test to verify the orchestrator schedules all 7 emails:

```bash
cd /Users/sangle/Dev/action/projects/perfect
python campaigns/christmas_campaign/flows/email_sequence_orchestrator.py
```

**What This Tests**:
- Segment classification (red/orange/yellow/green systems → CRITICAL/URGENT/OPTIMIZE)
- Notion contact search and update
- Scheduling all 7 email flows with correct delays
- Testing mode delay calculation (2-7 minutes instead of hours)

**Expected Output**:
```
🚀 Starting email sequence orchestration for test@example.com
📋 Testing mode: True
✅ Validating assessment data
🎯 Classifying contact segment
✅ Segment: URGENT
📋 Searching for contact: test@example.com
✅ Contact found: <page-id>
📝 Updating Notion with assessment data
📝 Updating contact phase to 'Phase 1 Assessment'
📅 Scheduling all 7 email flows with calculated delays

📧 Scheduling Email #1 (0 minutes from now)
✅ Email #1 scheduled: <flow-run-id-1>

📧 Scheduling Email #2 (2 minutes from now)
✅ Email #2 scheduled: <flow-run-id-2>

📧 Scheduling Email #3 (5 minutes from now)
✅ Email #3 scheduled: <flow-run-id-3>

[... emails 4-7 ...]

🎉 Successfully scheduled all 7 emails for test@example.com

✅ Test result: {
  "status": "success",
  "email": "test@example.com",
  "segment": "URGENT",
  "testing_mode": true,
  "scheduled_flows": [7 flow runs],
  "total_duration_hours": 27 (minutes in testing mode)
}
```

---

### Step 2.3: Monitor Flow Execution in Prefect UI

1. **Open Prefect UI**: http://127.0.0.1:4200/flow-runs
2. **Watch scheduled flows**: You should see 7 flows scheduled with start times 0, 2, 5, 9, 14, 20, 27 minutes from now
3. **Monitor execution**: As each email's scheduled time arrives, watch it execute
4. **Check logs**: Click on any flow run to see detailed logs

**What to Look For**:
- ✅ All 7 flows scheduled successfully
- ✅ Correct template IDs selected (universal vs segment-specific)
- ✅ Delays calculated correctly (cumulative: 0, 2, 5, 9, 14, 20, 27 min)
- ⚠️ Email sending will FAIL if templates don't exist in Notion yet (expected!)

---

## 📧 Phase 3: Create Email Templates in Notion (1-2 hours)

**IMPORTANT**: The flows will fail to send emails until templates exist in Notion.

### Step 3.1: Open Notion Email Templates Database

URL: https://sangletech.notion.site/2ab7c3741115811 5932cca6789c5b87b

(Database ID: `2ab7c374-1115-8115-932c-ca6789c5b87b`)

---

### Step 3.2: Create 10 Email Templates

Create these templates in the Email Templates database:

#### Template Properties

Each template needs:
- **template_id** (Title): Unique identifier (e.g., "christmas_email_1")
- **subject** (Rich Text): Email subject line
- **html_body** (Rich Text): HTML email content
- **segment** (Select): ALL, CRITICAL, URGENT, or OPTIMIZE

#### Template Variables

Use these placeholders in your email content:
- `{{first_name}}` - Contact's first name
- `{{business_name}}` - Business name
- `{{assessment_score}}` - BusOS score (0-100)
- `{{segment}}` - CRITICAL/URGENT/OPTIMIZE

---

#### Template 1: Results Delivery (Universal)

**template_id**: `christmas_email_1`
**subject**: `Your BusOS Assessment Results - {{business_name}}`
**segment**: `ALL`
**html_body**:

```html
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
  <h1 style="color: #2563eb;">Your BusOS Assessment Results</h1>

  <p>Hi {{first_name}},</p>

  <p>Thanks for completing the BusOS assessment for {{business_name}}!</p>

  <p><strong>Your BusOS Score: {{assessment_score}}/100</strong></p>

  <p>Over the next 10 days, I'll send you personalized insights and quick wins you can implement immediately to improve your systems.</p>

  <p>Check your inbox tomorrow for your first set of Quick Wins!</p>

  <p>Best,<br>
  Sang Le<br>
  BusOS Framework</p>
</body>
</html>
```

---

#### Template 2a: Quick Wins - CRITICAL

**template_id**: `christmas_email_2a_critical`
**subject**: `🚨 URGENT: 3 Quick Fixes for {{business_name}}`
**segment**: `CRITICAL`
**html_body**:

```html
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
  <h1 style="color: #dc2626;">🚨 Critical Systems Need Immediate Attention</h1>

  <p>Hi {{first_name}},</p>

  <p>Your assessment revealed <strong>critical issues</strong> in {{business_name}}'s systems. You have 2+ broken systems that need immediate attention.</p>

  <h2>3 Quick Fixes to Implement Today:</h2>

  <ol>
    <li><strong>Document your top 3 processes</strong> - Start with your most painful bottleneck</li>
    <li><strong>Create a daily standup</strong> - 15 minutes, same time, every day</li>
    <li><strong>Set up basic metrics tracking</strong> - What gets measured gets managed</li>
  </ol>

  <p><strong>Want help fixing these systems fast?</strong> Book a free diagnostic call below.</p>

  <p><a href="https://sangletech.com/book-diagnostic" style="background: #dc2626; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">Book Free Diagnostic →</a></p>

  <p>Best,<br>
  Sang Le</p>
</body>
</html>
```

---

#### Template 2b: Quick Wins - URGENT

**template_id**: `christmas_email_2b_urgent`
**subject**: `3 Quick Wins for {{business_name}}`
**segment**: `URGENT`
**html_body**:

```html
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
  <h1 style="color: #ea580c;">⚡ 3 Quick Wins for {{business_name}}</h1>

  <p>Hi {{first_name}},</p>

  <p>Your assessment showed some struggling systems. The good news? These are fixable with the right approach.</p>

  <h2>3 Quick Wins to Implement This Week:</h2>

  <ol>
    <li><strong>Map your customer journey</strong> - From first contact to delivery</li>
    <li><strong>Create SOPs for repeating tasks</strong> - Start with your most frequent processes</li>
    <li><strong>Set up weekly planning sessions</strong> - Plan Monday, review Friday</li>
  </ol>

  <p>Want a personalized roadmap? Book a free diagnostic call to get specific recommendations for {{business_name}}.</p>

  <p><a href="https://sangletech.com/book-diagnostic" style="background: #ea580c; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">Book Free Diagnostic →</a></p>

  <p>Best,<br>
  Sang Le</p>
</body>
</html>
```

---

#### Template 2c: Quick Wins - OPTIMIZE

**template_id**: `christmas_email_2c_optimize`
**subject**: `Level Up {{business_name}} with These 3 Strategies`
**segment**: `OPTIMIZE`
**html_body**:

```html
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
  <h1 style="color: #16a34a;">📈 3 Optimization Strategies for {{business_name}}</h1>

  <p>Hi {{first_name}},</p>

  <p>Your systems are functional - now let's make them exceptional!</p>

  <h2>3 Strategies to 10x Your Operations:</h2>

  <ol>
    <li><strong>Automate your bottlenecks</strong> - Identify repetitive tasks and build systems</li>
    <li><strong>Implement performance dashboards</strong> - Track KPIs in real-time</li>
    <li><strong>Build a scaling playbook</strong> - Document what's working so you can replicate it</li>
  </ol>

  <p>Want to see exactly where to optimize? Get a custom diagnostic for {{business_name}}.</p>

  <p><a href="https://sangletech.com/book-diagnostic" style="background: #16a34a; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">Book Free Diagnostic →</a></p>

  <p>Best,<br>
  Sang Le</p>
</body>
</html>
```

---

#### Templates 3-6: Universal Emails

Create similar templates for:
- **christmas_email_3**: Horror Story (Day 3)
- **christmas_email_4**: First Ask (Day 4)
- **christmas_email_5**: Case Study (Day 6)
- **christmas_email_6**: Checklist (Day 8)

---

#### Templates 7a-7c: Final Ask (Segment-Specific)

- **christmas_email_7a_critical**: Final Ask for CRITICAL segment
- **christmas_email_7b_urgent**: Final Ask for URGENT segment
- **christmas_email_7c_optimize**: Final Ask for OPTIMIZE segment

---

### Step 3.3: Verify Templates in Database

After creating all 10 templates:

1. Go to Email Templates database
2. Filter by "template_id" starts with "christmas"
3. Verify you have 10 templates
4. Check each has: template_id, subject, html_body

---

## ✅ Phase 4: End-to-End Testing (1 hour)

### Step 4.1: Create Test Contact in BusinessX Database

1. **Open BusinessX Canada database**: https://sangletech.notion.site/199c97e4c0a045278086941b7cca62f1
2. **Add new contact**:
   - **email**: test@example.com
   - **first_name**: Test
   - **business_name**: Test Corp
   - **Segment**: (leave empty - will be set by flow)
   - **Phase**: Phase 1 Assessment

---

### Step 4.2: Run Orchestrator Test Again

Now that templates exist, test the full flow:

```bash
cd /Users/sangle/Dev/action/projects/perfect
python campaigns/christmas_campaign/flows/email_sequence_orchestrator.py
```

**What Should Happen**:
1. Orchestrator finds test contact ✅
2. Classifies segment as URGENT (2 orange systems) ✅
3. Schedules 7 emails ✅
4. Email 1 sends immediately using `christmas_email_1` template ✅
5. Email 2 schedules for +2 min using `christmas_email_2b_urgent` template ✅
6. Emails 3-6 schedule with universal templates ✅
7. Email 7 schedules using `christmas_email_7b_urgent` template ✅

---

### Step 4.3: Verify Email Delivery

**Option 1: Check Resend Dashboard**
1. Go to https://resend.com/emails
2. Look for emails to test@example.com
3. Verify subject lines and content

**Option 2: Check Notion Tracking**
1. Go to BusinessX Canada database
2. Find test@example.com contact
3. Check fields:
   - `Christmas Email 1 Sent`: ✅ Checked
   - `Christmas Email 1 Date`: Today's date
   - `Christmas Campaign Status`: Nurture Sequence
   - `Segment`: URGENT

**Option 3: Check Prefect Logs**
1. Go to http://127.0.0.1:4200/flow-runs
2. Click on "christmas-email-1" flow run
3. Check logs for:
   - ✅ Email sent to test@example.com
   - ✅ Resend email ID returned
   - ✅ Notion tracking updated

---

### Step 4.4: Monitor 27-Minute Sequence

With `TESTING_MODE=true`, the full 7-email sequence runs in 27 minutes:
- 0 min: Email 1 ✅
- 2 min: Email 2 ✅
- 5 min: Email 3 ✅
- 9 min: Email 4 ✅
- 14 min: Email 5 ✅
- 20 min: Email 6 ✅
- 27 min: Email 7 ✅

**Watch in real-time**:
- Keep Prefect UI open: http://127.0.0.1:4200/flow-runs
- Refresh every minute to see new flows start
- Click on each to see detailed logs

---

## 🚀 Phase 5: Production Deployment (30 minutes)

### Step 5.1: Disable Testing Mode

Once testing is successful, switch to production delays:

```bash
# In .env, update:
TESTING_MODE=false
```

Now delays are:
- Email 1: Immediate
- Email 2: +48 hours (Day 2)
- Email 3: +24 hours (Day 3)
- Email 4: +24 hours (Day 4)
- Email 5: +48 hours (Day 6)
- Email 6: +48 hours (Day 8)
- Email 7: +48 hours (Day 10)

**Total sequence duration**: 10 days

---

### Step 5.2: Add FastAPI Webhook Endpoint

Create or update `server.py` to handle assessment webhook:

```python
from fastapi import FastAPI, BackgroundTasks
from campaigns.christmas_campaign.flows.email_sequence_orchestrator import (
    email_sequence_orchestrator_sync
)
from campaigns.christmas_campaign.tasks.models import AssessmentData

app = FastAPI()

@app.post("/webhook/christmas-assessment")
async def christmas_assessment_handler(
    assessment: AssessmentData,
    background_tasks: BackgroundTasks
):
    """
    Handle BusOS assessment completion webhook.

    Triggers the Christmas campaign 7-email nurture sequence.
    """
    # Trigger orchestrator flow in background
    background_tasks.add_task(
        email_sequence_orchestrator_sync,
        email=assessment.email,
        red_systems=assessment.red_systems,
        orange_systems=assessment.orange_systems,
        yellow_systems=assessment.yellow_systems,
        green_systems=assessment.green_systems,
        assessment_score=assessment.assessment_score,
        first_name=assessment.first_name or "there",
        business_name=assessment.business_name or "your business"
    )

    return {
        "status": "accepted",
        "message": f"Assessment processed for {assessment.email}",
        "segment": "Will be classified in background"
    }

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

### Step 5.3: Test Webhook

Start FastAPI server:

```bash
uvicorn server:app --reload --port 8000
```

Test webhook with curl:

```bash
curl -X POST http://localhost:8000/webhook/christmas-assessment \
  -H "Content-Type: application/json" \
  -d '{
    "email": "realtest@example.com",
    "red_systems": 3,
    "orange_systems": 2,
    "yellow_systems": 2,
    "green_systems": 1,
    "assessment_score": 25,
    "first_name": "Jane",
    "business_name": "Real Test Corp"
  }'
```

**Expected Response**:
```json
{
  "status": "accepted",
  "message": "Assessment processed for realtest@example.com",
  "segment": "Will be classified in background"
}
```

**Verify**:
- Check Prefect UI for new orchestrator flow run
- Contact should be classified as CRITICAL (3 red systems)
- 7 emails should be scheduled
- First email sends immediately

---

## 📊 Success Metrics

After testing, you should see:

✅ **Deployment**:
- 8 deployments in Prefect (7 emails + 1 orchestrator)
- All deployment IDs in .env
- Prefect UI accessible at http://127.0.0.1:4200

✅ **Templates**:
- 10 email templates in Notion Email Templates database
- Each with template_id, subject, html_body

✅ **Testing**:
- Orchestrator flow runs successfully
- All 7 emails schedule with correct delays
- Email 1 sends immediately
- Notion tracking updates correctly

✅ **Production**:
- FastAPI webhook endpoint responds
- Background task triggers orchestrator
- First real customer email sends

---

## 🎯 Next Phase: Wave 3+4 (Optional)

Once Wave 1+2 are validated in production, you can proceed with:

**Wave 3: Cal.com Integration** (5-6 hours)
- Booking webhook handler
- Pre-call prep sequence (3 emails)
- Customer portal delivery (<60 seconds)

**Wave 4: Long-Term Nurture** (4-5 hours)
- Day 14 decision email
- Phase 2B coaching sequence
- Unsubscribe handling

**Total Remaining**: 9-11 hours

---

## 🆘 Troubleshooting

### Issue: Deployment fails with "API not reachable"
**Solution**: Start Prefect Server first: `prefect server start`

### Issue: Emails not sending
**Solution**: Check that templates exist in Notion Email Templates database

### Issue: Wrong template selected
**Solution**: Verify segment classification logic in `campaigns/christmas_campaign/tasks/routing.py`

### Issue: Delays incorrect
**Solution**: Check `TESTING_MODE` in .env (true = minutes, false = hours)

### Issue: Contact not found
**Solution**: Verify email exists in BusinessX Canada database before triggering assessment

---

## 📞 Support

**Documentation**: See `/Users/sangle/Dev/action/projects/perfect/campaigns/christmas_campaign/` for code
**Plan**: `.claude/tasks/plans/PLAN-christmas-campaign-UPDATED-prefect-deployments.md`
**Progress**: `.claude/tasks/active/christmas-campaign-email-automation/PROGRESS.md`

---

**Status**: Ready to deploy! Start with Phase 1, Step 1.1 above. 🚀
