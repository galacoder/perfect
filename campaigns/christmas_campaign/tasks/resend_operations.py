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
import resend
import os
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Resend API
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
resend.api_key = RESEND_API_KEY

# Sender configuration
FROM_EMAIL = "noreply@sangletech.com"
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
    portal_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Build email variables dictionary for template substitution.

    Args:
        first_name: Contact first name (default: "there")
        business_name: Business name (default: "your business")
        assessment_score: BusOS score (optional)
        segment: Contact segment (optional)
        diagnostic_call_date: Scheduled call date (optional)
        portal_url: Customer portal URL (optional)

    Returns:
        Dictionary of variables for template substitution

    Example:
        variables = get_email_variables(
            first_name="John",
            business_name="Test Corp",
            assessment_score=45,
            segment="URGENT"
        )
        # Result: {
        #     "first_name": "John",
        #     "business_name": "Test Corp",
        #     "assessment_score": "45",
        #     "segment": "URGENT"
        # }
    """
    variables = {
        "first_name": first_name,
        "business_name": business_name
    }

    if assessment_score is not None:
        variables["assessment_score"] = str(assessment_score)

    if segment:
        variables["segment"] = segment

    if diagnostic_call_date:
        variables["diagnostic_call_date"] = diagnostic_call_date

    if portal_url:
        variables["portal_url"] = portal_url

    return variables


# ==============================================================================
# Fallback Email Templates (Static)
# ==============================================================================

def get_fallback_template(template_id: str) -> Dict[str, str]:
    """
    Get fallback email template if Notion fetch fails.

    These are minimal templates used only when Notion is unavailable.
    Production templates should be managed in Notion Email Templates database.

    Args:
        template_id: Template identifier

    Returns:
        Dict with 'subject' and 'html_body' keys

    Example:
        template = get_fallback_template("christmas_email_1")
    """
    templates = {
        "christmas_email_1": {
            "subject": "Your BusOS Assessment Results",
            "html_body": """
            <html>
            <body>
                <h1>Your BusOS Assessment Results</h1>
                <p>Hi {{first_name}},</p>
                <p>Thanks for completing the BusOS assessment for {{business_name}}!</p>
                <p>Your BusOS Score: {{assessment_score}}/100</p>
                <p>We'll send you more personalized insights over the next few days.</p>
                <p>Best,<br>Sang Le</p>
            </body>
            </html>
            """
        },
        "christmas_email_2": {
            "subject": "3 Quick Wins for {{business_name}}",
            "html_body": """
            <html>
            <body>
                <h1>3 Quick Wins for {{business_name}}</h1>
                <p>Hi {{first_name}},</p>
                <p>Based on your assessment results, here are 3 immediate actions you can take...</p>
                <p>Best,<br>Sang Le</p>
            </body>
            </html>
            """
        },
        # Add more fallback templates as needed
    }

    return templates.get(template_id, {
        "subject": "Update from BusOS",
        "html_body": "<html><body><p>Hi {{first_name}},</p><p>Thanks for being part of BusOS!</p></body></html>"
    })
