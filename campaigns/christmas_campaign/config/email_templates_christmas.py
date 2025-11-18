"""
Christmas Campaign Email Templates

These templates are extracted from the marketing team's handoff document and uploaded
to Notion Email Templates database for dynamic rendering by Prefect email flows.

Source: /Users/sangle/Dev/action/projects/@agents/businessX/docs/money-model/
        model-16-christmas-traditional-service-2997/implementation/HANDOFF-AUTOMATION-DEVELOPER.md

Template Variables:
- {{first_name}} - Contact first name
- {{email}} - Contact email
- {{assessment_score}} - BusOS assessment score (0-100)
- {{GPSScore}} - GPS system score
- {{GenerateScore}} - Generate subscore
- {{PersuadeScore}} - Persuade subscore
- {{ServeScore}} - Serve subscore
- {{MoneyScore}} - Money system score
- {{WeakestSystem1}} - Name of weakest system
- {{Score1}} - Score of weakest system
- {{RevenueLeakSystem1}} - Monthly revenue leak for System 1
- {{WeakestSystem2}} - Name of 2nd weakest system
- {{Score2}} - Score of 2nd weakest system
- {{RevenueLeakSystem2}} - Monthly revenue leak for System 2
- {{TotalRevenueLeak}} - Sum of System 1 + System 2 leaks
- {{AnnualRevenueLeak}} - TotalRevenueLeak × 12
- {{QuickWinAction}} - Specific action based on weakest system
- {{QuickWinExplanation}} - Why this action works
- {{QuickWinImpact}} - Expected revenue impact

Author: Marketing Team (extracted by automation developer)
Created: 2025-11-18
"""

