#!/usr/bin/env python3
"""Send all remaining 9 emails (No-Show 3, Post-Call 3, Onboarding 3) directly via Resend."""
import resend
import os

# Load API key directly from .env file
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('RESEND_API_KEY='):
            resend.api_key = line.strip().split('=', 1)[1]
            break

test_email = "lengobaosang@gmail.com"
first_name = "Wave10Test"

# Define email templates for each sequence
emails_to_send = [
    # No-Show Recovery (3 emails)
    {
        "subject": f"We missed you! Let's reschedule your discovery call",
        "html": f"""<h2>Hi {first_name},</h2>
        <p>We noticed you weren't able to make your scheduled discovery call. No worries - life gets busy!</p>
        <p>I'd still love to help you identify $5K-$15K in hidden revenue opportunities before December.</p>
        <p><strong>→ Click here to reschedule</strong></p>
        <p>The Christmas Priority diagnostic is still available, and there are only a few slots left.</p>
        <p>Talk soon,<br>Sang Le</p>
        <p><em>No-Show Recovery Email 1 of 3</em></p>"""
    },
    {
        "subject": f"Last chance to save $15K this December ({first_name})",
        "html": f"""<h2>Hi {first_name},</h2>
        <p>I wanted to follow up one more time about your missed discovery call.</p>
        <p>Your BusOS assessment showed you're losing approximately $14,000/month in your two weakest systems.</p>
        <p>With 40 days until December, there's still time to fix these systems before the holiday rush.</p>
        <p><strong>→ Reschedule your call now</strong></p>
        <p>If now isn't a good time, just reply and let me know. I'm here to help when you're ready.</p>
        <p>Best,<br>Sang Le</p>
        <p><em>No-Show Recovery Email 2 of 3</em></p>"""
    },
    {
        "subject": f"Final reminder: Your $2997 diagnostic expires soon",
        "html": f"""<h2>Hi {first_name},</h2>
        <p>This is my final follow-up about your missed discovery call.</p>
        <p>The Christmas Priority Diagnostic offer ($2,997, valued at $36,991) closes November 15.</p>
        <p>After that, there won't be enough time to implement fixes before December 20.</p>
        <p>If you still want to:</p>
        <ul>
            <li>Fix your broken systems before the holiday rush</li>
            <li>Capture $35K-$70K in December revenue</li>
            <li>Work with a team that's helped 30+ businesses generate $30M+</li>
        </ul>
        <p><strong>→ Book your call before it's too late</strong></p>
        <p>No more follow-ups after this. I'm here when you're ready.</p>
        <p>Sang Le</p>
        <p><em>No-Show Recovery Email 3 of 3</em></p>"""
    },
    # Post-Call Maybe (3 emails)
    {
        "subject": f"Great talking to you! Next steps for your salon",
        "html": f"""<h2>Hi {first_name},</h2>
        <p>Thanks for taking the time to chat with me today!</p>
        <p>I know you mentioned you need to think about the Christmas Priority Diagnostic ($2,997).</p>
        <p>Totally understand. It's a real investment.</p>
        <p>Here's a quick recap of what we found:</p>
        <ul>
            <li>Your two weakest systems: Bookings & Brand</li>
            <li>Estimated monthly revenue leak: $14,000</li>
            <li>Fix timeline: 45 days (Nov 15 → Dec 20)</li>
        </ul>
        <p>If you have any questions, just reply to this email. I'm here to help.</p>
        <p>Best,<br>Sang Le</p>
        <p><em>Post-Call Follow-up Email 1 of 3</em></p>"""
    },
    {
        "subject": f"How Sarah solved the same pricing objection",
        "html": f"""<h2>Hi {first_name},</h2>
        <p>I wanted to share a quick story about Sarah, a salon owner who had the same hesitation you mentioned.</p>
        <p>"$2,997 is a lot. Can I really make that back?"</p>
        <p>Sarah had the exact same thought. But here's what happened:</p>
        <ul>
            <li>She booked the diagnostic in October 2023</li>
            <li>We found $74K in hidden opportunities</li>
            <li>She fixed her broken systems in 45 days</li>
            <li>December 2023: She captured $52K extra revenue</li>
        </ul>
        <p>ROI: 17X return in 60 days.</p>
        <p>If you're on the fence about the investment, I get it. But sometimes the bigger risk is NOT investing.</p>
        <p><strong>→ Ready to book? Let me know.</strong></p>
        <p>Sang Le</p>
        <p><em>Post-Call Follow-up Email 2 of 3</em></p>"""
    },
    {
        "subject": f"Final offer: Lock in 2025 pricing before Dec 31",
        "html": f"""<h2>Hi {first_name},</h2>
        <p>I wanted to send one final note about our conversation.</p>
        <p>The Christmas Priority Diagnostic ($2,997) is only available until November 15.</p>
        <p>After that, the price goes up to $4,997 for the 2025 cohort.</p>
        <p>If you book before November 15:</p>
        <ul>
            <li>You lock in the $2,997 price</li>
            <li>You get the full $36,991 value package</li>
            <li>You have time to fix systems before December rush</li>
            <li>You're covered by the $5K-$15K guarantee</li>
        </ul>
        <p>No pressure. But I didn't want you to miss the deadline and regret it later.</p>
        <p><strong>→ Ready to book? Reply to this email.</strong></p>
        <p>Sang Le</p>
        <p><em>Post-Call Follow-up Email 3 of 3</em></p>"""
    },
    # Onboarding (3 emails)
    {
        "subject": f"Welcome to BusOS! Your Phase 1 starts soon",
        "html": f"""<h2>Welcome aboard, {first_name}!</h2>
        <p>Thank you for investing in the Christmas Priority Diagnostic ($2,997).</p>
        <p>Here's what happens next:</p>
        <h3>Phase 1: Observation (Dec 10-17)</h3>
        <ul>
            <li>Our team will observe your salon operations for 2 days</li>
            <li>We document every system, process, and bottleneck</li>
            <li>You don't need to change anything - just operate normally</li>
        </ul>
        <h3>Phase 2: Analysis (Dec 18-20)</h3>
        <ul>
            <li>We analyze the data and create your custom 90-day roadmap</li>
            <li>You receive the full Diagnostic Report (30+ pages)</li>
        </ul>
        <p>You'll receive a calendar invite for your observation days within 48 hours.</p>
        <p>Welcome to the BusOS family!</p>
        <p>Sang Le</p>
        <p><em>Onboarding Email 1 of 3</em></p>"""
    },
    {
        "subject": f"Prepare for your observation days (Dec 10-17)",
        "html": f"""<h2>Hi {first_name},</h2>
        <p>Your BusOS observation days are coming up (Dec 10-17).</p>
        <p>Here's how to prepare:</p>
        <h3>Before the Observation</h3>
        <ul>
            <li>Inform your team that observers will be present</li>
            <li>Operate normally - don't change anything</li>
            <li>Give us access to your booking system and POS</li>
        </ul>
        <h3>What We'll Be Looking At</h3>
        <ul>
            <li>Customer booking flow (online + walk-in)</li>
            <li>Team scheduling and utilization</li>
            <li>Service delivery and upselling</li>
            <li>Checkout and follow-up processes</li>
        </ul>
        <h3>What You Need to Provide</h3>
        <ul>
            <li>Access to your scheduling software</li>
            <li>Access to your POS system (read-only is fine)</li>
            <li>Team contact list (for brief interviews)</li>
        </ul>
        <p>Any questions? Reply to this email.</p>
        <p>Sang Le</p>
        <p><em>Onboarding Email 2 of 3</em></p>"""
    },
    {
        "subject": f"Phase 1 roadmap: What happens in the next 90 days",
        "html": f"""<h2>Hi {first_name},</h2>
        <p>Here's your complete 90-day transformation roadmap:</p>
        <h3>Phase 1: Diagnostic (Days 1-21)</h3>
        <ul>
            <li>Week 1-2: Observation days</li>
            <li>Week 3: Analysis and report preparation</li>
            <li>Deliverable: 30+ page Diagnostic Report</li>
        </ul>
        <h3>Phase 2: Quick Wins (Days 22-45)</h3>
        <ul>
            <li>Focus: Your 2 weakest systems</li>
            <li>Implementation: Step-by-step guidance</li>
            <li>Support: Daily Slack access + 2 coaching calls</li>
            <li>Expected outcome: $5K-$15K recovered</li>
        </ul>
        <h3>Phase 3: Optimization (Days 46-90)</h3>
        <ul>
            <li>Focus: Remaining systems + scaling</li>
            <li>Advanced strategies and automation</li>
            <li>Prepare for sustained growth</li>
            <li>Expected outcome: Systems running smoothly</li>
        </ul>
        <p>By Day 90, you'll have:</p>
        <ul>
            <li>Fixed your broken systems</li>
            <li>Recovered $15K-$50K in lost revenue</li>
            <li>Built a scalable operation</li>
        </ul>
        <p>Questions about the roadmap? Let me know.</p>
        <p>Sang Le</p>
        <p><em>Onboarding Email 3 of 3</em></p>"""
    }
]

# Send all 9 emails
sent_ids = []
for i, email_data in enumerate(emails_to_send, 1):
    try:
        result = resend.Emails.send({
            "from": "Sang Le - BusOS <value@galatek.dev>",
            "to": [test_email],
            "subject": email_data["subject"],
            "html": email_data["html"]
        })
        print(f"✅ Email {i}/9 sent: {result['id']} - {email_data['subject'][:40]}...")
        sent_ids.append(result['id'])
    except Exception as e:
        print(f"❌ Email {i}/9 failed: {e}")

print(f"\n🎉 Total emails sent: {len(sent_ids)}/9")
print(f"📧 Email IDs: {sent_ids}")
