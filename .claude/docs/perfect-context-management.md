## Context Management

### Clear Context Between Tasks

Use `/clear` between distinct tasks to reset the context window while preserving CLAUDE.md instructions.

**When to clear context**:
- After debugging authentication → before implementing new API endpoint
- After completing one campaign → before starting another
- After exploring codebase → before implementing features

### Subagent Isolation

Use Task tool with specialized agents for distinct phases:
- **Exploration**: Fresh perspective on codebase structure
- **Implementation**: Focused on specific patterns (invoke skills!)
- **Review**: Isolated security/quality checks

**CRITICAL**: Subagents don't inherit skills or context:
- Explicitly require skill usage in prompts
- Pass relevant context as prompt parameters
- Don't assume subagents read CLAUDE.md

### Example: Passing Skill Requirements to Subagent

```
Task(
  subagent_type: "coding",
  prompt: "
    Implement email scheduling feature.

    MANDATORY: Before writing any Prefect code:
    1. Invoke prefect-marketing-automation skill
    2. Verify import paths match Prefect v3.4.1
    3. Use Secret blocks (not environment variables)

    Follow patterns in campaigns/christmas_campaign/flows/
  "
)
```
