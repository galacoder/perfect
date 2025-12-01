"""
Fetch email templates from Notion Templates database with fallback to static templates.

Supports all sequence types:
- 5day: 5-day nurture sequence (Emails #2-5, Email #1 sent by website)
- noshow: No-show recovery sequence (3 emails)
- postcall: Post-call maybe sequence (3 emails)
- onboarding: Onboarding sequence (3 emails)
"""

import requests
from typing import Dict, Optional


# Static template fallbacks (used if Notion API fails)
STATIC_TEMPLATES = {
    "5day": {
        2: {
            "subject": "{{first_name}}, here's your personalized BusOS roadmap",
            "body": """Hi {{first_name}},

Thank you for completing the BusOS assessment for {{business_name}}!

Based on your results, you're in the {{segment}} segment. I've prepared a personalized roadmap to help you strengthen your business systems.

Here are my recommendations:
[Segment-specific recommendations here]

Let me know if you have any questions!

Best regards,
Sang Le"""
        },
        3: {
            "subject": "{{first_name}}, let's tackle your biggest bottleneck",
            "body": """Hi {{first_name}},

I wanted to follow up on your BusOS assessment for {{business_name}}.

Your biggest opportunity for improvement is [specific system]. Here's how we can address it:

[Action steps]

Ready to take the next step?

Best,
Sang"""
        },
        4: {
            "subject": "{{first_name}}, exclusive offer for {{business_name}}",
            "body": """Hi {{first_name}},

I have an exclusive offer for {{business_name}} to help you optimize your business systems.

[Offer details]

This is only available for the next 48 hours.

Let's chat!
Sang"""
        },
        5: {
            "subject": "Last chance: {{first_name}}, don't miss this opportunity",
            "body": """Hi {{first_name}},

This is my final message about the exclusive offer for {{business_name}}.

If you're still interested in optimizing your business systems, reply to this email within the next 24 hours.

Otherwise, I'll assume you're not ready yet, and that's totally fine!

Best wishes,
Sang Le"""
        }
    },
    "noshow": {
        1: {
            "subject": "{{first_name}}, we missed you today",
            "body": """Hi {{first_name}},

We had a call scheduled today for {{business_name}}, but it looks like you weren't able to make it.

No worries! Things come up.

Would you like to reschedule? Just reply to this email with your availability.

Best,
Sang"""
        },
        2: {
            "subject": "{{first_name}}, still want to optimize {{business_name}}?",
            "body": """Hi {{first_name}},

I haven't heard back from you about rescheduling our call for {{business_name}}.

If you're still interested in improving your business systems, let me know and we can find a time that works.

Best,
Sang"""
        },
        3: {
            "subject": "Final check-in: {{first_name}}",
            "body": """Hi {{first_name}},

This is my last check-in about rescheduling our call for {{business_name}}.

If you're no longer interested, no problem at all! Just let me know so I can close your file.

Otherwise, I'm here whenever you're ready.

Best wishes,
Sang Le"""
        }
    },
    "postcall": {
        1: {
            "subject": "Great chatting with you, {{first_name}}!",
            "body": """Hi {{first_name}},

Thanks for the call today! I enjoyed learning about {{business_name}}.

I'm sending over the proposal we discussed. Take a look and let me know if you have any questions.

Looking forward to working together!

Best,
Sang"""
        },
        2: {
            "subject": "{{first_name}}, any questions about the proposal?",
            "body": """Hi {{first_name}},

I wanted to check in about the proposal I sent for {{business_name}}.

Do you have any questions or concerns? I'm happy to hop on a quick call to discuss.

Best,
Sang"""
        },
        3: {
            "subject": "{{first_name}}, is this still a priority?",
            "body": """Hi {{first_name}},

I haven't heard back about the proposal for {{business_name}}.

If this is no longer a priority, that's completely fine! Just let me know so I can update my records.

Otherwise, I'm here to help whenever you're ready.

Best,
Sang"""
        }
    },
    "onboarding": {
        1: {
            "subject": "Welcome to the program, {{first_name}}!",
            "body": """Hi {{first_name}},

Welcome to the BusOS optimization program!

I'm excited to help you transform {{business_name}}. Here's what to expect in the coming weeks:

[Onboarding steps]

Let's get started!

Best,
Sang"""
        },
        2: {
            "subject": "{{first_name}}, week 1 check-in",
            "body": """Hi {{first_name}},

How's your first week going with the BusOS program?

I wanted to check in and see if you have any questions about {{business_name}}.

Let me know how I can help!

Best,
Sang"""
        },
        3: {
            "subject": "{{first_name}}, your progress so far",
            "body": """Hi {{first_name}},

Great progress on optimizing {{business_name}} so far!

Here's a summary of what we've accomplished:

[Progress summary]

Keep up the great work!

Best,
Sang"""
        }
    }
}


