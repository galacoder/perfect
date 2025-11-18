"""
Resend email operations for BusOS Email Sequence.

This module provides Prefect tasks for sending emails via Resend API:
- Send transactional emails with HTML content
- Template variable substitution
- Retry logic for API failures

All tasks include retry logic and proper error handling.
"""

from prefect import task
import httpx
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load environment variables
RESEND_API_KEY = os.getenv("RESEND_API_KEY")


@task(retries=3, retry_delay_seconds=60, name="resend-send-email")
def send_email(
    to_email: str,
    subject: str,
    html: str,
    from_email: str = "Sang Le <sang@sanglescalinglabs.com>",
    reply_to: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send email via Resend API with retry logic.

    Args:
        to_email: Recipient email address
        subject: Email subject line
        html: HTML email content
        from_email: Sender email (default: Sang Le)
        reply_to: Optional reply-to address

    Returns:
        Resend API response with email ID

    Raises:
        httpx.HTTPStatusError: If API request fails after retries

    Example:
        response = send_email(
            to_email="customer@example.com",
            subject="Welcome to BusOS Assessment",
            html="<h1>Welcome!</h1><p>Click here to start...</p>"
        )
        email_id = response["id"]
    """
    if not RESEND_API_KEY:
        raise ValueError("RESEND_API_KEY environment variable not set")

    payload = {
        "from": from_email,
        "to": [to_email],
        "subject": subject,
        "html": html
    }

    if reply_to:
        payload["reply_to"] = [reply_to]

    try:
        with httpx.Client() as client:
            response = client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {RESEND_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            print(f"✅ Email sent to {to_email} (email_id: {result.get('id')})")
            return result

    except httpx.HTTPStatusError as e:
        print(f"❌ Resend API error: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        print(f"❌ Error sending email to {to_email}: {e}")
        raise


@task(name="resend-substitute-variables")
def substitute_variables(template: str, variables: Dict[str, str]) -> str:
    """
    Substitute variables in email template.

    Replaces {{variable_name}} placeholders with actual values.

    Args:
        template: HTML template with {{variable}} placeholders
        variables: Dictionary of variable names to values

    Returns:
        HTML with all variables substituted

    Example:
        html = substitute_variables(
            template="<p>Hi {{first_name}}, welcome to {{business_name}}!</p>",
            variables={"first_name": "John", "business_name": "Acme Salon"}
        )
        # Result: "<p>Hi John, welcome to Acme Salon!</p>"
    """
    result = template
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"  # {{key}}
        result = result.replace(placeholder, str(value))
    return result


@task(retries=3, retry_delay_seconds=60, name="resend-send-template-email")
def send_template_email(
    to_email: str,
    subject: str,
    template: str,
    variables: Dict[str, str],
    from_email: str = "Sang Le <sang@sanglescalinglabs.com>",
    reply_to: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send email with template variable substitution.

    Convenience task that combines variable substitution and sending.

    Args:
        to_email: Recipient email address
        subject: Email subject line
        template: HTML template with {{variable}} placeholders
        variables: Dictionary of variable names to values
        from_email: Sender email (default: Sang Le)
        reply_to: Optional reply-to address

    Returns:
        Resend API response with email ID

    Example:
        response = send_template_email(
            to_email="customer@example.com",
            subject="Welcome {{first_name}}!",
            template="<p>Hi {{first_name}}, your business {{business_name}} is ready!</p>",
            variables={"first_name": "John", "business_name": "Acme Salon"}
        )
    """
    # Substitute variables in both subject and template
    final_subject = substitute_variables(subject, variables)
    final_html = substitute_variables(template, variables)

    # Send email
    return send_email(
        to_email=to_email,
        subject=final_subject,
        html=final_html,
        from_email=from_email,
        reply_to=reply_to
    )
