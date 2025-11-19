#!/bin/bash

# Production Deployment Script for Christmas Campaign
# Target: prefect.galatek.dev
# Method: Prefect CLI (Simplified Architecture)

set -e  # Exit on error

echo "🚀 Christmas Campaign - Production Deployment"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/home/sangle/perfect"  # ⚠️ UPDATE THIS PATH
FLOW_PATH="campaigns/christmas_campaign/flows/signup_handler.py"
FLOW_NAME="signup_handler_flow"
DEPLOYMENT_NAME="christmas-signup-handler"
WORK_POOL="default-pool"

# Functions
log_info() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 not found. Please install it first."
        exit 1
    fi
}

# Phase 1: Pre-flight Checks
echo "Phase 1: Pre-flight Checks"
echo "----------------------------"

# Check if we're in the right directory
if [ ! -f "${PROJECT_ROOT}/${FLOW_PATH}" ]; then
    log_error "Flow file not found at ${PROJECT_ROOT}/${FLOW_PATH}"
    log_warn "Please update PROJECT_ROOT variable in this script"
    exit 1
fi
log_info "Project root verified: ${PROJECT_ROOT}"

# Check required commands
check_command "prefect"
check_command "python"
log_info "Required commands available"

# Check .env file
if [ ! -f "${PROJECT_ROOT}/.env" ]; then
    log_error ".env file not found at ${PROJECT_ROOT}/.env"
    exit 1
fi
log_info ".env file found"

# Verify environment variables
if ! grep -q "NOTION_TOKEN" "${PROJECT_ROOT}/.env"; then
    log_error "NOTION_TOKEN not found in .env"
    exit 1
fi
if ! grep -q "RESEND_API_KEY" "${PROJECT_ROOT}/.env"; then
    log_error "RESEND_API_KEY not found in .env"
    exit 1
fi
log_info "Required environment variables present"

echo ""

# Phase 2: Set Python Path
echo "Phase 2: Environment Setup"
echo "---------------------------"

export PYTHONPATH="${PROJECT_ROOT}"
log_info "PYTHONPATH set to ${PYTHONPATH}"

# Verify Python can import the flow
if ! python -c "from campaigns.christmas_campaign.flows.signup_handler import signup_handler_flow; print('Import successful')" &> /dev/null; then
    log_error "Cannot import signup_handler_flow"
    exit 1
fi
log_info "Flow import verified"

echo ""

# Phase 3: Work Pool Setup
echo "Phase 3: Work Pool Setup"
echo "------------------------"

# Check if work pool exists
if prefect work-pool ls | grep -q "${WORK_POOL}"; then
    log_info "Work pool '${WORK_POOL}' already exists"
else
    log_warn "Work pool '${WORK_POOL}' not found. Creating..."
    if prefect work-pool create "${WORK_POOL}" --type process; then
        log_info "Work pool '${WORK_POOL}' created successfully"
    else
        log_error "Failed to create work pool"
        exit 1
    fi
fi

echo ""

# Phase 4: Deploy Flow
echo "Phase 4: Deploy Flow"
echo "--------------------"

cd "${PROJECT_ROOT}"

log_info "Deploying ${FLOW_NAME}..."

DEPLOY_OUTPUT=$(prefect deploy \
  "${FLOW_PATH}:${FLOW_NAME}" \
  --name "${DEPLOYMENT_NAME}" \
  --pool "${WORK_POOL}" \
  --tag christmas \
  --tag christmas-2025 \
  --tag email-nurture \
  --description "Christmas Campaign signup handler - creates email sequence for new signups" \
  --version 1.0.0 2>&1)

if [ $? -eq 0 ]; then
    log_info "Flow deployed successfully"
    echo "$DEPLOY_OUTPUT"

    # Extract deployment ID (if possible)
    DEPLOYMENT_ID=$(echo "$DEPLOY_OUTPUT" | grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | head -1)
    if [ -n "$DEPLOYMENT_ID" ]; then
        log_info "Deployment ID: ${DEPLOYMENT_ID}"
        echo "$DEPLOYMENT_ID" > /tmp/christmas_deployment_id.txt
    fi
else
    log_error "Deployment failed"
    echo "$DEPLOY_OUTPUT"
    exit 1
fi

echo ""

# Phase 5: Get Deployment ID
echo "Phase 5: Get Deployment ID"
echo "--------------------------"

log_info "Querying deployment information..."

DEPLOYMENT_INFO=$(prefect deployment ls | grep "${DEPLOYMENT_NAME}")
echo "$DEPLOYMENT_INFO"

# Try to get deployment ID via CLI
DEPLOYMENT_ID_CLI=$(prefect deployment inspect "${DEPLOYMENT_NAME}/${DEPLOYMENT_NAME}" 2>/dev/null | grep "id" | head -1 | awk '{print $2}' | tr -d "'\"," || echo "")

if [ -n "$DEPLOYMENT_ID_CLI" ]; then
    DEPLOYMENT_ID="$DEPLOYMENT_ID_CLI"
    log_info "Deployment ID (from CLI): ${DEPLOYMENT_ID}"
fi

# Save deployment ID to file
if [ -n "$DEPLOYMENT_ID" ]; then
    echo "$DEPLOYMENT_ID" > "${PROJECT_ROOT}/PRODUCTION_DEPLOYMENT_ID.txt"
    log_info "Deployment ID saved to PRODUCTION_DEPLOYMENT_ID.txt"
fi

echo ""

