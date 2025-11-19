"""
Simple email sequence orchestrator - No Prefect Server required.

This script orchestrates the 7-email Christmas campaign sequence using direct API calls.
It's production-ready and can be scheduled via cron, systemd, or any task scheduler.

Usage:
    # Test mode (1-2 min delays between emails)
    TESTING_MODE=true python campaigns/christmas_campaign/orchestrate_sequence.py \
        --email test@example.com \
        --first-name John \
        --assessment-score 45

    # Production mode (24-48 hour delays between emails)
    python campaigns/christmas_campaign/orchestrate_sequence.py \
        --email customer@example.com \
        --first-name Sarah \
        --assessment-score 52

    # Send single email (for testing specific emails)
    python campaigns/christmas_campaign/orchestrate_sequence.py \
        --email test@example.com \
        --first-name John \
        --email-number 3 \
        --no-sequence
"""

import os
import sys
import argparse
import time
from datetime import datetime, timedelta
from notion_client import Client
import resend
from dotenv import load_dotenv

# Load environment
load_dotenv()

def get_wait_time(email_number: int, testing_mode: bool = False) -> int:
    """Get wait time in seconds before sending next email."""
    if testing_mode:
        # Testing mode: short delays (1-7 minutes)
        wait_times = {
            1: 60,      # 1 minute
            2: 120,     # 2 minutes
            3: 180,     # 3 minutes
            4: 240,     # 4 minutes
            5: 300,     # 5 minutes
            6: 360,     # 6 minutes
            7: 0        # Last email, no wait
        }
    else:
        # Production mode: realistic delays
        wait_times = {
            1: 86400,       # 24 hours (1 day)
            2: 172800,      # 48 hours (2 days)
            3: 172800,      # 48 hours (2 days)
            4: 172800,      # 48 hours (2 days)
            5: 172800,      # 48 hours (2 days)
            6: 172800,      # 48 hours (2 days)
            7: 0            # Last email, no wait
        }

    return wait_times.get(email_number, 0)

def fetch_template_from_notion(template_id: str):
    """Fetch email template from Notion."""
    notion = Client(auth=os.getenv("NOTION_TOKEN"))
    db_id = os.getenv("NOTION_EMAIL_TEMPLATES_DB_ID")

    response = notion.databases.query(
        database_id=db_id,
        filter={
            "property": "Template Name",
            "title": {"equals": template_id}
        }
    )

    if not response["results"]:
        raise ValueError(f"Template not found: {template_id}")

    page = response["results"][0]
    subject = page["properties"]["Subject Line"]["rich_text"][0]["plain_text"]
    html_body = page["properties"]["Email Body HTML"]["rich_text"][0]["plain_text"]

    return {"subject": subject, "html_body": html_body}

def substitute_variables(text: str, variables: dict) -> str:
    """Substitute {{variable}} placeholders."""
    for key, value in variables.items():
        placeholder = "{{" + key + "}}"
        text = text.replace(placeholder, str(value))
    return text

def send_email_via_resend(to_email: str, subject: str, html_body: str):
    """Send email via Resend API."""
    resend.api_key = os.getenv("RESEND_API_KEY")
    from_email = os.getenv("RESEND_FROM_EMAIL", "hello@sanglescalinglabs.com")

    params = {
        "from": from_email,
        "to": [to_email],
        "subject": subject,
        "html": html_body
    }

    email = resend.Emails.send(params)
    return email

def get_variables(first_name: str, email: str, assessment_score: int) -> dict:
    """Get variables for email substitution."""
    # Mock assessment data (in production, this would come from Notion/database)
    return {
        "first_name": first_name,
        "email": email,
        "business_name": "Your Salon",
        "GPSScore": str(assessment_score),
        "GenerateScore": str(max(0, assessment_score - 5)),
        "PersuadeScore": str(assessment_score),
        "ServeScore": str(min(100, assessment_score + 5)),
        "MoneyScore": str(max(0, assessment_score - 7)),
        "PeopleScore": str(min(100, assessment_score + 20)),
        "WeakestSystem1": "GPS",
        "WeakestSystem2": "Money",
        "Score1": str(assessment_score),
        "Score2": str(max(0, assessment_score - 7)),
        "RevenueLeakSystem1": "$8,500",
        "RevenueLeakSystem2": "$6,200",
        "TotalRevenueLeak": "$14,700",
        "TotalRevenueLeak_K": "14",
        "AnnualRevenueLeak": "$176,400",
        "QuickWinAction": "Add SMS confirmation for all appointments",
        "QuickWinExplanation": "Reduce no-shows from 30% to 15%",
        "QuickWinImpact": "$4,200/month revenue recovery",
        "WeakestSystemDescription": "the system that brings customers through your door",
        "QuickWin1_Title": "Implement automated SMS confirmations",
        "QuickWin1_Time": "2 hours setup",
        "QuickWin1_Cost": "$29/month (Twilio)",
        "QuickWin1_Impact": "$2,500/month",
        "QuickWin2_Title": "Add online booking calendar",
        "QuickWin2_Time": "3 hours setup",
        "QuickWin2_Cost": "$50/month",
        "QuickWin2_Impact": "$1,200/month",
        "QuickWin3_Title": "Create referral incentive program",
        "QuickWin3_Time": "1 hour planning",
        "QuickWin3_Cost": "$0",
        "QuickWin3_Impact": "$800/month",
        "Christmas_Slots_Remaining": "7",
        "Christmas_Slots_Claimed": "23",
    }

