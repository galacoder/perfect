"""
Tests for Kestra health check flow.

This test validates the health-check.yml flow:
- Valid YAML syntax
- Proper flow structure (id, namespace, tasks)
- Health check task logs success message
- (Optional) Secret access verification

Author: Kestra Migration Team
Created: 2025-11-29
"""

import pytest
import yaml
from pathlib import Path


@pytest.fixture
def health_flow_path():
    """Return path to health-check.yml file."""
    project_root = Path(__file__).parent.parent.parent
    return project_root / "kestra" / "flows" / "christmas" / "health-check.yml"


@pytest.fixture
def health_flow_config(health_flow_path):
    """Load and parse health-check.yml."""
    if not health_flow_path.exists():
        pytest.fail(f"health-check.yml not found at {health_flow_path}")

    with open(health_flow_path) as f:
        return yaml.safe_load(f)


def test_health_flow_valid_yaml(health_flow_path):
    """Test that health-check.yml is valid YAML."""
    with open(health_flow_path) as f:
        try:
            yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML syntax: {e}")


def test_health_flow_has_id(health_flow_config):
    """Test that flow has an id field."""
    assert "id" in health_flow_config
    assert isinstance(health_flow_config["id"], str)
    assert len(health_flow_config["id"]) > 0


def test_health_flow_has_namespace(health_flow_config):
    """Test that flow has a namespace field."""
    assert "namespace" in health_flow_config
    assert isinstance(health_flow_config["namespace"], str)


def test_health_flow_namespace_is_christmas(health_flow_config):
    """Test that namespace is 'christmas' or similar."""
    namespace = health_flow_config["namespace"]
    assert "christmas" in namespace.lower(), \
        f"Expected namespace to contain 'christmas', got '{namespace}'"


def test_health_flow_has_tasks(health_flow_config):
    """Test that flow has tasks defined."""
    assert "tasks" in health_flow_config
    assert isinstance(health_flow_config["tasks"], list)
    assert len(health_flow_config["tasks"]) > 0


def test_health_flow_has_log_task(health_flow_config):
    """Test that flow has a log task."""
    tasks = health_flow_config["tasks"]

    # Check if any task is a Log task
    has_log_task = False
    for task in tasks:
        if "type" in task:
            task_type = task["type"]
            if "Log" in task_type or "log" in task_type.lower():
                has_log_task = True
                break

    assert has_log_task, "Flow should have at least one Log task"


def test_health_flow_log_message(health_flow_config):
    """Test that log task has a success message."""
    tasks = health_flow_config["tasks"]

    # Find log task and check message
    log_message_found = False
    for task in tasks:
        if "type" in task and ("Log" in task["type"] or "log" in task["type"].lower()):
            # Check for message field
            if "message" in task:
                message = task["message"].lower()
                # Should indicate Kestra is running/healthy
                if any(keyword in message for keyword in ["running", "healthy", "success", "ready"]):
                    log_message_found = True
                    break

    assert log_message_found, "Log task should have a message indicating Kestra is running"


def test_health_flow_has_description(health_flow_config):
    """Test that flow has a description field."""
    assert "description" in health_flow_config, \
        "Flow should have a description explaining its purpose"


def test_health_flow_id_format(health_flow_config):
    """Test that flow ID follows kebab-case naming convention."""
    flow_id = health_flow_config["id"]

    # Check for lowercase and hyphens
    assert flow_id.islower() or "-" in flow_id, \
        f"Flow ID should use kebab-case: {flow_id}"


def test_health_flow_has_task_ids(health_flow_config):
    """Test that all tasks have id fields."""
    tasks = health_flow_config["tasks"]

    for i, task in enumerate(tasks):
        assert "id" in task, f"Task {i} missing 'id' field"
        assert isinstance(task["id"], str), f"Task {i} 'id' must be a string"
        assert len(task["id"]) > 0, f"Task {i} 'id' cannot be empty"


def test_health_flow_has_task_types(health_flow_config):
    """Test that all tasks have type fields."""
    tasks = health_flow_config["tasks"]

    for i, task in enumerate(tasks):
        assert "type" in task, f"Task {i} missing 'type' field"
        assert isinstance(task["type"], str), f"Task {i} 'type' must be a string"
        # Type should look like a Java class path
        assert "." in task["type"], f"Task {i} 'type' should be fully qualified: {task['type']}"
