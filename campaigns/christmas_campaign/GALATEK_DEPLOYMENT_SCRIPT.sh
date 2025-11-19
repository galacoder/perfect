#!/bin/bash
#
# Galatek.dev Christmas Campaign Deployment Script
#
# This script deploys the Christmas Campaign webhook to your existing
# Galatek.dev infrastructure with Prefect already running.
#
# Prerequisites:
#   - Existing Prefect server at prefect.galatek.dev
#   - SSH access to the server
#   - sudo privileges
#
# Usage:
#   chmod +x campaigns/christmas_campaign/GALATEK_DEPLOYMENT_SCRIPT.sh
#   ./campaigns/christmas_campaign/GALATEK_DEPLOYMENT_SCRIPT.sh
#

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎄 Christmas Campaign - Galatek.dev Deployment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Configuration
APP_DIR="/opt/christmas-campaign"
VENV_DIR="${APP_DIR}/venv"
SERVICE_USER="www-data"
PREFECT_API_URL="https://prefect.galatek.dev/api"

# ==============================================================================
# Phase 1: Pre-deployment Checks
# ==============================================================================

echo -e "${BLUE}📋 Phase 1: Pre-deployment Checks${NC}"
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

# Check if Prefect is reachable
echo "Checking Prefect server connectivity..."
if curl -sf "${PREFECT_API_URL}/health" >/dev/null 2>&1; then
  echo -e "${GREEN}✓ Prefect server is reachable at ${PREFECT_API_URL}${NC}"
else
  echo -e "${RED}❌ Cannot reach Prefect server at ${PREFECT_API_URL}${NC}"
  echo "Please verify Prefect is running and accessible"
  exit 1
fi

echo ""
echo -e "${GREEN}✅ Phase 1 Complete: Pre-deployment checks passed${NC}"
echo ""

# ==============================================================================
# Phase 2: System Dependencies
# ==============================================================================

echo -e "${BLUE}📋 Phase 2: System Dependencies${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Update package list
echo "Updating package list..."
sudo apt update -qq

# Install essential tools (skip if already installed)
echo "Installing essential tools..."
sudo apt install -y python3.11 python3.11-venv python3.11-dev git curl jq >/dev/null 2>&1 || true

echo ""
echo -e "${GREEN}✅ Phase 2 Complete: Dependencies installed${NC}"
echo ""

# ==============================================================================
# Phase 3: Application Deployment
# ==============================================================================

echo -e "${BLUE}📋 Phase 3: Application Deployment${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Create application directory if it doesn't exist
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
  echo "Example:"
  echo "  git clone https://github.com/your-org/perfect.git ${APP_DIR}"
  echo ""
  read -p "Press Enter after repository is in place..."
fi

cd "${APP_DIR}"

# Create virtual environment if it doesn't exist
if [ ! -d "${VENV_DIR}" ]; then
  echo "Creating Python virtual environment..."
  python3.11 -m venv "${VENV_DIR}"
  echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate and install dependencies
echo "Installing Python dependencies..."
source "${VENV_DIR}/bin/activate"
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo ""
echo -e "${GREEN}✅ Phase 3 Complete: Application deployed${NC}"
echo ""

# ==============================================================================
# Phase 4: Environment Configuration
# ==============================================================================

echo -e "${BLUE}📋 Phase 4: Environment Configuration${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if .env exists
if [ -f "${APP_DIR}/.env" ]; then
  echo -e "${YELLOW}⚠️  .env file already exists${NC}"
  read -p "Overwrite? (y/N): " OVERWRITE
  if [ "$OVERWRITE" != "y" ]; then
    echo "Skipping .env creation (using existing file)"
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
  read -p "Resend From Email: " RESEND_FROM_EMAIL
  read -p "Discord Webhook URL (optional, press Enter to skip): " DISCORD_WEBHOOK_URL

  # Create .env file
  cat > "${APP_DIR}/.env" <<EOF
# Prefect Configuration
PREFECT_API_URL=${PREFECT_API_URL}

# Notion Configuration
NOTION_TOKEN=${NOTION_TOKEN}
NOTION_EMAIL_SEQUENCE_DB_ID=${NOTION_EMAIL_SEQUENCE_DB_ID}
NOTION_BUSINESSX_DB_ID=${NOTION_BUSINESSX_DB_ID}

