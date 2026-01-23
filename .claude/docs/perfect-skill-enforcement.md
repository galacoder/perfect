## ⚡ MANDATORY: Skill Usage Rules

**CRITICAL**: Before implementing ANY Prefect-related code, you MUST:

1. **Load the `prefect-marketing-automation` skill** - Use `Skill: prefect-marketing-automation`
2. **Research API patterns** before writing any Prefect code
3. **Pass skill requirements to subagents** when delegating tasks

### When to Use Which Skill

| Task Type | REQUIRED Skill | Reason |
|-----------|---------------|--------|
| **Prefect flows/tasks/deployments** | `prefect-marketing-automation` | Campaign-based patterns, correct API imports |
| **Python library research** | `library-docs-pure` | Accurate API usage for any library |
| **Notion operations** | `notion-integration` | Rate limits, pagination, error handling |
| **Browser automation/testing** | `playwright-skill` | E2E funnel testing |

### Subagent Requirements

**IMPORTANT**: Subagents do NOT inherit skill context - skills must be explicitly invoked.

When using `/start`, `/execute`, `/start-coding`, `/execute-coding`, or Task tool:
- **ALWAYS include in prompt**: "Use `prefect-marketing-automation` skill before writing any Prefect code"
- Subagents have isolated context and won't see this CLAUDE.md's skill guidance

### Anti-Pattern (NEVER DO)

```python
# ❌ WRONG: Guessing Prefect API without research
from prefect.client.schemas.states import Scheduled  # Doesn't exist in v3.4.1!

# ✅ CORRECT: Use skill first, then code
# Step 1: Invoke prefect-marketing-automation skill
# Step 2: Find correct import: from prefect.states import Scheduled
# Step 3: Implement with verified pattern
```

### Why This Matters

**Christmas Campaign Deployment (Nov 19, 2025)** - We wasted hours debugging because:
- ❌ Assumed `from prefect.client.schemas.states import Scheduled` existed (it doesn't)
- ❌ Tried dict-based state `{"type": "SCHEDULED", ...}` (causes 'dict' object has no attribute 'data')
- ✅ Correct pattern found via skill: `from prefect.states import Scheduled`

**Rule**: When unsure about ANY library API, use the appropriate skill FIRST.

