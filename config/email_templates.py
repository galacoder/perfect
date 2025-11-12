"""
Email templates for BusOS Email Sequence.

This module contains all 9 email HTML templates extracted from the n8n workflow:
- Email #1: Assessment invitation (universal)
- Email #2A, #2B, #2C: Segment-specific results (CRITICAL/URGENT/OPTIMIZE)
- Email #3: BusOS Framework introduction (universal)
- Email #4: Christmas Special offer (universal)
- Email #5A, #5B, #5C: Segment-specific closing (CRITICAL/URGENT/OPTIMIZE)

All templates use {{variable}} placeholders for substitution.
"""

# ============================================================================
# EMAIL #1: Assessment Invitation (Universal - sent immediately after signup)
# ============================================================================

EMAIL_1_SUBJECT = "Your Free BusOS Assessment is Ready, {{first_name}}"

EMAIL_1_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Your BusOS Assessment is Ready</title></head><body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;"><p>Hi {{first_name}},</p><p>Welcome! I'm excited to help you fix the broken systems in {{business_name}}.</p><p><strong>Here's your personalized BusOS assessment:</strong></p><p style="text-align: center; margin: 30px 0;"><a href="https://assessment.busos.io/beauty-salon?email={{email}}" style="display: inline-block; background-color: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">Take Your Free Assessment →</a></p><p><strong>This 5-minute assessment will show you:</strong></p><ul style="list-style: none; padding-left: 0;"><li style="margin-bottom: 10px;">✅ Which of your 8 business systems are broken (RED)</li><li style="margin-bottom: 10px;">✅ Which systems need attention soon (ORANGE)</li><li style="margin-bottom: 10px;">✅ Which systems are working well (GREEN)</li></ul><p>Take it now and you'll get your personalized scorecard in minutes.</p><p>Talk soon,<br>[Your Name]<br>BusinessX</p><p style="font-size: 14px; color: #666; margin-top: 30px;"><strong>P.S.</strong> The assessment is completely free. No credit card required.</p></body></html>"""

# ============================================================================
# EMAIL #2A: Results - CRITICAL (sent 24h after assessment completion)
# ============================================================================

EMAIL_2A_SUBJECT = "{{first_name}}, Your BusOS Results: {{red_systems}} Critical Issues Draining Revenue"

EMAIL_2A_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Your BusOS Results - Critical Issues</title></head><body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;"><p>Hi {{first_name}},</p><p>I just reviewed your BusOS assessment for {{business_name}}.</p><p><strong>I'm going to be honest: You have {{red_systems}} critical systems that are BROKEN right now.</strong></p><p style="margin-top: 30px; font-size: 16px;"><strong>Here's what this means:</strong></p><div style="background-color: #ffebee; border-left: 4px solid #f44336; padding: 15px; margin: 20px 0;"><p style="margin: 0 0 10px 0;"><strong>🔴 RED System #1: Lead Generation (Empty Pipeline)</strong></p><ul style="margin: 5px 0; padding-left: 20px; color: #666;"><li>You're relying on walk-ins and word-of-mouth</li><li>This is costing you $3,000-$8,000/month in lost revenue</li><li>New client acquisition is unpredictable and stressful</li></ul></div><div style="background-color: #ffebee; border-left: 4px solid #f44336; padding: 15px; margin: 20px 0;"><p style="margin: 0 0 10px 0;"><strong>🔴 RED System #2: Client Retention (40%+ Churn)</strong></p><ul style="margin: 5px 0; padding-left: 20px; color: #666;"><li>Clients come once or twice, then disappear</li><li>You're working harder to replace lost clients</li><li>Revenue feels like a rollercoaster every month</li></ul></div><div style="background-color: #ffebee; border-left: 4px solid #f44336; padding: 15px; margin: 20px 0;"><p style="margin: 0 0 10px 0;"><strong>🔴 RED System #3: Team Management (High Turnover)</strong></p><ul style="margin: 5px 0; padding-left: 20px; color: #666;"><li>Your best stylists keep leaving</li><li>You're constantly hiring and training</li><li>Service quality is inconsistent</li></ul></div><p style="margin-top: 30px;"><strong>The good news? These issues are fixable.</strong></p><p>I've helped 47 salon owners in {{city}} fix these exact problems in 90 days or less.</p><p><strong>Tomorrow I'll show you the BusOS Framework that makes it possible.</strong></p><p>Talk soon,<br>[Your Name]<br>BusinessX</p><p style="font-size: 14px; color: #666; margin-top: 30px;"><strong>P.S.</strong> If you want to talk about your results before my next email, just reply. I read every message.</p></body></html>"""