# Resend Configuration
RESEND_API_KEY=${RESEND_API_KEY}
RESEND_FROM_EMAIL=${RESEND_FROM_EMAIL}

# Discord Configuration (optional)
DISCORD_WEBHOOK_URL=${DISCORD_WEBHOOK_URL}

# Application Configuration
TESTING_MODE=true
API_HOST=0.0.0.0
API_PORT=8000
EOF

  chmod 600 "${APP_DIR}/.env"
  echo -e "${GREEN}✓ .env file created and secured${NC}"
fi

echo ""
echo -e "${GREEN}✅ Phase 4 Complete: Environment configured${NC}"
echo ""

# ==============================================================================
# Phase 5: Systemd Service (Webhook Server Only)
# ==============================================================================

echo -e "${BLUE}📋 Phase 5: Systemd Service Configuration${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Note: We only create webhook service, Prefect is already running
echo -e "${YELLOW}Note: Prefect server already running separately${NC}"
echo "Creating webhook service only..."
echo ""

# Create FastAPI Webhook service
echo "Creating christmas-webhook.service..."
sudo tee /etc/systemd/system/christmas-webhook.service > /dev/null <<EOF
[Unit]
Description=Christmas Campaign Webhook Server
After=network.target

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

# Enable service
echo "Enabling service..."
sudo systemctl enable christmas-webhook

# Start service
echo "Starting service..."
sudo systemctl start christmas-webhook

# Wait for startup
sleep 3

# Check status
echo ""
echo "Service Status:"
if sudo systemctl is-active christmas-webhook >/dev/null 2>&1; then
  echo -e "  ${GREEN}✅ Webhook Server running${NC}"
else
  echo -e "  ${RED}❌ Webhook Server failed to start${NC}"
  echo ""
  echo "Check logs with: sudo journalctl -u christmas-webhook -n 50"
  exit 1
fi

echo ""
echo -e "${GREEN}✅ Phase 5 Complete: Webhook service running${NC}"
echo ""

# ==============================================================================
# Phase 6: Deploy Prefect Flows
# ==============================================================================

echo -e "${BLUE}📋 Phase 6: Deploy Prefect Flows${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Deploying Prefect flows to ${PREFECT_API_URL}..."
cd "${APP_DIR}"
source "${VENV_DIR}/bin/activate"

# Set Prefect API URL for deployment
export PREFECT_API_URL="${PREFECT_API_URL}"

# Deploy flows
python campaigns/christmas_campaign/deployments/deploy_christmas.py

echo ""
echo -e "${GREEN}✅ Phase 6 Complete: Flows deployed${NC}"
echo ""

# ==============================================================================
# Summary
# ==============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 Galatek.dev Deployment Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Deployment Summary:"
echo "  ✅ Webhook server running on port 8000"
echo "  ✅ Connected to Prefect at ${PREFECT_API_URL}"
echo "  ✅ Flows deployed and ready"
echo ""
echo "Next Steps:"
echo ""
echo "1. Configure DNS for webhook subdomain:"
echo "   - Add A record or CNAME: webhook.galatek.dev → this server"
echo "   - Wait 5-10 minutes for DNS propagation"
echo ""
echo "2. Configure Nginx reverse proxy:"
echo "   - See: campaigns/christmas_campaign/GALATEK_NGINX_CONFIG.md"
echo "   - Add webhook.galatek.dev to your Nginx configuration"
echo ""
echo "3. Get SSL certificate:"
echo "   sudo certbot --nginx -d webhook.galatek.dev"
echo ""
echo "4. Test webhook endpoint:"
echo "   curl http://localhost:8000/health"
echo "   # After DNS + Nginx: curl https://webhook.galatek.dev/health"
echo ""
echo "5. Update website environment:"
echo "   PREFECT_WEBHOOK_URL=https://webhook.galatek.dev/webhook/christmas-signup"
echo ""
echo "6. Monitor logs:"
echo "   sudo journalctl -u christmas-webhook -f"
echo ""
echo "For detailed instructions, see:"
echo "  ${APP_DIR}/campaigns/christmas_campaign/GALATEK_DEPLOYMENT_PLAN.md"
echo ""