# Phase 6: Test Deployment
echo "Phase 6: Test Deployment"
echo "------------------------"

if [ -z "$DEPLOYMENT_ID" ]; then
    log_warn "Deployment ID not found automatically"
    log_warn "Please get deployment ID manually:"
    echo ""
    echo "  prefect deployment ls | grep ${DEPLOYMENT_NAME}"
    echo ""
    log_warn "Skipping API test. Continue manually."
else
    log_info "Testing deployment endpoint..."

    # Get Prefect API URL
    PREFECT_API_URL=$(grep "PREFECT_API_URL" "${PROJECT_ROOT}/.env" | cut -d'=' -f2 | tr -d ' "' || echo "https://prefect.galatek.dev/api")

    TEST_PAYLOAD='{
        "name": "production-deployment-test",
        "parameters": {
            "email": "deploy-test@example.com",
            "first_name": "Deploy",
            "business_name": "Test Deployment Corp",
            "assessment_score": 65,
            "red_systems": 1,
            "orange_systems": 1,
            "yellow_systems": 1,
            "green_systems": 0,
            "gps_score": 50,
            "money_score": 70,
            "weakest_system_1": "GPS System",
            "weakest_system_2": "Money System",
            "revenue_leak_total": 624
        }
    }'

    TEST_URL="${PREFECT_API_URL}/deployments/${DEPLOYMENT_ID}/create_flow_run"

    log_info "Testing: ${TEST_URL}"

    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${TEST_URL}" \
        -H "Content-Type: application/json" \
        -d "$TEST_PAYLOAD")

    HTTP_CODE=$(echo "$RESPONSE" | tail -1)
    BODY=$(echo "$RESPONSE" | head -n -1)

    if [ "$HTTP_CODE" = "201" ]; then
        log_info "Test successful! Flow run created (HTTP 201)"
        echo "$BODY" | python -m json.tool 2>/dev/null || echo "$BODY"
    else
        log_error "Test failed (HTTP ${HTTP_CODE})"
        echo "$BODY"
    fi
fi

echo ""

# Phase 7: Worker Service Setup
echo "Phase 7: Worker Service Setup"
echo "------------------------------"

log_warn "Worker service setup requires sudo access"
log_info "Creating systemd service file template..."

SERVICE_FILE="/tmp/prefect-worker.service"

cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Prefect Worker for default-pool
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=${PROJECT_ROOT}
Environment="PYTHONPATH=${PROJECT_ROOT}"
Environment="PREFECT_API_URL=https://prefect.galatek.dev/api"
ExecStart=$(which prefect) worker start --pool ${WORK_POOL}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

log_info "Service file created at: ${SERVICE_FILE}"
echo ""
echo "To install the service, run:"
echo ""
echo "  sudo cp ${SERVICE_FILE} /etc/systemd/system/prefect-worker.service"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable prefect-worker"
echo "  sudo systemctl start prefect-worker"
echo "  sudo systemctl status prefect-worker"
echo ""

# Ask if user wants to install now
read -p "Install and start worker service now? (requires sudo) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Installing worker service..."

    if sudo cp "$SERVICE_FILE" /etc/systemd/system/prefect-worker.service; then
        log_info "Service file copied"
    else
        log_error "Failed to copy service file"
        exit 1
    fi

    if sudo systemctl daemon-reload; then
        log_info "Systemd reloaded"
    else
        log_error "Failed to reload systemd"
        exit 1
    fi

    if sudo systemctl enable prefect-worker; then
        log_info "Service enabled"
    else
        log_error "Failed to enable service"
        exit 1
    fi

    if sudo systemctl start prefect-worker; then
        log_info "Service started"
    else
        log_error "Failed to start service"
        exit 1
    fi

    log_info "Checking service status..."
    sudo systemctl status prefect-worker --no-pager
else
    log_warn "Skipped worker service installation"
    log_warn "Worker must be running to execute flows!"
fi

echo ""

# Phase 8: Summary
echo "🎉 Deployment Summary"
echo "====================="
echo ""

log_info "Deployment completed successfully!"
echo ""
echo "Details:"
echo "  - Flow: ${FLOW_NAME}"
echo "  - Deployment: ${DEPLOYMENT_NAME}/${DEPLOYMENT_NAME}"
echo "  - Work Pool: ${WORK_POOL}"

if [ -n "$DEPLOYMENT_ID" ]; then
    echo "  - Deployment ID: ${DEPLOYMENT_ID}"
    echo ""
    echo "Production Endpoint:"
    echo "  https://prefect.galatek.dev/api/deployments/${DEPLOYMENT_ID}/create_flow_run"
fi

echo ""
echo "Next Steps:"
echo "  1. Verify worker is running:"
echo "       sudo systemctl status prefect-worker"
echo ""
echo "  2. Check Prefect UI:"
echo "       https://prefect.galatek.dev/"
echo ""
echo "  3. Update website environment variables:"
echo "       PREFECT_API_URL=https://prefect.galatek.dev/api"
echo "       CHRISTMAS_DEPLOYMENT_ID=${DEPLOYMENT_ID}"
echo ""
echo "  4. Monitor worker logs:"
echo "       sudo journalctl -u prefect-worker -f"
echo ""
echo "  5. Test end-to-end flow:"
echo "       Submit test form on website"
echo ""

log_info "Deployment guide: ${PROJECT_ROOT}/campaigns/christmas_campaign/PRODUCTION_DEPLOYMENT_EXECUTION.md"

echo ""
echo "✅ Production deployment complete!"
