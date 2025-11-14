# Migration Guide: Campaign-Based Structure

**Date**: November 14, 2025
**Status**: ✅ Complete
**Breaking Changes**: ❌ None (backward compatibility maintained)

---

## Overview

This guide documents the migration from a flat workflow structure to a campaign-based organization system for Prefect workflows.

### What Changed?

**Before** (Flat structure):
```
/flows/signup_handler.py
/flows/assessment_handler.py
/flows/email_sequence.py
/tasks/notion_operations.py
/tasks/resend_operations.py
/tasks/routing.py
/tasks/template_operations.py
```

**After** (Campaign-based structure):
```
/campaigns/businessx_canada_lead_nurture/
  ├── flows/
  │   ├── signup_handler.py
  │   ├── assessment_handler.py
  │   └── email_sequence.py
  ├── tasks/
  │   ├── notion_operations.py
  │   ├── resend_operations.py
  │   ├── routing.py
  │   └── template_operations.py
  ├── tests/
  │   ├── test_notion_operations.py
  │   ├── test_resend_operations.py
  │   └── test_routing.py
  ├── diagrams/
  │   ├── CAMPAIGN_OVERVIEW.txt
  │   ├── SIGNUP_HANDLER.txt
  │   ├── ASSESSMENT_HANDLER.txt
  │   └── EMAIL_SEQUENCE.txt
  ├── README.md
  └── ARCHITECTURE.md
```

---

## Why Campaign-Based Structure?

### Problem with Flat Structure

❌ **Namespace Conflicts**: Multiple campaigns → same file names
❌ **Poor Organization**: Hard to find campaign-specific code
❌ **Team Collaboration**: Unclear ownership and responsibility
❌ **Scalability**: Difficult to add new campaigns without conflicts

### Benefits of Campaign-Based Structure

✅ **Scalability**: Add new campaigns without file conflicts
✅ **Self-Documenting**: Each campaign has its own README and diagrams
✅ **Team Ownership**: Clear who owns what campaign
✅ **Better Testing**: Campaign-specific test files
✅ **Easier Maintenance**: All related code in one place

---

## Migration Details

### Phase 1: Scaffolding (Wave 1)

**Created**:
- `/campaigns/businessx_canada_lead_nurture/` directory structure
- `README.md` - Campaign overview
- `ARCHITECTURE.md` - Technical details

**Duration**: 15 minutes
**Commit**: `c638734`

### Phase 2: Documentation (Wave 2)

**Created**:
- 4 ASCII workflow diagrams:
  - `CAMPAIGN_OVERVIEW.txt` - High-level architecture
  - `SIGNUP_HANDLER.txt` - Signup flow
  - `ASSESSMENT_HANDLER.txt` - Assessment flow
  - `EMAIL_SEQUENCE.txt` - Complete 5-email sequence

**Why ASCII?**: No external dependencies, easy to version control, viewable in any editor

**Duration**: 15 minutes
**Commit**: `154755f`

### Phase 3: File Migration (Wave 3)

**Migrated**:
- 3 flow files (`flows/*.py` → `campaigns/.../flows/*.py`)
- 4 task modules (`tasks/*.py` → `campaigns/.../tasks/*.py`)
- 3 test files (`tests/*.py` → `campaigns/.../tests/*.py`)

**Backward Compatibility**:
- Created deprecation shims in original locations (`/flows/`, `/tasks/`)
- Old imports still work with deprecation warnings
- Example shim:
  ```python
  import warnings
  from campaigns.businessx_canada_lead_nurture.flows.signup_handler import *

  warnings.warn(
      "flows.signup_handler is deprecated. "
      "Use campaigns.businessx_canada_lead_nurture.flows.signup_handler instead.",
      DeprecationWarning,
      stacklevel=2
  )
  ```

**Duration**: 30 minutes
**Commit**: `29a8b38`

### Phase 4: Update References (Wave 4)

**Updated**:
- `server.py` - FastAPI webhook server imports
- `flows/deploy.py` - Prefect deployment config
- `flows/__init__.py` - Backward compatibility exports
- `scripts/seed_templates.py` - Template seeding script
- `test_integration_e2e.py` - E2E integration tests
- `test_flows_dry_run.py` - Dry-run structure tests
- `tests/test_template_operations.py` - Template operation unit tests

**Import Changes**:
```python
# OLD
from flows.signup_handler import signup_handler_flow
from tasks.notion_operations import create_contact

# NEW
from campaigns.businessx_canada_lead_nurture.flows.signup_handler import signup_handler_flow
from campaigns.businessx_canada_lead_nurture.tasks.notion_operations import create_contact
```

**Duration**: 30 minutes
**Commit**: `bd751ec`

### Phase 5: Cleanup & Polish (Wave 5)

**Updated**:
- `README.md` - Documented new structure
- Created `MIGRATION_GUIDE.md` (this file)

**Duration**: 15 minutes
**Commit**: (final wave)

---

## Updating Your Code

### If You Have Old Imports

**Option 1: Use Compatibility Shims (Quick Fix)**

Old imports still work thanks to compatibility shims:

```python
# This still works (with deprecation warning)
from flows.signup_handler import signup_handler_flow
from tasks.notion_operations import create_contact
```

**Option 2: Update to New Imports (Recommended)**

Update your imports to use the new structure:

```python
# Recommended
from campaigns.businessx_canada_lead_nurture.flows.signup_handler import signup_handler_flow
from campaigns.businessx_canada_lead_nurture.tasks.notion_operations import create_contact
```

### Search & Replace Guide