# ============================================================================
# EMAIL #2B: Results - URGENT (sent 24h after assessment completion)
# ============================================================================

EMAIL_2B_SUBJECT = "{{first_name}}, Your BusOS Results: 2 Fixable Problems Costing You $10K+/Month"

EMAIL_2B_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Your BusOS Results - Fixable Problems</title></head><body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;"><p>Hi {{first_name}},</p><p>I just reviewed your BusOS assessment for {{business_name}}.</p><p><strong>Here's the good news: Most of your systems are working.</strong></p><p style="margin-top: 30px; font-size: 16px;"><strong>Here's what needs attention:</strong></p><div style="background-color: #fff3e0; border-left: 4px solid #ff9800; padding: 15px; margin: 20px 0;"><p style="margin: 0 0 10px 0;"><strong>🟠 URGENT Issue #1: Client Retention System</strong></p><ul style="margin: 5px 0; padding-left: 20px; color: #666;"><li>You're losing 20-30% of clients after 1-2 visits</li><li>This is leaking $5,000-$8,000/month in recurring revenue</li><li>It's preventable with the right follow-up system</li></ul></div><div style="background-color: #fff3e0; border-left: 4px solid #ff9800; padding: 15px; margin: 20px 0;"><p style="margin: 0 0 10px 0;"><strong>🟠 URGENT Issue #2: Lead Generation Consistency</strong></p><ul style="margin: 5px 0; padding-left: 20px; color: #666;"><li>New client flow is unpredictable month-to-month</li><li>You rely too much on word-of-mouth</li><li>Your team feels the stress during slow months</li></ul></div><p style="margin-top: 30px;"><strong>The better news? You caught these early.</strong></p><p>Most salon owners wait until these turn RED (critical). You didn't.</p><p>That means fixing them will be faster and cheaper than you think.</p><p><strong>Tomorrow I'll show you the BusOS Framework that 47 salon owners in {{city}} used to fix these exact issues in 90 days.</strong></p><p>Talk soon,<br>[Your Name]<br>BusinessX</p><p style="font-size: 14px; color: #666; margin-top: 30px;"><strong>P.S.</strong> Want to chat about your results? Just reply—I read every message.</p></body></html>"""

# ============================================================================
# EMAIL #2C: Results - OPTIMIZE (sent 24h after assessment completion)
# ============================================================================

EMAIL_2C_SUBJECT = "{{first_name}}, Your BusOS Results: 3 Growth Opportunities You're Missing"

EMAIL_2C_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Your BusOS Results - Growth Opportunities</title></head><body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;"><p>Hi {{first_name}},</p><p>I just reviewed your BusOS assessment for {{business_name}}.</p><p>Congratulations! Your systems are mostly GREEN and YELLOW.</p><p>That puts you in the top 20% of salons we assess.</p><p style="margin-top: 30px; font-size: 16px;"><strong>But here's what I noticed:</strong></p><div style="background-color: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin: 20px 0;"><p style="margin: 0 0 10px 0;"><strong>💡 Growth Opportunity #1: Client Lifetime Value</strong></p><ul style="margin: 5px 0; padding-left: 20px; color: #666;"><li>You could add $3,000-$5,000/month by improving retention emails</li><li>It's not broken—it just needs optimization</li><li>Small tweaks = big revenue gains</li></ul></div><div style="background-color: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin: 20px 0;"><p style="margin: 0 0 10px 0;"><strong>💡 Growth Opportunity #2: Referral System</strong></p><ul style="margin: 5px 0; padding-left: 20px; color: #666;"><li>You're getting referrals, but not systematically</li><li>Your team doesn't ask for referrals consistently</li><li>A simple system could double your referral rate</li></ul></div><div style="background-color: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin: 20px 0;"><p style="margin: 0 0 10px 0;"><strong>💡 Growth Opportunity #3: Team Efficiency</strong></p><ul style="margin: 5px 0; padding-left: 20px; color: #666;"><li>Your team is working hard, but not working smart</li><li>Scheduling and processes could save 10+ hours/week</li><li>That's time you could spend on growth</li></ul></div><p style="margin-top: 30px;"><strong>Here's the thing: You've built a solid foundation.</strong></p><p>Now it's time to scale.</p><p><strong>Tomorrow I'll show you the BusOS Framework that helped 47 salon owners in {{city}} break through their revenue ceiling.</strong></p><p>Talk soon,<br>[Your Name]<br>BusinessX</p><p style="font-size: 14px; color: #666; margin-top: 30px;"><strong>P.S.</strong> Curious about your growth potential? Reply and let's chat.</p></body></html>"""

