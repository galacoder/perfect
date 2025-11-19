# Christmas Campaign - Automation Flow Analysis

**Date**: 2025-11-19
**Status**: Gap Analysis Complete
**Next**: Implementation Plan

---

## 🎯 Your Vision: Fully Automated Email Sequences

### What You Want

**Customer Journey**:
1. Lead signs up on website → **Webhook triggered automatically**
2. System receives webhook → **Schedules email sequence automatically**
3. Email 1 sent immediately → **Remaining 6 emails scheduled automatically**
4. Emails 2-7 sent on schedule (24-48 hour delays)
5. If lead books Cal.com meeting → **Pre-call prep sequence triggered**
6. After meeting → **Post-call follow-up sequence triggered**

**Key Requirement**: **ZERO MANUAL WORK** - Everything triggered by webhooks and scheduled automatically

---

## 📊 Current State Analysis

### What We Have ✅

**1. Email System (100% Ready)**:
- ✅ All 7 emails created and tested
- ✅ Template fetching from Notion working
- ✅ Variable substitution working (100%)
- ✅ Email delivery working via Resend
- ✅ Orchestrator script (`orchestrate_sequence.py`)

**2. Existing Webhook Server (`server.py`)**:
- ✅ FastAPI server with 2 webhook endpoints:
  - `POST /webhook/signup` - Handle new signups
  - `POST /webhook/assessment` - Handle completed assessments
- ✅ Background task processing
- ✅ CORS enabled for frontend integration
- ✅ Health check endpoint

**3. Existing Automation (BusinessX Campaign)**:
- ✅ Signup handler flow (creates contact in Notion)
- ✅ Assessment handler flow (triggers email sequence)
- ✅ Email sequence flow (sends emails with delays)

### What We DON'T Have ❌

**1. Christmas Campaign Webhook Integration**:
- ❌ No webhook endpoint for Christmas campaign signups
- ❌ No integration between webhook and orchestrator
- ❌ No automated scheduling (currently requires manual triggering)

**2. Background Job Scheduler**:
- ❌ No system to schedule emails in background
- ❌ No persistent queue for email sequences
- ❌ No retry logic for failed emails

**3. Cal.com Integration**:
- ❌ No Cal.com webhook endpoint
- ❌ No pre-call prep sequence
- ❌ No post-call follow-up sequence

---

## 🔍 The GAP: Manual vs. Automatic

### Current Flow (Manual)

```
Developer manually runs:
  python orchestrate_sequence.py --email customer@example.com --first-name Sarah ...

↓

Orchestrator sends Email 1 immediately

↓

Orchestrator sleeps for 24-48 hours (blocking process)

↓

Orchestrator sends Email 2, 3, 4, 5, 6, 7 sequentially

↓

Process ends
```

**Problems**:
- ❌ Requires manual execution for each customer
- ❌ Blocks process for entire sequence duration (11 days)
- ❌ Can't scale to multiple customers (one at a time)
- ❌ No webhook trigger
- ❌ No fault tolerance (if process dies, emails stop)

### Desired Flow (Automatic)

```
Website Form Submitted
    ↓
POST /webhook/christmas-signup
    ↓
Webhook validates & accepts (returns 202 immediately)
    ↓
Background Job Scheduler queues 7 emails with future send times:
  - Email 1: NOW (Day 0)
  - Email 2: Day 0 + 24h
  - Email 3: Day 0 + 72h (3 days)
  - Email 4: Day 0 + 120h (5 days)
  - Email 5: Day 0 + 168h (7 days)
  - Email 6: Day 0 + 216h (9 days)
  - Email 7: Day 0 + 264h (11 days)
    ↓
Background worker processes queue continuously:
  - Checks for emails due to send
  - Sends email via Resend
  - Logs to Notion Analytics
  - Retries on failure
```

**Benefits**:
- ✅ Fully automatic (no manual work)
- ✅ Scales to unlimited customers (non-blocking)
- ✅ Fault tolerant (queue persists)
- ✅ Webhook-driven (integrates with website)
- ✅ Retries failed sends

---

## 🏗️ Architecture: What We Need to Build

### Component 1: Christmas Campaign Webhook Endpoint

**File**: `server.py` (add new endpoint)

**Endpoint**: `POST /webhook/christmas-campaign-signup`

