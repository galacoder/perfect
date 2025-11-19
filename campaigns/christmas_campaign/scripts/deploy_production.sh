#!/bin/bash
#
# Production Deployment Script - Christmas Campaign
#
# This script automates the deployment of the Christmas Campaign webhook system
# to a production server (homelab or cloud).
#
# Usage:
#   chmod +x campaigns/christmas_campaign/scripts/deploy_production.sh
#   ./campaigns/christmas_campaign/scripts/deploy_production.sh
#
# Prerequisites:
#   - Ubuntu 22.04+ or Debian 11+
#   - sudo access
#   - Internet connection

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Christmas Campaign - Production Deployment Script"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Configuration
APP_DIR="/opt/christmas-campaign"
VENV_DIR="${APP_DIR}/venv"
SERVICE_USER="www-data"

# ==============================================================================
# Phase 1: System Preparation
# ==============================================================================

echo -e "${BLUE}📋 Phase 1: System Preparation${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
  echo -e "${YELLOW}⚠️  This script should not be run as root${NC}"
  echo "Please run as a regular user with sudo access"
  exit 1
fi

# Check for sudo access
if ! sudo -v; then
  echo -e "${RED}❌ This script requires sudo access${NC}"
  exit 1
fi

echo -e "${GREEN}✓ User has sudo access${NC}"
echo ""

# Update system packages
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential tools
echo "Installing essential tools..."
sudo apt install -y git curl wget vim htop nginx certbot python3-certbot-nginx postgresql postgresql-contrib jq

echo ""
echo -e "${GREEN}✅ Phase 1 Complete: System prepared${NC}"
echo ""

# ==============================================================================
# Phase 2: Python Environment Setup
# ==============================================================================

echo -e "${BLUE}📋 Phase 2: Python Environment Setup${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_VERSION="3.11"

echo "Detected Python version: ${PYTHON_VERSION}"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
  echo -e "${YELLOW}⚠️  Python ${REQUIRED_VERSION}+ required${NC}"
  echo "Installing Python 3.11..."

  sudo add-apt-repository ppa:deadsnakes/ppa -y
  sudo apt update
  sudo apt install -y python3.11 python3.11-venv python3.11-dev
fi

echo -e "${GREEN}✓ Python 3.11+ installed${NC}"
echo ""

# ==============================================================================
# Phase 3: PostgreSQL Configuration
# ==============================================================================

echo -e "${BLUE}📋 Phase 3: PostgreSQL Configuration${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Generate secure password
PG_PASSWORD=$(openssl rand -base64 32)

# Create Prefect database and user
echo "Creating Prefect database..."
sudo -u postgres psql -c "CREATE DATABASE prefect;" 2>/dev/null || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER prefect WITH PASSWORD '${PG_PASSWORD}';" 2>/dev/null || echo "User already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE prefect TO prefect;"

echo -e "${GREEN}✓ PostgreSQL configured${NC}"
echo ""
echo -e "${YELLOW}📝 Database Password (save this):${NC}"
echo "${PG_PASSWORD}"
echo ""

# ==============================================================================
# Phase 4: Application Deployment
# ==============================================================================

echo -e "${BLUE}📋 Phase 4: Application Deployment${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Create application directory
if [ ! -d "${APP_DIR}" ]; then
  sudo mkdir -p "${APP_DIR}"
  sudo chown $USER:$USER "${APP_DIR}"
  echo -e "${GREEN}✓ Created application directory: ${APP_DIR}${NC}"
fi

# Check if repository exists
if [ ! -d "${APP_DIR}/.git" ]; then
  echo -e "${YELLOW}Repository not cloned yet${NC}"
  echo ""
  echo "Please clone your repository to ${APP_DIR}"
  echo "Options:"
  echo "  1. git clone https://github.com/your-org/perfect.git ${APP_DIR}"
  echo "  2. rsync -avz /local/path/ ${APP_DIR}/"
  echo ""
  read -p "Press Enter after repository is in place..."
fi

cd "${APP_DIR}"

# Create virtual environment
if [ ! -d "${VENV_DIR}" ]; then
  echo "Creating Python virtual environment..."
  python3.11 -m venv "${VENV_DIR}"
  echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate and install dependencies
echo "Installing Python dependencies..."
source "${VENV_DIR}/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo -e "${GREEN}✅ Phase 4 Complete: Application deployed${NC}"
echo ""

# ==============================================================================
# Phase 5: Environment Configuration
# ==============================================================================

echo -e "${BLUE}📋 Phase 5: Environment Configuration${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if .env exists
if [ -f "${APP_DIR}/.env" ]; then
  echo -e "${YELLOW}⚠️  .env file already exists${NC}"
  read -p "Overwrite? (y/N): " OVERWRITE
  if [ "$OVERWRITE" != "y" ]; then
    echo "Skipping .env creation"
  else
    rm "${APP_DIR}/.env"
  fi
fi

if [ ! -f "${APP_DIR}/.env" ]; then
  echo "Creating .env file..."
  echo ""

  # Prompt for required variables
  read -p "Notion API Token (ntn_...): " NOTION_TOKEN
  read -p "Notion Email Sequence DB ID: " NOTION_EMAIL_SEQUENCE_DB_ID
  read -p "Notion BusinessX Canada DB ID: " NOTION_BUSINESSX_DB_ID
  read -p "Resend API Key (re_...): " RESEND_API_KEY
  read -p "Discord Webhook URL (optional, press Enter to skip): " DISCORD_WEBHOOK_URL

  # Create .env file
  cat > "${APP_DIR}/.env" <<EOF