# ============================================================================
# EMAIL #3: BusOS Framework Introduction (Universal - sent 48h after Email #2)
# ============================================================================

EMAIL_3_SUBJECT = "{{first_name}}, Why Your Salon is Like a Bus (And How to Fix It)"

EMAIL_3_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>BusOS Framework Introduction</title></head><body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;"><p>Hi {{first_name}},</p><p>Let me tell you a story.</p><p>Last year, I worked with a salon owner in {{city}}. Let's call her Sarah.</p><p>Sarah's salon was making $75K/month. Not bad.</p><p>But she was working 70-hour weeks. Her team was stressed. And 3 of her best stylists just quit.</p><p>Sound familiar?</p><p style="margin-top: 30px; font-size: 18px; font-weight: bold;">YOUR BUSINESS IS LIKE A BUS WITH 8 SYSTEMS</p><p>Just like a bus has 8 critical systems (engine, transmission, driver, fuel, GPS, etc.), your salon has 8 business systems:</p><ol style="line-height: 2; margin: 20px 0;"><li>🚀 Lead Generation (fuel) - New clients coming in</li><li>💰 Sales (driver) - Converting leads to paying clients</li><li>✂️ Fulfillment (engine) - Delivering your service</li><li>❤️ Client Success (passengers) - Keeping clients happy</li><li>📊 Finance (GPS) - Knowing where your money goes</li><li>⚙️ Operations (transmission) - Daily processes</li><li>👥 Team (crew) - Hiring and training staff</li><li>📣 Marketing (route) - Getting the word out</li></ol><p style="margin-top: 30px;"><strong>Here's the problem: If ONE system breaks, the whole bus stops.</strong></p><p>Sarah had 3 RED systems:</p><ul style="line-height: 2;"><li>No lead generation system (relying on walk-ins)</li><li>No client retention system (40% churn rate)</li><li>No team training system (constant staff turnover)</li></ul><p style="margin-top: 30px;">We fixed those 3 systems in 90 days.</p><p><strong>Result?</strong></p><ul style="line-height: 2;"><li>Revenue: $75K → $105K/month (+40%)</li><li>Hours worked: 70/week → 35/week (-50%)</li><li>Staff turnover: 60%/year → 15%/year (-75%)</li></ul><p style="margin-top: 30px; background-color: #f5f5f5; padding: 15px; border-radius: 5px;"><strong>The BusOS Framework is simple:</strong><br><br><strong>Step 1:</strong> Identify your RED systems (you did this in the assessment)<br><strong>Step 2:</strong> Fix them one at a time (starting with highest impact)<br><strong>Step 3:</strong> Move to ORANGE, then YELLOW, then optimize GREEN</p><p>That's it.</p><p><strong>Tomorrow I'll tell you about the Christmas Special that helped Sarah (and 46 other salon owners) fix their broken systems.</strong></p><p>Talk soon,<br>[Your Name]<br>BusinessX</p><p style="font-size: 14px; color: #666; margin-top: 30px;"><strong>P.S.</strong> Want to see Sarah's full case study? Reply and I'll send it.</p></body></html>"""

# ============================================================================
# EMAIL #4: Christmas Special Offer (Universal - sent 48h after Email #3)
# ============================================================================

EMAIL_4_SUBJECT = "{{first_name}}, The $2,997 Christmas Special for {{business_name}}"

