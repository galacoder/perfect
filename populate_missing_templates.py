"""
Populate Missing Email Templates in Notion

This script adds HTML content to 9 missing email templates:
- 3 No-Show Recovery emails
- 3 Post-Call Follow-Up emails
- 3 Onboarding emails

Author: Coding Agent
Created: 2025-11-27
"""

import os
from notion_client import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Notion client
notion = Client(auth=os.getenv('NOTION_TOKEN'))
db_id = os.getenv('NOTION_TEMPLATES_DB_ID')

# Email templates to populate
TEMPLATES = {
    # NO-SHOW RECOVERY SEQUENCE
    "noshow_recovery_email_1": {
        "subject": "Did we miss each other? {{first_name}}",
        "html_body": """<h2>Did We Miss Each Other?</h2>

<p>Hi {{first_name}},</p>

<p>I noticed you had a call scheduled with us, but we didn't get to connect.</p>

<p>No worries! Life happens, and I know running a salon keeps you incredibly busy.</p>

<h3>Quick Context Refresh</h3>

<p>You completed the BusOS Assessment and we found:</p>
<ul>
  <li>Your 2 weakest systems: {{WeakestSystem1}} + {{WeakestSystem2}}</li>
  <li>Estimated monthly revenue leak: ${{TotalRevenueLeak}}</li>
  <li>Annual opportunity cost: ${{AnnualRevenueLeak}}</li>
</ul>

<h3>Why This Call Matters</h3>

<p>The Christmas Diagnostic call isn't just another consultation. It's a 90-minute deep dive where we:</p>
<ol>
  <li>Audit your 5 critical business systems</li>
  <li>Identify $5K-$15K in hidden opportunities (guaranteed or refund)</li>
  <li>Build your custom 45-day fix timeline (before December 20)</li>
  <li>Create your $35K-$70K Christmas revenue capture plan</li>
</ol>

<h3>Reschedule Your Call</h3>

<p>I have a few priority slots still available this week.</p>

<p><a href="https://cal.com/sang-le/christmas-diagnostic" style="background: #059669; color: white; padding: 16px 32px; text-decoration: none; border-radius: 8px; display: inline-block; margin: 16px 0; font-weight: bold;">Reschedule Your Diagnostic Call →</a></p>

<p><strong>Investment</strong>: $2,997<br>
<strong>Value</strong>: $36,991 (12.3X)<br>
<strong>Guarantee</strong>: $5K-$15K opportunities or full refund</p>

<p>Talk soon,<br>Sang Le</p>

<p><em>P.S. If the timing isn't right, just reply and let me know. No hard feelings!</em></p>"""
    },

    "noshow_recovery_email_2": {
        "subject": "Quick question, {{first_name}}",
        "html_body": """<h2>Quick Question About Your Assessment</h2>

<p>Hi {{first_name}},</p>

<p>I wanted to check in because I saw your BusOS assessment results and something caught my attention.</p>

<h3>Your Situation (From Assessment)</h3>

<p>Two systems scored particularly low:</p>
<ul>
  <li><strong>{{WeakestSystem1}}</strong>: {{Score1}}/100</li>
  <li><strong>{{WeakestSystem2}}</strong>: {{Score2}}/100</li>
</ul>

<p>Combined, these are costing you approximately <strong>${{TotalRevenueLeak}}/month</strong> in lost revenue.</p>

<h3>My Question</h3>

<p>Are you already working on fixing these systems, or are they still on your "someday" list?</p>

<p>I ask because I've seen this pattern before:</p>
<ul>
  <li><strong>Scenario A</strong>: Owner knows about the problems but doesn't have time/expertise to fix them → systems stay broken → revenue leak continues</li>
  <li><strong>Scenario B</strong>: Owner brings in expert help → systems fixed in 45 days → revenue leak stops + December surge captured</li>
</ul>

<h3>The December Factor</h3>

<p>You have 40 days until Christmas rush.</p>

<p>If these systems aren't fixed by then, you'll face the same challenge Sarah did (remember the $33K disaster from my previous emails?).</p>

<h3>What I Can Do</h3>

<p>If you're in Scenario A (know the problems, need help fixing them), the Christmas Diagnostic is designed exactly for this:</p>
<ul>
  <li>90-minute diagnostic call with me</li>
  <li>Custom 45-day fix timeline for your specific systems</li>
  <li>$5K-$15K opportunity guarantee (or full refund)</li>
  <li>30-day implementation support included</li>
</ul>

<p><a href="https://cal.com/sang-le/christmas-diagnostic" style="background: #059669; color: white; padding: 16px 32px; text-decoration: none; border-radius: 8px; display: inline-block; margin: 16px 0; font-weight: bold;">Book Your Diagnostic Call →</a></p>

<p>Investment: $2,997 (12.3X value = $36,991 total package)</p>

<p>Talk soon,<br>Sang Le</p>

<p><em>P.S. If you're in Scenario B (already fixing the systems yourself), reply and let me know! I'd love to hear how it's going.</em></p>"""
    },

    "noshow_recovery_email_3": {
        "subject": "Last call for December readiness, {{first_name}}",
        "html_body": """<h2>Last Call: Christmas Priority Diagnostic</h2>

<p>Hi {{first_name}},</p>

<p>This is my final follow-up about the Christmas Diagnostic.</p>

<p>I want to respect your inbox, so after this email, I'll stop following up about your missed call.</p>

<h3>The Reality Check</h3>

<p>Your BusOS assessment showed two systems bleeding money:</p>
<ul>
  <li>{{WeakestSystem1}} ({{Score1}}/100)</li>
  <li>{{WeakestSystem2}} ({{Score2}}/100)</li>
</ul>

<p><strong>Monthly cost</strong>: ${{TotalRevenueLeak}}<br>
<strong>Annual cost</strong>: ${{AnnualRevenueLeak}}</p>

<h3>The December Window</h3>

<p>You have approximately 35-40 days before December 20 (peak Christmas season).</p>

<p>That's enough time to fix 2 critical systems IF you start this week.</p>

<h3>Two Paths Forward</h3>

<p><strong>Path 1: Book the Diagnostic (Last Chance)</strong></p>
<ul>
  <li>90-minute diagnostic call this week</li>
  <li>45-day fix timeline (systems working by Dec 20)</li>
  <li>$5K-$15K opportunity guarantee or full refund</li>
  <li>Capture $35K-$70K December surge revenue</li>
  <li>Investment: $2,997</li>
</ul>

<p><a href="https://cal.com/sang-le/christmas-diagnostic" style="background: #059669; color: white; padding: 16px 32px; text-decoration: none; border-radius: 8px; display: inline-block; margin: 16px 0; font-weight: bold;">Book Your Diagnostic Call →</a></p>

<p><strong>Path 2: Pass on This Opportunity</strong></p>
<ul>
  <li>Fix systems yourself (or wait until January)</li>
  <li>Risk missing December revenue opportunity</li>
  <li>Investment: $0</li>
</ul>

<h3>Final Reminder</h3>

<p>After November 15, it's mathematically too late to fix before Christmas.</p>

<p>That's 7 days from now.</p>

<h3>What Happens Next</h3>

<p>If you book the diagnostic:</p>
<ul>
  <li>We'll schedule your 90-minute call within 3-5 days</li>
  <li>You'll get your custom 45-day fix timeline</li>
  <li>You'll have 30 days of Slack support (daily check-ins)</li>
  <li>Your systems will be ready for December surge</li>
</ul>

<p>If you don't book:</p>
<ul>
  <li>You'll stay on my general email list (valuable content weekly)</li>
  <li>You won't hear from me about the diagnostic again</li>
  <li>You'll need to fix the systems yourself or wait until 2026</li>
</ul>

<p>No pressure either way. I respect whatever decision you make.</p>

<p>Talk soon,<br>Sang Le</p>

<p><em>P.S. If there's a specific reason you didn't make the original call (pricing, timing, skepticism), reply and let me know. I read every response and can often find a solution.</em></p>"""
    },

    # POST-CALL FOLLOW-UP SEQUENCE
    "postcall_maybe_email_1": {
        "subject": "Your Salon Diagnostic Summary - {{first_name}}",
        "html_body": """<h2>Your Christmas Diagnostic Summary</h2>

<p>Hi {{first_name}},</p>

<p>Thanks for the great conversation today! I wanted to recap what we discovered during your 90-minute diagnostic call.</p>

<h3>What We Found (Key Insights)</h3>

<p><strong>Your Current State:</strong></p>
<ul>
  <li>Monthly Revenue: ${{MonthlyRevenue}}</li>
  <li>Two Weakest Systems: {{WeakestSystem1}} ({{Score1}}/100) + {{WeakestSystem2}} ({{Score2}}/100)</li>
  <li>Estimated Monthly Revenue Leak: ${{TotalRevenueLeak}}</li>
  <li>Annual Opportunity Cost: ${{AnnualRevenueLeak}}</li>
</ul>

<p><strong>Hidden Opportunities We Identified:</strong></p>
<ol>
  <li><strong>{{Opportunity1_Name}}</strong>: ${{Opportunity1_Value}}/month potential</li>
  <li><strong>{{Opportunity2_Name}}</strong>: ${{Opportunity2_Value}}/month potential</li>
  <li><strong>{{Opportunity3_Name}}</strong>: ${{Opportunity3_Value}}/month potential</li>
</ol>

<p><strong>Total Opportunity Value</strong>: ${{TotalOpportunityValue}}/month = ${{AnnualOpportunityValue}}/year</p>

<h3>Your Custom 45-Day Fix Timeline</h3>

<p><strong>Phase 1: Weeks 1-2 (Foundation)</strong></p>
<ul>
  <li>Fix {{WeakestSystem1}} (highest priority)</li>
  <li>Expected impact: ${{Phase1_Impact}}/month</li>
</ul>

<p><strong>Phase 2: Weeks 3-4 (Optimization)</strong></p>
<ul>
  <li>Fix {{WeakestSystem2}} (second priority)</li>
  <li>Expected impact: ${{Phase2_Impact}}/month</li>
</ul>

<p><strong>Phase 3: Weeks 5-6 (Scale)</strong></p>
<ul>
  <li>Implement quick wins and optimizations</li>
  <li>Expected impact: ${{Phase3_Impact}}/month</li>
</ul>

<p><strong>Target Completion</strong>: December 20, 2025 (before Christmas peak)</p>

<h3>Next Steps</h3>

<p>You mentioned you wanted to think about Phase 2 (the 90-day coaching program).</p>

<p>I completely understand. This is a significant investment (${{Phase2_Investment}}) and you should take time to consider it.</p>

<p>Here's what I recommend:</p>

<h4>While You're Deciding:</h4>
<ol>
  <li><strong>Review the diagnostic summary</strong> (PDF attached to this email)</li>
  <li><strong>Test one quick win</strong> (try {{QuickWin1_Title}} this week)</li>
  <li><strong>Calculate your specific ROI</strong> (use the worksheet I sent)</li>
  <li><strong>Check your calendar</strong> (can you commit 5-8 hours/week for 90 days?)</li>
</ol>

<h4>Questions to Consider:</h4>
<ul>
  <li>Can I fix these systems myself with the diagnostic summary? (DIY path)</li>
  <li>Do I need hands-on coaching and accountability? (Phase 2 path)</li>
  <li>What's my risk tolerance? (December chaos vs. guided implementation)</li>
  <li>What's the opportunity cost of waiting until January 2026?</li>
</ul>

<h3>The Phase 2 Offer (Reminder)</h3>

<p><strong>Investment</strong>: ${{Phase2_Investment}}<br>
<strong>Duration</strong>: 90 days<br>
<strong>Deliverables</strong>: Fix 2-3 systems, 6 bi-weekly coaching calls, daily Slack support<br>
<strong>Expected Outcome</strong>: ${{Phase2_ExpectedRevenue}}/month additional revenue<br>
<strong>ROI Target</strong>: {{Phase2_ROI_Multiple}}X return in first year</p>

<p><strong>Guarantee</strong>: If you don't see ${{Phase2_MinimumRevenue}}/month increase in 90 days, you get a full refund + 30 days of free coaching.</p>

<h3>Timeline</h3>

<p>I'm holding your Phase 2 spot until <strong>{{Phase2_Deadline}}</strong> (5 days from now).</p>

<p>After that, the spot opens up to the next person on the waitlist.</p>

<p>To move forward, just reply "I'm in" and I'll send over the agreement + payment link.</p>

<p>Talk soon,<br>Sang Le</p>

<p><em>P.S. Attached to this email:</em></p>
<ul>
  <li><em>Your Diagnostic Summary (30-page PDF)</em></li>
  <li><em>Custom 45-Day Fix Timeline (Gantt chart)</em></li>
  <li><em>ROI Calculator Worksheet (Excel)</em></li>
  <li><em>Min-Ji Case Study (90-day transformation example)</em></li>
</ul>"""
    },

    "postcall_maybe_email_2": {
        "subject": "How Van Tiny fixed her business in 90 days (case study)",
        "html_body": """<h2>Van Tiny's 90-Day Transformation</h2>

<p>Hi {{first_name}},</p>

<p>I wanted to share a case study that's directly relevant to your situation.</p>

<p>Van Tiny is a Vietnamese salon owner in Seattle. Her situation 6 months ago was almost identical to yours.</p>

<h3>Van's Situation (May 2024)</h3>

<p><strong>The Numbers:</strong></p>
<ul>
  <li>Monthly Revenue: $48K (stuck for 14 months)</li>
  <li>Hours Worked: 72/week (burnout zone)</li>
  <li>No-show Rate: 31% (bleeding money)</li>
  <li>Team Turnover: 3 stylists quit in 6 months</li>
</ul>

<p><strong>BusOS Assessment:</strong></p>
<ul>
  <li>GPS System: 42/100 (RED)</li>
  <li>CREW System: 38/100 (RED)</li>
  <li>Estimated revenue leak: $6,200/month</li>
</ul>

<p><strong>Her Weakest Systems:</strong></p>
<ol>
  <li>Booking & No-Show Prevention (Generate)</li>
  <li>Team Operations & Retention (CREW)</li>
</ol>

<p>Sound familiar?</p>

<h3>The Diagnostic Call (May 15, 2024)</h3>

<p>During our 90-minute diagnostic, we found:</p>

<p><strong>Hidden Opportunity #1</strong>: $38K/year lost to no-shows</p>
<ul>
  <li>Root cause: No deposit system, manual booking process</li>
  <li>Fix: Automated booking + $50 deposits</li>
  <li>Timeline: 2 weeks</li>
</ul>

<p><strong>Hidden Opportunity #2</strong>: $28K/year lost to team inefficiency</p>
<ul>
  <li>Root cause: No role clarity, everyone does everything</li>
  <li>Fix: Role specialization + capacity planning</li>
  <li>Timeline: 3 weeks</li>
</ul>

<p><strong>Hidden Opportunity #3</strong>: $22K/year missed upsells</p>
<ul>
  <li>Root cause: No package system, team not trained on selling</li>
  <li>Fix: 3-tier package structure + sales training</li>
  <li>Timeline: 4 weeks</li>
</ul>

<p><strong>Total Opportunity</strong>: $88K/year ($7,333/month)</p>

<h3>The Decision</h3>

<p>Van said: "Sang, I've tried 4 consultants. They all gave me reports. Nothing changed. Why should I believe you?"</p>

<p>Fair question.</p>

<p>My answer: "This isn't consulting. This is coaching. I'm not giving you a report and leaving. I'm working WITH you for 90 days until the systems are fixed. Daily Slack check-ins, bi-weekly calls, templates, scripts. If it doesn't work, full refund."</p>

<p>She enrolled in Phase 2B (90-day coaching) on May 17, 2024.</p>

<h3>The 90-Day Implementation</h3>

<p><strong>Weeks 1-3: Fix Booking System</strong></p>
<ul>
  <li>Set up automated booking (Acuity + deposits)</li>
  <li>Created no-show prevention system (reminders + penalties)</li>
  <li>Result: No-show rate dropped from 31% → 14%</li>
  <li>Revenue impact: +$3,200/month</li>
</ul>

<p><strong>Weeks 4-6: Fix Team Operations</strong></p>
<ul>
  <li>Defined 4 clear roles (specialist model)</li>
  <li>Built capacity planning system (Excel tool)</li>
  <li>Result: Team efficiency up 28%, 0 turnover in 90 days</li>
  <li>Revenue impact: +$2,400/month</li>
</ul>

<p><strong>Weeks 7-10: Build Package System</strong></p>
<ul>
  <li>Created 3-tier package structure ($180/$320/$580)</li>
  <li>Trained team on upselling (scripts + role-play)</li>
  <li>Result: 38% of customers bought packages</li>
  <li>Revenue impact: +$1,850/month</li>
</ul>

<p><strong>Weeks 11-12: Optimize & Scale</strong></p>
<ul>
  <li>Fine-tuned processes, removed bottlenecks</li>
  <li>Set up metrics dashboard (weekly KPIs)</li>
  <li>Prepared for summer surge</li>
</ul>

<h3>The Results (August 2024)</h3>

<p><strong>Before (May 2024):</strong></p>
<ul>
  <li>Revenue: $48K/month</li>
  <li>Hours worked: 72/week</li>
  <li>No-show rate: 31%</li>
  <li>Team: 4 stylists (high turnover)</li>
</ul>

<p><strong>After (August 2024):</strong></p>
<ul>
  <li>Revenue: $80K/month (+67% increase)</li>
  <li>Hours worked: 45/week (-38% reduction)</li>
  <li>No-show rate: 12% (-61% reduction)</li>
  <li>Team: 6 stylists (zero turnover)</li>
</ul>

<p><strong>ROI Calculation:</strong></p>
<ul>
  <li>Investment: $12,000 (Phase 2B coaching)</li>
  <li>Additional monthly revenue: $32K</li>
  <li>First-year additional revenue: $384K</li>
  <li>ROI: 32X</li>
</ul>

<h3>Van's Biggest Regret</h3>

<p>"I should have done this 14 months earlier when I first got stuck at $48K. I would have made an extra $450K by now."</p>

<h3>Your Parallel Situation</h3>

<p>{{first_name}}, look at the similarities:</p>

<table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
  <tr style="background: #f3f4f6;">
    <th style="padding: 12px; text-align: left; border: 1px solid #e5e7eb;">Metric</th>
    <th style="padding: 12px; text-align: left; border: 1px solid #e5e7eb;">Van (May 2024)</th>
    <th style="padding: 12px; text-align: left; border: 1px solid #e5e7eb;">You (Today)</th>
  </tr>
  <tr>
    <td style="padding: 12px; border: 1px solid #e5e7eb;">Weakest System 1</td>
    <td style="padding: 12px; border: 1px solid #e5e7eb;">Generate (Booking)</td>
    <td style="padding: 12px; border: 1px solid #e5e7eb;">{{WeakestSystem1}}</td>
  </tr>
  <tr>
    <td style="padding: 12px; border: 1px solid #e5e7eb;">Weakest System 2</td>
    <td style="padding: 12px; border: 1px solid #e5e7eb;">CREW (Team Ops)</td>
    <td style="padding: 12px; border: 1px solid #e5e7eb;">{{WeakestSystem2}}</td>
  </tr>
  <tr>
    <td style="padding: 12px; border: 1px solid #e5e7eb;">Revenue Leak</td>
    <td style="padding: 12px; border: 1px solid #e5e7eb;">$6,200/month</td>
    <td style="padding: 12px; border: 1px solid #e5e7eb;">${{TotalRevenueLeak}}/month</td>
  </tr>
  <tr>
    <td style="padding: 12px; border: 1px solid #e5e7eb;">Opportunity Found</td>
    <td style="padding: 12px; border: 1px solid #e5e7eb;">$88K/year</td>
    <td style="padding: 12px; border: 1px solid #e5e7eb;">${{AnnualOpportunityValue}}/year</td>
  </tr>
</table>

<h3>The Question</h3>

<p>Van took 90 days to go from $48K → $80K/month.</p>

<p>What would an extra $32K/month mean for your business? Your life?</p>

<h3>Your Phase 2 Decision</h3>

<p>You have until <strong>{{Phase2_Deadline}}</strong> (3 days from now) to decide.</p>

<p><strong>Option A: Enroll in Phase 2B (Van's Path)</strong></p>
<ul>
  <li>Investment: ${{Phase2_Investment}}</li>
  <li>Timeline: 90 days</li>
  <li>Support: Daily Slack + bi-weekly calls</li>
  <li>Guarantee: ${{Phase2_MinimumRevenue}}/month increase or full refund</li>
  <li>Expected outcome: ${{Phase2_ExpectedRevenue}}/month additional revenue</li>
</ul>

<p><strong>Option B: DIY (Use Diagnostic Summary)</strong></p>
<ul>
  <li>Investment: $0 (you already paid for diagnostic)</li>
  <li>Timeline: Unknown (depends on your execution speed)</li>
  <li>Support: None (you're on your own)</li>
  <li>Risk: May not execute correctly, miss December opportunity</li>
</ul>

<p>To enroll in Phase 2B, just reply "I'm in" and I'll send the agreement.</p>

<p>Talk soon,<br>Sang Le</p>

<p><em>P.S. Van's full case study (30 pages, implementation details) is available if you enroll. You'll see the exact systems she fixed, templates she used, and mistakes she avoided.</em></p>"""
    },

    "postcall_maybe_email_3": {
        "subject": "Last chance for November start (closes Friday), {{first_name}}",
        "html_body": """<h2>Final Call: Phase 2 Enrollment (Closes Friday)</h2>

<p>Hi {{first_name}},</p>

<p>Your Phase 2 enrollment window closes on <strong>{{Phase2_Deadline}}</strong> (this Friday).</p>

<p>After that, your spot goes to the next person on the waitlist.</p>

<p>I wanted to send one final email to help you make the decision.</p>

<h3>Quick Recap: What You Get in Phase 2</h3>

<p><strong>The Program:</strong></p>
<ul>
  <li>90-day coaching program (November → January)</li>
  <li>Fix 2-3 critical business systems</li>
  <li>6 bi-weekly 1-on-1 coaching calls (60 min each)</li>
  <li>Daily Slack support (15-min response time during business hours)</li>
  <li>Templates, scripts, tools (everything Van used)</li>
</ul>

<p><strong>The Systems We'll Fix:</strong></p>
<ol>
  <li>{{WeakestSystem1}} (your #1 priority)</li>
  <li>{{WeakestSystem2}} (your #2 priority)</li>
  <li>Quick wins and optimizations (bonus systems as time allows)</li>
</ol>

<p><strong>The Timeline:</strong></p>
<ul>
  <li><strong>Weeks 1-4</strong>: Fix {{WeakestSystem1}} → Expected impact: ${{Phase1_Impact}}/month</li>
  <li><strong>Weeks 5-8</strong>: Fix {{WeakestSystem2}} → Expected impact: ${{Phase2_Impact}}/month</li>
  <li><strong>Weeks 9-12</strong>: Optimize, scale, prepare for surge → Expected impact: ${{Phase3_Impact}}/month</li>
</ul>

<p><strong>Target Completion</strong>: January 31, 2026 (systems ready for 2026 growth)</p>

<h3>The Numbers</h3>

<p><strong>Investment:</strong></p>
<ul>
  <li>Phase 2B: ${{Phase2_Investment}}</li>
  <li>Payment options: Full (5% discount) or 3 monthly installments</li>
</ul>

<p><strong>Expected Return:</strong></p>
<ul>
  <li>Conservative estimate: ${{Phase2_ExpectedRevenue}}/month additional revenue</li>
  <li>First-year total: ${{Phase2_FirstYearRevenue}}</li>
  <li>ROI: {{Phase2_ROI_Multiple}}X</li>
</ul>

<p><strong>Guarantee:</strong></p>
<ul>
  <li>If you don't see ${{Phase2_MinimumRevenue}}/month increase in 90 days, full refund + 30 days free coaching</li>
  <li>You keep all templates, tools, and resources even if you request refund</li>
</ul>

<h3>Common Objections (Honest Answers)</h3>

<p><strong>"I'm not sure I can commit 5-8 hours/week for 90 days"</strong></p>
<p>Valid concern. If you're already working 70+ hours/week, this might not be the right time. But consider: Van was working 72 hours/week when she started. By week 6, she was down to 52 hours. By week 12, she was at 45 hours. The time investment pays for itself by freeing up your calendar.</p>

<p><strong>"What if I can't execute the changes in my business?"</strong></p>
<p>That's why I'm here. This isn't consulting (here's a report, good luck). This is coaching. Daily Slack check-ins, bi-weekly calls, templates, scripts. I'm working WITH you until it's done. If you get stuck, we fix it together.</p>

<p><strong>"${{Phase2_Investment}} is a lot of money"</strong></p>
<p>Agreed. But compare to your current revenue leak: ${{TotalRevenueLeak}}/month = ${{AnnualRevenueLeak}}/year. You're already spending this money on broken systems. Phase 2 redirects that money into your revenue instead of the leak.</p>

<p><strong>"What if it doesn't work for me like it worked for Van?"</strong></p>
<p>Covered by the guarantee. If you don't see ${{Phase2_MinimumRevenue}}/month increase in 90 days, you get a full refund. Zero risk on your side. All risk on my side (I have to deliver results or I don't get paid).</p>

<h3>The Two Paths</h3>

<p><strong>Path A: Enroll in Phase 2B (Van's Path)</strong></p>
<ul>
  <li>Start: This week</li>
  <li>Finish: January 31, 2026</li>
  <li>Support: Daily (you're not alone)</li>
  <li>Outcome: Systems fixed, ${{Phase2_ExpectedRevenue}}/month additional revenue</li>
  <li>Risk: Low (guarantee protects you)</li>
</ul>

<p><strong>Path B: DIY with Diagnostic Summary</strong></p>
<ul>
  <li>Start: Whenever you have time</li>
  <li>Finish: Unknown</li>
  <li>Support: None (you figure it out)</li>
  <li>Outcome: Depends on execution quality</li>
  <li>Risk: Medium (might miss December, might not execute correctly)</li>
</ul>

<h3>Decision Time</h3>

<p>Your enrollment window closes on <strong>{{Phase2_Deadline}}</strong> (Friday at 11:59 PM).</p>

<p>After that, I can't hold your spot anymore.</p>

<p><strong>To enroll:</strong></p>
<ol>
  <li>Reply "I'm in" to this email</li>
  <li>I'll send the agreement + payment link (today)</li>
  <li>We'll schedule Kickoff Call #1 for next week</li>
  <li>You'll get access to Slack channel + resource library immediately</li>
</ol>

<p><strong>If you're passing:</strong></p>
<ul>
  <li>No hard feelings! I respect whatever decision is right for you</li>
  <li>You keep the diagnostic summary + all resources I sent</li>
  <li>You can re-apply for Phase 2 in the future (if spots available)</li>
  <li>You'll stay on my general email list (weekly valuable content)</li>
</ul>

<h3>Final Thought</h3>

<p>Van's biggest regret: "I should have done this 14 months earlier."</p>

<p>Don't let that be your regret in March 2026.</p>

<p>Talk soon,<br>Sang Le</p>

<p><em>P.S. Questions? Reply to this email. I read every response personally.</em></p>

<p><em>P.P.S. Reminder of what you get if you enroll:</em></p>
<ul>
  <li><em>90-day coaching program (6 bi-weekly calls + daily Slack)</em></li>
  <li><em>Fix 2-3 critical systems (custom implementation)</em></li>
  <li><em>Templates, scripts, tools (everything Van used)</em></li>
  <li><em>${{Phase2_MinimumRevenue}}/month guarantee or full refund</em></li>
  <li><em>Expected outcome: ${{Phase2_ExpectedRevenue}}/month additional revenue</em></li>
  <li><em>Investment: ${{Phase2_Investment}} (payment plan available)</em></li>
</ul>"""
    },

    # ONBOARDING SEQUENCE
    "onboarding_phase1_email_1": {
        "subject": "🎉 Welcome to the Christmas Readiness Diagnostic, {{first_name}}!",
        "html_body": """<h2>🎉 Welcome to Your 90-Day Business Transformation!</h2>

<p>Hi {{first_name}},</p>

<p>Congratulations on enrolling in Phase 2B!</p>

<p>You just made the decision that will change your business trajectory for 2026.</p>

<h3>What Happens Next</h3>

<p><strong>Today (Day 1):</strong></p>
<ul>
  <li>✅ You're reading this welcome email</li>
  <li>📧 You'll receive Slack invitation (check your email in next 15 minutes)</li>
  <li>📚 You'll get access to Resource Library (templates, scripts, tools)</li>
  <li>📅 We'll schedule Kickoff Call #1 (60 minutes, this week)</li>
</ul>

<p><strong>This Week (Days 1-7):</strong></p>
<ul>
  <li>📞 Kickoff Call #1: Review diagnostic results, confirm 90-day timeline</li>
  <li>🎯 Define success metrics (what does "win" look like?)</li>
  <li>🛠️ Start fixing {{WeakestSystem1}} (Week 1 tasks assigned)</li>
  <li>💬 Daily Slack check-ins (I'll ask for updates every morning)</li>
</ul>

<h3>Your 90-Day Roadmap</h3>

<p><strong>Phase 1: Weeks 1-4 (Foundation)</strong></p>
<ul>
  <li><strong>Focus</strong>: Fix {{WeakestSystem1}}</li>
  <li><strong>Calls</strong>: Kickoff Call #1 (Week 1) + Implementation Call #2 (Week 3)</li>
  <li><strong>Expected Impact</strong>: ${{Phase1_Impact}}/month</li>
</ul>

<p><strong>Phase 2: Weeks 5-8 (Optimization)</strong></p>
<ul>
  <li><strong>Focus</strong>: Fix {{WeakestSystem2}}</li>
  <li><strong>Calls</strong>: Implementation Call #3 (Week 5) + Implementation Call #4 (Week 7)</li>
  <li><strong>Expected Impact</strong>: ${{Phase2_Impact}}/month</li>
</ul>

<p><strong>Phase 3: Weeks 9-12 (Scale)</strong></p>
<ul>
  <li><strong>Focus</strong>: Quick wins, optimizations, team training</li>
  <li><strong>Calls</strong>: Implementation Call #5 (Week 9) + Graduation Call #6 (Week 12)</li>
  <li><strong>Expected Impact</strong>: ${{Phase3_Impact}}/month</li>
</ul>

<p><strong>Target Completion</strong>: {{Program_EndDate}}</p>

<h3>How This Program Works</h3>

<p><strong>Slack (Daily Communication):</strong></p>
<ul>
  <li>Post daily updates (what you did, what's blocking you)</li>
  <li>I'll respond within 15 minutes during business hours (Mon-Fri, 8am-6pm PST)</li>
  <li>Ask questions anytime (no such thing as a dumb question)</li>
  <li>Share wins, celebrate progress</li>
</ul>

<p><strong>Bi-Weekly Calls (Every 2 Weeks):</strong></p>
<ul>
  <li>60-minute deep-dive implementation calls</li>
  <li>Review progress, troubleshoot blockers, adjust timeline</li>
  <li>I'll share specific tactics and examples from other clients</li>
  <li>You'll leave each call with clear action items for next 2 weeks</li>
</ul>

<p><strong>Resource Library (Templates & Tools):</strong></p>
<ul>
  <li>Access granted today (check Slack for link)</li>
  <li>50+ templates (emails, scripts, checklists, calculators)</li>
  <li>Case studies from Van, Min-Ji, and 8 other clients</li>
  <li>Video walkthroughs (step-by-step implementation guides)</li>
</ul>

<h3>What I Need From You</h3>

<p><strong>1. Join Slack (Today):</strong></p>
<ul>
  <li>Check your email for Slack invitation</li>
  <li>Set up your profile (add photo + business name)</li>
  <li>Post intro message: "Hi, I'm [name], I own [business], my 2 weakest systems are [X] and [Y]"</li>
</ul>

<p><strong>2. Schedule Kickoff Call (This Week):</strong></p>
<ul>
  <li>Click this link to book: <a href="https://cal.com/sang-le/kickoff-call">Book Kickoff Call</a></li>
  <li>Choose time that works for you (60 minutes)</li>
  <li>I'll send Zoom link 24 hours before call</li>
</ul>

<p><strong>3. Complete Pre-Call Homework (Before Kickoff):</strong></p>
<ul>
  <li>Review diagnostic summary (PDF I sent earlier)</li>
  <li>Write down your top 3 goals for 90 days</li>
  <li>Identify your biggest fear/concern about the program</li>
  <li>Block 5-8 hours/week on your calendar for implementation</li>
</ul>

<h3>Your Success Metrics</h3>

<p>We'll track these KPIs weekly:</p>
<ul>
  <li><strong>Revenue</strong>: Monthly revenue (target: ${{Target_MonthlyRevenue}})</li>
  <li><strong>{{WeakestSystem1}} Score</strong>: BusOS assessment (target: 70+/100)</li>
  <li><strong>{{WeakestSystem2}} Score</strong>: BusOS assessment (target: 70+/100)</li>
  <li><strong>Revenue Leak</strong>: Monthly leak (target: <${{Target_RevenueLeak}})</li>
  <li><strong>Team Happiness</strong>: Team satisfaction score (target: 8+/10)</li>
</ul>

<p>You'll get weekly progress dashboard every Monday in Slack.</p>

<h3>The Guarantee (Reminder)</h3>

<p>If you don't see ${{Phase2_MinimumRevenue}}/month increase in revenue by Day 90, you get:</p>
<ul>
  <li>Full refund (100% of your investment back)</li>
  <li>30 days of free coaching (we keep working until you hit the goal)</li>
  <li>You keep all templates, tools, resources (no clawback)</li>
</ul>

<p>Zero risk on your side. All risk on my side.</p>

<h3>Let's Do This!</h3>

<p>I'm excited to work with you over the next 90 days.</p>

<p>Van went from $48K → $80K/month in this program.</p>

<p>Min-Ji went from $50K → $85K/month.</p>

<p>You're next.</p>

<p>See you in Slack!<br>Sang Le</p>

<p><em>P.S. Week 1 action items:</em></p>
<ol>
  <li><em>Join Slack (today)</em></li>
  <li><em>Book Kickoff Call (this week)</em></li>
  <li><em>Complete pre-call homework (before call)</em></li>
  <li><em>Review Resource Library (start browsing templates)</em></li>
</ol>"""
    },

    "onboarding_phase1_email_2": {
        "subject": "Week 1 Prep Checklist - {{first_name}}",
        "html_body": """<h2>Week 1 Prep Checklist</h2>

<p>Hi {{first_name}},</p>

<p>You're 3 days into the program. Here's your Week 1 prep checklist to make sure you're ready for our Kickoff Call.</p>

<h3>✅ Week 1 Checklist (Complete Before Kickoff Call)</h3>

<p><strong>1. Technical Setup (20 minutes):</strong></p>
<ul>
  <li>☐ Join Slack workspace (check email for invite)</li>
  <li>☐ Set up Slack profile (photo + business name)</li>
  <li>☐ Post intro message in #introductions channel</li>
  <li>☐ Download Resource Library (link in Slack #resources channel)</li>
  <li>☐ Test Zoom (make sure video/audio works)</li>
</ul>

<p><strong>2. Pre-Call Homework (60 minutes):</strong></p>
<ul>
  <li>☐ Re-read diagnostic summary (PDF, pages 1-15)</li>
  <li>☐ Write down top 3 goals for 90 days (be specific)</li>
  <li>☐ Identify biggest fear/concern (what could go wrong?)</li>
  <li>☐ Review current team capacity (how many hours/week can you commit?)</li>
  <li>☐ Gather baseline metrics (current revenue, no-show rate, team size)</li>
</ul>

<p><strong>3. Calendar Planning (30 minutes):</strong></p>
<ul>
  <li>☐ Block 5-8 hours/week for implementation (recurring calendar event)</li>
  <li>☐ Schedule all 6 coaching calls (every 2 weeks, 60 min each)</li>
  <li>☐ Add daily Slack check-in reminder (9am daily)</li>
  <li>☐ Block December 20-31 for holiday break (no work during this period)</li>
</ul>

<p><strong>4. Team Alignment (Optional, 30 minutes):</strong></p>
<ul>
  <li>☐ Inform team about 90-day transformation program</li>
  <li>☐ Explain what will change (new systems, processes)</li>
  <li>☐ Get buy-in from key team members</li>
  <li>☐ Assign point person for implementation support</li>
</ul>

<h3>Your Kickoff Call Agenda</h3>

<p>During our first call ({{Kickoff_Call_Date}}, {{Kickoff_Call_Time}}), we'll cover:</p>

<p><strong>Part 1: Diagnostic Deep Dive (20 minutes):</strong></p>
<ul>
  <li>Review your BusOS assessment results in detail</li>
  <li>Discuss your 2 weakest systems ({{WeakestSystem1}} + {{WeakestSystem2}})</li>
  <li>Clarify hidden opportunities we found (${{TotalOpportunityValue}}/month)</li>
  <li>Answer any questions about the diagnostic summary</li>
</ul>

<p><strong>Part 2: 90-Day Roadmap (20 minutes):</strong></p>
<ul>
  <li>Confirm Weeks 1-4 plan (fix {{WeakestSystem1}})</li>
  <li>Confirm Weeks 5-8 plan (fix {{WeakestSystem2}})</li>
  <li>Confirm Weeks 9-12 plan (optimize + scale)</li>
  <li>Adjust timeline based on your capacity</li>
</ul>

<p><strong>Part 3: Week 1 Action Items (15 minutes):</strong></p>
<ul>
  <li>Define specific tasks for Week 1 (fix {{WeakestSystem1}} foundation)</li>
  <li>Assign templates/resources you'll need</li>
  <li>Set success metrics (what does "done" look like?)</li>
  <li>Identify potential blockers (what could stop you?)</li>
</ul>

<p><strong>Part 4: Q&A + Next Steps (5 minutes):</strong></p>
<ul>
  <li>Answer your questions</li>
  <li>Schedule Implementation Call #2 (2 weeks from now)</li>
  <li>Confirm daily Slack check-in expectations</li>
</ul>

<h3>Common Week 1 Questions</h3>

<p><strong>Q: How much time will I need to commit each week?</strong></p>
<p>A: 5-8 hours/week on average. Week 1 is usually 6-8 hours (setup heavy). Weeks 2-12 are typically 4-6 hours (maintenance mode).</p>

<p><strong>Q: What if I get stuck on something?</strong></p>
<p>A: Post in Slack immediately. I'll respond within 15 minutes during business hours. Don't wait days to ask for help.</p>

<p><strong>Q: Can I involve my team in the implementation?</strong></p>
<p>A: Absolutely! In fact, I encourage it. You can add 1-2 team members to Slack (free). They'll see the templates, participate in discussions, help with execution.</p>

<p><strong>Q: What if I can't complete Week 1 tasks on time?</strong></p>
<p>A: No problem. We'll adjust the timeline. This is YOUR transformation, not a rigid boot camp. Life happens, businesses have emergencies. Just communicate in Slack and we'll figure it out.</p>

<h3>What to Bring to Kickoff Call</h3>

<ul>
  <li>✅ Your diagnostic summary (PDF, printed or on screen)</li>
  <li>✅ Top 3 goals for 90 days (written down)</li>
  <li>✅ Current baseline metrics (revenue, no-show rate, team size)</li>
  <li>✅ Questions list (anything you're confused about)</li>
  <li>✅ Open mindset (ready to implement, not just listen)</li>
</ul>

<h3>Week 1 Resources</h3>

<p>I've added these to Slack #resources channel:</p>
<ul>
  <li>📄 Van's Week 1 Implementation Guide (what she did, step-by-step)</li>
  <li>📄 Min-Ji's Kickoff Call Notes (example of good goal-setting)</li>
  <li>📊 Week 1 Task Template (Excel, track your progress)</li>
  <li>🎥 Video: "How to Set Up Your Business for 90-Day Transformation" (12 min)</li>
</ul>

<h3>Your Week 1 Focus</h3>

<p>This week is all about <strong>FOUNDATION</strong>:</p>
<ul>
  <li>Get set up (Slack, calendar, team alignment)</li>
  <li>Understand the roadmap (what we're doing and why)</li>
  <li>Start {{WeakestSystem1}} foundation (first small wins)</li>
</ul>

<p>Don't try to fix everything in Week 1. We have 90 days. Pace yourself.</p>

<h3>See You on the Call!</h3>

<p>Looking forward to our Kickoff Call on {{Kickoff_Call_Date}}.</p>

<p>If you haven't booked it yet, click here: <a href="https://cal.com/sang-le/kickoff-call">Book Kickoff Call</a></p>

<p>Talk soon,<br>Sang Le</p>

<p><em>P.S. Reminder to join Slack if you haven't already. That's where 90% of the magic happens.</em></p>"""
    },

    "onboarding_phase1_email_3": {
        "subject": "Week 1 starts tomorrow—ready? {{first_name}}",
        "html_body": """<h2>Week 1 Starts Tomorrow!</h2>

<p>Hi {{first_name}},</p>

<p>Tomorrow is your Kickoff Call: <strong>{{Kickoff_Call_Date}} at {{Kickoff_Call_Time}}</strong>.</p>

<p>This is where your 90-day transformation officially begins.</p>

<h3>Final Checklist (Complete Tonight)</h3>

<p><strong>Technical Setup:</strong></p>
<ul>
  <li>☐ Zoom link saved (check your calendar or Slack)</li>
  <li>☐ Camera and microphone tested</li>
  <li>☐ Quiet space booked (60 minutes, no interruptions)</li>
  <li>☐ Slack open in browser or app</li>
</ul>

<p><strong>Pre-Call Homework:</strong></p>
<ul>
  <li>☐ Diagnostic summary reviewed (PDF, pages 1-15)</li>
  <li>☐ Top 3 goals written down (specific, measurable)</li>
  <li>☐ Baseline metrics gathered (revenue, no-show rate, team size)</li>
  <li>☐ Questions list prepared (anything unclear from diagnostic)</li>
</ul>

<p><strong>Mindset Prep:</strong></p>
<ul>
  <li>☐ Calendar cleared for 60 minutes (no interruptions)</li>
  <li>☐ Notebook + pen ready (take notes during call)</li>
  <li>☐ Open mindset (ready to implement, not just listen)</li>
</ul>

<h3>What to Expect Tomorrow</h3>

<p><strong>Before the Call (15 minutes before):</strong></p>
<ul>
  <li>I'll post Zoom link in Slack (if not already in calendar)</li>
  <li>Join 5 minutes early to test audio/video</li>
  <li>Have diagnostic summary PDF open on screen</li>
</ul>

<p><strong>During the Call (60 minutes):</strong></p>
<ul>
  <li><strong>0-20 min</strong>: Diagnostic deep dive (review assessment results)</li>
  <li><strong>20-40 min</strong>: 90-day roadmap confirmation (Weeks 1-12 plan)</li>
  <li><strong>40-55 min</strong>: Week 1 action items (specific tasks for next 7 days)</li>
  <li><strong>55-60 min</strong>: Q&A + next steps</li>
</ul>

<p><strong>After the Call (Within 24 hours):</strong></p>
<ul>
  <li>I'll post Week 1 action items in Slack (detailed task list)</li>
  <li>You'll receive recording link (if you want to review later)</li>
  <li>You'll have access to Week 1 templates/resources</li>
  <li>We'll schedule Implementation Call #2 (2 weeks from now)</li>
</ul>

<h3>Your Week 1 Objectives</h3>

<p>After tomorrow's call, here's what you'll accomplish in Week 1:</p>

<p><strong>Primary Objective:</strong></p>
<ul>
  <li>Start fixing {{WeakestSystem1}} (foundation layer)</li>
  <li>Expected impact: First measurable results by Day 7</li>
</ul>

<p><strong>Secondary Objectives:</strong></p>
<ul>
  <li>Set up tracking dashboard (weekly KPI monitoring)</li>
  <li>Align team on transformation plan</li>
  <li>Establish daily Slack check-in habit</li>
</ul>

<h3>Questions I'll Ask You Tomorrow</h3>

<p>To help you prepare, here are the questions I'll ask during the call:</p>

<ol>
  <li><strong>"What are your top 3 goals for the next 90 days?"</strong> (Be specific: revenue target, team goal, personal goal)</li>
  <li><strong>"What's your biggest fear about this transformation?"</strong> (Common answers: team resistance, not having enough time, failing to execute)</li>
  <li><strong>"How much time can you realistically commit each week?"</strong> (Be honest: 4 hours? 8 hours? 12 hours?)</li>
  <li><strong>"What would make this program a '10/10 success' for you?"</strong> (What specific outcome would make you say "this was worth it"?)</li>
  <li><strong>"What's blocking you right now from fixing {{WeakestSystem1}}?"</strong> (Lack of knowledge? Lack of time? Team resistance?)</li>
</ol>

<p>Think about these tonight. Your answers will shape our 90-day plan.</p>

<h3>The Van / Min-Ji Reminder</h3>

<p><strong>Van's Week 1 (May 2024):</strong></p>
<ul>
  <li>Goal: Fix booking system (reduce 31% no-show rate)</li>
  <li>Action: Set up Acuity + $50 deposits</li>
  <li>Result: No-show rate dropped to 22% in first week (9% improvement)</li>
  <li>Revenue impact: +$1,200 in Week 1 alone</li>
</ul>

<p><strong>Min-Ji's Week 1 (April 2024):</strong></p>
<ul>
  <li>Goal: Fix team scheduling (reduce burnout)</li>
  <li>Action: Define 4 clear roles (specialist model)</li>
  <li>Result: Team efficiency up 12% in first week</li>
  <li>Revenue impact: +$800 in Week 1 alone</li>
</ul>

<p><strong>Your Week 1 (starts tomorrow):</strong></p>
<ul>
  <li>Goal: Fix {{WeakestSystem1}}</li>
  <li>Action: We'll define together on the call</li>
  <li>Expected result: First measurable improvement by Day 7</li>
  <li>Expected revenue impact: ${{Week1_ExpectedImpact}}</li>
</ul>

<h3>Last Reminders</h3>

<p><strong>Kickoff Call Details:</strong></p>
<ul>
  <li><strong>Date</strong>: {{Kickoff_Call_Date}}</li>
  <li><strong>Time</strong>: {{Kickoff_Call_Time}} (your timezone)</li>
  <li><strong>Duration</strong>: 60 minutes</li>
  <li><strong>Zoom Link</strong>: Check Slack or calendar invite</li>
</ul>

<p><strong>What to Bring:</strong></p>
<ul>
  <li>✅ Diagnostic summary PDF (printed or on screen)</li>
  <li>✅ Top 3 goals (written down)</li>
  <li>✅ Baseline metrics (current numbers)</li>
  <li>✅ Questions list</li>
  <li>✅ Notebook + pen (take notes)</li>
</ul>

<h3>See You Tomorrow!</h3>

<p>I'm excited to kick off your transformation.</p>

<p>This is the beginning of your ${{Phase2_ExpectedRevenue}}/month revenue increase.</p>

<p>Get ready to work. Get ready to win.</p>

<p>Talk tomorrow,<br>Sang Le</p>

<p><em>P.S. Can't make the call? Reply ASAP and we'll reschedule. Don't just no-show.</em></p>

<p><em>P.P.S. Already in Slack? Post "Ready for Week 1!" in #general channel. Let's get hyped.</em></p>"""
    }
}


