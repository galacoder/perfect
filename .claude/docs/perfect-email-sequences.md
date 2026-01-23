## Email Sequence Logic

### Segment Classification

Contacts are classified into 3 segments based on assessment results:

| Segment | Condition | Action |
|---------|-----------|--------|
| **CRITICAL** | `red_systems >= 2` | Discord alert + personalized emails |
| **URGENT** | `red_systems == 1` OR `orange_systems >= 2` | Personalized emails |
| **OPTIMIZE** | All others | Standard emails |

**Routing logic**: `campaigns/.../tasks/routing.py:classify_segment()`

### Email Sequence Timeline

**Production Mode** (`TESTING_MODE=false`):
1. Email 1 (universal) → Wait 24h
2. Email 2 (segment-specific: 2A/2B/2C) → Wait 48h
3. Email 3 (universal) → Wait 48h
4. Email 4 (universal) → Wait 48h
5. Email 5 (segment-specific: 5A/5B/5C) → Done

**Total duration**: 7 days

**Testing Mode** (`TESTING_MODE=true`):
- Wait times: 1min → 2min → 3min → 4min (~10 minutes total)

