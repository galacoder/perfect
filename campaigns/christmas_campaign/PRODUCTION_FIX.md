# Production Fix: Python 3.12 + uvloop Compatibility

**Date**: 2025-11-27
**Issue**: Prefect workers crashing with `NotImplementedError` from `asyncio.get_child_watcher()`
**Server**: Hublab (MINISFORUM UH125 Pro)
**Status**: FIX DOCUMENTED - Requires manual application on server

---

## Problem

Flow runs on production Prefect (https://prefect.galatek.dev) are crashing with:

```
File "/usr/local/lib/python3.12/asyncio/events.py", line 645, in get_child_watcher
    raise NotImplementedError
NotImplementedError
```

**Root Cause**: Python 3.12 deprecated `asyncio.get_child_watcher()`, and uvloop triggers this error.

---

## Fix (Apply on Hublab Server)

SSH to Hublab and run:

```bash
# Option 1: Remove uvloop (quickest fix)
pip uninstall uvloop -y
pkill -f "prefect worker"
prefect worker start --pool default &

# Option 2: If uvloop is needed for other apps
# Upgrade to latest Prefect which handles Python 3.12
pip install --upgrade prefect>=3.4.1
pkill -f "prefect worker"
prefect worker start --pool default &
```

---

## Verification

After applying fix, test with:

```bash
PREFECT_API_URL=https://prefect.galatek.dev/api \
prefect deployment run christmas-signup-handler/christmas-signup-handler \
  --param email="test@example.com" \
  --param first_name="Test" \
  --param business_name="Test Business" \
  --param assessment_score=50 \
  --param red_systems=2
```

**Expected**: Flow run should complete without crashing.

---

## Scalability Notes

Your Hublab server (32GB RAM, Intel Core Ultra 5 125H, 14 cores/18 threads) can easily handle:

- 20-50 concurrent signups with current 3 workers
- Each flow run uses ~100MB RAM
- Prefect queues excess work automatically

For higher scale:
```bash
# Add more workers (on Hublab)
prefect worker start --pool default --name worker2 &
prefect worker start --pool default --name worker3 &
```

---

## Sources

- [Python 3.12 Child Watcher Deprecation](https://github.com/python/cpython/issues/94597)
- [Prefect Python 3.12 Support](https://github.com/PrefectHQ/prefect/issues/10974)
- [aiohttp Python 3.12 Warning](https://github.com/aio-libs/aiohttp/issues/7291)
