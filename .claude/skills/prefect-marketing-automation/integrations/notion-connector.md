# Notion CRM Integration Guide

## Overview

Notion serves as the CRM system for tracking leads, visitor activity, content calendar, and analytics. This guide shows how to integrate Notion databases with Prefect for bi-directional data sync.

**Use Cases:**
- Lead tracking and scoring
- Visitor activity tracking
- Content calendar management
- Analytics dashboard
- Campaign performance tracking

## Prerequisites

1. **Notion Account**: Sign up at [https://notion.so/](https://notion.so/)
2. **Notion Integration**: Create in Settings → Integrations
3. **API Key**: Get from integration settings
4. **Database IDs**: Get from database URLs

## Setup Steps

### 1. Create Notion Integration

```bash
# 1. Login to Notion
# 2. Go to: Settings & Members → Integrations
# 3. Click "+ New integration"
# 4. Name: "Prefect Marketing Automation"
# 5. Set capabilities:
#    - Read content ✅
#    - Update content ✅
#    - Insert content ✅
# 6. Click "Submit"
# 7. Copy "Internal Integration Token" (starts with "secret_...")

# Set as environment variable
export NOTION_API_KEY="secret_your_token_here"
```

### 2. Create Database Structures

#### A. Leads Database

**Properties:**
- `Email` (Title) - Lead email address
- `Name` (Text) - Lead first name
- `Phone` (Phone) - Optional phone number
- `Visitor ID` (Text) - Tracking identifier
- `Created` (Date) - Lead creation date
- `Stage` (Select) - opted_in, assessment_complete, sales_call_booked, closed_won
- `Score` (Number) - Lead score (0-100)
- `Status` (Select) - new, hot, warm, cold, converted
- `Priority` (Select) - high, medium, low
- `Last Email` (Date) - Last email sent date
- `Email Stage` (Number) - Current email in sequence (1-7)
- `Engagement Score` (Number) - Email engagement points
- `Segment` (Select) - beauty-salon, auto-repair, fitness, etc.

**Create Database:**
1. Create new page in Notion
2. Type `/database` and select "Database - Full page"
3. Add all properties above
4. Click "Share" → Add your integration
5. Copy database ID from URL: `https://notion.so/workspace/DATABASE_ID?v=...`

```bash
export NOTION_LEADS_DB_ID="your_database_id_here"
```

#### B. Visitors Database

**Properties:**
- `Visitor ID` (Title) - Unique visitor identifier
- `Email` (Email) - If captured
- `Lead ID` (Text) - Link to Leads database
- `Source` (Select) - facebook, google, organic
- `UTM Campaign` (Text)
- `UTM Medium` (Text)
- `Visit Date` (Date)
- `Stage` (Select) - landing_page, opted_in, assessment_started, assessment_complete, sales_page
- `Status` (Select) - active, abandoned, converted
- `Page URL` (URL) - Last page visited
- `Duration` (Number) - Time on site (seconds)

#### C. Content Calendar Database

**Properties:**
- `Content` (Title) - Post text
- `Scheduled Date` (Date)
- `Scheduled Time` (Text) - e.g., "09:00"
- `Platforms` (Multi-select) - twitter, linkedin, facebook
- `Image URL` (URL)
- `Link URL` (URL)
- `Hashtags` (Text)
- `Status` (Select) - draft, scheduled, published, failed
- `Published At` (Date)
- `Post URLs` (Text) - URLs of published posts

#### D. Analytics Dashboard Database

**Properties:**
- `Date` (Title) - Report date
- `Total Spend` (Number) - Ad spend
- `Total Conversions` (Number) - Leads generated
- `Cost Per Lead` (Number) - CPL
- `CTR` (Number) - Click-through rate
- `Opt-in Rate` (Number) - Landing → Opt-in %
- `Assessment Rate` (Number) - Opt-in → Assessment %
- `Booking Rate` (Number) - Assessment → Booking %
- `Close Rate` (Number) - Booking → Close %

### 3. Install Python Dependencies

```bash
pip install notion-client httpx prefect
```

### 4. Test API Connection

```python
from notion_client import Client
import os

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_LEADS_DB_ID = os.getenv("NOTION_LEADS_DB_ID")

# Initialize client
notion = Client(auth=NOTION_API_KEY)

# Test connection - list databases
try:
    response = notion.search(filter={"property": "object", "value": "database"})
    print(f"✅ Notion API connection successful!")
    print(f"   Found {len(response['results'])} databases")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

## Prefect Integration

### Basic Operations

#### 1. Create Lead Record

```python
from prefect import task
from notion_client import Client
from datetime import datetime
import os

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_LEADS_DB_ID = os.getenv("NOTION_LEADS_DB_ID")

@task(retries=3, retry_delay_seconds=30)
def create_lead(email: str, first_name: str, segment: str, phone: str = None):
    """
    Create new lead record in Notion.

    Args:
        email: Lead email address
        first_name: Lead first name
        segment: Lead segment (e.g., "beauty-salon")
        phone: Optional phone number

    Returns:
        dict with notion_id and lead data
    """
    notion = Client(auth=NOTION_API_KEY)

    lead_record = notion.pages.create(
        parent={"database_id": NOTION_LEADS_DB_ID},
        properties={
            "Email": {"title": [{"text": {"content": email}}]},
            "Name": {"rich_text": [{"text": {"content": first_name}}]},
            "Phone": {"phone_number": phone} if phone else {"phone_number": None},
            "Created": {"date": {"start": datetime.now().isoformat()}},
            "Stage": {"select": {"name": "opted_in"}},
            "Score": {"number": 0},
            "Status": {"select": {"name": "new"}},
            "Priority": {"select": {"name": "medium"}},
            "Segment": {"select": {"name": segment}}
        }
    )

    return {
        "notion_id": lead_record["id"],
        "email": email,
        "first_name": first_name
    }
```

#### 2. Update Lead Record

```python
@task(retries=2, retry_delay_seconds=30)
def update_lead(notion_id: str, properties: dict):
    """
    Update existing lead record in Notion.

    Args:
        notion_id: Notion page ID
        properties: Dictionary of properties to update

    Example:
        update_lead(
            notion_id="page-id-here",
            properties={
                "score": 85,
                "status": "hot",
                "priority": "high"
            }
        )
    """
    notion = Client(auth=NOTION_API_KEY)

    # Build Notion property format
    notion_props = {}

    if "score" in properties:
        notion_props["Score"] = {"number": properties["score"]}

    if "status" in properties:
        notion_props["Status"] = {"select": {"name": properties["status"]}}

    if "priority" in properties:
        notion_props["Priority"] = {"select": {"name": properties["priority"]}}

    if "stage" in properties:
        notion_props["Stage"] = {"select": {"name": properties["stage"]}}

    if "email_stage" in properties:
        notion_props["Email Stage"] = {"number": properties["email_stage"]}

    if "last_email_sent" in properties:
        notion_props["Last Email"] = {"date": {"start": properties["last_email_sent"]}}

    notion.pages.update(page_id=notion_id, properties=notion_props)
```

#### 3. Query Leads

```python
@task
def query_leads(status: str = None, min_score: int = None):
    """
    Query leads from Notion with filters.

    Args:
        status: Filter by status (hot, warm, cold)
        min_score: Minimum lead score

    Returns:
        List of lead records
    """
    notion = Client(auth=NOTION_API_KEY)

    # Build filter
    filters = []

    if status:
        filters.append({
            "property": "Status",
            "select": {"equals": status}
        })

    if min_score is not None:
        filters.append({
            "property": "Score",
            "number": {"greater_than_or_equal_to": min_score}
        })

    # Query database
    if filters:
        query_filter = {"and": filters} if len(filters) > 1 else filters[0]
    else:
        query_filter = None

    results = notion.databases.query(
        database_id=NOTION_LEADS_DB_ID,
        filter=query_filter
    )

    # Parse results
    leads = []
    for page in results["results"]:
        props = page["properties"]

        leads.append({
            "notion_id": page["id"],
            "email": props.get("Email", {}).get("title", [{}])[0].get("plain_text", ""),
            "first_name": props.get("Name", {}).get("rich_text", [{}])[0].get("plain_text", ""),
            "score": props.get("Score", {}).get("number", 0),
            "status": props.get("Status", {}).get("select", {}).get("name", "new"),
            "stage": props.get("Stage", {}).get("select", {}).get("name", "opted_in")
        })

    return leads
```

### Advanced Features

#### 1. Bi-Directional Sync Flow

```python
from prefect import flow

@flow(name="notion-sync-bidirectional")
def sync_notion_with_external(external_data: list):
    """
    Sync external data (email engagement, website activity) with Notion.

    Args:
        external_data: List of records from external sources
    """

    for record in external_data:
        # Find existing lead by email
        existing_leads = query_leads_by_email(record["email"])

        if existing_leads:
            # Update existing lead
            update_lead(
                notion_id=existing_leads[0]["notion_id"],
                properties={
                    "score": record["score"],
                    "last_email_sent": record["last_email_date"]
                }
            )
        else:
            # Create new lead
            create_lead(
                email=record["email"],
                first_name=record["first_name"],
                segment=record["segment"]
            )
```

#### 2. Bulk Operations

```python
@task
def bulk_update_leads(updates: list):
    """
    Bulk update multiple leads efficiently.

    Args:
        updates: List of {notion_id, properties} dicts
    """
    notion = Client(auth=NOTION_API_KEY)

    for update in updates:
        try:
            update_lead(update["notion_id"], update["properties"])
        except Exception as e:
            print(f"❌ Failed to update {update['notion_id']}: {e}")
```

## Rate Limits

Notion API limits:
- **3 requests/second** per integration
- **1000 requests/minute** (temporary burst)

**Best Practices:**
```python
import time

@task(retries=3, retry_delay_seconds=5)
def rate_limited_notion_update(notion_id: str, properties: dict):
    """Update with rate limit handling."""

    try:
        update_lead(notion_id, properties)
    except Exception as e:
        if "rate_limited" in str(e):
            time.sleep(2)  # Wait 2 seconds
            raise  # Retry
        else:
            raise
```

## Error Handling

```python
@task(retries=3, retry_delay_seconds=30)
def safe_notion_operation(operation_func, *args, **kwargs):
    """Wrapper for safe Notion operations."""

    try:
        return operation_func(*args, **kwargs)

    except APIResponseError as e:
        if e.code == "rate_limited":
            print("⚠️ Rate limited, retrying...")
            raise  # Will retry

        elif e.code == "object_not_found":
            print(f"❌ Object not found: {e}")
            return None  # Don't retry

        else:
            print(f"❌ Notion API error: {e}")
            raise
```

## Best Practices

1. **Database Structure**: Plan property types carefully (can't change later)
2. **Rate Limiting**: Batch operations and add delays
3. **Error Handling**: Use retries for transient errors
4. **Data Validation**: Validate before creating/updating
5. **Performance**: Query with filters to reduce data transfer
6. **Security**: Never log API keys or sensitive data

## Common Issues

### Issue 1: "Object not found"

**Solution:**
```bash
# Verify database is shared with integration
# In Notion: Database → Share → Add your integration
```

### Issue 2: "Validation failed"

**Solution:**
```python
# Check property types match database schema
# Notion is strict about property formats
```

### Issue 3: Rate Limit Errors

**Solution:**
```python
# Add exponential backoff
@task(retries=5, retry_delay_seconds=5, retry_jitter_factor=0.5)
def notion_operation(...):
    # Implementation
```

## Resources

- [Notion API Documentation](https://developers.notion.com/)
- [notion-client Python Library](https://github.com/ramnes/notion-sdk-py)
- [Property Types Reference](https://developers.notion.com/reference/property-value-object)
- [Filter Reference](https://developers.notion.com/reference/post-database-query-filter)

## Next Steps

1. ✅ Create Notion integration and get API key
2. ✅ Set up database structures (Leads, Visitors, Content, Analytics)
3. ✅ Share databases with your integration
4. ✅ Test API connection with Python script
5. ✅ Integrate with Prefect flows
6. ✅ Set up bi-directional sync
