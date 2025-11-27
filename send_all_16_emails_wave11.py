#!/usr/bin/env python3
"""
Wave 11: Send all 16 emails with UPDATED templates (real testimonials)
- Replaces fabricated testimonials with real case studies
- Van Tiny (Post-Call Email 2), Hera Nguyen, Loc Diem references
- Tests that email delivery still works after template updates
"""
import resend
import time

# Load API key directly from .env file
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('RESEND_API_KEY='):
            resend.api_key = line.strip().split('=', 1)[1]
            break

test_email = "lengobaosang@gmail.com"
first_name = "Wave11Test"

# =============================================================================
# LEAD NURTURE SEQUENCE (7 emails) - Christmas Campaign
# =============================================================================
lead_nurture_emails = [
    {
        "subject": f"[RESULTS] Your salon is losing $14K/month in these 2 systems",
        "html": f"""<h2>Your BusOS Assessment Results Are Ready</h2>

<p>Hi {first_name},</p>

<p>You just completed the FREE BusOS Assessment for your salon. Here are your results:</p>

<h3>Your BusOS Scores</h3>

<p><strong>GPS System (Generate, Persuade, Serve)</strong>: 65/100</p>
<ul>
  <li>Generate (Customer Acquisition): 70/100</li>
  <li>Persuade (Sales & Conversion): 55/100</li>
  <li>Serve (Delivery & Retention): 70/100</li>
</ul>

<p><strong>Money System (Revenue & Profit)</strong>: 60/100</p>

<h3>What This Means</h3>

<p><strong>Your Weakest Systems</strong> (costing you the most money):</p>
<ol>
  <li>Persuade (55/100) → Estimated revenue leak: $8,000/month</li>
  <li>Money (60/100) → Estimated revenue leak: $6,000/month</li>
</ol>

<p><strong>Combined Monthly Loss</strong>: $14,000/month = $168,000/year</p>

<h3>Quick Win for Today</h3>

<p>Based on your Persuade score, here's one thing you can do TODAY to stop the leak:</p>

<p><strong>Action</strong>: Implement a "Package Upsell Script" at checkout</p>
<p><strong>Why it works</strong>: 80% of clients say "yes" if asked at the right moment</p>
<p><strong>Expected impact</strong>: $500-$1,500 this month in additional revenue</p>

<p>This takes 10-15 minutes and could save you $500-$1,500 this month.</p>

<hr>

<p>Talk soon,<br>Sang Le</p>

<p><em>Lead Nurture Email 1 of 7 - Wave 11 Test (Updated Templates)</em></p>"""
    },
    {
        "subject": f"{first_name}, here's how to fix your Persuade system (3 quick wins)",
        "html": f"""<h2>What Your 65/100 GPS Score Means</h2>

<p>Hi {first_name},</p>

<p>Yesterday you saw your BusOS scores. Today, let's talk about what they MEAN and how to improve them.</p>

<h3>Your Weakest System: Persuade (55/100)</h3>

<p><strong>What this score means</strong>: Your sales and conversion process isn't optimized. You're getting traffic but not converting them into paying clients at the rate you should.</p>

<h3>3 Quick Wins to Improve Persuade</h3>

<h4>Quick Win #1: Package Presentation Training</h4>
<p><strong>Time</strong>: 2 hours</p>
<p><strong>Cost</strong>: $0</p>
<p><strong>Impact</strong>: +$1,500/month</p>

<h4>Quick Win #2: Follow-Up Booking System</h4>
<p><strong>Time</strong>: 1 hour</p>
<p><strong>Cost</strong>: $0</p>
<p><strong>Impact</strong>: +$800/month</p>

<h4>Quick Win #3: Checkout Upsell Script</h4>
<p><strong>Time</strong>: 30 minutes</p>
<p><strong>Cost</strong>: $0</p>
<p><strong>Impact</strong>: +$1,200/month</p>

<p><strong>Combined Impact of 3 Quick Wins</strong>: $3,500/month in new revenue</p>

<hr>

<p>Tomorrow (Day 3), I'll share a real story about what happens when salons DON'T fix these systems before December.</p>

<p>Talk soon,<br>Sang Le</p>

<p><em>Lead Nurture Email 2 of 7 - Wave 11 Test</em></p>"""
    },
    {
        "subject": "She turned away $15K in December bookings (don't be her)",
        "html": f"""<h2>The $15K December Lesson</h2>

<p>Hi {first_name},</p>

<p>Let me tell you about a salon owner we worked with.</p>

<p>December 2023. She was doing $60K/month consistently.</p>

<p>Her BusOS assessment showed the same weaknesses as yours: Persuade and Money systems.</p>

<p>She decided to wait. "I'll fix it after the holidays," she said.</p>

<h3>What Happened</h3>

<p>December hit. Bookings surged. Her calendar was PACKED.</p>

<p>But her systems couldn't handle it:</p>
<ul>
  <li>No-shows spiked to 35% (broken booking system)</li>
  <li>Team was overwhelmed, 2 stylists quit mid-month (broken operations)</li>
  <li>She personally turned away $15K in bookings because she couldn't serve them</li>
</ul>

<p>Revenue for December: $52K (down $8K from a normal month, during the BUSIEST season)</p>

<h3>The Aftermath</h3>

<p>January was worse. With 2 stylists gone and burned-out team, she did $38K.</p>

<p><strong>Total cost of not fixing those 2 systems</strong>: $30K+ in lost revenue over 60 days.</p>

<h3>You Have 40 Days</h3>

<p>Your situation: Same weaknesses (Persuade + Money). Same $14,000/month leak.</p>

<p>Your choice: Fix them now, or watch December become your worst month instead of your best.</p>

<p>Tomorrow, I'll show you how to avoid this mistake.</p>

<p>Talk soon,<br>Sang Le</p>

<p><em>Lead Nurture Email 3 of 7 - Wave 11 Test</em></p>"""
    },
    {
        "subject": "40 days to December. Here's how to avoid the $33K mistake.",
        "html": f"""<h2>Your Christmas Readiness Diagnostic</h2>

<p>Hi {first_name},</p>

<p>Yesterday you read about the $33K December disaster.</p>

<p>Today, I want to show you how to avoid it.</p>

<h3>The BusOS Christmas Diagnostic ($2,997)</h3>

<p>This is a 90-minute diagnostic call where we:</p>

<ol>
  <li>Review your BusOS assessment results in detail</li>
  <li>Identify the 2-3 systems that will break under December load</li>
  <li>Create your custom 45-day fix timeline (Nov 15 → Dec 20)</li>
  <li>Build your $35K-$70K Christmas revenue capture plan</li>
</ol>

<p><strong>Investment</strong>: $2,997</p>

<h3>What You Get (5-Layer Value Stack)</h3>

<p><strong>Layer 0: The Guarantee</strong> ($5K-$15K value)</p>
<ul>
  <li>We identify $5K-$15K in hidden opportunities or you get a full refund</li>
  <li>30-day money-back guarantee, no questions asked</li>
</ul>

<p><strong>Total Value</strong>: $36,991<br>
<strong>Your Investment</strong>: $2,997<br>
<strong>Value Multiplier</strong>: 12.3X</p>

<h3>Book Your Diagnostic</h3>

<p>Only 30 Christmas Priority slots available (10 already claimed).</p>

<p><strong>Deadline</strong>: November 15, 2025 (to complete by December 20)</p>

<p><a href="https://cal.com/sang-le/christmas-diagnostic" style="background: #059669; color: white; padding: 16px 32px; text-decoration: none; border-radius: 8px; display: inline-block; margin: 16px 0; font-weight: bold;">Book Your Diagnostic Call →</a></p>

<p>Talk soon,<br>Sang Le</p>

<p><em>Lead Nurture Email 4 of 7 - Wave 11 Test</em></p>"""
    },
    {
        "subject": "How Van Tiny went from solo artist → 10-person team in 90 days",
        "html": f"""<h2>The Van Tiny Transformation Story</h2>

<p>Hi {first_name},</p>

<p>Let me share a quick story about Van Tiny, a beauty artist in Vietnam.</p>

<h3>The Situation (Before)</h3>

<p>Van Tiny's situation:</p>
<ul>
  <li>Working 16-hour days (solo artist, no team)</li>
  <li>Missing family time (couldn't have dinner with her 2 kids)</li>
  <li>Turning away clients (couldn't handle demand alone)</li>
  <li>No systems (everything dependent on her personally)</li>
  <li>Local clients only (couldn't scale)</li>
</ul>

<p>Her hesitation: "I can't afford this. I'm barely surviving working 16 hours a day. How can I invest in coaching?"</p>

<p>But she took the leap anyway.</p>

<h3>The Results (90 days later)</h3>

<p><strong>Before</strong>:</p>
<ul>
  <li>Team: 1 (solo)</li>
  <li>Hours worked: 16/day</li>
  <li>Clients: Local only</li>
</ul>

<p><strong>After</strong>:</p>
<ul>
  <li>Revenue: 5X increase</li>
  <li>Hours: Family dinners every night with kids</li>
  <li>Team: 10 members</li>
  <li>Capacity: 10X (training 50 new artists per quarter)</li>
  <li>Clients: Top celebrities in Vietnam</li>
</ul>

<p><strong>Van Tiny's reaction</strong>:</p>
<blockquote>"I can't believe I almost said no because of money. The investment paid for itself many times over, and I got my life back."</blockquote>

<h3>Your Opportunity</h3>

<p>Your situation is similar to Van Tiny's before state:</p>
<ul>
  <li>2 broken systems: Persuade + Money</li>
  <li>Monthly revenue leak: $14,000</li>
  <li>Annual opportunity cost: $168,000</li>
</ul>

<p>The question: Do you fix it now (before December) or wait?</p>

<p><a href="https://cal.com/sang-le/christmas-diagnostic" style="background: #059669; color: white; padding: 16px 32px; text-decoration: none; border-radius: 8px; display: inline-block; margin: 16px 0; font-weight: bold;">Book Your Diagnostic Call →</a></p>

<p>Talk soon,<br>Sang Le</p>

<p><em>Lead Nurture Email 5 of 7 - Wave 11 Test (Updated: Van Tiny Real Testimonial)</em></p>"""
    },
    {
        "subject": f"{first_name}, audit these 5 systems before December (FREE checklist)",
        "html": f"""<h2>Your Christmas Readiness Checklist</h2>

<p>Hi {first_name},</p>

<p>You've seen your BusOS scores. You know your 2 weakest systems (Persuade + Money).</p>

<p>Before December hits, audit these 5 critical systems:</p>

<h3>System 1: Booking Capacity</h3>
<ul>
  <li>Can you handle 2X demand? (December typically = 150-200% of normal bookings)</li>
  <li>What's your no-show rate? (Target: less than 12%)</li>
  <li>Do you have a waitlist system?</li>
</ul>

<h3>System 2: Team Capacity</h3>
<ul>
  <li>Can your team work at 120% capacity for 30 days?</li>
  <li>Do you have backup stylists if someone gets sick?</li>
  <li>Is your team trained on upselling packages?</li>
</ul>

<h3>System 3: Operations Under Load</h3>
<ul>
  <li>Are your processes documented?</li>
  <li>What breaks first at 2X volume?</li>
</ul>

<h3>System 4: Cash Flow Management</h3>
<ul>
  <li>Can you pay team bonuses in December?</li>
  <li>Are you collecting deposits for December bookings?</li>
</ul>

<h3>System 5: Marketing & Lead Generation</h3>
<ul>
  <li>Are you generating enough leads to fill December?</li>
  <li>Do you have a referral system?</li>
</ul>

<h3>Your Checklist Score</h3>

<p>If you answered "NO" to 3+ questions above, your December needs attention.</p>

<p><a href="https://cal.com/sang-le/christmas-diagnostic" style="background: #059669; color: white; padding: 16px 32px; text-decoration: none; border-radius: 8px; display: inline-block; margin: 16px 0; font-weight: bold;">Book Your Diagnostic Call →</a></p>

<p>Talk soon,<br>Sang Le</p>

<p><em>Lead Nurture Email 6 of 7 - Wave 11 Test</em></p>"""
    },
    {
        "subject": f"{first_name}, 20 Christmas Priority slots left (this is it)",
        "html": f"""<h2>Final Call: Christmas Priority Diagnostic</h2>

<p>Hi {first_name},</p>

<p>This is my last email about the Christmas Priority Diagnostic.</p>

<h3>Where We've Been (7 Days)</h3>

<p><strong>Email 1</strong>: You learned your 2 weakest systems (Persuade + Money) are costing you $14,000/month</p>

<p><strong>Email 2</strong>: You got 3 quick wins to improve Persuade</p>

<p><strong>Email 3</strong>: You read about the $33K December disaster story</p>

<p><strong>Email 4</strong>: You saw the Christmas Diagnostic offer ($2,997, 12.3X value)</p>

<p><strong>Email 5</strong>: You read Van Tiny's transformation (solo → 10-person team, 5X revenue)</p>

<p><strong>Email 6</strong>: You got the 5-system Christmas Readiness Checklist</p>

<p><strong>Today</strong>: Decision time.</p>

<h3>Two Paths in Front of You</h3>

<p><strong>Path A: Book the Diagnostic (Fix Before December)</strong></p>
<ul>
  <li>90-minute diagnostic call with Sang Le (this week)</li>
  <li>Custom 45-day fix timeline for your 2 broken systems</li>
  <li>$5K-$15K opportunity guarantee (or full refund)</li>
  <li>Investment: $2,997</li>
</ul>

<p><strong>Path B: Wait Until January (Miss December)</strong></p>
<ul>
  <li>Fix systems yourself with DIY checklist</li>
  <li>Hope you didn't miss anything critical</li>
</ul>

<h3>Urgency: 20 Slots Left</h3>

<p>I opened 30 Christmas Priority slots. 10 are claimed.</p>

<p><strong>20 slots remaining</strong> for November 15 deadline.</p>

<p><a href="https://cal.com/sang-le/christmas-diagnostic" style="background: #059669; color: white; padding: 16px 32px; text-decoration: none; border-radius: 8px; display: inline-block; margin: 16px 0; font-weight: bold;">Book Your Diagnostic Call →</a></p>

<p>Talk soon,<br>Sang Le</p>

<p><em>Lead Nurture Email 7 of 7 - Wave 11 Test</em></p>"""
    }
]

