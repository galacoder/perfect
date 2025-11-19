# Galatek.dev Deployment Plan - Christmas Campaign

**Server**: Existing infrastructure (prefect.galatek.dev)
**Domain**: galatek.dev (Prefect UI already deployed)
**Status**: 🚀 Ready to deploy
**Date**: 2025-11-19

---

## Key Discovery: Existing Prefect Server

You already have **Prefect deployed at `https://prefect.galatek.dev/`**!

This changes our deployment approach:
- ✅ Prefect Server already running
- ✅ Domain infrastructure exists
- ✅ SSL certificates likely already configured
- ✅ Server access already established

**New approach**: Deploy webhook server to same infrastructure, connect to existing Prefect.

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Galatek.dev Infrastructure                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  prefect.galatek.dev (existing)                                 │
│       │                                                          │
│       ├──► Prefect Server UI (port 4200)                        │
│       ├──► Prefect Worker (running flows)                       │
│       └──► PostgreSQL Database                                   │
│                                                                   │
│  webhook.galatek.dev (new - to be deployed)                     │
│       │                                                          │
│       ├──► FastAPI Webhook Server (port 8000)                   │
│       │    - POST /webhook/christmas-signup                     │
│       │    - POST /webhook/calcom-booking                       │
│       │    - GET /health                                        │
│       │                                                          │
│       └──► Connects to existing Prefect Server via API         │
│                                                                   │
│  Website (Vercel)                                                │
│       │                                                          │
│       └──► POST to webhook.galatek.dev/webhook/christmas-signup │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Questions About Your Setup

Before we proceed, I need to understand your existing infrastructure:

### 1. Server Access

**Question**: How is Prefect currently deployed?
- [ ] Docker container?
- [ ] Systemd service?
- [ ] Cloud-managed (Prefect Cloud)?
- [ ] Other?

**I need**:
- SSH access to the server running Prefect
- Username and server IP/hostname
- Location where Prefect is installed

### 2. Prefect Configuration

**Question**: Where is Prefect Server running?
- [ ] Same server as where we'll deploy webhook?
- [ ] Different server (need to connect via network)?

**I need**:
- Prefect API URL (e.g., `http://localhost:4200/api` or `https://prefect.galatek.dev/api`)
- Can webhook server reach Prefect API? (same network? firewall rules?)

### 3. Domain Setup

**Current**:
- ✅ `prefect.galatek.dev` → Prefect UI

**Need to add**:
- ⏳ `webhook.galatek.dev` → FastAPI webhook server

**Question**: Do you have DNS access to add subdomain?
- [ ] Yes, I can add A record or CNAME
- [ ] Yes, but need help configuring
- [ ] No, need someone else to do it

### 4. SSL Certificates

