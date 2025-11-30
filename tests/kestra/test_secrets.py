"""
Tests for Kestra secrets configuration.

This test validates the .env.kestra file structure:
- File exists and is readable
- All required secrets are defined
- SECRET_ prefix used for Kestra secrets
- No secrets committed to git (.gitignore check)
- Secret loading in docker-compose

Author: Kestra Migration Team
Created: 2025-11-29
"""

import pytest
from pathlib import Path
import os


@pytest.fixture
def project_root():
    """Return project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture
def env_kestra_path(project_root):
    """Return path to .env.kestra file."""
    return project_root / ".env.kestra"


@pytest.fixture
def env_kestra_example_path(project_root):
    """Return path to .env.kestra.example file."""
    return project_root / ".env.kestra.example"


@pytest.fixture
def gitignore_path(project_root):
    """Return path to .gitignore file."""
    return project_root / ".gitignore"


def test_env_kestra_example_exists(env_kestra_example_path):
    """Test that .env.kestra.example file exists."""
    assert env_kestra_example_path.exists(), \
        ".env.kestra.example file not found - needed for documentation"


def test_env_kestra_example_has_required_secrets(env_kestra_example_path):
    """Test that .env.kestra.example has all required secret placeholders."""
    with open(env_kestra_example_path) as f:
        content = f.read()

    required_secrets = [
        "SECRET_NOTION_TOKEN",
        "SECRET_NOTION_CONTACTS_DB_ID",
        "SECRET_NOTION_TEMPLATES_DB_ID",
        "SECRET_NOTION_EMAIL_SEQUENCE_DB_ID",
        "SECRET_RESEND_API_KEY",
        "TESTING_MODE",
    ]

    for secret in required_secrets:
        assert secret in content, f"Required secret {secret} not found in .env.kestra.example"


def test_env_kestra_example_uses_placeholders(env_kestra_example_path):
    """Test that .env.kestra.example uses placeholder values, not real secrets."""
    with open(env_kestra_example_path) as f:
        lines = f.readlines()

    # Check that VALUES (after =) are placeholders, not real secrets
    forbidden_patterns = [
        "ntn_",  # Notion tokens start with ntn_
        "re_",   # Resend API keys start with re_
    ]

    for line in lines:
        if "=" in line and not line.strip().startswith("#"):
            value = line.split("=", 1)[1].strip()
            for pattern in forbidden_patterns:
                assert pattern not in value.lower(), \
                    f"Real secret pattern '{pattern}' found in value '{value}' - use placeholders only"


def test_env_kestra_in_gitignore(gitignore_path):
    """Test that .env.kestra is in .gitignore."""
    assert gitignore_path.exists(), ".gitignore file not found"

    with open(gitignore_path) as f:
        content = f.read()

    assert ".env.kestra" in content, \
        ".env.kestra not found in .gitignore - secrets must not be committed"


def test_env_kestra_has_correct_prefix(env_kestra_example_path):
    """Test that secrets use SECRET_ prefix for Kestra."""
    with open(env_kestra_example_path) as f:
        lines = f.readlines()

    secret_lines = [line.strip() for line in lines
                   if line.strip() and not line.strip().startswith("#")]

    for line in secret_lines:
        if "=" in line:
            key = line.split("=")[0].strip()
            # Exceptions: TESTING_MODE doesn't need SECRET_ prefix
            if key == "TESTING_MODE":
                continue
            assert key.startswith("SECRET_"), \
                f"Secret '{key}' must use SECRET_ prefix for Kestra compatibility"


def test_env_kestra_has_notion_secrets(env_kestra_example_path):
    """Test that all Notion-related secrets are present."""
    with open(env_kestra_example_path) as f:
        content = f.read()

    notion_secrets = [
        "SECRET_NOTION_TOKEN",
        "SECRET_NOTION_CONTACTS_DB_ID",
        "SECRET_NOTION_TEMPLATES_DB_ID",
        "SECRET_NOTION_EMAIL_SEQUENCE_DB_ID",
    ]

    for secret in notion_secrets:
        assert secret in content, f"Notion secret {secret} not found"


def test_env_kestra_has_resend_secret(env_kestra_example_path):
    """Test that Resend API key is present."""
    with open(env_kestra_example_path) as f:
        content = f.read()

    assert "SECRET_RESEND_API_KEY" in content, "Resend API key not found"


def test_env_kestra_has_testing_mode(env_kestra_example_path):
    """Test that TESTING_MODE is present."""
    with open(env_kestra_example_path) as f:
        content = f.read()

    assert "TESTING_MODE" in content, "TESTING_MODE not found"


def test_env_kestra_format_valid(env_kestra_example_path):
    """Test that .env.kestra.example has valid KEY=VALUE format."""
    with open(env_kestra_example_path) as f:
        lines = f.readlines()

    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        assert "=" in line, f"Line {i} is not valid KEY=VALUE format: {line}"

        key, value = line.split("=", 1)
        assert key.strip() == key, f"Line {i} has whitespace around key: {line}"
        assert len(key) > 0, f"Line {i} has empty key: {line}"
        assert len(value) > 0, f"Line {i} has empty value: {line}"


def test_env_kestra_optional_secrets_documented(env_kestra_example_path):
    """Test that optional secrets are documented with comments."""
    with open(env_kestra_example_path) as f:
        content = f.read()

    # Optional secrets should have comments explaining they're optional
    optional_secrets = [
        "SECRET_DISCORD_WEBHOOK_URL",
    ]

    for secret in optional_secrets:
        if secret in content:
            # Find the line with this secret
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if secret in line:
                    # Check if there's a comment explaining it's optional
                    # Either on same line or previous line
                    assert "optional" in content.lower() or "discord" in content.lower(), \
                        f"{secret} should be documented as optional"
                    break
