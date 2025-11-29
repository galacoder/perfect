#!/usr/bin/env python3
"""
Test direct Resend API call to send test email.

This script:
1. Loads Resend API key from Prefect Secret blocks or .env
2. Sends a simple test email to verify email delivery
3. Reports the email ID and delivery status

Usage:
    python campaigns/christmas_campaign/scripts/test_resend_send.py

Author: Christmas Campaign Team
Created: 2025-11-28
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

# Try Prefect Secret blocks first (production server)
PREFECT_API_URL = os.getenv("PREFECT_API_URL", "https://prefect.galatek.dev/api")
os.environ["PREFECT_API_URL"] = PREFECT_API_URL

try:
    from prefect.blocks.system import Secret
    RESEND_API_KEY = Secret.load("resend-api-key").get()
    print(f"✅ Loaded Resend API key from Prefect Secret blocks (via {PREFECT_API_URL})")
except Exception as e:
    print(f"⚠️  Failed to load from Secret blocks, using environment variables: {e}")
    RESEND_API_KEY = os.getenv("RESEND_API_KEY")

if not RESEND_API_KEY:
    print("❌ RESEND_API_KEY not found in Secret blocks or environment variables")
    sys.exit(1)

import resend
resend.api_key = RESEND_API_KEY


def send_test_email(to_email: str = "lengobaosang@gmail.com"):
    """
    Send a simple test email via Resend API.

    Args:
        to_email: Recipient email address
    """
    print(f"\n📧 Sending test email to: {to_email}")
    print("=" * 80)

    # Email content
    subject = f"🧪 Resend API Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    html_body = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #4CAF50;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px;
            }}
            .content {{
                padding: 20px;
                background-color: #f9f9f9;
                margin-top: 20px;
                border-radius: 5px;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                color: #777;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🧪 Resend API Test Email</h1>
        </div>
        <div class="content">
            <h2>Test Successful!</h2>
            <p>This is a test email from the Christmas Campaign Resend API integration.</p>
            <p><strong>Sent at:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>From:</strong> Sang Le - BusOS (value@galatek.dev)</p>
            <p><strong>Campaign:</strong> Christmas 2025</p>

            <h3>✅ What This Confirms:</h3>
            <ul>
                <li>Resend API key is valid and working</li>
                <li>Email sending functionality is operational</li>
                <li>HTML email formatting is correct</li>
                <li>Sender domain (galatek.dev) is verified</li>
            </ul>

            <h3>📋 Next Steps:</h3>
            <ol>
                <li>Check Resend dashboard for delivery status</li>
                <li>Verify email arrived in inbox (not spam)</li>
                <li>Test template variable substitution</li>
                <li>Send test emails for all 21 templates</li>
            </ol>
        </div>
        <div class="footer">
            <p>This is an automated test email. No action required.</p>
            <p>&copy; 2025 Sang Le Scaling Labs</p>
        </div>
    </body>
    </html>
    """

    try:
        # Send email
        print("\n📤 Sending email...")
        params = {
            "from": "Sang Le - BusOS <value@galatek.dev>",
            "to": [to_email],
            "subject": subject,
            "html": html_body
        }

        response = resend.Emails.send(params)

        print("\n✅ Email sent successfully!")
        print(f"   Email ID: {response['id']}")
        print(f"   Recipient: {to_email}")
        print(f"   Subject: {subject}")

        print("\n" + "=" * 80)
        print("📊 Verification Steps:")
        print("1. Check Resend dashboard: https://resend.com/emails")
        print(f"2. Search for email ID: {response['id']}")
        print(f"3. Check inbox: {to_email}")
        print("4. Verify email is not in spam folder")

        return response['id']

    except Exception as e:
        print(f"\n❌ Error sending test email: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Verify Resend API key is valid")
        print("   2. Check sender domain (galatek.dev) is verified in Resend")
        print("   3. Ensure recipient email is valid")
        print("   4. Check Resend account limits/quota")
        return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Send test email via Resend API")
    parser.add_argument("--email", default="lengobaosang@gmail.com", help="Recipient email address")

    args = parser.parse_args()

    email_id = send_test_email(to_email=args.email)
    sys.exit(0 if email_id else 1)
