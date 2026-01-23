## Prefect Deployment Best Practices

**CRITICAL LEARNINGS** from Christmas Campaign deployment (Nov 19, 2025):

### 1. Always Use Prefect Secret Blocks for Credentials

**DO NOT use environment variables on production workers!**

**✅ CORRECT Approach (Secret Blocks)**:

```python
from prefect.blocks.system import Secret

# Load credentials from Prefect Secret blocks
try:
    NOTION_TOKEN = Secret.load("notion-token").get()
    NOTION_DB_ID = Secret.load("notion-db-id").get()
    RESEND_API_KEY = Secret.load("resend-api-key").get()
    print("✅ Loaded credentials from Prefect Secret blocks")
except Exception as e:
    # Fallback to environment variables for local development only
    print(f"⚠️  Failed to load from Secret blocks, using environment variables: {e}")
    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    NOTION_DB_ID = os.getenv("NOTION_DB_ID")
    RESEND_API_KEY = os.getenv("RESEND_API_KEY")
```

**❌ WRONG Approach (Environment Variables)**:
```python
# Never do this for production!
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
```

**Creating Secret Blocks**:
```bash
# Set environment variables from .env file
set -a && source .env && set +a

# Create Secret blocks on production Prefect server
PREFECT_API_URL=https://prefect.galatek.dev/api python3 -c "
from prefect.blocks.system import Secret
import os

blocks = [
    ('notion-token', 'NOTION_TOKEN'),
    ('notion-db-id', 'NOTION_DB_ID'),
    ('resend-api-key', 'RESEND_API_KEY'),
]

for name, env_var in blocks:
    value = os.getenv(env_var)
    if value:
        Secret(value=value).save(name, overwrite=True)
        print(f'✅ Created secret block: {name}')
"
```

**Benefits of Secret Blocks**:
- ✅ Encrypted storage in Prefect
- ✅ Zero environment variables needed on worker
- ✅ Easy credential rotation (update block, no code changes)
- ✅ No credentials in code or git
- ✅ Centralized secret management

### 2. Always Use Git-Based Deployments

**✅ CORRECT Approach**:

Configure `prefect.yaml` with `git_clone` pull step:

```yaml
pull:
  - prefect.deployments.steps.git_clone:
      repository: https://github.com/galacoder/perfect.git
      branch: main
      access_token: null
```

**Benefits**:
- ✅ Code auto-pulls from GitHub on each run
- ✅ No manual code deployment needed
- ✅ Always runs latest code
- ✅ Version control integration

**Deployment Process**:
```bash
# 1. Make code changes
git add .
git commit -m "feat: add new feature"
git push

# 2. Code automatically deployed on next flow run!
# No manual deployment step needed
```

### 3. Proper Prefect API Usage (v3.4.1)

**✅ CORRECT: Scheduling Flow Runs**

```python
from prefect.states import Scheduled  # ← Correct import path!
from prefect.client.orchestration import get_client

async def schedule_flow():
    async with get_client() as client:
        deployment = await client.read_deployment_by_name("flow-name/deployment-name")

        flow_run = await client.create_flow_run_from_deployment(
            deployment_id=deployment.id,
            parameters={"param1": "value1"},
            state=Scheduled(scheduled_time=scheduled_time)  # ← Use Scheduled object
        )

        return flow_run.id
```

**❌ WRONG: Using Dict for State**
```python
# Never do this!
state={"type": "SCHEDULED", "timestamp": scheduled_time.isoformat()}
# Error: 'dict' object has no attribute 'data'
```

