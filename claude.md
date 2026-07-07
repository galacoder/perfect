# CLAUDE.md - Perfect Marketing Automation

**Role**: Campaign-based email sequence automation with Prefect

## ⚠️ MANDATORY: Skill Enforcement

**ALWAYS use these skills** (non-negotiable):
- `test-driven-development` - Before ANY code changes
- `verifying-completion` - Before claiming work complete
- `building-data-pipelines` - For all Prefect workflow development

See: `.claude/docs/perfect-skill-enforcement.md` for full enforcement rules

## Quick Start

Campaign structure: `campaigns/<campaign-name>/flows/`
Deployment best practices: `.claude/docs/perfect-prefect-deployment.md` ⭐

### Session Setup
```bash
cd /Users/sangle/Dev/action/projects/perfect
export PROJECT_ROOT="/Users/sangle/Dev/action/projects/perfect"
```

### Essential Commands

| Command | Purpose |
|---------|---------|
| `prefect deploy --all` | Deploy all flows to Prefect Cloud |
| `python flows/main.py` | Test flow locally |
| `pytest tests/` | Run test suite |
| `prefect server start` | Start local Prefect server |

## Architecture

### Campaign-Based Structure
```
campaigns/
├── campaign-name/
│   ├── flows/          # Prefect workflows
│   ├── tasks/          # Reusable task functions
│   ├── config/         # Campaign configuration
│   └── tests/          # Campaign-specific tests
```

See `.claude/docs/perfect-campaign-architecture.md` for migration status and detailed patterns.

### Email Sequences
Email sequence logic and patterns: `.claude/docs/perfect-email-sequences.md`

## Documentation

Full guides in `.claude/docs/`:

1. **perfect-prefect-deployment.md** ⭐ **CRITICAL**
   - 300+ lines of production deployment learnings
   - Best practices from real experience
   - Prefect Cloud configuration
   - Work pool setup and management

2. **perfect-skill-enforcement.md**
   - Mandatory skill usage rules
   - Enforcement patterns and verification

3. **perfect-campaign-architecture.md**
   - Campaign-based structure explanation
   - Migration status from old patterns
   - File organization best practices

4. **perfect-email-sequences.md**
   - Email sequence logic and timing
   - Sequence patterns and templates

5. **perfect-testing-guide.md**
   - Testing strategy for Prefect flows
   - Test requirements and patterns

6. **perfect-env-setup.md**
   - Environment variable configuration
   - Required credentials and secrets

7. **perfect-commands-reference.md**
   - Common tasks and workflows
   - Quick reference commands

8. **perfect-context-management.md**
   - Context handling in flows
   - State management patterns

9. **perfect-design-decisions.md**
   - Key architectural decisions
   - Trade-offs and rationale

## Critical Rules

1. **TDD Always**: Write tests before implementation
   - Use `test-driven-development` skill
   - Tests must pass before claiming complete

2. **Mandatory Skills**: Use enforced skills for their domains
   - `building-data-pipelines` for Prefect work
   - `verifying-completion` before completion claims
   - See `.claude/docs/perfect-skill-enforcement.md`

3. **Campaign Organization**: Follow campaign-based structure
   - Each campaign is self-contained
   - Shared code in `libs/`
   - See `.claude/docs/perfect-campaign-architecture.md`

4. **Prefect Deployment**: Follow deployment guide
   - See `.claude/docs/perfect-prefect-deployment.md`
   - Use work pools correctly
   - Tag deployments appropriately

## Task Workflows

| Complexity | Workflow |
|------------|----------|
| Simple | Fast iteration with tests |
| Standard | Full TDD cycle |
| Complex | See `.claude/docs/perfect-commands-reference.md` |

## Environment Variables

Required environment variables:
```bash
PREFECT_API_KEY=...
PREFECT_WORKSPACE=...
RESEND_API_KEY=...
```

See `.claude/docs/perfect-env-setup.md` for complete configuration.

## Troubleshooting

### Deployment Issues
→ Check work pool configuration
→ See `.claude/docs/perfect-prefect-deployment.md`

### Flow Errors
→ Check logs in Prefect Cloud dashboard
→ Verify environment variables set

### Test Failures
→ Run `pytest -v` for detailed output
→ See `.claude/docs/perfect-testing-guide.md`

## Quick Reference

### Common Tasks
```bash
# Deploy specific campaign
prefect deploy campaigns/welcome/flows/main.py

# Run flow locally
python campaigns/welcome/flows/main.py

# View deployments
prefect deployment ls

# View flow runs
prefect flow-run ls
```

See `.claude/docs/perfect-commands-reference.md` for complete reference.

---

**Last Updated**: 2025-01-23
**Maintained By**: Sang Le
**Project**: Perfect Marketing Automation
**Full Documentation**: See `.claude/docs/` directory
**Mandatory Skills**: test-driven-development, verifying-completion, building-data-pipelines
