"""
Resend API operations for Christmas Campaign email sending.

This module provides Prefect tasks for:
- Sending emails via Resend API
- Template variable substitution
- Email delivery tracking

All tasks include retry logic for API failures.

Author: Christmas Campaign Team
Created: 2025-11-16
"""

from prefect import task
from prefect.blocks.system import Secret
import resend
import os
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables (fallback for local development)
load_dotenv()

# Configure Resend API
# Try Prefect Secret blocks first, fallback to environment variables
try:
    RESEND_API_KEY = Secret.load("resend-api-key").get()
    print("✅ Loaded Resend API key from Prefect Secret blocks")
except Exception as e:
    print(f"⚠️  Failed to load from Secret blocks, using environment variables: {e}")
    RESEND_API_KEY = os.getenv("RESEND_API_KEY")

resend.api_key = RESEND_API_KEY

# Sender configuration - using verified galatek.dev domain with alias
FROM_EMAIL = "value@galatek.dev"
FROM_NAME = "Sang Le - BusOS"


@task(retries=3, retry_delay_seconds=30, name="christmas-send-email")
def send_email(
    to_email: str,
    subject: str,
    html_body: str
) -> str:
    """
    Send email via Resend API.

    Args:
        to_email: Recipient email address
        subject: Email subject line
        html_body: HTML email body

    Returns:
        Resend email ID

    Raises:
        Exception: If email send fails after retries

    Example:
        email_id = send_email(
            to_email="john@testcorp.com",
            subject="Your BusOS Results",
            html_body="<html><body>Hi John...</body></html>"
        )
    """
    try:
        params = {
            "from": f"{FROM_NAME} <{FROM_EMAIL}>",
            "to": [to_email],
            "subject": subject,
            "html": html_body
        }

        response = resend.Emails.send(params)

        print(f"✅ Email sent to {to_email}: {response['id']}")
        return response["id"]

    except Exception as e:
        print(f"❌ Error sending email to {to_email}: {e}")
        raise


@task(name="christmas-substitute-variables")
def substitute_variables(
    template: str,
    variables: Dict[str, Any]
) -> str:
    """
    Replace {{variable}} placeholders in template with actual values.

    Args:
        template: Template string with {{variable}} placeholders
        variables: Dictionary of variable names and values

    Returns:
        Template with variables substituted

    Example:
        html = substitute_variables(
            template="Hi {{first_name}}, your score is {{assessment_score}}!",
            variables={"first_name": "John", "assessment_score": 45}
        )
        # Result: "Hi John, your score is 45!"
    """
    result = template

    for key, value in variables.items():
        # Replace {{key}} with value
        pattern = r'\{\{' + re.escape(key) + r'\}\}'
        result = re.sub(pattern, str(value), result)

    return result


@task(retries=3, retry_delay_seconds=30, name="christmas-send-template-email")
def send_template_email(
    to_email: str,
    subject: str,
    template: str,
    variables: Dict[str, Any]
) -> str:
    """
    Send email with template variable substitution.

    This is the primary email sending function used by flows.

    Args:
        to_email: Recipient email address
        subject: Email subject line
        template: HTML template with {{variable}} placeholders
        variables: Dictionary of variable names and values

    Returns:
        Resend email ID

    Example:
        send_template_email(
            to_email="john@testcorp.com",
            subject="Your BusOS Results",
            template="<html><body>Hi {{first_name}}...</body></html>",
            variables={"first_name": "John", "assessment_score": 45}
        )
    """
    # Substitute variables in template
    final_html = substitute_variables(template, variables)

    # Substitute variables in subject line too
    final_subject = substitute_variables(subject, variables)

    # Send email
    return send_email(to_email, final_subject, final_html)