EMAIL_4_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Christmas Special Offer</title></head><body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;"><p>Hi {{first_name}},</p><p>Remember Sarah from yesterday's email?</p><p>The $75K/month salon owner who was working 70 hours/week?</p><p>Here's what I did for her:</p><p style="margin-top: 30px; font-size: 18px; font-weight: bold; text-align: center; background-color: #f5f5f5; padding: 20px; border-radius: 5px;">THE BUSOS TRADITIONAL SERVICE DIAGNOSTIC</p><p>A 90-minute video call where I:</p><ul style="line-height: 2; margin: 20px 0;"><li>✅ Reviewed her full BusOS assessment (all 8 systems)</li><li>✅ Identified her 3 highest-impact fixes</li><li>✅ Created a 30-day action plan (step-by-step)</li><li>✅ Gave her my client retention email templates (worth $5K alone)</li></ul><p>She implemented the plan. 90 days later, she hit $105K/month.</p><p style="margin-top: 30px;"><strong>Now I'm offering the same diagnostic to 12 salon owners before Christmas.</strong></p><p style="margin-top: 30px; font-size: 16px;"><strong>Here's what you get:</strong></p><div style="background-color: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; margin: 20px 0;"><p style="margin: 0 0 10px 0;"><strong>📞 90-Minute Diagnostic Call ($5,000 value)</strong></p><ul style="margin: 5px 0; padding-left: 20px; color: #666;"><li>Deep dive into your {{red_systems}} RED systems</li><li>Priority ranking (what to fix first)</li><li>Roadmap with specific action steps</li></ul></div><div style="background-color: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; margin: 20px 0;"><p style="margin: 0 0 10px 0;"><strong>📋 Personalized Implementation Roadmap ($3,000 value)</strong></p><ul style="margin: 5px 0; padding-left: 20px; color: #666;"><li>30-day action plan</li><li>Weekly milestones and metrics</li><li>Accountability checkpoints</li></ul></div><div style="background-color: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; margin: 20px 0;"><p style="margin: 0 0 10px 0;"><strong>📧 Bonus: Client Retention Email Templates ($4,000 value)</strong></p><ul style="margin: 5px 0; padding-left: 20px; color: #666;"><li>12 proven email templates</li><li>Reduces churn by 20-40%</li><li>Plug-and-play for your salon</li></ul></div><p style="margin-top: 30px; text-align: center; background-color: #fff3e0; padding: 20px; border-radius: 5px;"><strong style="font-size: 18px;">Total Value: $12,000</strong><br><strong style="font-size: 24px; color: #ff5722;">Christmas Special: $2,997</strong></p><p style="margin-top: 30px;"><strong>But here's the catch:</strong></p><p>I'm only taking 12 clients before December 15th.</p><p>Why? Because I work with each client personally. No team. No assistants. Just me.</p><p>As of today, 3 spots are filled.</p><p><strong>Want one of the remaining 9?</strong></p><p style="text-align: center; margin: 30px 0;"><a href="https://calendly.com/businessx/diagnostic-call" style="display: inline-block; background-color: #ff5722; color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 18px;">Book Your Diagnostic Call →</a></p><p>I'll send you a prep questionnaire 24 hours before our call.</p><p>Talk soon,<br>[Your Name]<br>BusinessX</p><p style="font-size: 14px; color: #666; margin-top: 30px;"><strong>P.S.</strong> Not sure if this is right for you? Reply with your biggest question. I'll answer personally within 24 hours.</p><hr style="border: none; border-top: 1px solid #eee; margin: 40px 0;"><p style="font-size: 14px; color: #666;"><strong>FAQ:</strong></p><p style="font-size: 14px; color: #666;"><strong>Q: What if I'm too busy?</strong><br>A: This 90-minute call will save you 10+ hours/week. You can't afford NOT to do this.</p><p style="font-size: 14px; color: #666;"><strong>Q: What if it doesn't work?</strong><br>A: If you implement the roadmap and don't see results in 90 days, I'll refund 100% of your $2,997.</p><p style="font-size: 14px; color: #666;"><strong>Q: Why $2,997?</strong><br>A: One new client pays for this. If you can't get one new client in 90 days, your issues are bigger than I thought.</p></body></html>"""

# ============================================================================
# EMAIL #5A: Final Push - CRITICAL (sent 48h after Email #4)
# ============================================================================

EMAIL_5A_SUBJECT = "{{first_name}}, Last Chance: 3 Spots Left Before Christmas"

