# Deployment Naming Convention

**Status**: ✅ Approved
**Version**: 1.0
**Date**: 2025-11-28
**Author**: Christmas Campaign Team

---

## Overview

This document defines the official deployment naming convention for Prefect flows across multiple marketing campaigns. The convention ensures:
- No name collisions between campaigns
- Clear identification of campaign, flow type, and version
- Future-proof for multiple campaigns running simultaneously
- Backward compatibility with existing deployments

---

## Naming Format

### Format: `{campaign}-{flow-type}-{variant}`

**Components**:
1. **campaign**: Campaign identifier (e.g., `christmas`, `businessx`, `summer2026`)
2. **flow-type**: Flow function (e.g., `signup`, `noshow-recovery`, `send-email`)
3. **variant**: Optional variant or version (e.g., `handler`, `v2`, `phase1`)

**Pattern**: `{campaign}-{flow-type}-{variant}`

---

## Campaign Identifiers

| Campaign | Identifier | Example |
|----------|-----------|---------|
| **Christmas 2025** | `christmas` | `christmas-signup-handler` |
| **BusinessX Canada Lead Nurture** | `businessx` | `businessx-signup-handler` |
| **Summer 2026 Campaign** | `summer2026` | `summer2026-signup-handler` |

**Rules**:
- Use lowercase
- No spaces (use hyphens)
- Keep it short (max 15 chars)
- Year suffix only if needed for disambiguation

---

## Flow Types

| Flow Type | Identifier | Description |
|-----------|-----------|-------------|
| **Signup Handler** | `signup-handler` | Initial opt-in, create contact + sequence |
| **No-Show Recovery** | `noshow-recovery-handler` | Calendly no-show event trigger |
| **Post-Call Follow-Up** | `postcall-maybe-handler` | "Maybe" prospect follow-up |
| **Onboarding** | `onboarding-handler` | New client onboarding sequence |
| **Send Email** | `send-email` | Individual email send (generic) |
| **Assessment Handler** | `assessment-handler` | Assessment completion trigger |
| **Email Sequence** | `email-sequence` | Multi-email orchestrator |

**Rules**:
- Use descriptive names
- Hyphenated (no underscores)
- Suffix with `-handler` for webhook triggers
- Avoid generic names like `flow1`, `test`

---

## Current Deployments (Christmas 2025)

| Deployment Name | Deployment ID | Status | Notes |
|-----------------|---------------|--------|-------|
| `christmas-signup-handler` | `1ae3a3b3-e076-49c5-9b08-9c176aa47aa0` | ✅ Active | Handles opt-in + assessment completion |
| `christmas-noshow-recovery-handler` | `3400e152-1cbe-4d8f-9f8a-0dd73569afa1` | ✅ Active | Handles Calendly no-show events |
| `christmas-postcall-maybe-handler` | `ed929cd9-34b3-4655-b128-1a1e08a59cbd` | ✅ Active | Handles "maybe" prospects |
| `christmas-onboarding-handler` | `db47b919-1e55-4de2-b52c-6e2b0b2a2285` | ✅ Active | Handles new client onboarding |
| `christmas-send-email` | *(deployment ID)* | ✅ Active | Generic email sender for all sequences |

**Decision**: Current naming is CORRECT - no renaming needed.

---

## Multi-Campaign Scenarios

### Scenario 1: Same Flow Type, Different Campaigns

**Example**: Signup handlers for multiple campaigns

```
christmas-signup-handler          ← Christmas 2025
businessx-signup-handler          ← BusinessX Canada
summer2026-signup-handler         ← Summer 2026
```

**Result**: ✅ No collision - campaign prefix differentiates them

---

### Scenario 2: Multiple Versions of Same Campaign

**Example**: Christmas campaign runs annually

**Option A: Year Suffix (Recommended)**
```
christmas2025-signup-handler      ← Christmas 2025
christmas2026-signup-handler      ← Christmas 2026
```

**Option B: Version Suffix**
```
christmas-signup-handler          ← Current year
christmas-signup-handler-v2       ← Next year
```

**Decision**: Use Option A (year suffix) for annual campaigns.

---

### Scenario 3: A/B Testing Variants

**Example**: Testing different email timing strategies

```
christmas-signup-handler          ← Control (5-day sequence)
christmas-signup-handler-fast     ← Variant A (3-day sequence)
christmas-signup-handler-slow     ← Variant B (7-day sequence)
```

**Rules**:
- Base deployment name is the control
- Add descriptive suffix for variants
- Document in deployment description

---

## Naming Anti-Patterns

❌ **DON'T DO THIS**:
```
signup-handler                    ← Too generic (which campaign?)
christmas_signup_handler          ← Use hyphens, not underscores
Christmas-Signup-Handler          ← Use lowercase only
christmas-flow-1                  ← Non-descriptive name
xmas-signup                       ← Ambiguous abbreviation
```

