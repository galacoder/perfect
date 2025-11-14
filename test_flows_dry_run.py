"""
Dry-run test script for Prefect flows.

Tests flow structure and imports without executing external API calls.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🧪 Testing Prefect flows (dry-run)...\n")

# Test 1: Import all flows
print("1️⃣ Testing flow imports...")
try:
    from campaigns.businessx_canada_lead_nurture.flows.signup_handler import signup_handler_flow
    from campaigns.businessx_canada_lead_nurture.flows.assessment_handler import assessment_handler_flow
    from campaigns.businessx_canada_lead_nurture.flows.email_sequence import email_sequence_flow
    print("   ✅ All flows imported successfully")
except Exception as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

# Test 2: Verify flow structure
print("\n2️⃣ Verifying flow structure...")
try:
    # Check signup handler
    assert signup_handler_flow.name == "signup-handler"
    print(f"   ✅ signup_handler_flow: {signup_handler_flow.name}")

    # Check assessment handler
    assert assessment_handler_flow.name == "assessment-handler"
    print(f"   ✅ assessment_handler_flow: {assessment_handler_flow.name}")

    # Check email sequence
    assert email_sequence_flow.name == "email-sequence-5-emails"
    print(f"   ✅ email_sequence_flow: {email_sequence_flow.name}")

except AssertionError as e:
    print(f"   ❌ Flow structure error: {e}")
    sys.exit(1)

# Test 3: Import all tasks
print("\n3️⃣ Testing task imports...")
try:
    from campaigns.businessx_canada_lead_nurture.tasks.notion_operations import (
        search_contact_by_email,
        create_contact,
        update_contact,
        get_contact
    )
    from campaigns.businessx_canada_lead_nurture.tasks.resend_operations import (
        send_email,
        substitute_variables,
        send_template_email
    )
    from campaigns.businessx_canada_lead_nurture.tasks.routing import (
        determine_segment,
        select_email_template,
        get_wait_duration
    )
    from campaigns.businessx_canada_lead_nurture.tasks.template_operations import (
        fetch_template_from_notion,
        fetch_template_cached,
        list_all_templates,
        seed_templates_to_notion,
        get_template
    )
    print("   ✅ All tasks imported successfully")
except Exception as e:
    print(f"   ❌ Task import error: {e}")
    sys.exit(1)

# Test 4: Verify routing logic
print("\n4️⃣ Testing routing logic...")
try:
    # Test segment classification
    from campaigns.businessx_canada_lead_nurture.tasks.routing import determine_segment

    segment_critical = determine_segment(red_systems=2, orange_systems=1)
    assert segment_critical == "CRITICAL"
    print(f"   ✅ CRITICAL segment: {segment_critical}")

    segment_urgent = determine_segment(red_systems=1, orange_systems=0)
    assert segment_urgent == "URGENT"
    print(f"   ✅ URGENT segment: {segment_urgent}")

    segment_optimize = determine_segment(red_systems=0, orange_systems=0)
    assert segment_optimize == "OPTIMIZE"
    print(f"   ✅ OPTIMIZE segment: {segment_optimize}")

except Exception as e:
    print(f"   ❌ Routing logic error: {e}")
    sys.exit(1)

# Test 5: Verify email template selection
print("\n5️⃣ Testing email template selection...")
try:
    from campaigns.businessx_canada_lead_nurture.tasks.routing import select_email_template

    # Email #1 (universal)
    email_1 = select_email_template(email_number=1, segment="CRITICAL")
    assert email_1 == "email_1"
    print(f"   ✅ Email #1 (universal): {email_1}")

    # Email #2 (segment-specific)
    email_2a = select_email_template(email_number=2, segment="CRITICAL")
    assert email_2a == "email_2a_critical"
    print(f"   ✅ Email #2 (CRITICAL): {email_2a}")

    email_2b = select_email_template(email_number=2, segment="URGENT")
    assert email_2b == "email_2b_urgent"
    print(f"   ✅ Email #2 (URGENT): {email_2b}")

    email_2c = select_email_template(email_number=2, segment="OPTIMIZE")
    assert email_2c == "email_2c_optimize"
    print(f"   ✅ Email #2 (OPTIMIZE): {email_2c}")

except Exception as e:
    print(f"   ❌ Template selection error: {e}")
    sys.exit(1)

# Test 6: Verify wait duration logic
print("\n6️⃣ Testing wait duration logic...")
try:
    from campaigns.businessx_canada_lead_nurture.tasks.routing import get_wait_duration

    # Production mode
    wait_prod_1 = get_wait_duration(email_number=1, testing_mode=False)
    assert wait_prod_1 == 86400  # 24 hours
    print(f"   ✅ Production wait #1: {wait_prod_1}s (24h)")

    # Testing mode
    wait_test_1 = get_wait_duration(email_number=1, testing_mode=True)
    assert wait_test_1 == 60  # 1 minute
    print(f"   ✅ Testing wait #1: {wait_test_1}s (1min)")

except Exception as e:
    print(f"   ❌ Wait duration error: {e}")
    sys.exit(1)

# Test 7: Verify variable substitution
print("\n7️⃣ Testing variable substitution...")
try:
    from campaigns.businessx_canada_lead_nurture.tasks.resend_operations import substitute_variables

    template = "Hello {{first_name}}, welcome to {{business_name}}!"
    variables = {"first_name": "John", "business_name": "Acme Corp"}
    result = substitute_variables(template, variables)

    expected = "Hello John, welcome to Acme Corp!"
    assert result == expected
    print(f"   ✅ Variable substitution: {result}")

except Exception as e:
    print(f"   ❌ Variable substitution error: {e}")
    sys.exit(1)

# All tests passed
print("\n" + "="*60)
print("🎉 All dry-run tests passed!")
print("="*60)
print("\n✅ Flow structure is valid")
print("✅ All imports working")
print("✅ Routing logic correct")
print("✅ Template selection working")
print("✅ Wait duration logic correct")
print("✅ Variable substitution working")

print("\n📝 Next steps:")
print("1. Seed templates to Notion: python scripts/seed_templates.py")
print("2. Run integration test: python flows/signup_handler.py")
print("3. Deploy flows: python flows/deploy.py")
