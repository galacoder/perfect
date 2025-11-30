#!/bin/bash
# Upload Kestra flows to production instance
# Usage: ./upload_flows.sh

set -e

# Configuration
KESTRA_URL="https://kestra.galatek.dev"
FLOWS_DIR="/Users/sangle/Dev/action/projects/perfect/kestra/flows"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Kestra Flow Upload Script${NC}"
echo "Target: $KESTRA_URL"
echo ""

# Check if admin credentials are provided
if [ -z "$KESTRA_USER" ] || [ -z "$KESTRA_PASS" ]; then
    echo -e "${RED}Error: KESTRA_USER and KESTRA_PASS environment variables must be set${NC}"
    echo ""
    echo "Usage:"
    echo "  export KESTRA_USER='galacoder69@gmail.com'"
    echo "  export KESTRA_PASS='your-password'"
    echo "  ./upload_flows.sh"
    exit 1
fi

# Find all YAML files
flow_files=$(find "$FLOWS_DIR" -name "*.yml" -type f | sort)
total_flows=$(echo "$flow_files" | wc -l | tr -d ' ')

echo -e "Found ${GREEN}$total_flows${NC} flow files"
echo ""

# Upload each flow
count=0
success=0
failed=0

for flow_file in $flow_files; do
    count=$((count + 1))
    flow_name=$(basename "$flow_file")
    relative_path=${flow_file#$FLOWS_DIR/}

    echo -e "[${count}/${total_flows}] Uploading: ${YELLOW}$relative_path${NC}"

    # Upload flow via Kestra API
    response=$(curl -sk -X POST "$KESTRA_URL/api/v1/flows" \
        -H "Content-Type: application/x-yaml" \
        -u "$KESTRA_USER:$KESTRA_PASS" \
        --data-binary "@$flow_file" \
        -w "\n%{http_code}" 2>&1)

    # Extract HTTP status code (last line)
    http_code=$(echo "$response" | tail -1)

    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo -e "  ${GREEN}✓${NC} Success (HTTP $http_code)"
        success=$((success + 1))
    else
        echo -e "  ${RED}✗${NC} Failed (HTTP $http_code)"
        echo "$response" | head -n -1  # Show error message
        failed=$((failed + 1))
    fi
    echo ""
done

# Summary
echo "=================================================="
echo -e "Upload Summary:"
echo -e "  Total:   ${YELLOW}$total_flows${NC}"
echo -e "  Success: ${GREEN}$success${NC}"
echo -e "  Failed:  ${RED}$failed${NC}"
echo "=================================================="

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}All flows uploaded successfully!${NC}"
    exit 0
else
    echo -e "${RED}Some flows failed to upload${NC}"
    exit 1
fi