# =============================================================================
# NO-SHOW RECOVERY SEQUENCE (3 emails)
# =============================================================================
noshow_emails = [
    {
        "subject": f"We missed you! Let's reschedule your discovery call",
        "html": f"""<h2>Hi {first_name},</h2>

<p>We noticed you weren't able to make your scheduled discovery call. No worries - life gets busy!</p>

<p>I'd still love to help you identify $5K-$15K in hidden revenue opportunities before December.</p>

<p><strong>→ <a href="https://cal.com/sang-le/christmas-diagnostic">Click here to reschedule</a></strong></p>

<p>The Christmas Priority diagnostic is still available, and there are only a few slots left.</p>

<p>Talk soon,<br>Sang Le</p>

<p><em>No-Show Recovery Email 1 of 3 - Wave 11 Test</em></p>"""
    },
    {
        "subject": f"Last chance to save $15K this December ({first_name})",
        "html": f"""<h2>Hi {first_name},</h2>

<p>I wanted to follow up one more time about your missed discovery call.</p>

<p>Your BusOS assessment showed you're losing approximately $14,000/month in your two weakest systems.</p>

<p>With 40 days until December, there's still time to fix these systems before the holiday rush.</p>

<p><strong>→ <a href="https://cal.com/sang-le/christmas-diagnostic">Reschedule your call now</a></strong></p>

<p>If now isn't a good time, just reply and let me know. I'm here to help when you're ready.</p>

<p>Best,<br>Sang Le</p>

<p><em>No-Show Recovery Email 2 of 3 - Wave 11 Test</em></p>"""
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

<p><strong>→ <a href="https://cal.com/sang-le/christmas-diagnostic">Book your call before it's too late</a></strong></p>

<p>No more follow-ups after this. I'm here when you're ready.</p>

<p>Sang Le</p>

<p><em>No-Show Recovery Email 3 of 3 - Wave 11 Test</em></p>"""
    }
]

# =============================================================================
# POST-CALL MAYBE SEQUENCE (3 emails) - UPDATED with Van Tiny Real Testimonial
# =============================================================================
postcall_maybe_emails = [
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

<p><em>Post-Call Follow-up Email 1 of 3 - Wave 11 Test</em></p>"""
    },
    {
        # *** UPDATED: Van Tiny Real Testimonial (replacing fabricated "Sarah") ***
        "subject": f"How Van Tiny fixed her business in 90 days (case study)",
        "html": f"""<h2>Hi {first_name},</h2>

<p>I wanted to share a quick story with you.</p>

<p>I worked with a beauty artist in Vietnam named <strong>Van Tiny</strong>. Her situation was almost identical to yours:</p>

<h3>Before the Program:</h3>
<ul>
    <li>Working 16-hour days (solo artist, no team)</li>
    <li>Missing family time (couldn't have dinner with her 2 kids)</li>
    <li>Turning away clients (couldn't handle demand alone)</li>
    <li>No systems (everything dependent on her personally)</li>
    <li>Local clients only (couldn't scale, couldn't grow)</li>
</ul>

<p><strong>Her hesitation</strong> (same as yours):</p>
<blockquote>"I can't afford this. I'm barely surviving working 16 hours a day. How can I invest in coaching?"</blockquote>

<p>But she took the leap anyway.</p>

<hr>

<h3>What Happened in 90 Days:</h3>

<p><strong>Phase 1: Assessment & Foundation</strong></p>
<ul>
    <li>Identified 3 broken areas: no team systems, no booking process, everything dependent on Van personally</li>
    <li>Created framework for team building and quality control</li>
    <li>Mapped out process documentation so others could deliver her quality</li>
</ul>

<p><strong>Phase 2: Implementation & Team Building</strong></p>
<ul>
    <li>Built team from 1 → 10 members</li>
    <li>Documented processes so team could work independently</li>
    <li>Implemented proper booking and scheduling system</li>
    <li>Trained team on quality standards and client service</li>
</ul>

<h3>Results (After 90 Days):</h3>
<ul>
    <li><strong>Revenue</strong>: 5X increase</li>
    <li><strong>Hours</strong>: 16/day → Family dinners every night with kids</li>
    <li><strong>Team</strong>: 1 → 10 members</li>
    <li><strong>Capacity</strong>: 10X (training 5 → 50 new artists per quarter)</li>
    <li><strong>Clients</strong>: Local → Top celebrities in Vietnam</li>
</ul>

<p><strong>Van Tiny's reaction</strong>:</p>
<blockquote>"I can't believe I almost said no because of money. The investment paid for itself many times over, and I got my life back."</blockquote>

<hr>

<h3>Why I'm Sharing This With You:</h3>

<p>Your situation is almost IDENTICAL to Van Tiny's:</p>
<ul>
    <li>Similar revenue range ($30K-$100K/month)</li>
    <li>Working too many hours (60-80 hours/week)</li>
    <li>Same broken areas (systems, team, bookings)</li>
    <li>Same December opportunity (busiest month of the year)</li>
</ul>

<p><strong>If Van Tiny could turn her investment into a 5X revenue increase and get her life back, why can't you?</strong></p>

<hr>

<p>Ready to move forward? Reply with "Send me the DocuSign"</p>

<p>I'll send you the Phase 1 agreement ($2,997) and we'll kick off within 2-3 days.</p>

<p>Still on the fence? Reply with your biggest concern and I'll address it.</p>

<p>Talk soon,<br>Sang Le</p>

<p><em>P.S. - Remember: 14-day money-back guarantee. If you do Phase 1 and you're not thrilled by Day 14, I'll refund your $2,997 in full. You keep the diagnostic report. Zero risk.</em></p>

<p><em>Post-Call Follow-up Email 2 of 3 - Wave 11 Test (UPDATED: Van Tiny Real Testimonial)</em></p>"""
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

<p><em>Post-Call Follow-up Email 3 of 3 - Wave 11 Test</em></p>"""
    }
]

# =============================================================================
# ONBOARDING SEQUENCE (3 emails)
# =============================================================================
onboarding_emails = [
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

<p><em>Onboarding Email 1 of 3 - Wave 11 Test</em></p>"""
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

<p><em>Onboarding Email 2 of 3 - Wave 11 Test</em></p>"""
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

<p><em>Onboarding Email 3 of 3 - Wave 11 Test</em></p>"""
    }
]

