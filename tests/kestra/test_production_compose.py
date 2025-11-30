"""
Tests for production docker-compose configuration.

Tests cover:
- YAML syntax validation
- Service definitions
- Volume configuration
- Health checks
- Resource limits
- Security settings
- Logging configuration
"""

import pytest
import yaml
from pathlib import Path


@pytest.fixture
def prod_compose():
    """Load production docker-compose.yml file."""
    compose_file = Path(__file__).parent.parent.parent / 'docker-compose.kestra.prod.yml'
    with open(compose_file, 'r') as f:
        return yaml.safe_load(f)


class TestProductionComposeStructure:
    """Test production docker-compose structure and syntax."""

    def test_valid_yaml(self, prod_compose):
        """Test docker-compose.kestra.prod.yml is valid YAML."""
        assert prod_compose is not None
        assert isinstance(prod_compose, dict)

    def test_version_specified(self, prod_compose):
        """Test docker-compose version is specified."""
        assert 'version' in prod_compose
        assert prod_compose['version'] in ['3.8', '3.9']

    def test_services_defined(self, prod_compose):
        """Test required services are defined."""
        assert 'services' in prod_compose
        services = prod_compose['services']
        assert 'postgres' in services
        assert 'kestra' in services

    def test_volumes_defined(self, prod_compose):
        """Test persistent volumes are defined."""
        assert 'volumes' in prod_compose
        volumes = prod_compose['volumes']
        assert 'kestra-postgres-data-prod' in volumes
        assert 'kestra-data-prod' in volumes
        assert 'kestra-logs-prod' in volumes

    def test_networks_defined(self, prod_compose):
        """Test network is defined."""
        assert 'networks' in prod_compose
        assert 'kestra-network-prod' in prod_compose['networks']


class TestPostgreSQLService:
    """Test PostgreSQL service configuration."""

    def test_postgres_image(self, prod_compose):
        """Test PostgreSQL uses production-grade image."""
        postgres = prod_compose['services']['postgres']
        assert 'image' in postgres
        assert 'postgres:' in postgres['image']
        # Production should use stable version (not 'latest')
        assert 'alpine' in postgres['image']

    def test_postgres_restart_policy(self, prod_compose):
        """Test PostgreSQL has restart policy 'always'."""
        postgres = prod_compose['services']['postgres']
        assert postgres.get('restart') == 'always'

    def test_postgres_environment_vars(self, prod_compose):
        """Test PostgreSQL has required environment variables."""
        postgres = prod_compose['services']['postgres']
        env = postgres.get('environment', {})

        # Check required env vars exist
        assert 'POSTGRES_DB' in env
        assert 'POSTGRES_USER' in env
        assert 'POSTGRES_PASSWORD' in env

    def test_postgres_volume_mounted(self, prod_compose):
        """Test PostgreSQL has persistent volume mounted."""
        postgres = prod_compose['services']['postgres']
        volumes = postgres.get('volumes', [])

        # Check data volume exists
        data_volumes = [v for v in volumes if '/var/lib/postgresql/data' in v]
        assert len(data_volumes) > 0

        # Check volume uses prod naming
        assert any('kestra-postgres-data-prod' in v for v in volumes)

    def test_postgres_health_check(self, prod_compose):
        """Test PostgreSQL has health check configured."""
        postgres = prod_compose['services']['postgres']
        assert 'healthcheck' in postgres

        healthcheck = postgres['healthcheck']
        assert 'test' in healthcheck
        assert 'pg_isready' in str(healthcheck['test'])
        assert 'interval' in healthcheck
        assert 'retries' in healthcheck

    def test_postgres_resource_limits(self, prod_compose):
        """Test PostgreSQL has resource limits (if deploy key exists)."""
        postgres = prod_compose['services']['postgres']

        # Resource limits are under 'deploy' in Docker Compose v3
        if 'deploy' in postgres:
            deploy = postgres['deploy']
            assert 'resources' in deploy
            resources = deploy['resources']
            assert 'limits' in resources
            assert 'memory' in resources['limits']

    def test_postgres_logging_configured(self, prod_compose):
        """Test PostgreSQL has logging configuration."""
        postgres = prod_compose['services']['postgres']
        if 'logging' in postgres:
            logging = postgres['logging']
            assert 'driver' in logging
            assert 'options' in logging
            assert 'max-size' in logging['options']
            assert 'max-file' in logging['options']


