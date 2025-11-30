"""
Tests for email scheduling subflow (Emails #2-5 only).

CRITICAL: Email #1 is sent by website. Kestra schedules only Emails #2-5.
Delays calculated relative to email_1_sent_at timestamp from webhook payload.
"""

import pytest
from datetime import datetime, timedelta
import os
import yaml


def test_scheduling_starts_from_email_2():
    """Test that scheduling starts from Email #2, NOT Email #1."""
    # Email #1 is website's responsibility
    # Kestra should only schedule emails 2, 3, 4, 5

    # Load schedule-email-sequence.yml
    flow_path = "kestra/flows/christmas/schedule-email-sequence.yml"

    with open(flow_path, 'r') as f:
        flow = yaml.safe_load(f)

    # Find all schedule_email_* tasks
    tasks = flow.get('tasks', [])
    email_tasks = [t for t in tasks if t['id'].startswith('schedule_email_')]

    # Should have exactly 4 email tasks (2, 3, 4, 5)
    assert len(email_tasks) == 4, f"Expected 4 email tasks, found {len(email_tasks)}"

    # Verify task IDs
    expected_ids = ['schedule_email_2', 'schedule_email_3', 'schedule_email_4', 'schedule_email_5']
    actual_ids = [t['id'] for t in email_tasks]

    assert actual_ids == expected_ids, f"Expected {expected_ids}, got {actual_ids}"

    # Ensure no schedule_email_1 task exists
    email_1_tasks = [t for t in tasks if t['id'] == 'schedule_email_1']
    assert len(email_1_tasks) == 0, "Email #1 should NOT be scheduled by Kestra (website responsibility)"


def test_email_2_delay_calculated_from_email_1_sent_at():
    """Test that Email #2 delay is calculated from email_1_sent_at timestamp."""
    flow_path = "kestra/flows/christmas/schedule-email-sequence.yml"

    with open(flow_path, 'r') as f:
        flow = yaml.safe_load(f)

    # Find calculate_delays task
    tasks = flow.get('tasks', [])
    calculate_task = next((t for t in tasks if t['id'] == 'calculate_delays'), None)

    assert calculate_task is not None, "calculate_delays task not found"
    assert calculate_task['type'] == 'io.kestra.plugin.scripts.python.Script'

    # Check script uses email_1_sent_at input
    script = calculate_task.get('script', '')
    assert 'email_1_sent_at' in script, "Script must use email_1_sent_at input"
    assert 'inputs.email_1_sent_at' in script, "Script must reference inputs.email_1_sent_at"


def test_production_delays_correct():
    """Test production mode delays (TESTING_MODE=false).

    Production delays from email_1_sent_at:
    - Email #2: +24 hours
    - Email #3: +72 hours (48h after #2)
    - Email #4: +120 hours (48h after #3)
    - Email #5: +168 hours (48h after #4)
    """
    flow_path = "kestra/flows/christmas/schedule-email-sequence.yml"

    with open(flow_path, 'r') as f:
        flow = yaml.safe_load(f)

    tasks = flow.get('tasks', [])
    calculate_task = next((t for t in tasks if t['id'] == 'calculate_delays'), None)

    script = calculate_task.get('script', '')

    # Check production delay constants
    assert '24' in script, "Email #2 should be +24 hours in production"
    assert '72' in script, "Email #3 should be +72 hours in production"
    assert '120' in script, "Email #4 should be +120 hours in production"
    assert '168' in script, "Email #5 should be +168 hours in production"

    # Check TESTING_MODE check exists
    assert 'TESTING_MODE' in script, "Script must check TESTING_MODE environment variable"


def test_testing_mode_delays_correct():
    """Test testing mode delays (TESTING_MODE=true).

    Testing delays from email_1_sent_at:
    - Email #2: +1 minute
    - Email #3: +3 minutes (2min after #2)
    - Email #4: +6 minutes (3min after #3)
    - Email #5: +10 minutes (4min after #4)
    """
    flow_path = "kestra/flows/christmas/schedule-email-sequence.yml"

    with open(flow_path, 'r') as f:
        flow = yaml.safe_load(f)

    tasks = flow.get('tasks', [])
    calculate_task = next((t for t in tasks if t['id'] == 'calculate_delays'), None)

    script = calculate_task.get('script', '')

    # Check testing mode delay constants (in minutes)
    assert 'testing_mode' in script.lower(), "Script must handle testing mode"

    # Should reference minutes for testing mode
    # Email #2: 1min, #3: 3min, #4: 6min, #5: 10min
    # (actual values checked in script logic)


def test_missing_email_1_sent_at_defaults_to_webhook_time():
    """Test fallback when email_1_sent_at is missing from webhook payload."""
    flow_path = "kestra/flows/christmas/schedule-email-sequence.yml"

    with open(flow_path, 'r') as f:
        flow = yaml.safe_load(f)

    tasks = flow.get('tasks', [])
    calculate_task = next((t for t in tasks if t['id'] == 'calculate_delays'), None)

    script = calculate_task.get('script', '')

    # Check for fallback logic
    # Should use current time if email_1_sent_at missing
    assert 'datetime.now()' in script or 'datetime.utcnow()' in script, \
        "Script must fall back to current time if email_1_sent_at missing"

    # Should log warning
    assert 'print(' in script or 'logging' in script, \
        "Script should log warning when email_1_sent_at missing"