EMAIL_5A_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Last Chance - Christmas Special</title></head><body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;"><p>Hi {{first_name}},</p><p><strong>This is my last email before the deadline.</strong></p><p>You have {{red_systems}} critical issues in {{business_name}}.</p><p><strong style="color: #f44336;">These issues won't fix themselves.</strong></p><p style="margin-top: 30px; font-size: 16px;"><strong>Every day you wait:</strong></p><ul style="line-height: 2; margin: 20px 0;"><li>→ You lose $300-$500 in revenue</li><li>→ Your team gets more stressed</li><li>→ Your best clients leave for competitors</li></ul><p style="margin-top: 30px;">I've helped 47 salon owners fix these exact problems.</p><p>But I can only help 12 before Christmas.</p><p style="text-align: center; margin: 30px 0; background-color: #ffebee; padding: 20px; border-radius: 5px;"><strong style="font-size: 20px; color: #f44336;">9 spots are filled. 3 spots left.</strong></p><p><strong>If you're serious about fixing {{business_name}} before 2026, book your diagnostic now:</strong></p><p style="text-align: center; margin: 30px 0;"><a href="https://calendly.com/businessx/diagnostic-call" style="display: inline-block; background-color: #f44336; color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 18px;">Book Now - 3 Spots Left →</a></p><p style="text-align: center; font-size: 16px; color: #f44336;"><strong>Deadline: December 15th, 11:59 PM EST</strong></p><p>After that, I'm closing the calendar until February.</p><p style="margin-top: 30px; background-color: #f5f5f5; padding: 20px; border-radius: 5px;"><strong>Your choice:</strong><br><br><strong>1. Book now</strong> and fix your salon in 90 days<br><strong>2. Wait until February</strong> (and lose another $15,000-$25,000)</p><p style="margin-top: 30px;">I hope I see your name on my calendar.</p><p>[Your Name]<br>BusinessX</p><p style="font-size: 14px; color: #666; margin-top: 30px;"><strong>P.S.</strong> If you're not ready, I understand. But please don't wait until it's too late. These critical issues compound over time.</p></body></html>"""

# ============================================================================
# EMAIL #5B: Final Push - URGENT (sent 48h after Email #4)
# ============================================================================

EMAIL_5B_SUBJECT = "{{first_name}}, 48 Hours Left: Secure Your Spot for the $2,997 Diagnostic"

EMAIL_5B_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>48 Hours Left - Christmas Special</title></head><body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;"><p>Hi {{first_name}},</p><p><strong>Quick update: 7 spots left for the Christmas diagnostic.</strong></p><p>You identified {{orange_systems}} urgent issues in your assessment.</p><p><strong style="color: #ff9800;">These aren't critical yet—but they will be if you don't fix them.</strong></p><p style="margin-top: 30px; font-size: 16px;"><strong>I've seen this pattern 100+ times:</strong></p><ul style="line-height: 2; margin: 20px 0;"><li>→ ORANGE issues become RED issues within 6 months</li><li>→ RED issues cost 3× more to fix than ORANGE</li><li>→ Prevention is cheaper than cure</li></ul><p style="margin-top: 30px;"><strong>You have a choice:</strong></p><div style="background-color: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; margin: 20px 0;"><p style="margin: 0 0 10px 0;"><strong>Option 1: Fix these issues now while they're still manageable</strong></p><ul style="margin: 5px 0; padding-left: 20px; color: #666;"><li>90-minute diagnostic: $2,997</li><li>30-day roadmap included</li><li>Results in 90 days</li></ul></div><div style="background-color: #ffebee; border-left: 4px solid #f44336; padding: 15px; margin: 20px 0;"><p style="margin: 0 0 10px 0;"><strong>Option 2: Wait 6 months and pay 3× more when they're critical</strong></p><ul style="margin: 5px 0; padding-left: 20px; color: #666;"><li>Much harder to fix</li><li>More revenue lost</li><li>More stress for you and your team</li></ul></div><p style="margin-top: 30px;"><strong>I know which one I'd choose.</strong></p><p style="text-align: center; margin: 30px 0;"><a href="https://calendly.com/businessx/diagnostic-call" style="display: inline-block; background-color: #ff9800; color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 18px;">Book Your Diagnostic →</a></p><p style="text-align: center; font-size: 16px; color: #ff9800;"><strong>Deadline: December 15th, 11:59 PM EST</strong></p><p>Talk soon,<br>[Your Name]<br>BusinessX</p><p style="font-size: 14px; color: #666; margin-top: 30px;"><strong>P.S.</strong> Still on the fence? Reply with your biggest objection. I'll respond personally.</p></body></html>"""

# ============================================================================
# EMAIL #5C: Final Push - OPTIMIZE (sent 48h after Email #4)
# ============================================================================

EMAIL_5C_SUBJECT = "{{first_name}}, Ready to Scale {{business_name}}? Let's Build Your Roadmap"