**Request Payload**:
```json
{
  "email": "customer@example.com",
  "first_name": "Sarah",
  "business_name": "Sarah's Salon",
  "assessment_score": 52,
  "assessment_data": {
    "red_systems": 2,
    "orange_systems": 1,
    "gps_score": 45,
    "money_score": 38,
    "weakest_system_1": "GPS",
    "weakest_system_2": "Money",
    "revenue_leak_total": 14700
  }
}
```

**What It Does**:
1. Validates request payload
2. Immediately returns 202 Accepted
3. Queues 7 emails in background job scheduler
4. Logs customer to Notion Contacts DB

**Status**: ❌ Not implemented

---

### Component 2: Background Job Scheduler

**Options** (choose one):

#### Option A: Prefect Cloud (Recommended for Enterprise)

**Pros**:
- ✅ Built-in scheduling
- ✅ Retry logic
- ✅ Dashboard UI
- ✅ Distributed execution

**Cons**:
- ❌ Requires Prefect Cloud account
- ❌ Monthly cost (~$0-50 depending on usage)
- ❌ More complex setup

**Implementation**:
- Use existing Prefect flows
- Deploy to Prefect Cloud
- Schedule via deployment config

---

#### Option B: Celery + Redis (Recommended for MVP)

**Pros**:
- ✅ Open source (free)
- ✅ Mature and battle-tested
- ✅ Scales well
- ✅ Self-hosted (full control)

**Cons**:
- ❌ Requires Redis server
- ❌ Need to set up workers
- ❌ More code to write

**Implementation**:
- Install Celery + Redis
- Create tasks for each email
- Schedule via Celery Beat

---

#### Option C: APScheduler (Simplest for MVP)

**Pros**:
- ✅ Pure Python (no external services)
- ✅ Lightweight
- ✅ Easy to set up
- ✅ Good for MVP

**Cons**:
- ❌ Not distributed (single process)
- ❌ Jobs lost if process dies
- ❌ Limited scalability

**Implementation**:
- Add APScheduler to server.py
- Schedule jobs in memory
- Persist jobs to database

---

#### Option D: Database-Backed Queue (RECOMMENDED ⭐)

**Pros**:
- ✅ No external dependencies (uses existing Notion DB)
- ✅ Fault tolerant (jobs persist in database)
- ✅ Simple to implement
- ✅ Easy to debug (view jobs in Notion)
- ✅ Can pause/resume sequences manually

**Cons**:
- ❌ Requires polling (check database every minute)
- ❌ Not real-time (up to 1-min delay)
- ❌ More Notion API calls

**Implementation**:
- Create "Email Queue" database in Notion
- Webhook adds 7 rows (one per email)
- Background worker polls queue every minute
- Sends emails when `scheduled_time <= now()`

**Schema**:
```
Email Queue Database:
- Email Address (email)
- First Name (text)
- Email Number (number) [1-7]
- Template ID (select) [christmas_email_1, ..., christmas_email_7]
- Scheduled Time (date)
- Status (select) [queued, sent, failed]
- Sent At (date)
- Error Message (text)
- Customer ID (relation to Contacts DB)
```

---

### Component 3: Background Worker Process

**File**: `campaigns/christmas_campaign/background_worker.py`

**What It Does**:
1. Runs continuously (infinite loop)
2. Every 1 minute:
   - Query Notion Email Queue for emails where:
     - Status = "queued"
     - Scheduled Time <= now()
   - Send each email via Resend
   - Update status to "sent" (or "failed" with error)
   - Log to Notion Analytics
3. Handles errors gracefully (retry logic)

**Running**:
```bash
# Development
python campaigns/christmas_campaign/background_worker.py

# Production (with systemd or supervisor)
systemctl start christmas-worker
```

**Status**: ❌ Not implemented

---

### Component 4: Cal.com Webhook Integration

**File**: `server.py` (add new endpoint)

**Endpoint**: `POST /webhook/calcom-booking`

**Request Payload** (from Cal.com):
```json
{
  "triggerEvent": "BOOKING_CREATED",
  "payload": {
    "booking": {
      "id": 12345,
      "startTime": "2025-11-25T14:00:00Z",
      "endTime": "2025-11-25T15:00:00Z",
      "attendees": [
        {
          "email": "customer@example.com",
          "name": "Sarah Johnson"
        }
      ]
    }
  }
}
```