If you have custom scripts or external integrations, use these patterns:

```bash
# Find old imports
grep -r "from flows\." .
grep -r "from tasks\." .

# Replace in your editor or use sed:
sed -i '' 's/from flows\./from campaigns.businessx_canada_lead_nurture.flows./g' your_file.py
sed -i '' 's/from tasks\./from campaigns.businessx_canada_lead_nurture.tasks./g' your_file.py
```

---

## Testing After Migration

### 1. Dry-Run Validation

```bash
python test_flows_dry_run.py
```

**Expected output**:
```
🧪 Testing Prefect flows (dry-run)...

1️⃣ Testing flow imports...
   ✅ All flows imported successfully

2️⃣ Verifying flow structure...
   ✅ signup_handler_flow: signup-handler
   ✅ assessment_handler_flow: assessment-handler
   ✅ email_sequence_flow: email-sequence-5-emails

... (all tests pass)

🎉 All dry-run tests passed!
```

### 2. Integration Tests

```bash
python test_integration_e2e.py --mode mock
```

**Expected output**:
```
🧪 End-to-End Integration Test
============================================================

1️⃣ Testing Signup Flow
   ✅ Signup flow passed (mocked)

2️⃣ Testing Assessment Flow
   ✅ Assessment flow passed (mocked)

3️⃣ Testing Email Sequence Flow
   ✅ Email sequence flow passed (mocked)

✅ Integration Test Suite Complete
```

### 3. Unit Tests

```bash
pytest campaigns/businessx_canada_lead_nurture/tests/ -v
```

**Expected**: All 93 tests pass

---

## What to Do Next

### Immediate Actions

✅ **No action required** - backward compatibility maintained
✅ All existing code continues to work with deprecation warnings

### Recommended Actions (Optional)

1. **Update your imports** to use new campaign-based paths
2. **Review diagrams** in `campaigns/businessx_canada_lead_nurture/diagrams/`
3. **Read campaign documentation**:
   - `campaigns/businessx_canada_lead_nurture/README.md`
   - `campaigns/businessx_canada_lead_nurture/ARCHITECTURE.md`

### Future Actions (When Ready)

When you're confident everything works with the new structure:

1. Remove compatibility shims:
   ```bash
   rm -rf flows/signup_handler.py
   rm -rf flows/assessment_handler.py
   rm -rf flows/email_sequence.py
   rm -rf tasks/notion_operations.py
   rm -rf tasks/resend_operations.py
   rm -rf tasks/routing.py
   rm -rf tasks/template_operations.py
   ```

2. Remove old test files:
   ```bash
   rm -rf tests/test_notion_operations.py
   rm -rf tests/test_resend_operations.py
   rm -rf tests/test_routing.py
   ```

3. Clean up `flows/__init__.py` and `tasks/__init__.py`

---

## Adding New Campaigns

### Template Structure

```bash
campaigns/
├── businessx_canada_lead_nurture/  # Existing campaign
└── your_new_campaign/               # New campaign
    ├── README.md                    # Campaign overview
    ├── ARCHITECTURE.md              # Technical architecture
    ├── flows/                       # Prefect flows
    ├── tasks/                       # Prefect tasks
    ├── tests/                       # Unit tests
    └── diagrams/                    # ASCII workflow diagrams
```

### Steps to Create New Campaign

1. **Create directory structure**:
   ```bash
   mkdir -p campaigns/your_new_campaign/{flows,tasks,tests,diagrams}
   touch campaigns/your_new_campaign/{README.md,ARCHITECTURE.md}
   ```

2. **Copy template files** from `businessx_canada_lead_nurture/`

3. **Update imports**:
   ```python
   from campaigns.your_new_campaign.flows.your_flow import your_flow
   from campaigns.your_new_campaign.tasks.your_task import your_task
   ```

4. **Create ASCII diagrams** documenting your workflow

5. **Write tests** in `campaigns/your_new_campaign/tests/`

---

## Troubleshooting

### Deprecation Warnings

**Symptom**:
```
DeprecationWarning: flows.signup_handler is deprecated.
Use campaigns.businessx_canada_lead_nurture.flows.signup_handler instead.
```

**Solution**: Update your imports to use the new campaign-based structure (see "Updating Your Code" section above).

### Import Errors

**Symptom**:
```
ModuleNotFoundError: No module named 'campaigns'
```

**Solution**: Ensure you're running from the project root directory:
```bash
cd /path/to/perfect/
python your_script.py
```

### Test Failures

**Symptom**: Tests fail after migration

**Solution**:
1. Check that all imports are updated to new paths
2. Verify mock patch paths in tests:
   ```python
   # OLD
   with patch('tasks.notion_operations.notion') as mock:

   # NEW
   with patch('campaigns.businessx_canada_lead_nurture.tasks.notion_operations.notion') as mock:
   ```

---

## Summary

✅ **Migration completed successfully**
✅ **Zero breaking changes** (backward compatibility maintained)
✅ **All tests passing** (93 unit tests + integration tests)
✅ **Documentation updated** (README, diagrams, architecture)
✅ **Ready for production** (no action required)

### Key Takeaways

1. **Backward Compatible**: Old imports still work with deprecation warnings
2. **Campaign-Based**: Better organization for multiple campaigns
3. **Self-Documenting**: Each campaign has README, ARCHITECTURE, and diagrams
4. **Scalable**: Easy to add new campaigns without conflicts
5. **Tested**: All tests pass, production-ready

---

**Questions?** See [README.md](README.md) or contact sang@sanglescalinglabs.com

**Last Updated**: November 14, 2025
