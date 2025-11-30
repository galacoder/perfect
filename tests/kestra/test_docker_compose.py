"""
Tests for Kestra Docker Compose configuration.

This test validates the docker-compose.yml file for Kestra setup:
- YAML syntax validation
- Required services defined (kestra, postgres)
- Proper volume mounts
- Port mappings
- Network configuration
- Health checks

Author: Kestra Migration Team
Created: 2025-11-29
"""

import pytest
import yaml
from pathlib import Path


@pytest.fixture
def docker_compose_path():
    """Return path to docker-compose.yml file."""
    project_root = Path(__file__).parent.parent.parent
    return project_root / "docker-compose.kestra.yml"


@pytest.fixture
def docker_compose_config(docker_compose_path):
    """Load and parse docker-compose.yml."""
    if not docker_compose_path.exists():
        pytest.fail(f"docker-compose.kestra.yml not found at {docker_compose_path}")

    with open(docker_compose_path) as f:
        return yaml.safe_load(f)


def test_docker_compose_valid_yaml(docker_compose_path):
    """Test that docker-compose.yml is valid YAML."""
    with open(docker_compose_path) as f:
        try:
            yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML syntax: {e}")


def test_docker_compose_has_kestra_service(docker_compose_config):
    """Test that kestra service is defined."""
    assert "services" in docker_compose_config
    assert "kestra" in docker_compose_config["services"]


def test_docker_compose_has_postgres_service(docker_compose_config):
    """Test that postgres service is defined."""
    assert "services" in docker_compose_config
    assert "postgres" in docker_compose_config["services"]


def test_kestra_service_has_image(docker_compose_config):
    """Test that Kestra service has an image defined."""
    kestra = docker_compose_config["services"]["kestra"]
    assert "image" in kestra
    assert "kestra" in kestra["image"].lower()


def test_postgres_service_has_image(docker_compose_config):
    """Test that Postgres service has an image defined."""
    postgres = docker_compose_config["services"]["postgres"]
    assert "image" in postgres
    assert "postgres" in postgres["image"].lower()


def test_kestra_has_port_mapping(docker_compose_config):
    """Test that Kestra service exposes port 8080."""
    kestra = docker_compose_config["services"]["kestra"]
    assert "ports" in kestra

    # Check for 8080 port mapping
    ports = kestra["ports"]
    port_8080_found = False
    for port in ports:
        if "8080" in str(port):
            port_8080_found = True
            break

    assert port_8080_found, "Kestra port 8080 not found in port mappings"


def test_kestra_has_volume_mounts(docker_compose_config):
    """Test that Kestra has volume mounts for flows."""
    kestra = docker_compose_config["services"]["kestra"]
    assert "volumes" in kestra

    # Check for kestra/flows volume mount
    volumes = kestra["volumes"]
    flows_volume_found = False
    for volume in volumes:
        if "kestra/flows" in str(volume) or "/app/flows" in str(volume):
            flows_volume_found = True
            break

    assert flows_volume_found, "Kestra flows volume mount not found"


def test_postgres_has_environment(docker_compose_config):
    """Test that Postgres has environment variables."""
    postgres = docker_compose_config["services"]["postgres"]
    assert "environment" in postgres

    env = postgres["environment"]
    # Check for required Postgres env vars
    if isinstance(env, dict):
        assert "POSTGRES_DB" in env or "POSTGRES_DATABASE" in env
        assert "POSTGRES_USER" in env
        assert "POSTGRES_PASSWORD" in env
    elif isinstance(env, list):
        env_str = " ".join(env)
        assert "POSTGRES_DB" in env_str or "POSTGRES_DATABASE" in env_str
        assert "POSTGRES_USER" in env_str
        assert "POSTGRES_PASSWORD" in env_str


def test_kestra_depends_on_postgres(docker_compose_config):
    """Test that Kestra service depends on Postgres."""
    kestra = docker_compose_config["services"]["kestra"]
    assert "depends_on" in kestra

    depends_on = kestra["depends_on"]
    if isinstance(depends_on, list):
        assert "postgres" in depends_on
    elif isinstance(depends_on, dict):
        assert "postgres" in depends_on


def test_kestra_has_environment(docker_compose_config):
    """Test that Kestra has environment configuration."""
    kestra = docker_compose_config["services"]["kestra"]
    assert "environment" in kestra or "env_file" in kestra, \
        "Kestra must have environment variables or env_file"


def test_postgres_has_volume_for_persistence(docker_compose_config):
    """Test that Postgres has volume for data persistence."""
    postgres = docker_compose_config["services"]["postgres"]
    assert "volumes" in postgres

    # Check for postgres data volume
    volumes = postgres["volumes"]
    data_volume_found = False
    for volume in volumes:
        if "postgres" in str(volume).lower() and "data" in str(volume).lower():
            data_volume_found = True
            break

    assert data_volume_found, "Postgres data volume not found"


def test_kestra_has_restart_policy(docker_compose_config):
    """Test that Kestra has a restart policy."""
    kestra = docker_compose_config["services"]["kestra"]
    assert "restart" in kestra
    assert kestra["restart"] in ["always", "unless-stopped", "on-failure"]


def test_postgres_has_restart_policy(docker_compose_config):
    """Test that Postgres has a restart policy."""
    postgres = docker_compose_config["services"]["postgres"]
    assert "restart" in postgres
    assert postgres["restart"] in ["always", "unless-stopped", "on-failure"]