✅ **DO THIS**:
```
christmas-signup-handler          ← Clear, descriptive, follows pattern
businessx-assessment-handler      ← Campaign + flow type
summer2026-email-sequence         ← Year suffix for clarity
```

---

## Implementation Rules

### 1. Deployment Name = Flow Name (Prefect Requirement)

**Prefect requires**: `deployment_name` must match `flow_name`

```python
# ✅ CORRECT: Deployment name matches flow name
@flow(name="christmas-signup-handler")
def signup_handler_flow(...):
    pass

# Deployment
deployment = await flow.to_deployment(
    name="christmas-signup-handler",  # Matches flow name
    ...
)
```

**Result**: Deployment ID = `christmas-signup-handler/christmas-signup-handler`

---

### 2. Flow Name in Code

**File**: `campaigns/christmas_campaign/flows/signup_handler.py`

```python
@flow(
    name="christmas-signup-handler",  # ← Use deployment naming convention
    description="Handle Christmas campaign signup and start nurture sequence",
    log_prints=True
)
def signup_handler_flow(...):
    pass
```

**Rules**:
- Flow `name` parameter = deployment name
- Flow function name can be different (e.g., `signup_handler_flow`)
- Description should be campaign-specific

---

### 3. Reading Deployment by Name (Prefect API)

**Pattern**: `{flow_name}/{deployment_name}`

```python
deployment = await client.read_deployment_by_name(
    "christmas-send-email/christmas-send-email"
)
```

**Format**: `{flow_name}/{deployment_name}`

---

## Migration Strategy (If Needed)

### Step 1: Evaluate Risk

**Questions**:
1. Are current deployments active in production?
2. Are webhooks hardcoded with deployment names?
3. Is renaming worth the migration risk?

**Christmas Campaign Assessment**:
- ✅ Current naming follows convention
- ✅ No collision risks identified
- ❌ Renaming NOT needed

---

### Step 2: Create New Deployments (If Renaming)

**Process**:
```python
# 1. Deploy new deployment with new name
await flow.to_deployment(
    name="christmas2025-signup-handler",  # New name
    ...
)

# 2. Test new deployment
prefect deployment run christmas2025-signup-handler

# 3. Update webhooks to use new deployment

# 4. Deprecate old deployment (keep for 30 days)
```

---

### Step 3: Deprecation Timeline

**Week 1-2**:
- Deploy new deployments
- Update webhook URLs
- Test end-to-end

**Week 3-4**:
- Monitor logs for old deployment usage
- Update documentation
- Add deprecation warnings

**Week 5+**:
- Delete old deployments
- Clean up code references

---

## Documentation Requirements

**ARCHITECTURE.md Updates**:

Each campaign's `ARCHITECTURE.md` must include:

```markdown
## Deployment Naming

| Flow | Deployment Name | Description |
|------|-----------------|-------------|
| Signup Handler | `christmas-signup-handler` | Handles opt-in events |
| No-Show Recovery | `christmas-noshow-recovery-handler` | Handles no-show events |
| Post-Call Follow-Up | `christmas-postcall-maybe-handler` | Handles "maybe" prospects |
| Onboarding | `christmas-onboarding-handler` | Handles new client onboarding |
| Send Email | `christmas-send-email` | Generic email sender |

**Convention**: `{campaign}-{flow-type}-{variant}`
```

---

## Future Campaigns Checklist

When launching a new campaign:

1. [ ] Choose campaign identifier (e.g., `summer2026`)
2. [ ] List all flow types needed (signup, noshow, etc.)
3. [ ] Generate deployment names using convention
4. [ ] Check for name collisions with existing deployments
5. [ ] Update flow `name` parameters in code
6. [ ] Deploy to Prefect
7. [ ] Update campaign ARCHITECTURE.md
8. [ ] Test webhook → deployment mapping

---

## Examples: Other Campaigns

### BusinessX Canada Lead Nurture Campaign

```
businessx-signup-handler          ← Initial signup
businessx-assessment-handler      ← Assessment completion
businessx-email-sequence          ← 5-email nurture sequence
businessx-send-email              ← Individual email sender
```

**File**: `campaigns/businessx_canada_lead_nurture/flows/signup_handler.py`

```python
@flow(name="businessx-signup-handler")
def signup_handler_flow(...):
    pass
```

---

### Summer 2026 Promo Campaign

```
summer2026-signup-handler         ← Promo opt-in
summer2026-early-bird-reminder    ← Early bird deadline reminder
summer2026-last-chance            ← Last chance email
summer2026-send-email             ← Generic email sender
```

---

## Decision Summary

**For Christmas 2025 Campaign**:
- ✅ Current naming follows convention
- ✅ No renaming needed
- ✅ Document in ARCHITECTURE.md

**For Future Campaigns**:
- ✅ Use `{campaign}-{flow-type}-{variant}` format
- ✅ Add year suffix for annual campaigns
- ✅ Check for collisions before deploying

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-28 | Christmas Team | Initial convention defined |

---

**Approved by**: Christmas Campaign Team
**Next Review**: Before next campaign launch