EMAIL_5C_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Ready to Scale - Christmas Special</title></head><body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;"><p>Hi {{first_name}},</p><p><strong>Your BusOS assessment showed something impressive:</strong></p><p>Most of your systems are GREEN or YELLOW.</p><p>That means you've built a solid foundation.</p><p style="margin-top: 30px; font-size: 18px; font-weight: bold; color: #2196f3;">Now it's time to scale.</p><p style="margin-top: 30px;"><strong>Here's what I see salon owners at your level do wrong:</strong></p><p>They keep doing MORE of what got them here:</p><ul style="line-height: 2; margin: 20px 0;"><li>→ Work more hours</li><li>→ Hire more staff</li><li>→ Spend more on ads</li></ul><p><strong style="color: #f44336;">But that's not scaling. That's just growing linearly.</strong></p><p style="margin-top: 30px; background-color: #e3f2fd; padding: 20px; border-radius: 5px;"><strong>Scaling means:</strong><br><br>→ Revenue grows 2× while you work LESS<br>→ Systems run without you<br>→ Profit margins increase, not decrease</p><p style="margin-top: 30px;"><strong>The BusOS diagnostic helps you identify your 3 highest-leverage opportunities.</strong></p><p>For salons at your level, it's usually:</p><ol style="line-height: 2; margin: 20px 0;"><li><strong>Client retention system</strong> (turns $50K/month → $70K)</li><li><strong>Referral system</strong> (30% of new clients from referrals)</li><li><strong>Team training system</strong> (staff can run salon without you)</li></ol><p style="margin-top: 30px; background-color: #f5f5f5; padding: 20px; border-radius: 5px; text-align: center;"><strong>Fix those 3 systems → You break $100K/month in 6 months.</strong></p><p style="margin-top: 30px;"><strong>Want to build your roadmap?</strong></p><p style="text-align: center; margin: 30px 0;"><a href="https://calendly.com/businessx/diagnostic-call" style="display: inline-block; background-color: #2196f3; color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 18px;">Book Your Diagnostic →</a></p><p style="text-align: center; font-size: 16px; color: #2196f3;"><strong>10 spots left before Christmas</strong></p><p style="margin-top: 30px;">This isn't for everyone. If you're happy at $50K/month, that's great.</p><p><strong>But if you're ready to scale to $100K+, I can help.</strong></p><p>Talk soon,<br>[Your Name]<br>BusinessX</p><p style="font-size: 14px; color: #666; margin-top: 30px;"><strong>P.S.</strong> Not sure if you're ready? Reply with "Not yet" and tell me what's holding you back. I'll give you my honest opinion.</p></body></html>"""

# ============================================================================
# TEMPLATE LOOKUP DICTIONARY
# ============================================================================

TEMPLATES = {
    "email_1": {
        "subject": EMAIL_1_SUBJECT,
        "html": EMAIL_1_HTML
    },
    "email_2a_critical": {
        "subject": EMAIL_2A_SUBJECT,
        "html": EMAIL_2A_HTML
    },
    "email_2b_urgent": {
        "subject": EMAIL_2B_SUBJECT,
        "html": EMAIL_2B_HTML
    },
    "email_2c_optimize": {
        "subject": EMAIL_2C_SUBJECT,
        "html": EMAIL_2C_HTML
    },
    "email_3": {
        "subject": EMAIL_3_SUBJECT,
        "html": EMAIL_3_HTML
    },
    "email_4": {
        "subject": EMAIL_4_SUBJECT,
        "html": EMAIL_4_HTML
    },
    "email_5a_critical": {
        "subject": EMAIL_5A_SUBJECT,
        "html": EMAIL_5A_HTML
    },
    "email_5b_urgent": {
        "subject": EMAIL_5B_SUBJECT,
        "html": EMAIL_5B_HTML
    },
    "email_5c_optimize": {
        "subject": EMAIL_5C_SUBJECT,
        "html": EMAIL_5C_HTML
    }
}


def get_template(template_name: str) -> dict:
    """
    Get email template by name.

    Args:
        template_name: Template identifier (e.g., "email_1", "email_2a_critical")

    Returns:
        Dictionary with "subject" and "html" keys

    Raises:
        KeyError: If template_name is not found

    Example:
        template = get_template("email_1")
        subject = template["subject"]
        html = template["html"]
    """
    if template_name not in TEMPLATES:
        raise KeyError(f"Template '{template_name}' not found. Available: {list(TEMPLATES.keys())}")
    return TEMPLATES[template_name]
