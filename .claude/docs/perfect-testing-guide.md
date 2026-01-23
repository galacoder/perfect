## Testing Strategy

### Test Hierarchy

1. **Unit Tests** (Fast, Isolated):
   - Location: `campaigns/.../tests/`
   - Coverage: 93 tests across 3 modules
   - Run: `pytest campaigns/businessx_canada_lead_nurture/tests/ -v`

2. **Dry-Run Tests** (Structure Validation):
   - Location: `test_flows_dry_run.py`
   - Purpose: Validate flow structure without API calls
   - Run: `python test_flows_dry_run.py`

3. **Integration Tests** (E2E):
   - Location: `test_integration_e2e.py`
   - Modes: `mock` (safe) or `real` (creates records)
   - Run: `python test_integration_e2e.py --mode mock`

### Test Before Commit

```bash
# Quick validation (30 seconds)
python test_flows_dry_run.py

# Full unit tests (1-2 minutes)
pytest campaigns/businessx_canada_lead_nurture/tests/ -v

# Integration test (2-3 minutes)
python test_integration_e2e.py --mode mock
```
