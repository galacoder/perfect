# Plan: Upload Marketing Email Templates to Notion

**Task ID**: 1118-upload-marketing-email-templates-to-notion
**Domain**: coding
**Created**: 2025-11-18
**Status**: Planning
**Source**: Marketing team handoff document

---

## Implementation Strategy

### Approach
**Method**: Extract-Transform-Load (ETL) pattern with TDD
**Paradigm**: Functional programming for data transformation
**Estimated Time**: 3-4 hours total
**Risk Level**: Low (well-defined task, existing patterns to follow)

### Key Decisions

- **Why this approach**: Marketing provided complete email copy in handoff document; extract to Python config → transform to Notion format → upload via Notion API
- **Alternatives considered**:
  - Manual copy-paste to Notion UI: Rejected (error-prone, not version-controlled, not repeatable)
  - Store templates in database migration: Rejected (Notion is source of truth for marketing content)
- **Critical success factors**:
  - Templates must preserve {{variable}} placeholders exactly
  - Upload must be idempotent (can run multiple times without duplicates)
  - Marketing team can edit templates in Notion without code changes

## Execution Waves

### Wave 1: Extract Email Templates from Handoff Document (45-60 min)
**Objective**: Create Python config file with all 7 email templates extracted from marketing handoff

**Tasks**:

1. [ ] Create directory structure
   ```bash
   mkdir -p campaigns/christmas_campaign/scripts
   mkdir -p campaigns/christmas_campaign/config
   ```

2. [ ] Extract email templates from HANDOFF-AUTOMATION-DEVELOPER.md
   - Read `/Users/sangle/Dev/action/projects/@agents/businessX/docs/money-model/model-16-christmas-traditional-service-2997/implementation/HANDOFF-AUTOMATION-DEVELOPER.md`
   - Extract Email 1 (lines 165-222): Assessment Results (universal)
   - Extract Email 2 variants (lines 225-282): System fixes (segmented by CRITICAL/URGENT/OPTIMIZE)
   - Extract Emails 3-7 from lead-nurture-7-days.md (reference document)

3. [ ] Create `campaigns/christmas_campaign/config/email_templates_christmas.py`
   - Define TEMPLATES dict with 7 email templates
   - Structure: `{"template_id": {"subject": "...", "html_body": "..."}}`
   - Convert markdown format to HTML format
   - Preserve {{variable}} placeholders (e.g., `{{first_name}}`, `{{assessment_score}}`)

4. [ ] Define template naming convention
   - `christmas_email_1` - Email 1 (universal)
   - `christmas_email_2a_critical` - Email 2 (CRITICAL segment)
   - `christmas_email_2b_urgent` - Email 2 (URGENT segment)
   - `christmas_email_2c_optimize` - Email 2 (OPTIMIZE segment)
   - `christmas_email_3` - Email 3 (universal)
   - `christmas_email_4` - Email 4 (universal)
   - `christmas_email_5` - Email 5 (universal)

5. [ ] Commit: "feat(christmas): extract email templates from marketing handoff"

**Success Criteria**:
- [ ] `email_templates_christmas.py` file created
- [ ] 7 templates defined with correct template_id, subject, html_body
- [ ] All {{variables}} preserved (no escaping/processing)
- [ ] File imports without errors
- [ ] Templates match marketing team's content

---

### Wave 2: Create Upload Script with TDD (1.5-2 hours)
**Objective**: Implement Notion upload script using test-driven development

**Code Organization Philosophy**:
- **Top-Down Structure**: Main function orchestrates, helper functions handle details
- **Separation of Concerns**: Notion API logic separate from template data
- **Idempotency**: Check existence before create/update

**TDD Approach**:

#### 2.1 Test Suite Setup

1. [ ] **RED**: Write test structure
   ```python
   # campaigns/christmas_campaign/tests/test_seed_email_templates.py
   import pytest
   from unittest.mock import Mock, patch

   class TestSeedEmailTemplates:
       def test_template_config_loads_7_templates(self):
           """Verify 7 templates defined in config."""
           from campaigns.christmas_campaign.config.email_templates_christmas import TEMPLATES
           assert len(TEMPLATES) == 7

       def test_template_has_required_fields(self):
           """Verify each template has template_id, subject, html_body."""
           # Test implementation

       def test_template_preserves_variables(self):
           """Verify {{variable}} placeholders not escaped."""
           # Test implementation
   ```

2. [ ] **GREEN**: Implement config file to pass tests