# Prefect Configuration
PREFECT_API_DATABASE_CONNECTION_URL=postgresql+asyncpg://prefect:${PG_PASSWORD}@localhost/prefect
PREFECT_SERVER_API_HOST=0.0.0.0
PREFECT_SERVER_API_PORT=4200

# Notion Configuration
NOTION_TOKEN=${NOTION_TOKEN}
NOTION_EMAIL_SEQUENCE_DB_ID=${NOTION_EMAIL_SEQUENCE_DB_ID}
NOTION_BUSINESSX_DB_ID=${NOTION_BUSINESSX_DB_ID}

# Resend Configuration
RESEND_API_KEY=${RESEND_API_KEY}

# Discord Configuration (optional)
DISCORD_WEBHOOK_URL=${DISCORD_WEBHOOK_URL}

# Application Configuration
TESTING_MODE=false
API_HOST=0.0.0.0
API_PORT=8000
EOF

  chmod 600 "${APP_DIR}/.env"
  echo -e "${GREEN}✓ .env file created and secured${NC}"
fi

echo ""
echo -e "${GREEN}✅ Phase 5 Complete: Environment configured${NC}"
echo ""

# ==============================================================================
# Phase 6: Systemd Services
# ==============================================================================

echo -e "${BLUE}📋 Phase 6: Systemd Service Configuration${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Create Prefect Server service
echo "Creating prefect-server.service..."
sudo tee /etc/systemd/system/prefect-server.service > /dev/null <<EOF
[Unit]
Description=Prefect Server
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=${SERVICE_USER}
Group=${SERVICE_USER}
WorkingDirectory=${APP_DIR}
Environment="PATH=${VENV_DIR}/bin"
EnvironmentFile=${APP_DIR}/.env
ExecStart=${VENV_DIR}/bin/prefect server start --host 0.0.0.0 --port 4200
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create Prefect Worker service
echo "Creating prefect-worker.service..."
sudo tee /etc/systemd/system/prefect-worker.service > /dev/null <<EOF
[Unit]
Description=Prefect Worker
After=network.target prefect-server.service
Wants=prefect-server.service

[Service]
Type=simple
User=${SERVICE_USER}
Group=${SERVICE_USER}
WorkingDirectory=${APP_DIR}
Environment="PATH=${VENV_DIR}/bin"
EnvironmentFile=${APP_DIR}/.env
ExecStart=${VENV_DIR}/bin/prefect worker start --pool default
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create FastAPI Webhook service
echo "Creating christmas-webhook.service..."
sudo tee /etc/systemd/system/christmas-webhook.service > /dev/null <<EOF
[Unit]
Description=Christmas Campaign Webhook Server
After=network.target prefect-server.service
Wants=prefect-server.service

[Service]
Type=simple
User=${SERVICE_USER}
Group=${SERVICE_USER}
WorkingDirectory=${APP_DIR}
Environment="PATH=${VENV_DIR}/bin"
EnvironmentFile=${APP_DIR}/.env
ExecStart=${VENV_DIR}/bin/uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Set permissions
sudo chown -R ${SERVICE_USER}:${SERVICE_USER} "${APP_DIR}"

# Reload systemd
sudo systemctl daemon-reload

# Enable services
echo "Enabling services..."
sudo systemctl enable prefect-server
sudo systemctl enable prefect-worker
sudo systemctl enable christmas-webhook

# Start services
echo "Starting services..."
sudo systemctl start prefect-server
sleep 5  # Wait for Prefect server to initialize
sudo systemctl start prefect-worker
sudo systemctl start christmas-webhook

# Check status
echo ""
echo "Service Status:"
sudo systemctl is-active prefect-server && echo "  ✅ Prefect Server" || echo "  ❌ Prefect Server"
sudo systemctl is-active prefect-worker && echo "  ✅ Prefect Worker" || echo "  ❌ Prefect Worker"
sudo systemctl is-active christmas-webhook && echo "  ✅ Webhook Server" || echo "  ❌ Webhook Server"

echo ""
echo -e "${GREEN}✅ Phase 6 Complete: Services running${NC}"
echo ""

# ==============================================================================
# Phase 7: Deploy Prefect Flows
# ==============================================================================

echo -e "${BLUE}📋 Phase 7: Deploy Prefect Flows${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Deploying Prefect flows..."
cd "${APP_DIR}"
source "${VENV_DIR}/bin/activate"

# Deploy flows
python campaigns/christmas_campaign/deployments/deploy_christmas.py

echo ""
echo -e "${GREEN}✅ Phase 7 Complete: Flows deployed${NC}"
echo ""

# ==============================================================================
# Summary
# ==============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 Production Deployment Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next Steps:"
echo ""
echo "1. Configure Nginx reverse proxy with SSL:"
echo "   - See: campaigns/christmas_campaign/WAVE4_PRODUCTION_DEPLOYMENT.md (Phase 4)"
echo ""
echo "2. Configure domain DNS:"
echo "   - Point webhook.yourdomain.com to this server's IP"
echo ""
echo "3. Update website environment:"
echo "   - Set PREFECT_WEBHOOK_URL=https://webhook.yourdomain.com/webhook/christmas-signup"
echo ""
echo "4. Test webhook endpoint:"
echo "   curl http://localhost:8000/health"
echo ""
echo "5. View Prefect UI:"
echo "   http://localhost:4200"
echo ""
echo "6. Monitor logs:"
echo "   sudo journalctl -u christmas-webhook -f"
echo ""
echo "For detailed instructions, see:"
echo "  ${APP_DIR}/campaigns/christmas_campaign/WAVE4_PRODUCTION_DEPLOYMENT.md"
echo ""