**What It Does**:
1. Validates Cal.com webhook signature
2. Extracts customer email and meeting time
3. Queues pre-call prep emails:
   - Email 1: 3 days before meeting
   - Email 2: 1 day before meeting
   - Email 3: 2 hours before meeting
4. Updates Notion Contacts with meeting info

**Status**: ❌ Not implemented

---

## 📋 Implementation Plan

### Phase 1: Core Automation (Highest Priority) ⭐

**Goal**: Webhook → Automatic email sequence

**Tasks**:
1. Create Notion Email Queue database
2. Add Christmas campaign webhook endpoint
3. Implement background worker
4. Test end-to-end flow

**Time Estimate**: 4-6 hours

**Files to Create/Modify**:
- `server.py` - Add `/webhook/christmas-campaign-signup` endpoint
- `campaigns/christmas_campaign/background_worker.py` - New worker process
- `campaigns/christmas_campaign/tasks/queue_operations.py` - Notion queue management
- `.env` - Add `NOTION_EMAIL_QUEUE_DB_ID`

**Testing**:
```bash
# 1. Start background worker
python campaigns/christmas_campaign/background_worker.py

# 2. Send webhook (different terminal)
curl -X POST http://localhost:8000/webhook/christmas-campaign-signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "first_name": "Test",
    "assessment_score": 45
  }'

# 3. Check Notion Email Queue - should see 7 emails scheduled
# 4. Wait for worker to send Email 1 (should happen within 1 minute)
# 5. Verify Email 1 delivered via Resend dashboard
```

---

### Phase 2: Cal.com Integration (Medium Priority)

**Goal**: Meeting booking → Pre-call prep sequence

**Tasks**:
1. Set up Cal.com webhook
2. Add Cal.com webhook endpoint
3. Create pre-call prep email templates (3 emails)
4. Test booking → email flow

**Time Estimate**: 3-4 hours

**Files to Create/Modify**:
- `server.py` - Add `/webhook/calcom-booking` endpoint
- `campaigns/christmas_campaign/config/precall_email_templates.py` - 3 new templates
- `campaigns/christmas_campaign/scripts/seed_precall_templates.py` - Upload to Notion

---

### Phase 3: Post-Call Sequence (Lower Priority)

**Goal**: After diagnostic call → Customer portal + Phase 2B coaching

**Tasks**:
1. Create customer portal delivery flow
2. Create Phase 2B coaching sequence (52 emails over 12 weeks)
3. Webhook for marking diagnostic complete

**Time Estimate**: 8-10 hours

**Status**: Can wait until Phase 1+2 are working

---

## 🚀 Recommendation: Database-Backed Queue Approach

**Why This Approach**:

1. **No New Infrastructure** - Uses existing Notion (you already have it)
2. **Visual Debugging** - View queued emails in Notion database
3. **Fault Tolerant** - Jobs persist even if worker crashes
4. **Simple to Implement** - ~200 lines of Python code
5. **Manual Control** - Can pause/resume sequences via Notion
6. **Easy Monitoring** - See all scheduled emails at a glance

**Architecture**:

```
Website Form
    ↓
POST /webhook/christmas-campaign-signup
    ↓
Webhook Handler:
  - Validates payload
  - Creates customer in Notion Contacts
  - Adds 7 rows to Notion Email Queue:
    Row 1: Email 1, scheduled_time = NOW
    Row 2: Email 2, scheduled_time = NOW + 24h
    Row 3: Email 3, scheduled_time = NOW + 72h
    ...
    Row 7: Email 7, scheduled_time = NOW + 264h
  - Returns 202 Accepted
    ↓
Background Worker (runs continuously):
  Every 1 minute:
    - Query Email Queue WHERE status = "queued" AND scheduled_time <= now()
    - For each email:
      1. Fetch template from Notion Templates DB
      2. Substitute variables
      3. Send via Resend
      4. Update status to "sent" (log sent_at, email_id)
      5. Log to Analytics DB
    - Handle errors (update status to "failed", log error)
```

**Notion Databases Needed**:

1. **Email Queue** (new):
   - Stores scheduled emails
   - Worker reads from this

2. **Email Templates** (existing):
   - Already have 7 Christmas templates
   - Will add 3 pre-call prep templates later

3. **Contacts** (existing or new):
   - Customer information
   - Links to queued emails