def query_template_by_name(template_name: str) -> str:
    """Query Notion database to find page ID by template name."""
    try:
        results = notion.databases.query(
            database_id=db_id,
            filter={
                "property": "Template Name",
                "title": {
                    "equals": template_name
                }
            }
        )

        if not results['results']:
            return None

        return results['results'][0]['id']
    except Exception as e:
        print(f"Error querying template '{template_name}': {e}")
        return None


def update_email_body(page_id: str, html_content: str) -> bool:
    """Update the Email Body HTML field in Notion."""
    try:
        # Notion rich_text has 2000 char limit per block, so we need to chunk
        chunks = []
        chunk_size = 1900  # Use 1900 to be safe (below 2000 limit)

        for i in range(0, len(html_content), chunk_size):
            chunk = html_content[i:i + chunk_size]
            chunks.append({"text": {"content": chunk}})

        notion.pages.update(
            page_id=page_id,
            properties={
                "Email Body HTML": {
                    "rich_text": chunks
                }
            }
        )
        return True
    except Exception as e:
        print(f"Error updating page {page_id}: {e}")
        return False


def main():
    """Main execution function."""
    print("="*80)
    print("POPULATING MISSING EMAIL TEMPLATES IN NOTION")
    print("="*80)
    print()

    results = {
        "success": [],
        "failed": [],
        "not_found": []
    }

    for idx, (template_name, template_data) in enumerate(TEMPLATES.items(), 1):
        print(f"[{idx}/9] Processing: {template_name}")
        print(f"  Subject: {template_data['subject']}")

        # Query Notion for page ID
        page_id = query_template_by_name(template_name)

        if not page_id:
            print(f"  ❌ Template not found in Notion database")
            results["not_found"].append(template_name)
            print()
            continue

        print(f"  ✅ Found page ID: {page_id}")

        # Update email body
        success = update_email_body(page_id, template_data['html_body'])

        if success:
            print(f"  ✅ Updated Email Body HTML")
            results["success"].append({
                "name": template_name,
                "page_id": page_id,
                "subject": template_data['subject']
            })
        else:
            print(f"  ❌ Failed to update Email Body HTML")
            results["failed"].append(template_name)

        print()

    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"✅ Successfully updated: {len(results['success'])}")
    print(f"❌ Failed to update: {len(results['failed'])}")
    print(f"⚠️  Not found in database: {len(results['not_found'])}")
    print()

    if results["success"]:
        print("Successfully Updated Templates:")
        for item in results["success"]:
            print(f"  - {item['name']}")
            print(f"    Page ID: {item['page_id']}")
            print(f"    Subject: {item['subject']}")
        print()

    if results["failed"]:
        print("Failed Templates:")
        for name in results["failed"]:
            print(f"  - {name}")
        print()

    if results["not_found"]:
        print("Templates Not Found in Database:")
        for name in results["not_found"]:
            print(f"  - {name}")
        print()

    return results


if __name__ == "__main__":
    main()