TEMPLATES = {
    "christmas_email_1": {
        "subject": "[RESULTS] Your salon is losing ${{TotalRevenueLeak_K}}K/month in these 2 systems",
        "html_body": """<h2>Your BusOS Assessment Results Are Ready</h2>

<p>Hi {{first_name}},</p>

<p>You just completed the FREE BusOS Assessment for your salon. Here are your results:</p>

<h3>Your BusOS Scores</h3>

<p><strong>GPS System (Generate, Persuade, Serve)</strong>: {{GPSScore}}/100</p>
<ul>
  <li>Generate (Customer Acquisition): {{GenerateScore}}/100</li>
  <li>Persuade (Sales & Conversion): {{PersuadeScore}}/100</li>
  <li>Serve (Delivery & Retention): {{ServeScore}}/100</li>
</ul>

<p><strong>Money System (Revenue & Profit)</strong>: {{MoneyScore}}/100</p>

<h3>What This Means</h3>

<p><strong>Your Weakest Systems</strong> (costing you the most money):</p>
<ol>
  <li>{{WeakestSystem1}} ({{Score1}}/100) → Estimated revenue leak: ${{RevenueLeakSystem1}}/month</li>
  <li>{{WeakestSystem2}} ({{Score2}}/100) → Estimated revenue leak: ${{RevenueLeakSystem2}}/month</li>
</ol>

<p><strong>Combined Monthly Loss</strong>: ${{TotalRevenueLeak}}/month = ${{AnnualRevenueLeak}}/year</p>

<h3>Quick Win for Today</h3>

<p>Based on your {{WeakestSystem1}} score, here's one thing you can do TODAY to stop the leak:</p>

<p><strong>Action</strong>: {{QuickWinAction}}</p>
<p><strong>Why it works</strong>: {{QuickWinExplanation}}</p>
<p><strong>Expected impact</strong>: {{QuickWinImpact}}</p>

<p>This takes 10-15 minutes and could save you $500-$1,500 this month.</p>

<hr>

<p>Talk soon,<br>Sang Le</p>

<p><em>P.S. Your full assessment report is attached (PDF). Print it and circle the 2 systems you want to fix first.</em></p>""",
        "campaign": "Christmas Campaign",
        "email_number": 1,
        "segment": ["universal"],
        "active": True
    },

    "christmas_email_2": {
        "subject": "{{first_name}}, here's how to fix your {{WeakestSystem1}} system (3 quick wins)",
        "html_body": """<h2>What Your {{GPSScore}}/100 GPS Score Means</h2>

<p>Hi {{first_name}},</p>

<p>Yesterday you saw your BusOS scores. Today, let's talk about what they MEAN and how to improve them.</p>

<h3>Your Weakest System: {{WeakestSystem1}} ({{Score1}}/100)</h3>

<p><strong>What this score means</strong>: {{WeakestSystem1}} = {{WeakestSystemDescription}}. Your {{Score1}}/100 score indicates specific challenges in this area.</p>

<h3>3 Quick Wins to Improve {{WeakestSystem1}}</h3>

<h4>Quick Win #1: {{QuickWin1_Title}}</h4>
<p><strong>Time</strong>: {{QuickWin1_Time}}</p>
<p><strong>Cost</strong>: {{QuickWin1_Cost}}</p>
<p><strong>Impact</strong>: {{QuickWin1_Impact}}</p>

<h4>Quick Win #2: {{QuickWin2_Title}}</h4>
<p><strong>Time</strong>: {{QuickWin2_Time}}</p>
<p><strong>Cost</strong>: {{QuickWin2_Cost}}</p>
<p><strong>Impact</strong>: {{QuickWin2_Impact}}</p>

<h4>Quick Win #3: {{QuickWin3_Title}}</h4>
<p><strong>Time</strong>: {{QuickWin3_Time}}</p>
<p><strong>Cost</strong>: {{QuickWin3_Cost}}</p>
<p><strong>Impact</strong>: {{QuickWin3_Impact}}</p>

<p><strong>Combined Impact of 3 Quick Wins</strong>: $2,500-$4,000/month in new customer revenue</p>

<hr>

<p>Tomorrow (Day 3), I'll share a real December horror story from a salon owner who DIDN'T fix these systems before the rush.</p>

<p>Talk soon,<br>Sang Le</p>""",
        "campaign": "Christmas Campaign",
        "email_number": 2,
        "segment": ["universal"],
        "active": True
    },

    "christmas_email_3": {
        "subject": "She turned away $15K in December bookings (don't be her)",
        "html_body": """<h2>The $15K December Mistake</h2>

<p>Hi {{first_name}},</p>

<p>Let me tell you about Sarah.</p>

<p>December 2023. Sarah owned a successful salon in Vancouver. She was doing $60K/month consistently.</p>

<p>Her BusOS assessment showed the same weaknesses as yours: {{WeakestSystem1}} and {{WeakestSystem2}}.</p>

<p>She ignored it. "I'll fix it after the holidays," she said.</p>

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

<p>Your situation: Same weaknesses ({{WeakestSystem1}} + {{WeakestSystem2}}). Same ${{TotalRevenueLeak}}/month leak.</p>

<p>Your choice: Fix them now, or watch December become your worst month instead of your best.</p>

<p>Tomorrow, I'll show you how to avoid Sarah's mistake.</p>

<p>Talk soon,<br>Sang Le</p>

<p><em>P.S. Sarah eventually fixed her systems in March. She's now at $85K/month. But she'll never get that December 2023 opportunity back.</em></p>""",
        "campaign": "Christmas Campaign",
        "email_number": 3,
        "segment": ["universal"],
        "active": True
    },

    "christmas_email_4": {
        "subject": "40 days to December. Here's how to avoid Sarah's $33K mistake.",
        "html_body": """<h2>Your Christmas Readiness Diagnostic</h2>

<p>Hi {{first_name}},</p>

<p>Yesterday you read about Sarah's $33K December disaster.</p>

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

<p><strong>Layer 1: The Diagnostic</strong> ($3,000 value)</p>
<ul>
  <li>90-minute deep-dive diagnostic call with Sang Le</li>
  <li>Custom 45-day implementation timeline</li>
  <li>Christmas revenue maximizer checklist (47 items)</li>
</ul>

<p><strong>Layer 2: Implementation Support</strong> ($12,000 value)</p>
<ul>
  <li>30-day Slack channel access (daily check-ins)</li>
  <li>2 follow-up implementation calls (30 min each)</li>
  <li>Priority email support (24-hour response)</li>
</ul>

<p><strong>Layer 3: Templates & Resources</strong> ($8,000 value)</p>
<ul>
  <li>No-show reduction system (templates + scripts)</li>
  <li>Team capacity calculator (Excel tool)</li>
  <li>Holiday booking optimization playbook</li>
</ul>

<p><strong>Layer 4: Case Study Library</strong> ($4,000 value)</p>
<ul>
  <li>12 traditional service business case studies</li>
  <li>$10M+ in combined revenue generated</li>
  <li>Specific to salons, spas, fitness studios</li>
</ul>

<p><strong>Layer 5: Founding Member Bonus</strong> ($9,991 value)</p>
<ul>
  <li>$5,997 credit toward Phase 2 (if you choose to continue)</li>
  <li>First access to 90-day transformation program</li>
  <li>Founding member pricing locked forever</li>
</ul>

<p><strong>Total Value</strong>: $36,991<br>
<strong>Your Investment</strong>: $2,997<br>
<strong>Value Multiplier</strong>: 12.3X</p>

<h3>Book Your Diagnostic</h3>

<p>Only 30 Christmas Priority slots available (10 already claimed).</p>

<p><strong>Deadline</strong>: November 15, 2025 (to complete by December 20)</p>

<p><a href="https://cal.com/sang-le/christmas-diagnostic" style="background: #059669; color: white; padding: 16px 32px; text-decoration: none; border-radius: 8px; display: inline-block; margin: 16px 0; font-weight: bold;">Book Your Diagnostic Call →</a></p>

<p>Questions? Reply to this email.</p>

<p>Talk soon,<br>Sang Le</p>

<p><em>P.S. Remember Sarah's mistake: "I'll fix it after the holidays." That cost her $33K. Don't be Sarah.</em></p>""",
        "campaign": "Christmas Campaign",
        "email_number": 4,
        "segment": ["universal"],
        "active": True
    },

    "christmas_email_5": {
        "subject": "How Min-Ji went from $50K/mo → $85K/mo in 90 days (case study)",
        "html_body": """<h2>The Min-Ji Transformation Story</h2>

<p>Hi {{first_name}},</p>

<p>Let me share a quick story about Min-Ji, a Korean salon owner in Toronto.</p>

<h3>The Situation (March 2024)</h3>

<p>Min-Ji's salon:</p>
<ul>
  <li>Revenue: $50K/month (stuck for 18 months)</li>
  <li>She was working 68 hours/week</li>
  <li>BusOS assessment: 2 RED systems (GPS + CREW)</li>
  <li>No-show rate: 28% (industry average: 15%)</li>
</ul>

<p>She almost didn't book the diagnostic. "Sang, I've tried 6 consultants. They all promise results. Why should I believe you?"</p>

<h3>The Diagnostic Call (April 2024)</h3>

<p>We found $74K in hidden opportunities:</p>
<ul>
  <li>$32K/year lost to no-shows (fixable with booking system)</li>
  <li>$18K/year lost to inefficient team scheduling (fixable with operations upgrade)</li>
  <li>$24K/year missed from package upsells (fixable with sales training)</li>
</ul>

<p>She enrolled in Phase 2B (12-week coaching).</p>

<h3>The Results (90 days later)</h3>

<p><strong>Before</strong> (March 2024):</p>
<ul>
  <li>Revenue: $50K/month</li>
  <li>Hours worked: 68/week</li>
  <li>No-show rate: 28%</li>
  <li>Team: 4 stylists (high turnover)</li>
</ul>

<p><strong>After</strong> (June 2024):</p>
<ul>
  <li>Revenue: $85K/month (+70% increase)</li>
  <li>Hours worked: 42/week (-38% reduction)</li>
  <li>No-show rate: 11% (-61% reduction)</li>
  <li>Team: 6 stylists (stable, no turnover)</li>
</ul>

<p><strong>ROI</strong>: $35K additional monthly revenue = $420K/year on a $10,000 investment (Phase 2B) = 42X return</p>

<h3>What She Fixed (In Order)</h3>

<ol>
  <li><strong>Weeks 1-3</strong>: Booking system overhaul (no-show prevention)</li>
  <li><strong>Weeks 4-6</strong>: Team capacity optimization (scheduling + roles)</li>
  <li><strong>Weeks 7-9</strong>: Package upsell system (sales training)</li>
  <li><strong>Weeks 10-12</strong>: Maintenance and optimization</li>
</ol>

<p>Total implementation time: 90 days. Total additional revenue in first year: $420K.</p>

<h3>Her Biggest Regret</h3>

<p>"I should have done this 18 months earlier. I would have made an extra $600K by now."</p>

<h3>Your Opportunity</h3>

<p>Your situation is similar to Min-Ji's March 2024 state:</p>
<ul>
  <li>2 broken systems: {{WeakestSystem1}} + {{WeakestSystem2}}</li>
  <li>Monthly revenue leak: ${{TotalRevenueLeak}}</li>
  <li>Annual opportunity cost: ${{AnnualRevenueLeak}}</li>
</ul>

<p>The question: Do you fix it now (before December) or wait 18 months like Min-Ji?</p>

<p><a href="https://cal.com/sang-le/christmas-diagnostic" style="background: #059669; color: white; padding: 16px 32px; text-decoration: none; border-radius: 8px; display: inline-block; margin: 16px 0; font-weight: bold;">Book Your Diagnostic Call →</a></p>

<p>Talk soon,<br>Sang Le</p>

<p><em>P.S. Min-Ji's transformation case study (full 30-page PDF) is included in your diagnostic package. You'll see the exact systems she fixed and how.</em></p>""",
        "campaign": "Christmas Campaign",
        "email_number": 5,
        "segment": ["universal"],
        "active": True
    },

    "christmas_email_6": {
        "subject": "{{first_name}}, audit these 5 systems before December (FREE checklist)",
        "html_body": """<h2>Your Christmas Readiness Checklist</h2>

<p>Hi {{first_name}},</p>

<p>You've seen your BusOS scores. You know your 2 weakest systems ({{WeakestSystem1}} + {{WeakestSystem2}}).</p>

<p>Before December hits, audit these 5 critical systems:</p>

<h3>System 1: Booking Capacity</h3>

<p>Questions to ask:</p>
<ul>
  <li>Can you handle 2X demand? (December typically = 150-200% of normal bookings)</li>
  <li>What's your no-show rate? (Target: <12%)</li>
  <li>Do you have a waitlist system? (Capture overflow demand)</li>
  <li>Can customers book online 24/7? (Don't lose midnight browsers)</li>
</ul>

<h3>System 2: Team Capacity</h3>

<p>Questions to ask:</p>
<ul>
  <li>Can your team work at 120% capacity for 30 days? (Burnout test)</li>
  <li>Do you have backup stylists if someone gets sick?</li>
  <li>Are roles clearly defined? (No "everyone does everything" chaos)</li>
  <li>Is your team trained on upselling packages? ($180-$250 average ticket goal)</li>
</ul>

<h3>System 3: Operations Under Load</h3>

<p>Questions to ask:</p>
<ul>
  <li>Are your processes documented? (Can team execute without you?)</li>
  <li>What breaks first at 2X volume? (Identify bottlenecks now)</li>
  <li>Do you have peak-load backup plans? (Equipment, supplies, space)</li>
</ul>

<h3>System 4: Cash Flow Management</h3>

<p>Questions to ask:</p>
<ul>
  <li>Can you pay team bonuses in December? (Retention = critical)</li>
  <li>Do you have emergency cash reserves? (3-month runway minimum)</li>
  <li>Are you collecting deposits for December bookings? (Reduce no-shows)</li>
</ul>

<h3>System 5: Marketing & Lead Generation</h3>

<p>Questions to ask:</p>
<ul>
  <li>Are you generating enough leads to fill December? (Start NOW, not Dec 1)</li>
  <li>Do you have a referral system? (Existing customers = best source)</li>
  <li>Are you running holiday promotions? (Gift cards, packages, bundles)</li>
</ul>

<h3>Your Checklist Score</h3>

<p>If you answered "NO" or "MAYBE" to 3+ questions above, your December will look like Sarah's (the $33K disaster from Email 3).</p>

<h3>Two Paths Forward</h3>

<p><strong>Path 1: DIY Audit</strong></p>
<ul>
  <li>Go through this checklist yourself</li>
  <li>Fix what you can before December</li>
  <li>Hope you identified everything critical</li>
</ul>

<p><strong>Path 2: Expert Diagnostic</strong></p>
<ul>
  <li>90-minute diagnostic call with Sang Le</li>
  <li>We audit all 5 systems + your specific weaknesses</li>
  <li>Get a custom 45-day fix timeline</li>
  <li>$5K-$15K opportunity guarantee or full refund</li>
</ul>

<p><a href="https://cal.com/sang-le/christmas-diagnostic" style="background: #059669; color: white; padding: 16px 32px; text-decoration: none; border-radius: 8px; display: inline-block; margin: 16px 0; font-weight: bold;">Book Your Diagnostic Call →</a></p>

<p>Investment: $2,997 (12.3X value = $36,991 total package)</p>

<p>Talk soon,<br>Sang Le</p>

<p><em>P.S. The full Christmas Readiness Checklist (47 items, Excel format) is included in your diagnostic package.</em></p>""",
        "campaign": "Christmas Campaign",
        "email_number": 6,
        "segment": ["universal"],
        "active": True
    },

    "christmas_email_7": {
        "subject": "{{first_name}}, {{Christmas_Slots_Remaining}} Christmas Priority slots left (this is it)",
        "html_body": """<h2>Final Call: Christmas Priority Diagnostic</h2>

<p>Hi {{first_name}},</p>

<p>This is my last email about the Christmas Priority Diagnostic.</p>

<p>After today, I'm closing this email sequence.</p>

<h3>Where We've Been (7 Days)</h3>

<p><strong>Email 1</strong>: You learned your 2 weakest systems ({{WeakestSystem1}} + {{WeakestSystem2}}) are costing you ${{TotalRevenueLeak}}/month</p>

<p><strong>Email 2</strong>: You got 3 quick wins to improve {{WeakestSystem1}}</p>

<p><strong>Email 3</strong>: You read Sarah's $33K December disaster story (ignoring broken systems)</p>

<p><strong>Email 4</strong>: You saw the Christmas Diagnostic offer ($2,997, 12.3X value)</p>

<p><strong>Email 5</strong>: You read Min-Ji's transformation ($50K → $85K in 90 days)</p>

<p><strong>Email 6</strong>: You got the 5-system Christmas Readiness Checklist</p>

<p><strong>Today</strong>: Decision time.</p>

<h3>Two Paths in Front of You</h3>

<p><strong>Path A: Book the Diagnostic (Fix Before December)</strong></p>
<ul>
  <li>90-minute diagnostic call with Sang Le (this week)</li>
  <li>Custom 45-day fix timeline for your 2 broken systems</li>
  <li>$5K-$15K opportunity guarantee (or full refund)</li>
  <li>$36,991 total value package (diagnostic + support + resources)</li>
  <li>Investment: $2,997</li>
  <li><strong>December outcome</strong>: Capture $35K-$70K surge (systems working)</li>
</ul>

<p><strong>Path B: Wait Until January (Miss December)</strong></p>
<ul>
  <li>Fix systems yourself with DIY checklist</li>
  <li>Hope you didn't miss anything critical</li>
  <li>Investment: $0</li>
  <li><strong>December outcome</strong>: Unknown (could be great, could be Sarah's disaster)</li>
</ul>

<h3>The Math</h3>

<p><strong>If you book</strong>:</p>
<ul>
  <li>Investment: $2,997</li>
  <li>Conservative December capture: $35K (extra revenue from fixed systems)</li>
  <li>ROI: 11.7X in 30 days</li>
  <li>Downside protection: $5K-$15K guarantee (full refund if we don't find opportunities)</li>
</ul>

<p><strong>If you wait</strong>:</p>
<ul>
  <li>Investment: $0</li>
  <li>Opportunity cost: $35K-$70K (missed December surge)</li>
  <li>Risk: Systems break under load (Sarah's scenario)</li>
  <li>Timeline: Fix in January = miss the biggest revenue month</li>
</ul>

<h3>Urgency: {{Christmas_Slots_Remaining}} Slots Left</h3>

<p>I opened 30 Christmas Priority slots.</p>

<p>{{Christmas_Slots_Claimed}} are claimed.</p>

<p><strong>{{Christmas_Slots_Remaining}} slots remaining</strong> for November 15 deadline (45-day implementation window).</p>

<p>After November 15, it's too late to fix before December 20.</p>

<h3>What Happens After You Book</h3>

<ol>
  <li><strong>Today</strong>: Book your 90-minute diagnostic call (within 3-5 days)</li>
  <li><strong>Diagnostic call</strong>: We audit your systems, create 45-day timeline</li>
  <li><strong>Days 1-21</strong>: Fix your 2 broken systems (Slack support daily)</li>
  <li><strong>Days 22-45</strong>: Optimize, test under load, prepare team</li>
  <li><strong>December 20</strong>: Systems working, ready for surge</li>
</ol>

<h3>This Is It</h3>

<p>After today, no more emails about the diagnostic.</p>

<p>You'll stay on my general email list (valuable content weekly).</p>

<p>But the Christmas Priority offer closes tonight.</p>

<p><a href="https://cal.com/sang-le/christmas-diagnostic" style="background: #059669; color: white; padding: 16px 32px; text-decoration: none; border-radius: 8px; display: inline-block; margin: 16px 0; font-weight: bold;">Book Your Diagnostic Call →</a></p>

<p><strong>Reminder</strong>:</p>
<ul>
  <li>Investment: $2,997</li>
  <li>Value: $36,991 (12.3X)</li>
  <li>Guarantee: $5K-$15K opportunities or full refund</li>
  <li>Timeline: 45 days (Nov 15 → Dec 20)</li>
  <li>Slots: {{Christmas_Slots_Remaining}} remaining</li>
</ul>

<p>Talk soon,<br>Sang Le</p>

<p><em>P.S. If you're still on the fence, reply to this email with your biggest concern. I read every response.</em></p>

<p><em>P.P.S. Remember: Sarah waited. Cost her $33K. Min-Ji acted. Made $420K extra in first year. Which path will you choose?</em></p>""",
        "campaign": "Christmas Campaign",
        "email_number": 7,
        "segment": ["universal"],
        "active": True
    }
}
