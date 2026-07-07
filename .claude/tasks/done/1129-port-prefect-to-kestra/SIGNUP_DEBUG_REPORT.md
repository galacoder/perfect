# Signup Handler Flow Debugging Report

**Date**: 2025-11-30
**Flow**: christmas/signup-handler
**Issue**: Flow execution failing with variable evaluation errors

---

## Root Cause Analysis

### Primary Issue: Missing Environment Variables

The Kestra deployment is missing required environment variables that the flow needs to access Notion API:

**Missing Environment Variables:**
- `SECRET_NOTION_TOKEN` - Notion integration token
- `SECRET_NOTION_CONTACTS_DB_ID` - Notion Contacts database ID
- `SECRET_NOTION_TEMPLATES_DB_ID` - Notion Templates database ID (for other flows)
- `SECRET_RESEND_API_KEY` - Resend email API key (for other flows)

### Error Progression

#### Error 1: Invalid Secret Function Call (Fixed)
**Original Code:**
```yaml
uri: "https://api.notion.com/v1/databases/{{ secret('SECRET_NOTION_CONTACTS_DB_ID') }}/query"
Authorization: "Bearer {{ secret('SECRET_NOTION_TOKEN') }}"
```

**Problem:**
- Used `secret()` function which requires Kestra Enterprise Edition
- Open-source Kestra doesn't support this function

**Fix Applied:**
```yaml
uri: "https://api.notion.com/v1/databases/{{ envs.SECRET_NOTION_CONTACTS_DB_ID }}/query"
Authorization: "Bearer {{ envs.SECRET_NOTION_TOKEN }}"
```

**Status:** ✅ Fixed (changed from `secret()` to `envs.` pattern)

#### Error 2: Invalid Error Handler Variables (Fixed)
**Original Code:**
```yaml
errors:
  - id: log_error
    message: "❌ Error processing signup for {{ inputs.email }}: {{ error.message }}"
```

**Problem:**
- `inputs.email` not available in error handler context
- `error.message` not available in Kestra's error context

**Fix Applied:**
```yaml
errors:
  - id: log_error
    message: "❌ Error processing signup - check execution logs for details"
```

**Status:** ✅ Fixed (simplified error message)

#### Error 3: Notion Property Name Mismatch (Fixed)
**Original Code:**
```yaml
"filter": {
  "property": "email",
  "email": {
    "equals": "{{ inputs.email }}"
  }
}
```

**Problem:**
- Notion database uses capital "Email", not lowercase "email"

**Fix Applied:**
```yaml
"filter": {
  "property": "Email",
  "email": {
    "equals": "{{ inputs.email }}"
  }
}
```

**Status:** ✅ Fixed (capitalized property name)

#### Error 4: Missing Environment Variables (BLOCKER)
**Current Error:**
```
io.kestra.core.exceptions.IllegalVariableEvaluationException:
Unable to find 'SECRET_NOTION_CONTACTS_DB_ID' used in the expression
```

**Problem:**
- Environment variables are not configured in the Kestra deployment
- Docker Compose expects Dokploy to inject these variables
- Variables are not currently set in Dokploy environment

**Status:** ❌ BLOCKER - Requires deployment configuration

---

## Fixes Applied

### 1. Updated signup-handler.yml (Revision 3)

**Changes:**
1. ✅ Changed `secret()` → `envs.` for all credential access
2. ✅ Fixed Notion property name: `email` → `Email`
3. ✅ Simplified error handler message
4. ✅ Maintained all flow logic and structure

**Flow Status:** Code is correct, uploaded to Kestra as revision 3

### 2. Similar Fixes Needed for Other Flows

The following flows also need the same `secret()` → `envs.` conversion:
- assessment-handler.yml
- noshow-recovery-handler.yml
- postcall-maybe-handler.yml
- onboarding-handler.yml
- send-email.yml

**Status:** Modified but not yet uploaded

---

## Required Actions

### CRITICAL: Configure Environment Variables in Dokploy

