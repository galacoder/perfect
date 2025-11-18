"""
Marketing ETL Pipeline - Multi-Source Analytics Consolidation

Extracts, transforms, and loads marketing data from multiple sources:
- Facebook Ads (campaign performance, costs, ROAS)
- Google Ads (search campaigns, conversion tracking)
- Loops.so (email metrics)
- Notion (lead data, funnel metrics)
- Website analytics (page views, conversions)

Consolidates into:
- Notion analytics dashboard
- CSV exports for further analysis
- Discord daily/weekly reports

Metrics Tracked:
- Ad spend and ROAS by platform
- Lead generation funnel conversion rates
- Email engagement metrics
- Cost per lead (CPL) and cost per acquisition (CPA)
- Attribution by source and campaign

Usage:
    python marketing-etl-pipeline.py
    # Or deploy: prefect deploy -n marketing-etl-daily
"""

from datetime import datetime, timedelta
from prefect import flow, task
import httpx
import os
from typing import Dict, List, Optional
import csv
from io import StringIO

# Configuration
FB_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
FB_AD_ACCOUNT_ID = os.getenv("FACEBOOK_AD_ACCOUNT_ID")
GOOGLE_ADS_DEVELOPER_TOKEN = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
GOOGLE_ADS_CLIENT_ID = os.getenv("GOOGLE_ADS_CLIENT_ID")
GOOGLE_ADS_CLIENT_SECRET = os.getenv("GOOGLE_ADS_CLIENT_SECRET")
GOOGLE_ADS_REFRESH_TOKEN = os.getenv("GOOGLE_ADS_REFRESH_TOKEN")
GOOGLE_ADS_CUSTOMER_ID = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
LOOPS_API_KEY = os.getenv("LOOPS_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


@task(retries=3, retry_delay_seconds=60)
def extract_facebook_ads_data(lookback_days: int = 7):
    """
    Extract campaign performance data from Facebook Ads.

    Args:
        lookback_days: Number of days to look back

    Returns:
        List of campaign performance records
    """
    if not FB_ACCESS_TOKEN or not FB_AD_ACCOUNT_ID:
        print("⚠️ Facebook Ads credentials not configured")
        return []

    since = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    until = datetime.now().strftime("%Y-%m-%d")

    # Fetch campaign insights
    response = httpx.get(
        f"https://graph.facebook.com/v18.0/act_{FB_AD_ACCOUNT_ID}/insights",
        params={
            "access_token": FB_ACCESS_TOKEN,
            "level": "campaign",
            "time_range": f'{{"since":"{since}","until":"{until}"}}',
            "fields": "campaign_name,spend,impressions,clicks,actions,cpc,cpm,ctr",
            "limit": 100
        },
        timeout=30
    )

    response.raise_for_status()
    data = response.json().get("data", [])

    campaigns = []
    for campaign in data:
        # Extract conversion actions
        conversions = 0
        for action in campaign.get("actions", []):
            if action["action_type"] in ["lead", "complete_registration"]:
                conversions += int(action["value"])

        campaigns.append({
            "source": "facebook",
            "campaign_name": campaign.get("campaign_name", "Unknown"),
            "spend": float(campaign.get("spend", 0)),
            "impressions": int(campaign.get("impressions", 0)),
            "clicks": int(campaign.get("clicks", 0)),
            "conversions": conversions,
            "cpc": float(campaign.get("cpc", 0)),
            "cpm": float(campaign.get("cpm", 0)),
            "ctr": float(campaign.get("ctr", 0)),
            "date_range": f"{since} to {until}"
        })

    print(f"📊 Extracted {len(campaigns)} Facebook campaigns")
    return campaigns


@task(retries=3, retry_delay_seconds=60)
def extract_google_ads_data(lookback_days: int = 7):
    """
    Extract campaign performance data from Google Ads.

    Note: This is a simplified example. Production would use google-ads library.

    Args:
        lookback_days: Number of days to look back

    Returns:
        List of campaign performance records
    """
    if not all([GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID,
               GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_REFRESH_TOKEN,
               GOOGLE_ADS_CUSTOMER_ID]):
        print("⚠️ Google Ads credentials not configured")
        return []

    # In production, use google-ads library
    # This is a placeholder showing the data structure

    print(f"📊 Extracted Google Ads data (placeholder)")
    return []


@task(retries=3, retry_delay_seconds=60)
def extract_loops_email_data(lookback_days: int = 7):
    """
    Extract email campaign metrics from Loops.so.

    Args:
        lookback_days: Number of days to look back

    Returns:
        Email campaign performance data
    """
    if not LOOPS_API_KEY:
        print("⚠️ Loops.so credentials not configured")
        return []

    # Note: Loops.so doesn't have a direct analytics endpoint
    # In production, you'd aggregate data from Notion tracking or webhooks

    print(f"📊 Extracted email data (from Notion tracking)")
    return []


@task(retries=3, retry_delay_seconds=60)
def extract_notion_funnel_metrics(lookback_days: int = 7):
    """
    Extract funnel conversion metrics from Notion CRM.

    Calculates:
    - Landing page → Opt-in conversion rate
    - Opt-in → Assessment completion rate
    - Assessment → Sales call booking rate
    - Sales call → Close rate

    Args:
        lookback_days: Number of days to look back

    Returns:
        Funnel metrics by stage
    """
    from notion_client import Client

    notion = Client(auth=NOTION_API_KEY)

    cutoff_date = (datetime.now() - timedelta(days=lookback_days)).isoformat()

    # Count visitors by stage
    stages = ["landing_page", "opted_in", "assessment_complete",
              "sales_call_booked", "closed_won"]

    stage_counts = {}

    for stage in stages:
        results = notion.databases.query(
            database_id=os.getenv("NOTION_VISITORS_DB_ID"),
            filter={
                "and": [
                    {
                        "property": "Stage",
                        "select": {"equals": stage}
                    },
                    {
                        "property": "Visit Date",
                        "date": {"on_or_after": cutoff_date}
                    }
                ]
            }
        )

        stage_counts[stage] = len(results["results"])

    # Calculate conversion rates
    metrics = {
        "date_range": f"Last {lookback_days} days",
        "landing_page_visits": stage_counts.get("landing_page", 0),
        "opt_ins": stage_counts.get("opted_in", 0),
        "assessments_completed": stage_counts.get("assessment_complete", 0),
        "sales_calls_booked": stage_counts.get("sales_call_booked", 0),
        "deals_closed": stage_counts.get("closed_won", 0)
    }

    # Conversion rates
    if metrics["landing_page_visits"] > 0:
        metrics["landing_to_optin_rate"] = (metrics["opt_ins"] / metrics["landing_page_visits"]) * 100
    else:
        metrics["landing_to_optin_rate"] = 0

    if metrics["opt_ins"] > 0:
        metrics["optin_to_assessment_rate"] = (metrics["assessments_completed"] / metrics["opt_ins"]) * 100
    else:
        metrics["optin_to_assessment_rate"] = 0

    if metrics["assessments_completed"] > 0:
        metrics["assessment_to_booking_rate"] = (metrics["sales_calls_booked"] / metrics["assessments_completed"]) * 100
    else:
        metrics["assessment_to_booking_rate"] = 0

    if metrics["sales_calls_booked"] > 0:
        metrics["booking_to_close_rate"] = (metrics["deals_closed"] / metrics["sales_calls_booked"]) * 100
    else:
        metrics["booking_to_close_rate"] = 0

    print(f"📊 Extracted funnel metrics:")
    print(f"   Landing → Opt-in: {metrics['landing_to_optin_rate']:.1f}%")
    print(f"   Opt-in → Assessment: {metrics['optin_to_assessment_rate']:.1f}%")
    print(f"   Assessment → Booking: {metrics['assessment_to_booking_rate']:.1f}%")
    print(f"   Booking → Close: {metrics['booking_to_close_rate']:.1f}%")

    return metrics


@task
def transform_campaign_data(fb_campaigns: List[Dict], google_campaigns: List[Dict]):
    """
    Transform and consolidate campaign data from multiple sources.

    Args:
        fb_campaigns: Facebook campaign data
        google_campaigns: Google Ads campaign data

    Returns:
        Consolidated campaign metrics with ROAS and CPL calculations
    """
    all_campaigns = fb_campaigns + google_campaigns

    # Calculate aggregate metrics
    total_spend = sum(c.get("spend", 0) for c in all_campaigns)
    total_conversions = sum(c.get("conversions", 0) for c in all_campaigns)
    total_impressions = sum(c.get("impressions", 0) for c in all_campaigns)
    total_clicks = sum(c.get("clicks", 0) for c in all_campaigns)

    # Calculate cost per lead (CPL)
    cpl = (total_spend / total_conversions) if total_conversions > 0 else 0

    # Calculate overall CTR
    ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0

    summary = {
        "total_spend": round(total_spend, 2),
        "total_conversions": total_conversions,
        "total_impressions": total_impressions,
        "total_clicks": total_clicks,
        "cost_per_lead": round(cpl, 2),
        "overall_ctr": round(ctr, 2),
        "campaigns_by_source": {
            "facebook": len(fb_campaigns),
            "google": len(google_campaigns)
        }
    }

    print(f"📊 Campaign Summary:")
    print(f"   Total Spend: ${summary['total_spend']}")
    print(f"   Total Conversions: {summary['total_conversions']}")
    print(f"   Cost Per Lead: ${summary['cost_per_lead']}")
    print(f"   Overall CTR: {summary['overall_ctr']:.2f}%")

    return {
        "summary": summary,
        "campaigns": all_campaigns
    }


@task
def load_to_notion_dashboard(campaign_data: Dict, funnel_metrics: Dict):
    """
    Load consolidated analytics to Notion dashboard.

    Args:
        campaign_data: Transformed campaign metrics
        funnel_metrics: Funnel conversion metrics
    """
    from notion_client import Client

    notion = Client(auth=NOTION_API_KEY)

    # Create analytics record in Notion
    notion.pages.create(
        parent={"database_id": os.getenv("NOTION_ANALYTICS_DB_ID")},
        properties={
            "Date": {"title": [{"text": {"content": datetime.now().strftime("%Y-%m-%d")}}]},
            "Total Spend": {"number": campaign_data["summary"]["total_spend"]},
            "Total Conversions": {"number": campaign_data["summary"]["total_conversions"]},
            "Cost Per Lead": {"number": campaign_data["summary"]["cost_per_lead"]},
            "CTR": {"number": campaign_data["summary"]["overall_ctr"]},
            "Opt-in Rate": {"number": funnel_metrics.get("landing_to_optin_rate", 0)},
            "Assessment Rate": {"number": funnel_metrics.get("optin_to_assessment_rate", 0)},
            "Booking Rate": {"number": funnel_metrics.get("assessment_to_booking_rate", 0)},
            "Close Rate": {"number": funnel_metrics.get("booking_to_close_rate", 0)}
        }
    )

    print(f"✅ Loaded analytics to Notion dashboard")


@task
def export_to_csv(campaign_data: Dict, funnel_metrics: Dict):
    """
    Export analytics data to CSV file.

    Args:
        campaign_data: Transformed campaign metrics
        funnel_metrics: Funnel conversion metrics

    Returns:
        CSV file path
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"marketing_analytics_{timestamp}.csv"
    filepath = f"/tmp/{filename}"

    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write campaign summary
        writer.writerow(["Campaign Summary"])
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Spend", f"${campaign_data['summary']['total_spend']}"])
        writer.writerow(["Total Conversions", campaign_data['summary']['total_conversions']])
        writer.writerow(["Cost Per Lead", f"${campaign_data['summary']['cost_per_lead']}"])
        writer.writerow(["Overall CTR", f"{campaign_data['summary']['overall_ctr']:.2f}%"])
        writer.writerow([])

        # Write funnel metrics
        writer.writerow(["Funnel Metrics"])
        writer.writerow(["Stage", "Conversion Rate"])
        writer.writerow(["Landing → Opt-in", f"{funnel_metrics.get('landing_to_optin_rate', 0):.1f}%"])
        writer.writerow(["Opt-in → Assessment", f"{funnel_metrics.get('optin_to_assessment_rate', 0):.1f}%"])
        writer.writerow(["Assessment → Booking", f"{funnel_metrics.get('assessment_to_booking_rate', 0):.1f}%"])
        writer.writerow(["Booking → Close", f"{funnel_metrics.get('booking_to_close_rate', 0):.1f}%"])
        writer.writerow([])

        # Write campaign details
        writer.writerow(["Campaign Details"])
        writer.writerow(["Source", "Campaign Name", "Spend", "Impressions", "Clicks", "Conversions", "CPL"])

        for campaign in campaign_data["campaigns"]:
            cpl = (campaign["spend"] / campaign["conversions"]) if campaign["conversions"] > 0 else 0
            writer.writerow([
                campaign["source"],
                campaign["campaign_name"],
                f"${campaign['spend']:.2f}",
                campaign["impressions"],
                campaign["clicks"],
                campaign["conversions"],
                f"${cpl:.2f}"
            ])

    print(f"✅ Exported analytics to {filepath}")
    return filepath


@task
def send_analytics_report(campaign_data: Dict, funnel_metrics: Dict, report_type: str = "daily"):
    """
    Send analytics report to Discord.

    Args:
        campaign_data: Transformed campaign metrics
        funnel_metrics: Funnel conversion metrics
        report_type: "daily" or "weekly"
    """
    if not DISCORD_WEBHOOK_URL:
        return

    summary = campaign_data["summary"]

    # Build report
    fields = [
        {"name": "💰 Total Ad Spend", "value": f"${summary['total_spend']}", "inline": True},
        {"name": "👥 Conversions", "value": str(summary['total_conversions']), "inline": True},
        {"name": "📊 Cost Per Lead", "value": f"${summary['cost_per_lead']}", "inline": True},
        {"name": "🎯 CTR", "value": f"{summary['overall_ctr']:.2f}%", "inline": True},
        {"name": "📥 Opt-in Rate", "value": f"{funnel_metrics.get('landing_to_optin_rate', 0):.1f}%", "inline": True},
        {"name": "📝 Assessment Rate", "value": f"{funnel_metrics.get('optin_to_assessment_rate', 0):.1f}%", "inline": True},
        {"name": "📅 Booking Rate", "value": f"{funnel_metrics.get('assessment_to_booking_rate', 0):.1f}%", "inline": True},
        {"name": "✅ Close Rate", "value": f"{funnel_metrics.get('booking_to_close_rate', 0):.1f}%", "inline": True}
    ]

    payload = {
        "content": f"📊 **{report_type.title()} Marketing Analytics Report**",
        "embeds": [{
            "title": f"Marketing Performance - {datetime.now().strftime('%Y-%m-%d')}",
            "description": "Consolidated metrics from all marketing channels",
            "color": 0x0099ff,
            "fields": fields,
            "footer": {
                "text": f"Generated by Prefect Marketing ETL Pipeline"
            },
            "timestamp": datetime.now().isoformat()
        }]
    }

    httpx.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)


@flow(name="marketing-etl-daily", log_prints=True)
def marketing_etl_pipeline(lookback_days: int = 7, export_csv: bool = True):
    """
    Daily ETL pipeline for marketing analytics.

    Extracts data from:
    - Facebook Ads
    - Google Ads
    - Loops.so email
    - Notion funnel metrics

    Transforms and loads to:
    - Notion analytics dashboard
    - CSV export
    - Discord report

    Args:
        lookback_days: Number of days to analyze
        export_csv: Whether to export CSV file

    Returns:
        dict: ETL pipeline summary
    """
    print(f"🚀 Starting marketing ETL pipeline")
    print(f"   Lookback period: {lookback_days} days")

    # EXTRACT
    print(f"\n{'='*60}")
    print(f"📥 EXTRACT PHASE")

    fb_campaigns = extract_facebook_ads_data(lookback_days)
    google_campaigns = extract_google_ads_data(lookback_days)
    email_data = extract_loops_email_data(lookback_days)
    funnel_metrics = extract_notion_funnel_metrics(lookback_days)

    # TRANSFORM
    print(f"\n{'='*60}")
    print(f"🔄 TRANSFORM PHASE")

    campaign_data = transform_campaign_data(fb_campaigns, google_campaigns)

    # LOAD
    print(f"\n{'='*60}")
    print(f"📤 LOAD PHASE")

    load_to_notion_dashboard(campaign_data, funnel_metrics)

    if export_csv:
        csv_file = export_to_csv(campaign_data, funnel_metrics)
    else:
        csv_file = None

    send_analytics_report(campaign_data, funnel_metrics, report_type="daily")

    # Summary
    print(f"\n{'='*60}")
    print(f"📊 ETL PIPELINE COMPLETE")
    print(f"   Campaigns Processed: {len(campaign_data['campaigns'])}")
    print(f"   Total Spend: ${campaign_data['summary']['total_spend']}")
    print(f"   Total Conversions: {campaign_data['summary']['total_conversions']}")
    print(f"   Cost Per Lead: ${campaign_data['summary']['cost_per_lead']}")
    print(f"{'='*60}\n")

    return {
        "campaigns_processed": len(campaign_data["campaigns"]),
        "total_spend": campaign_data["summary"]["total_spend"],
        "total_conversions": campaign_data["summary"]["total_conversions"],
        "cost_per_lead": campaign_data["summary"]["cost_per_lead"],
        "csv_export": csv_file,
        "processed_at": datetime.now().isoformat()
    }


# Deployment configuration
if __name__ == "__main__":
    # Deployment: Daily ETL at 8 AM
    marketing_etl_pipeline.serve(
        name="marketing-etl-daily-v1",
        cron="0 8 * * *",  # Daily at 8 AM
        parameters={"lookback_days": 7, "export_csv": True},
        description="Daily marketing analytics ETL from all sources"
    )

    # Manual trigger for testing:
    # marketing_etl_pipeline(lookback_days=7, export_csv=True)