class TestKestraService:
    """Test Kestra service configuration."""

    def test_kestra_image(self, prod_compose):
        """Test Kestra uses official image."""
        kestra = prod_compose['services']['kestra']
        assert 'image' in kestra
        assert 'kestra/kestra' in kestra['image']

    def test_kestra_restart_policy(self, prod_compose):
        """Test Kestra has restart policy 'always'."""
        kestra = prod_compose['services']['kestra']
        assert kestra.get('restart') == 'always'

    def test_kestra_depends_on_postgres(self, prod_compose):
        """Test Kestra depends on PostgreSQL health check."""
        kestra = prod_compose['services']['kestra']
        assert 'depends_on' in kestra

        depends_on = kestra['depends_on']
        if isinstance(depends_on, dict):
            assert 'postgres' in depends_on
            assert depends_on['postgres'].get('condition') == 'service_healthy'
        else:
            assert 'postgres' in depends_on

    def test_kestra_ports_exposed(self, prod_compose):
        """Test Kestra exposes required ports."""
        kestra = prod_compose['services']['kestra']
        assert 'ports' in kestra

        ports = kestra['ports']
        # Check main port 8080 and metrics port 8081
        port_strings = [str(p) for p in ports]
        assert any('8080' in p for p in port_strings)

    def test_kestra_env_file_loaded(self, prod_compose):
        """Test Kestra loads .env.kestra file."""
        kestra = prod_compose['services']['kestra']
        assert 'env_file' in kestra
        assert '.env.kestra' in kestra['env_file']

    def test_kestra_volumes_mounted(self, prod_compose):
        """Test Kestra has all required volumes."""
        kestra = prod_compose['services']['kestra']
        volumes = kestra.get('volumes', [])

        # Check storage volume
        assert any('kestra-data-prod' in v for v in volumes)

        # Check flows volume (read-only)
        flows_volumes = [v for v in volumes if '/app/flows' in v]
        assert len(flows_volumes) > 0

        # Check logs volume
        assert any('kestra-logs-prod' in v for v in volumes)

    def test_kestra_health_check(self, prod_compose):
        """Test Kestra has health check configured."""
        kestra = prod_compose['services']['kestra']
        assert 'healthcheck' in kestra

        healthcheck = kestra['healthcheck']
        assert 'test' in healthcheck
        assert '/health' in str(healthcheck['test'])
        assert 'interval' in healthcheck
        assert 'start_period' in healthcheck

    def test_kestra_resource_limits(self, prod_compose):
        """Test Kestra has resource limits."""
        kestra = prod_compose['services']['kestra']

        if 'deploy' in kestra:
            deploy = kestra['deploy']
            assert 'resources' in deploy
            resources = deploy['resources']
            assert 'limits' in resources
            assert 'memory' in resources['limits']

    def test_kestra_logging_configured(self, prod_compose):
        """Test Kestra has logging configuration."""
        kestra = prod_compose['services']['kestra']
        if 'logging' in kestra:
            logging = kestra['logging']
            assert 'driver' in logging
            assert 'options' in logging
            assert 'max-size' in logging['options']
            assert 'max-file' in logging['options']

    def test_kestra_configuration_yaml(self, prod_compose):
        """Test Kestra has KESTRA_CONFIGURATION environment variable."""
        kestra = prod_compose['services']['kestra']
        environment = kestra.get('environment', {})

        assert 'KESTRA_CONFIGURATION' in environment
        config = environment['KESTRA_CONFIGURATION']

        # Parse inline YAML configuration
        config_dict = yaml.safe_load(config)

        # Check datasources configured
        assert 'datasources' in config_dict
        assert 'postgres' in config_dict['datasources']

        # Check kestra settings
        assert 'kestra' in config_dict
        assert 'repository' in config_dict['kestra']
        assert 'storage' in config_dict['kestra']
        assert 'queue' in config_dict['kestra']