**Question**: How is SSL managed for `prefect.galatek.dev`?
- [ ] Certbot (Let's Encrypt)
- [ ] Cloudflare (proxy + SSL)
- [ ] Other provider?

**We'll need**: Same SSL setup for `webhook.galatek.dev`

### 5. Nginx/Reverse Proxy

**Question**: Is there Nginx or other reverse proxy?
- [ ] Yes, Nginx
- [ ] Yes, Caddy/Traefik/other
- [ ] No, direct access

**We'll need**: Configure reverse proxy for webhook server

---

## Simplified Deployment Options

Based on your existing setup, here are 3 deployment approaches:

### Option A: Same Server as Prefect (Recommended)

**If webhook server can run on same machine as Prefect**:

**Pros**:
- ✅ No network configuration needed
- ✅ Prefect API accessible via localhost
- ✅ SSL already configured
- ✅ Fastest deployment

**Steps**:
1. Deploy webhook server to same server (systemd service)
2. Configure Nginx to route `webhook.galatek.dev` to port 8000
3. Deploy Prefect flows
4. Test and monitor

**Time**: 1-2 hours

---

### Option B: Separate Server (If Needed)

**If webhook must run on different machine**:

**Pros**:
- ✅ Separation of concerns
- ✅ Dedicated resources for webhook

**Cons**:
- ⚠️ Need network access between servers
- ⚠️ More complex configuration

**Steps**:
1. Provision new server OR use existing different server
2. Deploy webhook server
3. Configure to connect to Prefect at `https://prefect.galatek.dev/api`
4. Configure DNS and SSL
5. Deploy flows
6. Test and monitor

**Time**: 2-3 hours

---

### Option C: Docker Deployment (If Using Docker)

**If Prefect is containerized**:

**Pros**:
- ✅ Consistent with existing setup
- ✅ Easy to manage with docker-compose

**Cons**:
- ⚠️ Requires Docker knowledge
- ⚠️ Need to create Dockerfile

**Steps**:
1. Create Dockerfile for webhook server
2. Add to existing docker-compose.yml
3. Deploy flows to Prefect container
4. Configure reverse proxy
5. Test and monitor

**Time**: 1-2 hours

---

## What I Need to Proceed

Please provide:

### Critical Information

**1. Server Access**:
```bash
# SSH access
ssh username@server-ip-or-hostname

# OR provide:
- Server IP/hostname: ?
- SSH username: ?
- SSH key or password access?
```

**2. Prefect API Endpoint**:
```bash
# What's the Prefect API URL?
# Options:
- http://localhost:4200/api (if same server)
- https://prefect.galatek.dev/api (if remote)
- Other: ?
```

**3. Current Setup**:
- How is Prefect deployed? (Docker/systemd/cloud)
- Where is the code located on server? (/opt/prefect?, /home/user/?, other?)
- Is there a reverse proxy? (Nginx/Caddy/other?)

**4. DNS Access**:
- Can you add DNS record for `webhook.galatek.dev`?
- DNS provider? (Cloudflare/Namecheap/other?)

### Optional But Helpful

**5. Deployment Preference**:
- Same server as Prefect (Option A)?
- Different server (Option B)?
- Docker (Option C)?

**6. Discord Webhook URL**:
- For CRITICAL segment notifications
- Format: `https://discord.com/api/webhooks/...`

---

## Environment Variables Summary

**We'll use from your local `.env`**:
```bash
NOTION_TOKEN=secret_eXSRJe3C3J2CAgE4AjG25HzplCiXVIIxFwO2AsQVysM
NOTION_BUSINESSX_DB_ID=199c97e4c0a045278086941b7cca62f1
NOTION_EMAIL_SEQUENCE_DB_ID=576de1aa-6064-4201-a5e6-623b7f2be79a
NOTION_EMAIL_TEMPLATES_DB_ID=2ab7c374-1115-8115-932c-ca6789c5b87b
RESEND_API_KEY=re_e5qfBYsX_B9wNs12TKG82XoSi79kuMyWe
RESEND_FROM_EMAIL=value@galatek.dev
TESTING_MODE=true  # Start with testing mode
```

**We'll add**:
```bash
PREFECT_API_URL=[your-prefect-api-url]  # Need this!
DISCORD_WEBHOOK_URL=[your-discord-webhook]  # Optional
```

---

## Quick Assessment Questions

To proceed efficiently, please answer:

1. **Can you SSH to the server running Prefect?**
   - [ ] Yes, I have access
   - [ ] No, but I can get it
   - [ ] No, someone else manages it

2. **Is Prefect running on a server you control?**
   - [ ] Yes, my server
   - [ ] Yes, company server (I have access)
   - [ ] No, using Prefect Cloud

3. **Can webhook server run on same machine as Prefect?**
   - [ ] Yes (recommended)
   - [ ] No, must be separate
   - [ ] Not sure

4. **Can you add DNS record for `webhook.galatek.dev`?**
   - [ ] Yes, I can do it now
   - [ ] Yes, but need help
   - [ ] No, need to contact someone

5. **What's your preferred deployment method?**
   - [ ] Option A: Same server as Prefect
   - [ ] Option B: Separate server
   - [ ] Option C: Docker
   - [ ] Not sure, recommend best option

---

## Next Steps Based on Your Answers

**If you have SSH access + same server**:
→ We can deploy in 1-2 hours using Option A

**If you have SSH access + separate server**:
→ We can deploy in 2-3 hours using Option B

**If no direct access**:
→ I can create deployment package for your team to install

**If using Prefect Cloud (not self-hosted)**:
→ Different approach needed (connect to cloud API)

---

## Recommendation

**Based on having `prefect.galatek.dev` already working**, I recommend:

**Option A: Deploy webhook to same server**
1. ✅ Fastest deployment
2. ✅ No network complexity
3. ✅ SSL already configured
4. ✅ Can reuse existing infrastructure

**Please provide**:
- SSH access details
- Confirm Prefect is self-hosted (not Prefect Cloud)
- Confirm you can add `webhook.galatek.dev` DNS record

---

## I'm Ready to Deploy!

Just need the answers to the questions above, and we can start deployment immediately.

**Quick response format**:
```
1. SSH: yes, username@server-ip
2. Prefect API: http://localhost:4200/api (same server)
3. Setup: systemd service, code in /opt/prefect
4. DNS: yes, using Cloudflare
5. Preference: Option A (same server)
6. Discord: [webhook URL or "skip for now"]
```

**What can you tell me about your current setup?**