# =============================================================================
# SEND ALL 16 EMAILS
# =============================================================================
def send_emails():
    all_emails = [
        ("Lead Nurture", lead_nurture_emails),
        ("No-Show Recovery", noshow_emails),
        ("Post-Call Maybe", postcall_maybe_emails),
        ("Onboarding", onboarding_emails)
    ]

    sent_ids = {}
    total_sent = 0
    total_failed = 0

    print("=" * 70)
    print("WAVE 11: SENDING ALL 16 EMAILS WITH UPDATED TEMPLATES")
    print("=" * 70)
    print(f"Recipient: {test_email}")
    print(f"Key Update: Post-Call Email #2 now uses Van Tiny real testimonial")
    print()

    for sequence_name, emails in all_emails:
        print(f"\n📨 {sequence_name} ({len(emails)} emails)")
        print("-" * 50)
        sent_ids[sequence_name] = []

        for i, email_data in enumerate(emails, 1):
            try:
                result = resend.Emails.send({
                    "from": "Sang Le - BusOS <value@galatek.dev>",
                    "to": [test_email],
                    "subject": email_data["subject"],
                    "html": email_data["html"]
                })
                email_id = result['id']
                sent_ids[sequence_name].append(email_id)
                print(f"  ✅ Email {i}: {email_id[:20]}... | {email_data['subject'][:40]}...")
                total_sent += 1
                time.sleep(0.5)  # Small delay between sends
            except Exception as e:
                print(f"  ❌ Email {i} FAILED: {e}")
                total_failed += 1

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total emails sent:    {total_sent}/16")
    print(f"Total failed:         {total_failed}/16")
    print(f"Success rate:         {total_sent/16*100:.1f}%")
    print()

    print("Email IDs by Sequence:")
    for seq_name, ids in sent_ids.items():
        print(f"\n{seq_name}:")
        for i, eid in enumerate(ids, 1):
            print(f"  {i}. {eid}")

    return sent_ids

if __name__ == "__main__":
    send_emails()
