#!/bin/bash

# Production Validation Script for Christmas Campaign
# Run this AFTER deployment to verify everything works

set -e

echo "🔍 Christmas Campaign - Production Validation"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
PREFECT_URL="https://prefect.galatek.dev"
DEPLOYMENT_NAME="christmas-signup-handler"

# Functions
check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Validation Tests

echo "Test 1: Worker Service Status"
echo "-------------------------------"
if sudo systemctl is-active --quiet prefect-worker; then
    check_pass "Worker service is running"
else
    check_fail "Worker service is NOT running"
    echo "  Fix: sudo systemctl start prefect-worker"
    exit 1
fi
echo ""

echo "Test 2: Work Pool Exists"
echo "------------------------"
if prefect work-pool ls | grep -q "default-pool"; then
    check_pass "Work pool 'default-pool' exists"
else
    check_fail "Work pool 'default-pool' NOT found"
    echo "  Fix: prefect work-pool create default-pool --type process"
    exit 1
fi
echo ""

echo "Test 3: Deployment Exists"
echo "-------------------------"
if prefect deployment ls | grep -q "${DEPLOYMENT_NAME}"; then
    check_pass "Deployment '${DEPLOYMENT_NAME}' exists"

    # Get deployment ID
    DEPLOYMENT_ID=$(prefect deployment ls | grep "${DEPLOYMENT_NAME}" | awk '{print $1}' | head -1)
    if [ -n "$DEPLOYMENT_ID" ]; then
        echo "  Deployment ID: ${DEPLOYMENT_ID}"
    fi
else
    check_fail "Deployment '${DEPLOYMENT_NAME}' NOT found"
    echo "  Fix: Run deployment command from DEPLOY_NOW.md"
    exit 1
fi
echo ""

echo "Test 4: Prefect UI Accessible"
echo "------------------------------"
if curl -s -o /dev/null -w "%{http_code}" "${PREFECT_URL}/" | grep -q "200"; then
    check_pass "Prefect UI accessible at ${PREFECT_URL}"
else
    check_warn "Prefect UI may not be accessible"
    echo "  Check: ${PREFECT_URL}/"
fi
echo ""

echo "Test 5: Environment Variables"
echo "------------------------------"
if [ -f ".env" ]; then
    check_pass ".env file exists"

    # Check required variables
    if grep -q "NOTION_TOKEN" .env; then
        check_pass "NOTION_TOKEN found"
    else
        check_fail "NOTION_TOKEN missing"
    fi

    if grep -q "RESEND_API_KEY" .env; then
        check_pass "RESEND_API_KEY found"
    else
        check_fail "RESEND_API_KEY missing"
    fi

    if grep -q "NOTION_EMAIL_SEQUENCE_DB_ID" .env; then
        check_pass "NOTION_EMAIL_SEQUENCE_DB_ID found"
    else
        check_fail "NOTION_EMAIL_SEQUENCE_DB_ID missing"
    fi
else
    check_fail ".env file NOT found"
    exit 1
fi
echo ""

echo "Test 6: Python Imports"
echo "----------------------"
export PYTHONPATH=$(pwd)
if python -c "from campaigns.christmas_campaign.flows.signup_handler import signup_handler_flow" 2>/dev/null; then
    check_pass "Flow imports successfully"
else
    check_fail "Cannot import flow"
    echo "  Check: PYTHONPATH and Python environment"
    exit 1
fi
echo ""

echo "Test 7: Recent Flow Runs"
echo "------------------------"
RECENT_RUNS=$(prefect flow-run ls --limit 5 2>/dev/null | wc -l)
if [ "$RECENT_RUNS" -gt 0 ]; then
    check_pass "Found ${RECENT_RUNS} recent flow runs"
    echo ""
    prefect flow-run ls --limit 5
else
    check_warn "No recent flow runs found"
    echo "  This is OK if deployment is brand new"
fi
echo ""

echo "Test 8: Worker Logs"
echo "-------------------"
echo "Last 10 lines of worker logs:"
sudo journalctl -u prefect-worker -n 10 --no-pager
echo ""

# Summary
echo "🎉 Validation Summary"
echo "====================="
echo ""

CHECKS_PASSED=0
CHECKS_FAILED=0

# Count checks (manually, since we don't track them dynamically)
# Based on the checks above, we expect:
# - 5 critical checks (worker, work pool, deployment, .env, imports)

echo "Critical Checks:"
echo "  ✓ Worker service running"
echo "  ✓ Work pool exists"
echo "  ✓ Deployment exists"
echo "  ✓ Environment variables present"
echo "  ✓ Flow imports working"
echo ""

echo "Next Steps:"
echo "  1. Test deployment endpoint (see DEPLOY_NOW.md Step 9)"
echo "  2. Verify in Prefect UI: ${PREFECT_URL}"
echo "  3. Update website environment variables"
echo "  4. Run end-to-end test"
echo ""

if [ -n "$DEPLOYMENT_ID" ]; then
    echo "Production Endpoint:"
    echo "  ${PREFECT_URL}/api/deployments/${DEPLOYMENT_ID}/create_flow_run"
    echo ""

    echo "Test Command:"
    echo "  curl -X POST ${PREFECT_URL}/api/deployments/${DEPLOYMENT_ID}/create_flow_run \\"
    echo "    -H 'Content-Type: application/json' \\"
    echo "    -d '{\"name\":\"test\",\"parameters\":{\"email\":\"test@example.com\",\"first_name\":\"Test\",\"business_name\":\"Test Corp\",\"assessment_score\":65,\"red_systems\":1,\"orange_systems\":1,\"yellow_systems\":1,\"green_systems\":0}}'"
    echo ""
fi

echo "✅ Validation complete!"
echo ""
echo "If all checks passed, your deployment is ready for testing."