3. [ ] **REFACTOR**: Clean up template structure

#### 2.2 Upload Function

1. [ ] **RED**: Write test for upload_template_to_notion()
   ```python
   def test_upload_template_creates_new_page(self, mock_notion):
       """Test creating new template in Notion."""
       mock_notion.databases.query.return_value = {"results": []}
       result = upload_template_to_notion("christmas_email_1", template_data)
       assert mock_notion.pages.create.called
   ```

2. [ ] **GREEN**: Implement upload_template_to_notion()
   ```python
   def upload_template_to_notion(template_id: str, template_data: Dict) -> str:
       """Upload single template to Notion (create or update)."""
       # Query to check if exists
       # Create new or update existing
       # Return page_id
   ```

3. [ ] **REFACTOR**: Add error handling, logging

#### 2.3 Idempotency Logic

1. [ ] **RED**: Write test for update existing template
   ```python
   def test_upload_template_updates_existing_page(self, mock_notion):
       """Test updating existing template in Notion."""
       mock_notion.databases.query.return_value = {"results": [{"id": "page-123"}]}
       result = upload_template_to_notion("christmas_email_1", template_data)
       assert mock_notion.pages.update.called
   ```

2. [ ] **GREEN**: Implement update logic

3. [ ] **REFACTOR**: Extract query logic to helper function

#### 2.4 Main Script

1. [ ] **RED**: Write integration test for seed_all_templates()
   ```python
   def test_seed_all_templates_uploads_7_templates(self, mock_notion):
       """Test uploading all 7 templates."""
       result = seed_all_templates()
       assert len(result) == 7
       assert mock_notion.pages.create.call_count <= 7
   ```

2. [ ] **GREEN**: Implement main script
   ```python
   # campaigns/christmas_campaign/scripts/seed_email_templates.py
   def seed_all_templates() -> Dict[str, str]:
       """Upload all Christmas campaign templates to Notion."""
       results = {}
       for template_id, template_data in TEMPLATES.items():
           page_id = upload_template_to_notion(template_id, template_data)
           results[template_id] = page_id
       return results
   ```

3. [ ] **REFACTOR**: Add progress logging, error summary

**Implementation Details**:

```python
# High-level orchestration
def seed_all_templates() -> Dict[str, str]:
    """Upload all templates. Returns {template_id: page_id}."""
    validate_environment()
    results = {}
    for template_id, template_data in TEMPLATES.items():
        page_id = upload_template_to_notion(template_id, template_data)
        results[template_id] = page_id
    return results

# Medium-level: Upload logic
def upload_template_to_notion(template_id: str, template_data: Dict) -> str:
    """Create or update template in Notion."""
    existing_page = find_existing_template(template_id)
    if existing_page:
        return update_template(existing_page["id"], template_data)
    else:
        return create_template(template_id, template_data)

# Low-level: Notion API calls
def find_existing_template(template_id: str) -> Optional[Dict]:
    """Query Notion database for existing template."""
    response = notion.databases.query(
        database_id=NOTION_EMAIL_TEMPLATES_DB_ID,
        filter={"property": "template_id", "rich_text": {"equals": template_id}}
    )
    return response["results"][0] if response["results"] else None
```

**Success Criteria**:
- [ ] All unit tests pass (>80% code coverage)
- [ ] Script handles create and update cases
- [ ] Script is idempotent (can run multiple times)
- [ ] Clear logging for each template upload
- [ ] Error handling for API failures

---

### Wave 3: Integration with Notion API (45-60 min)
**Objective**: Test upload script with real Notion API

**Tasks**:

1. [ ] Create integration test environment
   - Use real NOTION_TOKEN and NOTION_EMAIL_TEMPLATES_DB_ID from .env
   - Mark tests with `@pytest.mark.integration`

2. [ ] Test upload to Notion (dry run)
   ```bash
   # Test with first template only
   python -c "from campaigns.christmas_campaign.scripts.seed_email_templates import upload_template_to_notion; upload_template_to_notion('christmas_email_1', {...})"
   ```

3. [ ] Verify template in Notion UI
   - Open Notion database: https://notion.so/2ab7c374-1115-8115-932c-ca6789c5b87b
   - Check template_id = "christmas_email_1"
   - Check subject line matches
   - Check html_body matches
   - Check {{variables}} preserved

4. [ ] Test idempotency
   - Run upload script twice
   - Verify no duplicate templates created
   - Verify second run updates existing template