4. **Email Analytics** (optional):
   - Logs all sent emails
   - Tracks opens/clicks (if Resend webhook added)

---

## 🎯 Next Steps (Your Decision)

### Option 1: Implement Phase 1 Now (Recommended) ⭐

**What**: Build the core automation (webhook → automatic scheduling)

**Time**: 4-6 hours

**Result**: Website form can trigger automatic 7-email sequence

**Action**: I'll start building now

---

### Option 2: Plan First, Then Implement

**What**: Review and approve this plan, then implement

**Time**: Review (30 min) + Implementation (4-6 hours)

**Result**: Same as Option 1, but with your input first

**Action**: Tell me any changes you want to the plan

---

### Option 3: Different Approach

**What**: You prefer a different architecture (Celery, Prefect Cloud, etc.)

**Time**: Varies by approach

**Result**: Different implementation

**Action**: Tell me which approach you prefer

---

## 📊 Comparison: Scheduling Approaches

| Approach | Setup Time | Infrastructure | Fault Tolerance | Scalability | Cost | Complexity |
|----------|------------|----------------|-----------------|-------------|------|------------|
| **Notion Queue** | ⭐⭐⭐⭐⭐ 1h | None (use existing) | ⭐⭐⭐⭐ High | ⭐⭐⭐ Medium | $0 | ⭐⭐⭐⭐ Low |
| **Celery + Redis** | ⭐⭐ 4h | Redis server | ⭐⭐⭐⭐⭐ Very High | ⭐⭐⭐⭐⭐ Very High | $5-10/mo | ⭐⭐ Medium |
| **Prefect Cloud** | ⭐⭐⭐ 2h | Prefect Cloud | ⭐⭐⭐⭐⭐ Very High | ⭐⭐⭐⭐⭐ Very High | $0-50/mo | ⭐⭐⭐ Medium |
| **APScheduler** | ⭐⭐⭐⭐ 1h | None | ⭐ Low | ⭐⭐ Low | $0 | ⭐⭐⭐⭐ Low |

**Recommendation**: Start with **Notion Queue** (fastest to implement, good enough for MVP), then migrate to Celery/Prefect later if needed.

---

## 🔥 Quick Start: Phase 1 Implementation

If you approve, here's what I'll build:

### 1. Create Notion Email Queue Database

**Fields**:
- Email Address (email)
- First Name (text)
- Email Number (number)
- Template ID (text)
- Scheduled Time (date)
- Status (select: queued/sent/failed)
- Sent At (date)
- Resend Email ID (text)
- Error Message (text)

### 2. Add Webhook Endpoint

**File**: `server.py`

```python
@app.post("/webhook/christmas-campaign-signup")
async def christmas_signup_webhook(request: ChristmasSignupRequest):
    # 1. Create customer in Notion Contacts
    # 2. Queue 7 emails in Email Queue DB
    # 3. Return 202 Accepted
```

### 3. Create Background Worker

**File**: `campaigns/christmas_campaign/background_worker.py`

```python
while True:
    # 1. Query Notion Email Queue for due emails
    # 2. Send each email via Resend
    # 3. Update status in Notion
    # 4. Sleep 60 seconds
```

### 4. Test End-to-End

```bash
# Terminal 1: Start worker
python campaigns/christmas_campaign/background_worker.py

# Terminal 2: Send webhook
curl -X POST http://localhost:8000/webhook/christmas-campaign-signup -d {...}

# Terminal 3: Check Notion Email Queue
# Should see 7 emails scheduled, Email 1 sent within 1 minute
```

---

## 💡 My Recommendation

**Start with Phase 1 using Notion Queue approach**:

**Reasons**:
1. Fastest to implement (4-6 hours)
2. No new infrastructure needed
3. Good enough for MVP (handles 100s of customers)
4. Easy to debug (visual queue in Notion)
5. Can migrate to Celery/Prefect later if needed

**What you'll get**:
- ✅ Webhook endpoint for website form
- ✅ Automatic email scheduling (no manual work)
- ✅ Fault-tolerant queue (jobs persist)
- ✅ Background worker (continuous processing)
- ✅ Ready for production

**Your call**: Should I proceed with Phase 1 implementation? 🚀

---

**Last Updated**: 2025-11-19
**Status**: Awaiting approval to proceed
**Recommended**: Phase 1 - Notion Queue Approach