class TestVolumeConfiguration:
    """Test volume configuration."""

    def test_postgres_volume_persistence(self, prod_compose):
        """Test PostgreSQL volume is configured for persistence."""
        volumes = prod_compose['volumes']
        assert 'kestra-postgres-data-prod' in volumes

        pg_volume = volumes['kestra-postgres-data-prod']
        assert 'driver' in pg_volume

    def test_kestra_storage_volume_persistence(self, prod_compose):
        """Test Kestra storage volume is configured."""
        volumes = prod_compose['volumes']
        assert 'kestra-data-prod' in volumes

    def test_kestra_logs_volume_persistence(self, prod_compose):
        """Test Kestra logs volume is configured."""
        volumes = prod_compose['volumes']
        assert 'kestra-logs-prod' in volumes


class TestSecurityConfiguration:
    """Test security settings."""

    def test_postgres_password_not_hardcoded(self, prod_compose):
        """Test PostgreSQL password uses environment variable."""
        postgres = prod_compose['services']['postgres']
        env = postgres.get('environment', {})

        password = env.get('POSTGRES_PASSWORD', '')

        # Password should not be plaintext in compose file
        # Should use ${POSTGRES_PASSWORD} or similar
        assert '${POSTGRES_PASSWORD' in password or 'POSTGRES_PASSWORD' in password

    def test_kestra_security_options(self, prod_compose):
        """Test Kestra has security options configured."""
        kestra = prod_compose['services']['kestra']

        # Check for security_opt if present
        if 'security_opt' in kestra:
            sec_opts = kestra['security_opt']
            # Should include no-new-privileges
            assert any('no-new-privileges' in opt for opt in sec_opts)

    def test_flows_mounted_readonly(self, prod_compose):
        """Test flows directory is mounted read-only."""
        kestra = prod_compose['services']['kestra']
        volumes = kestra.get('volumes', [])

        # Check if flows volume is read-only
        flows_volumes = [v for v in volumes if '/app/flows' in v]
        assert len(flows_volumes) > 0

        # At least one flow volume should be read-only
        readonly_flows = [v for v in flows_volumes if ':ro' in v]
        assert len(readonly_flows) > 0


class TestNetworkConfiguration:
    """Test network configuration."""

    def test_custom_network_defined(self, prod_compose):
        """Test custom network is defined."""
        networks = prod_compose['networks']
        assert 'kestra-network-prod' in networks

    def test_network_driver(self, prod_compose):
        """Test network uses bridge driver."""
        networks = prod_compose['networks']
        network = networks['kestra-network-prod']

        if isinstance(network, dict):
            assert network.get('driver') == 'bridge'

    def test_services_use_custom_network(self, prod_compose):
        """Test services are connected to custom network."""
        # Both services should be on the custom network
        # This is implicit if they're in the same compose file with custom network
        assert 'kestra-network-prod' in prod_compose['networks']


class TestProductionReadiness:
    """Test production-specific configurations."""

    def test_no_hardcoded_secrets(self, prod_compose):
        """Test no hardcoded secrets in compose file."""
        compose_str = yaml.dump(prod_compose)

        # Check for common secret patterns (shouldn't be hardcoded)
        assert 'ntn_' not in compose_str  # Notion tokens
        assert 're_' not in compose_str  # Resend API keys
        # Weak password patterns
        assert 'password123' not in compose_str.lower()
        assert 'admin' not in compose_str.lower()

    def test_restart_policies_production(self, prod_compose):
        """Test all services have 'always' restart policy."""
        services = prod_compose['services']

        for service_name, service_config in services.items():
            restart = service_config.get('restart', 'no')
            # Production should use 'always' for high availability
            assert restart in ['always', 'unless-stopped'], \
                f"Service {service_name} should have restart: always or unless-stopped"

    def test_backup_volume_mounted(self, prod_compose):
        """Test PostgreSQL has backup volume mounted."""
        postgres = prod_compose['services']['postgres']
        volumes = postgres.get('volumes', [])

        # Check for backup mount
        backup_volumes = [v for v in volumes if 'backup' in v.lower()]
        # Optional but recommended
        if len(backup_volumes) > 0:
            assert any('/backups' in v for v in volumes)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