5. [ ] Upload all 7 templates
   ```bash
   python campaigns/christmas_campaign/scripts/seed_email_templates.py
   ```

6. [ ] Manual verification in Notion
   - All 7 templates visible in database
   - Each template has correct content
   - Variables like `{{first_name}}`, `{{GPSScore}}` intact

7. [ ] Test template retrieval
   ```python
   # Verify fetch_email_template() works with uploaded templates
   from campaigns.christmas_campaign.tasks.notion_operations import fetch_email_template
   template = fetch_email_template("christmas_email_1")
   assert template is not None
   assert "{{first_name}}" in template["html_body"]
   ```

8. [ ] Commit: "feat(christmas): implement email template upload script"

**Integration Points**:
- Notion API: Create/update pages in Email Templates database
- Environment variables: NOTION_TOKEN, NOTION_EMAIL_TEMPLATES_DB_ID
- fetch_email_template(): Verify retrieval works

**Success Criteria**:
- [ ] All 7 templates uploaded successfully
- [ ] Templates visible in Notion UI
- [ ] fetch_email_template() retrieves templates correctly
- [ ] Idempotency verified (no duplicates)
- [ ] Variables preserved ({{first_name}}, etc.)

---

### Wave 4: Documentation & Testing (30-45 min)
**Objective**: Document script usage and add comprehensive tests

**Tasks**:

1. [ ] Add CLI interface to script
   ```python
   # Add argparse for options
   parser = argparse.ArgumentParser(description="Seed Christmas campaign email templates to Notion")
   parser.add_argument("--template", help="Upload single template by ID")
   parser.add_argument("--dry-run", action="store_true", help="Show what would be uploaded without uploading")
   parser.add_argument("--force", action="store_true", help="Force update even if template unchanged")
   ```

2. [ ] Add usage documentation to script docstring
   ```python
   """
   Seed Christmas Campaign Email Templates to Notion

   Usage:
       # Upload all templates
       python campaigns/christmas_campaign/scripts/seed_email_templates.py

       # Upload single template
       python campaigns/christmas_campaign/scripts/seed_email_templates.py --template christmas_email_1

       # Dry run (show what would be uploaded)
       python campaigns/christmas_campaign/scripts/seed_email_templates.py --dry-run

       # Force update all templates
       python campaigns/christmas_campaign/scripts/seed_email_templates.py --force
   """
   ```

3. [ ] Create README for christmas_campaign
   - Document email template upload process
   - Add troubleshooting section
   - Link to marketing handoff document

4. [ ] Add integration test
   ```python
   @pytest.mark.integration
   def test_full_upload_flow_integration():
       """Integration test: upload all templates to real Notion database."""
       # Upload all templates
       results = seed_all_templates()
       assert len(results) == 7

       # Verify each template can be fetched
       for template_id in results.keys():
           template = fetch_email_template(template_id)
           assert template is not None
   ```

5. [ ] Test error scenarios
   - Invalid NOTION_TOKEN (should fail gracefully)
   - Network failure during upload (should retry)
   - Malformed template data (should validate before upload)

6. [ ] Commit: "docs(christmas): add email template upload documentation"

**Documentation Needs**:
- **Script usage**: How to run, what options available
- **Configuration**: Where templates defined, how to add new ones
- **Troubleshooting**: Common errors and fixes
- **Marketing team workflow**: How to edit templates in Notion

**Success Criteria**:
- [ ] Script has clear --help output
- [ ] README documents upload process
- [ ] Integration test passes
- [ ] Error handling tested
- [ ] Documentation complete

---

## Quality & Validation Checklist

Before considering complete:
- [ ] All unit tests pass
- [ ] Integration test passes (real Notion API)
- [ ] All 7 templates uploaded to Notion
- [ ] Templates visible and editable in Notion UI
- [ ] fetch_email_template() works for all 7 templates
- [ ] Variables ({{first_name}}, etc.) preserved
- [ ] Script is idempotent (can run multiple times)
- [ ] Clear error messages for failures
- [ ] Documentation complete
- [ ] Code follows project patterns
- [ ] No hardcoded secrets (use .env)

## Rollback & Contingency Plan

**If blocked or failed:**

1. **Stop immediately** - Don't continue if stuck

2. **Document blocker** in `BLOCKERS.md`:
   - What you were trying (e.g., uploading Email 2a template)
   - What failed (e.g., Notion API 400 error: property 'html_body' too long)
   - Error messages (full stack trace)
   - What you've tried to fix it