The Kestra deployment needs these environment variables set in Dokploy:

```bash
# Notion Configuration
SECRET_NOTION_TOKEN=ntn_xxxxx
SECRET_NOTION_CONTACTS_DB_ID=xxxxx
SECRET_NOTION_TEMPLATES_DB_ID=xxxxx

# Resend Email API
SECRET_RESEND_API_KEY=re_xxxxx

# Testing Mode
SECRET_TESTING_MODE=false

# Kestra Encryption
KESTRA_ENCRYPTION_SECRET_KEY=your-secure-key

# PostgreSQL
POSTGRES_PASSWORD=your-secure-password
```

**Where to set:**
1. Log into Dokploy dashboard
2. Navigate to Kestra application
3. Go to Environment Variables section
4. Add all SECRET_* variables listed above
5. Restart Kestra container

**Verification:**
After setting variables, test with:
```bash
curl -X POST \
  -u "galacoder69@gmail.com:Kestra2025Admin!" \
  -H "Content-Type: application/json" \
  -d '{"email":"lengobaosang@gmail.com","first_name":"Test","business_name":"Test Corp"}' \
  "https://kestra.galatek.dev/api/v1/executions/webhook/christmas/signup-handler/christmas-signup-webhook"
```

---

## Test Results

### Before Fix
- ❌ Flow failed with: "Cannot find secret for key 'SECRET_NOTION_CONTACTS_DB_ID'"
- ❌ Error handler also failed: "Unable to find 'inputs' used in expression"

### After Code Fix
- ✅ Flow code syntax correct
- ✅ Error handler works correctly
- ❌ Still fails: "Unable to find 'SECRET_NOTION_CONTACTS_DB_ID' environment variable"

### After Environment Variables (Expected)
- ✅ Flow executes successfully
- ✅ Contact created/updated in Notion
- ✅ No emails sent (as designed)

---

## Execution Logs Analysis

**Latest Execution:** `3oXpMCv0hPMVe5A7OZydYW`
**Revision:** 3
**Status:** FAILED
**Duration:** 1.08s

**Error Stack:**
```
Unable to find 'SECRET_NOTION_CONTACTS_DB_ID' used in the expression
'https://api.notion.com/v1/databases/{{ envs.SECRET_NOTION_CONTACTS_DB_ID }}/query'
at line 1
```

**Conclusion:** Environment variables are not available in Kestra runtime

---

## Docker Compose Configuration

**File:** `/Users/sangle/Dev/action/projects/kestra-automation/docker-compose.kestra.dokploy.yml`

**Relevant Section (Lines 110-118):**
```yaml
# Secret environment variables from Dokploy
# These will be injected by Dokploy at runtime:
# - SECRET_NOTION_TOKEN
# - SECRET_NOTION_CONTACTS_DB_ID
# - SECRET_NOTION_TEMPLATES_DB_ID
# - SECRET_RESEND_API_KEY
# - SECRET_TESTING_MODE
# - KESTRA_ENCRYPTION_SECRET_KEY
# - POSTGRES_PASSWORD
```

**Issue:** These are documented but not actually injected by Dokploy yet.

---

## Next Steps

### Immediate (Required to Unblock)
1. ⚠️ **Configure environment variables in Dokploy** (see Required Actions section)
2. ⚠️ **Restart Kestra container** after setting variables
3. ✅ Re-test signup webhook

### Follow-up (After Unblocking)
1. Apply same fixes to all other handler flows
2. Upload all fixed flows to Kestra
3. Run full E2E test suite
4. Update feature_list.json with results

---

## Summary

**Root Cause:** Missing environment variables in Kestra deployment

**Fixes Applied:**
- ✅ Changed `secret()` to `envs.` pattern
- ✅ Fixed Notion property name capitalization
- ✅ Simplified error handler

**Blocker:** Environment variables not configured in Dokploy

**Resolution:** Set environment variables in Dokploy UI, restart container, re-test

**ETA to Working:** 5-10 minutes after environment variables are configured