async def fetch_template_from_notion(
    sequence_type: str,
    email_number: int,
    notion_token: str,
    templates_db_id: str
) -> Optional[Dict[str, str]]:
    """
    Fetch email template from Notion Templates database.

    Args:
        sequence_type: Type of sequence (5day, noshow, postcall, onboarding)
        email_number: Email number in sequence (1-5 for 5day, 1-3 for others)
        notion_token: Notion API token
        templates_db_id: Notion Templates database ID

    Returns:
        Dictionary with 'subject' and 'body' keys, or None if not found

    Falls back to static templates if Notion API fails.
    """
    try:
        # Query Notion Templates database
        url = f"https://api.notion.com/v1/databases/{templates_db_id}/query"
        headers = {
            "Authorization": f"Bearer {notion_token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

        # Filter by sequence_type and email_number
        body = {
            "filter": {
                "and": [
                    {
                        "property": "sequence_type",
                        "select": {
                            "equals": sequence_type
                        }
                    },
                    {
                        "property": "email_number",
                        "number": {
                            "equals": email_number
                        }
                    }
                ]
            }
        }

        response = requests.post(url, headers=headers, json=body, timeout=10)

        if response.status_code == 200:
            results = response.json().get("results", [])

            if results:
                # Extract template from first result
                props = results[0]["properties"]

                subject_prop = props.get("subject", {})
                body_prop = props.get("body", {})

                # Extract text content
                subject = ""
                if subject_prop.get("title"):
                    subject = subject_prop["title"][0]["text"]["content"]

                body = ""
                if body_prop.get("rich_text"):
                    body = body_prop["rich_text"][0]["text"]["content"]

                print(f"✅ Fetched template from Notion: {sequence_type} Email #{email_number}")

                return {
                    "subject": subject,
                    "body": body
                }
            else:
                print(f"⚠️  No template found in Notion for {sequence_type} Email #{email_number}")
                # Fall back to static
                return STATIC_TEMPLATES.get(sequence_type, {}).get(email_number)
        else:
            print(f"⚠️  Notion API error: {response.status_code}")
            # Fall back to static
            return STATIC_TEMPLATES.get(sequence_type, {}).get(email_number)

    except Exception as e:
        print(f"⚠️  Failed to fetch template from Notion: {e}")
        print(f"📋 Using static fallback template for {sequence_type} Email #{email_number}")

        # Fall back to static templates
        return STATIC_TEMPLATES.get(sequence_type, {}).get(email_number)


def render_template(template: Dict[str, str], variables: Dict[str, str]) -> Dict[str, str]:
    """
    Render template by substituting variables.

    Args:
        template: Dictionary with 'subject' and 'body' keys containing {{variable}} placeholders
        variables: Dictionary of variable name -> value mappings

    Returns:
        Rendered template with all variables substituted
    """
    rendered = {
        "subject": template["subject"],
        "body": template["body"]
    }

    # Substitute all variables
    for var_name, var_value in variables.items():
        placeholder = f"{{{{{var_name}}}}}"  # {{variable}}
        rendered["subject"] = rendered["subject"].replace(placeholder, var_value)
        rendered["body"] = rendered["body"].replace(placeholder, var_value)

    return rendered


# For standalone testing
if __name__ == "__main__":
    import asyncio

    async def test():
        # Test static templates
        template = STATIC_TEMPLATES["5day"][2]
        print("Template:", template)

        variables = {
            "first_name": "John",
            "business_name": "Acme Corp",
            "segment": "CRITICAL"
        }

        rendered = render_template(template, variables)
        print("\nRendered:")
        print("Subject:", rendered["subject"])
        print("Body:", rendered["body"][:100])

    asyncio.run(test())