@task(name="christmas-get-email-variables")
def get_email_variables(
    first_name: str = "there",
    business_name: str = "your business",
    assessment_score: Optional[int] = None,
    segment: Optional[str] = None,
    diagnostic_call_date: Optional[str] = None,
    portal_url: Optional[str] = None,
    # Additional assessment data for 5-Day sequence templates
    red_systems: Optional[int] = None,
    orange_systems: Optional[int] = None,
    yellow_systems: Optional[int] = None,
    green_systems: Optional[int] = None,
    gps_score: Optional[int] = None,
    money_score: Optional[int] = None,
    weakest_system_1: Optional[str] = None,
    weakest_system_2: Optional[str] = None,
    strongest_system: Optional[str] = None,
    revenue_leak_total: Optional[int] = None,
    calendly_link: Optional[str] = None
) -> Dict[str, Any]:
    """
    Build email variables dictionary for template substitution.

    This function prepares ALL variables needed for the 5-Day email sequence:
    - E1: 12 variables (TotalRevenueLeak_K, first_name, overall_score, etc.)
    - E2: 2 variables (first_name, WeakestSystem1)
    - E3-E5: 0 variables (static templates)

    Variables are provided in BOTH snake_case and CamelCase for template compatibility.

    Args:
        first_name: Contact first name (default: "there")
        business_name: Business name (default: "your business")
        assessment_score: BusOS overall score (0-100)
        segment: Contact segment (CRITICAL/URGENT/OPTIMIZE)
        diagnostic_call_date: Scheduled call date (optional)
        portal_url: Customer portal URL (optional)
        red_systems: Number of red (broken) systems
        orange_systems: Number of orange (struggling) systems
        yellow_systems: Number of yellow (functional) systems
        green_systems: Number of green (optimized) systems
        gps_score: GPS system score (optional)
        money_score: Money system score (optional)
        weakest_system_1: First weakest system name
        weakest_system_2: Second weakest system name
        strongest_system: Strongest system name
        revenue_leak_total: Total revenue leak estimate
        calendly_link: Calendly booking link

    Returns:
        Dictionary of variables for template substitution (both cases)

    Example:
        variables = get_email_variables(
            first_name="Sarah",
            business_name="Sarah's Salon",
            assessment_score=45,
            segment="CRITICAL",
            weakest_system_1="GPS",
            weakest_system_2="FUEL",
            strongest_system="CABIN",
            revenue_leak_total=14700
        )
        # Result includes: first_name, WeakestSystem1, TotalRevenueLeak_K, etc.
    """
    from datetime import datetime

    # Calculate days to deadline (December 5, 2025)
    deadline_date = "December 5, 2025"
    deadline = datetime(2025, 12, 5)
    today = datetime.now()
    days_to_deadline = max(0, (deadline - today).days)

    # Determine readiness zone based on segment
    readiness_zones = {
        "CRITICAL": "Crisis Zone",
        "URGENT": "Warning Zone",
        "OPTIMIZE": "Growth Zone"
    }
    readiness_zone = readiness_zones.get(segment, "Growth Zone")

    # Generate personalized tips based on weakest systems
    tips = _generate_personalized_tips(weakest_system_1, weakest_system_2)

    # Calculate revenue leak in K
    total_revenue_leak_k = round(revenue_leak_total / 1000) if revenue_leak_total else 0

    # Default calendly link
    default_calendly = "https://cal.com/sangletech/discovery-call"

    # Build variables dictionary with BOTH snake_case and CamelCase
    variables = {
        # Core variables (snake_case)
        "first_name": first_name,
        "business_name": business_name,

        # Assessment data (snake_case)
        "overall_score": str(assessment_score) if assessment_score is not None else "N/A",
        "assessment_score": str(assessment_score) if assessment_score is not None else "N/A",
        "segment": segment or "OPTIMIZE",
        "readiness_zone": readiness_zone,

        # Weakest/Strongest systems (snake_case)
        "weakest_system_1": weakest_system_1 or "GPS",
        "weakest_system_2": weakest_system_2 or "FUEL",
        "strongest_system": strongest_system or "CABIN",

        # CamelCase variants for templates
        "WeakestSystem1": weakest_system_1 or "GPS",
        "WeakestSystem2": weakest_system_2 or "FUEL",
        "StrongestSystem": strongest_system or "CABIN",

        # Revenue leak (snake_case and template format)
        "revenue_leak_total": str(revenue_leak_total) if revenue_leak_total else "0",
        "TotalRevenueLeak_K": str(total_revenue_leak_k),

        # Deadline info
        "days_to_deadline": str(days_to_deadline),
        "deadline_date": deadline_date,

        # Personalized tips
        "personalized_tip_1": tips[0],
        "personalized_tip_2": tips[1],
        "personalized_tip_3": tips[2],

        # Links
        "calendly_link": calendly_link or default_calendly,

        # System counts (for debugging/analytics)
        "red_systems": str(red_systems) if red_systems is not None else "0",
        "orange_systems": str(orange_systems) if orange_systems is not None else "0",
        "yellow_systems": str(yellow_systems) if yellow_systems is not None else "0",
        "green_systems": str(green_systems) if green_systems is not None else "0",

        # NEW: Additional variables for 5-Day email templates (E3-E5)
        # These are used in the beautifully formatted HTML templates
        # NOTE: pdf_download_link now points to assessment results page (stores user's results)
        "pdf_download_link": "https://sangletech.com/en/flows/businessX/dfu/xmas-a01/assessment",
        "spots_remaining": "12",  # Dynamic spot counter
        "bookings_count": "18",   # Number of bookings this week
        "weakest_system": weakest_system_1 or "GPS",  # Alias for weakest_system_1
    }

    # Add optional fields if provided
    if diagnostic_call_date:
        variables["diagnostic_call_date"] = diagnostic_call_date

    if portal_url:
        variables["portal_url"] = portal_url

    return variables


def _generate_personalized_tips(weakest1: Optional[str], weakest2: Optional[str]) -> list:
    """
    Generate personalized tips based on weakest systems.

    Args:
        weakest1: First weakest system name
        weakest2: Second weakest system name

    Returns:
        List of 3 personalized tips
    """
    tips_by_system = {
        "GPS": "Map your customer journey from first contact to payment in a Google Doc",
        "CREW": "Write down 3 tasks you do every day that someone else could do with a checklist",
        "ENGINE": "List your top 3 services by profit margin (not revenue)",
        "FUEL": "Track where your last 10 clients came from",
        "CABIN": "Send a 'How are we doing?' text to 5 recent clients today",
        "COCKPIT": "Check if you know your exact profit margin per service",
        "RADAR": "Create a simple spreadsheet tracking daily bookings for 1 week",
        "AUTOPILOT": "Identify 1 task you do manually that could be automated"
    }

    tips = []

    # Tip 1: Based on weakest system
    if weakest1:
        w1_key = next((k for k in tips_by_system.keys() if weakest1.upper().find(k) != -1), None)
        tips.append(tips_by_system.get(w1_key, tips_by_system["GPS"]))
    else:
        tips.append(tips_by_system["GPS"])

    # Tip 2: Based on second weakest or default
    if weakest2:
        w2_key = next((k for k in tips_by_system.keys() if weakest2.upper().find(k) != -1), None)
        tips.append(tips_by_system.get(w2_key, tips_by_system["CREW"]))
    else:
        tips.append(tips_by_system["CREW"])

    # Tip 3: General holiday prep
    tips.append("Block 2 hours this weekend to plan your December capacity.")

    return tips
