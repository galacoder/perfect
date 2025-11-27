# Task: Fix AsyncIO, Remove Hardcoded Templates, E2E Production Test

**Task ID**: 1127-fix-asyncio-remove-hardcoded-production-e2e
**Domain**: CODING
**Started**: 2025-11-27T15:00:00Z
**Status**: AWAITING_APPROVAL

## State Files
- **feature_list.json** - Source of truth (JSON)
- **tests.json** - Test tracking (JSON)
- **PLAN.md** - Human-readable plan
- **DISCOVERY.md** - Exploration findings

## Phase Checklist
- [x] EXPLORE - Discovery complete
- [x] PLAN - Implementation plan created
- [ ] CODE - Implementation (via /execute-coding)
- [ ] COMMIT - Validation and packaging

## Task Summary

Three critical requirements for Christmas Campaign production deployment:

1. **Fix Python 3.12 AsyncIO Issue**
   - Workers crash with `NotImplementedError` from `asyncio.get_child_watcher()`
   - Solution: Remove uvloop or upgrade Prefect
   - Blocker causing 85.71% success rate (6/7 emails)

2. **Remove Hardcoded Email Templates**
   - Delete `get_fallback_template()` from `resend_operations.py`
   - Modify `send_email_flow.py` to error (not fallback)
   - All templates MUST come from Notion database

3. **Full E2E Production Test**
   - Puppeteer automation of production funnel
   - Test email: `lengobaosang@gmail.com` (MANDATORY)
   - Verify 7/7 emails delivered in TESTING_MODE

## Waves Overview

| Wave | Name | Features | Status |
|------|------|----------|--------|
| 1 | Fix AsyncIO Issue | 4 | Pending |
| 2 | Remove Hardcoded Templates | 4 | Pending |
| 3 | E2E Production Test | 6 | Pending |
| 4 | Verification & Documentation | 4 | Pending |

**Total Features**: 18
**Estimated Duration**: ~90 minutes

## Key Files to Modify

| File | Wave | Change |
|------|------|--------|
| `resend_operations.py` | 2 | Delete `get_fallback_template()` |
| `send_email_flow.py` | 2 | Remove fallback, raise error |
| `STATUS.md` | 4 | Update to production-ready |

## External Dependencies

- **Coolify Skill**: Server access for uvloop removal
- **Puppeteer MCP**: Browser automation for E2E test
- **Prefect Dashboard**: Flow run monitoring

## Progress Log

| Timestamp | Action |
|-----------|--------|
| 2025-11-27T15:00:00Z | Task initialized via /start-coding |
| 2025-11-27T15:10:00Z | EXPLORE phase complete |
| 2025-11-27T15:20:00Z | PLAN phase complete |
| 2025-11-27T15:20:00Z | Awaiting user approval |

## Next Steps

1. **Review Plan**: Check PLAN.md for implementation details
2. **Approve**: If plan looks good, run `/execute-coding`
3. **Monitor**: Watch for Wave progress updates

## Critical Notes

- **TESTING_MODE must be TRUE** for 1-minute email intervals
- **Use lengobaosang@gmail.com** for all testing
- **Wave 1 requires server access** via Coolify or SSH
- **Prefect skill required** before writing Prefect code

---

**Last Updated**: 2025-11-27T15:20:00Z