3. **Preserve work**: Commit WIP to branch
   ```bash
   git add .
   git commit -m "wip(christmas): template upload script (blocked on Notion API error)

   Blocked on: Notion rich_text field limit (2000 chars)
   See BLOCKERS.md for details"
   ```

4. **Offer options**:
   - Option A: Split long html_body into multiple rich_text blocks
   - Option B: Use Notion blocks API instead of page properties
   - Option C: Store HTML in external file, link in Notion

5. **Don't force it** - Quality over speed

## Dependencies & Risk Management

**External Dependencies**:
- **notion-client**: Notion API SDK
  - Alternatives: Direct REST API calls
  - Risk: API rate limits (handled by retry logic)
- **python-dotenv**: Environment variable loading
  - Alternatives: Manual os.getenv()
  - Risk: None (simple library)

**Risks**:

- **High Risk**: Notion rich_text field limit (2000 chars per block)
  - Mitigation: Check template length, split into multiple blocks if needed
  - Detection: Test with longest template (Email 5)

- **Medium Risk**: Template variable escaping during upload
  - Monitoring: Integration test checks for {{variable}} preservation
  - Plan B: Manual regex check after upload

- **Low Risk**: Network timeout during upload
  - Acceptance: Retry logic handles transient failures
  - Monitoring: Log retry attempts

## Success Definition

This plan succeeds when:
- ✅ All 4 waves completed
- ✅ All 7 email templates uploaded to Notion
- ✅ Templates editable by marketing team in Notion
- ✅ fetch_email_template() retrieves templates correctly
- ✅ Variables preserved for template rendering
- ✅ Script is idempotent and reusable
- ✅ Documentation complete
- ✅ Tests passing (unit + integration)
- ✅ Ready for use in Prefect email flows

---

## Template Structure Reference

### Notion Database Schema (Existing)

```python
{
    "template_id": {
        "type": "rich_text",
        "rich_text": [{"text": {"content": "christmas_email_1"}}]
    },
    "subject": {
        "type": "title",
        "title": [{"text": {"content": "Your BusOS Assessment Results"}}]
    },
    "html_body": {
        "type": "rich_text",
        "rich_text": [{"text": {"content": "<html>...</html>"}}]
    },
    "campaign": {
        "type": "select",
        "select": {"name": "Christmas Campaign"}
    },
    "email_number": {
        "type": "number",
        "number": 1
    },
    "segment": {
        "type": "multi_select",
        "multi_select": [{"name": "universal"}]
    },
    "active": {
        "type": "checkbox",
        "checkbox": True
    }
}
```

### Template Variables to Preserve

Must remain unescaped in html_body:
- `{{first_name}}` - Contact first name
- `{{email}}` - Contact email
- `{{assessment_score}}` - BusOS assessment score (0-100)
- `{{GPSScore}}` - GPS system score
- `{{GenerateScore}}` - Generate subscore
- `{{PersuadeScore}}` - Persuade subscore
- `{{ServeScore}}` - Serve subscore
- `{{MoneyScore}}` - Money system score
- `{{MarketingScore}}` - Marketing system score
- `{{WeakestSystem1}}` - Name of weakest system
- `{{Score1}}` - Score of weakest system
- `{{RevenueLeakSystem1}}` - Monthly revenue leak for System 1
- `{{WeakestSystem2}}` - Name of 2nd weakest system
- `{{Score2}}` - Score of 2nd weakest system
- `{{RevenueLeakSystem2}}` - Monthly revenue leak for System 2
- `{{TotalRevenueLeak}}` - Sum of System 1 + System 2 leaks
- `{{AnnualRevenueLeak}}` - TotalRevenueLeak × 12
- `{{QuickWinAction}}` - Specific action based on weakest system
- `{{QuickWinExplanation}}` - Why this action works
- `{{QuickWinImpact}}` - Expected revenue impact

---

## Next Steps After Completion

Once this task is complete:

1. **Update Prefect flows**: Modify email_sequence flows to use fetch_email_template() with Christmas campaign template_ids
2. **Test email rendering**: Send test emails with real contact data to verify template substitution
3. **Marketing team handoff**: Show marketing team how to edit templates in Notion
4. **Monitor**: Track email open rates, click rates for each template
5. **Iterate**: Marketing team can update templates in Notion without code changes

---

**Ready to proceed?** Reply with "Yes" or describe any changes needed.

If approved, I'll implement using `/execute-coding` command.