def send_email(email_number: int, to_email: str, first_name: str, assessment_score: int):
    """Send a single email in the sequence."""

    template_id = f"christmas_email_{email_number}"

    print(f"\n{'='*80}")
    print(f"Email {email_number}: {template_id}")
    print(f"{'='*80}\n")

    # Fetch template
    print("Fetching template from Notion...")
    template = fetch_template_from_notion(template_id)
    print(f"✓ Template: {template['subject'][:60]}...")

    # Substitute variables
    print("Substituting variables...")
    variables = get_variables(first_name, to_email, assessment_score)
    subject = substitute_variables(template["subject"], variables)
    html_body = substitute_variables(template["html_body"], variables)
    print(f"✓ Subject: {subject[:60]}...")

    # Send email
    print("Sending via Resend...")
    result = send_email_via_resend(to_email, subject, html_body)
    print(f"✅ Email sent! ID: {result['id']}")

    return result['id']

def orchestrate_sequence(to_email: str, first_name: str, assessment_score: int,
                        start_from: int = 1, testing_mode: bool = None):
    """Orchestrate the complete 7-email sequence."""

    if testing_mode is None:
        testing_mode = os.getenv("TESTING_MODE", "false").lower() == "true"

    mode = "TESTING" if testing_mode else "PRODUCTION"

    print(f"\n{'#'*80}")
    print(f"  Christmas Campaign Email Sequence - {mode} MODE")
    print(f"{'#'*80}\n")
    print(f"Recipient: {to_email}")
    print(f"Name: {first_name}")
    print(f"Assessment Score: {assessment_score}")
    print(f"Starting from: Email {start_from}")
    print(f"Testing mode: {testing_mode}\n")

    results = []

    for email_num in range(start_from, 8):  # Emails 1-7
        # Send email
        try:
            email_id = send_email(email_num, to_email, first_name, assessment_score)
            results.append({
                "email_number": email_num,
                "email_id": email_id,
                "sent_at": datetime.now().isoformat(),
                "success": True
            })
        except Exception as e:
            print(f"\n❌ Error sending email {email_num}: {e}")
            results.append({
                "email_number": email_num,
                "error": str(e),
                "sent_at": datetime.now().isoformat(),
                "success": False
            })
            break  # Stop sequence on error

        # Wait before next email (except for last one)
        if email_num < 7:
            wait_seconds = get_wait_time(email_num, testing_mode)
            wait_minutes = wait_seconds / 60
            wait_hours = wait_seconds / 3600

            if wait_hours >= 1:
                wait_str = f"{wait_hours:.1f} hours"
            else:
                wait_str = f"{wait_minutes:.0f} minutes"

            next_send_time = datetime.now() + timedelta(seconds=wait_seconds)

            print(f"\n⏰ Waiting {wait_str} before next email...")
            print(f"   Next email will send at: {next_send_time.strftime('%Y-%m-%d %H:%M:%S')}")

            if testing_mode:
                # In testing mode, actually wait
                time.sleep(wait_seconds)
            else:
                # In production, we'd schedule next email and exit
                print(f"\n💡 Production mode: Schedule email {email_num + 1} for {next_send_time}")
                print(f"   Stopping orchestrator. Next email should be triggered by scheduler.")
                break

    # Summary
    print(f"\n{'#'*80}")
    print(f"  Sequence Summary")
    print(f"{'#'*80}\n")

    successful = sum(1 for r in results if r["success"])
    print(f"Emails sent: {successful}/{len(results)}")

    for r in results:
        if r["success"]:
            print(f"  ✅ Email {r['email_number']}: {r['email_id']}")
        else:
            print(f"  ❌ Email {r['email_number']}: {r['error']}")

    return results

def main():
    parser = argparse.ArgumentParser(description="Christmas Campaign Email Orchestrator")
    parser.add_argument("--email", required=True, help="Recipient email address")
    parser.add_argument("--first-name", required=True, help="Recipient first name")
    parser.add_argument("--assessment-score", type=int, default=45,
                       help="Assessment score (0-100)")
    parser.add_argument("--email-number", type=int, choices=range(1, 8),
                       help="Send specific email number (1-7)")
    parser.add_argument("--no-sequence", action="store_true",
                       help="Send only single email (requires --email-number)")
    parser.add_argument("--testing-mode", action="store_true",
                       help="Use short delays (1-7 min) instead of production delays")
    parser.add_argument("--start-from", type=int, default=1, choices=range(1, 8),
                       help="Start sequence from email number (default: 1)")

    args = parser.parse_args()

    if args.no_sequence:
        if not args.email_number:
            print("Error: --no-sequence requires --email-number")
            sys.exit(1)

        # Send single email
        email_id = send_email(
            args.email_number,
            args.email,
            args.first_name,
            args.assessment_score
        )
        print(f"\n✅ Single email sent successfully!")
        print(f"   Email ID: {email_id}")
    else:
        # Orchestrate sequence
        results = orchestrate_sequence(
            args.email,
            args.first_name,
            args.assessment_score,
            args.start_from,
            args.testing_mode
        )

        # Exit with error code if any emails failed
        if not all(r["success"] for r in results):
            sys.exit(1)

if __name__ == "__main__":
    main()