**Import Paths for Prefect v3.4.1**:
- ✅ `from prefect.states import Scheduled`
- ❌ `from prefect.client.schemas.states import Scheduled` (doesn't exist)

### 4. Research Unknown APIs/Libraries

**ALWAYS use skills when encountering unfamiliar code:**

**Use `prefect-marketing-automation` skill**:
- When working with Prefect v3 flows, deployments, or tasks
- When unsure about Prefect API usage
- When implementing new Prefect patterns

**Use `library-docs-pure` skill**:
- When researching Python libraries (requests, pydantic, etc.)
- When checking API documentation
- When learning new library features

**Use WebSearch**:
- For recent changes or updates (post-knowledge cutoff)
- For troubleshooting specific errors
- For community best practices

**Example**:
```
User: "How do I schedule a flow run in Prefect v3?"

Claude: Let me research the correct Prefect v3 API...
[Uses prefect-marketing-automation skill to look up proper API]
[Finds correct usage: Scheduled(scheduled_time=...)]
```

### 5. Development Workflow

**Standard Development Process**:

1. **Local Development**:
   ```bash
   # Use .env file for local testing
   export TESTING_MODE=true
   python campaigns/christmas_campaign/flows/signup_handler.py
   ```

2. **Commit and Push**:
   ```bash
   git add .
   git commit -m "feat(campaign): add new feature"
   git push
   ```

3. **Code Auto-Deploys**:
   - Worker pulls latest code from GitHub on next run
   - No manual deployment step needed

4. **Test on Production**:
   ```bash
   PREFECT_API_URL=https://prefect.galatek.dev/api \
   prefect deployment run flow-name/deployment-name \
     --param email="test@example.com"
   ```

5. **Monitor Logs**:
   ```bash
   PREFECT_API_URL=https://prefect.galatek.dev/api \
   prefect flow-run logs <flow-run-id>
   ```

### 6. Campaign Structure Template

**When creating new campaigns**:

```
campaigns/
└── new_campaign_name/
    ├── README.md                    # Campaign overview
    ├── ARCHITECTURE.md              # Technical details
    ├── STATUS.md                    # Deployment status (IMPORTANT!)
    ├── WEBSITE_INTEGRATION.md       # API integration guide
    ├── flows/
    │   ├── signup_handler.py        # Main entry flow
    │   └── send_email.py            # Email sending flow
    ├── tasks/
    │   ├── notion_operations.py     # Database operations
    │   └── resend_operations.py     # Email operations
    ├── tests/
    │   ├── test_notion_operations.py
    │   └── test_resend_operations.py
    └── diagrams/
        └── CAMPAIGN_OVERVIEW.txt
```

**STATUS.md Template**:
```markdown
# Campaign Name - Production Deployment Status

**Last Updated**: YYYY-MM-DD HH:MM TZ
**Status**: 🟡/✅ [X]% COMPLETE - [brief status]

## 🎯 Quick Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Flows Developed** | ✅/🟡/❌ | Description |
| **Git Repository** | ✅/🟡/❌ | GitHub URL |
| **Prefect Deployments** | ✅/🟡/❌ | Deployment details |
| **Secret Blocks** | ✅/🟡/❌ | Number of blocks |
| **End-to-End Testing** | ✅/🟡/❌ | Test results |

## ✅ What's Working
[List completed items]

## 🟡 What's Pending
[List pending items]

## 📊 Test Results Summary
[Latest test results with flow run IDs]
```

### 7. Testing Strategy

**Always test in this order**:

1. **Local Dry Run**:
   ```bash
   python campaigns/campaign_name/flows/flow_name.py
   ```

2. **Commit and Push**:
   ```bash
   git add . && git commit -m "..." && git push
   ```

3. **Production Test Run**:
   ```bash
   PREFECT_API_URL=https://prefect.galatek.dev/api \
   prefect deployment run flow-name/deployment-name \
     --param test_param="test_value"
   ```

4. **Check Logs**:
   ```bash
   PREFECT_API_URL=https://prefect.galatek.dev/api \
   prefect flow-run logs <flow-run-id>
   ```

5. **Verify in Notion/External Systems**:
   - Check database records created
   - Verify email sent (if applicable)
   - Confirm data accuracy

### 8. Common Pitfalls to Avoid

❌ **NEVER**:
- Use environment variables for production credentials (use Secret blocks)
- Assume import paths without checking Prefect version
- Deploy code without pushing to GitHub first
- Skip testing after making changes
- Forget to update STATUS.md after changes

✅ **ALWAYS**:
- Use Secret blocks for ALL credentials
- Research unfamiliar APIs with skills (prefect-marketing-automation, library-docs-pure)
- Push code to GitHub before testing production
- Update STATUS.md with test results
- Document deployment progress
- Use git-based deployments (not manual code copy)

### 9. Key Learnings Summary

**Christmas Campaign Deployment (Nov 19, 2025)**:

1. **Secret Blocks are Required**: Don't ask users to set environment variables on workers
2. **Git-Based Deployments Work**: Code auto-pulls from GitHub on each run
3. **Prefect v3 API**: Use `from prefect.states import Scheduled`, not dict
4. **Always Research**: Use skills when unsure about APIs/libraries
5. **STATUS.md is Critical**: Track deployment progress, test results, blockers
6. **Zero Environment Variables**: Proper setup needs ZERO env vars on worker
7. **Test End-to-End**: Verify complete flow including scheduling, database writes, etc.

