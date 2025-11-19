#!/bin/bash
#
# Manual testing script for Wave 3: Cal.com Webhook Integration
#
# This script tests the Cal.com webhook endpoint with various payloads.
#
# Usage:
#   chmod +x campaigns/christmas_campaign/tests/test_wave3_manual.sh
#   ./campaigns/christmas_campaign/tests/test_wave3_manual.sh
#
# Prerequisites:
#   - Server must be running: uvicorn server:app --reload
#   - Prefect server must be running: prefect server start
#   - Environment variables configured in .env

BASE_URL="http://localhost:8000"

echo "🧪 Wave 3 Manual Testing: Cal.com Webhook Integration"
echo "=================================================="
echo ""

# ==============================================================================
# Test 1: Valid BOOKING_CREATED Event
# ==============================================================================

echo "📋 Test 1: Valid BOOKING_CREATED Event"
echo "Expected: 202 Accepted, flow queued successfully"
echo ""

curl -X POST "${BASE_URL}/webhook/calcom-booking" \
  -H "Content-Type: application/json" \
  -d '{
    "triggerEvent": "BOOKING_CREATED",
    "payload": {
      "booking": {
        "id": 12345,
        "uid": "test-booking-123",
        "title": "BusOS Diagnostic Call",
        "startTime": "2025-11-25T14:00:00.000Z",
        "endTime": "2025-11-25T15:00:00.000Z",
        "attendees": [
          {
            "email": "wave3test@example.com",
            "name": "Wave 3 Test Customer",
            "timeZone": "America/Toronto"
          }
        ]
      }
    }
  }' | jq .

echo ""
echo "---"
echo ""

# ==============================================================================
# Test 2: Non-Booking Event (Should be ignored)
# ==============================================================================

echo "📋 Test 2: Non-Booking Event (BOOKING_CANCELLED)"
echo "Expected: 200 OK, status: ignored"
echo ""

curl -X POST "${BASE_URL}/webhook/calcom-booking" \
  -H "Content-Type: application/json" \
  -d '{
    "triggerEvent": "BOOKING_CANCELLED",
    "payload": {
      "booking": {
        "id": 12346,
        "uid": "cancelled-booking-123"
      }
    }
  }' | jq .

echo ""
echo "---"
echo ""

# ==============================================================================
# Test 3: Invalid Payload (Missing attendees)
# ==============================================================================

echo "📋 Test 3: Invalid Payload (Missing attendees)"
echo "Expected: 400 Bad Request, error message"
echo ""

curl -X POST "${BASE_URL}/webhook/calcom-booking" \
  -H "Content-Type: application/json" \
  -d '{
    "triggerEvent": "BOOKING_CREATED",
    "payload": {
      "booking": {
        "id": 12347,
        "startTime": "2025-11-25T14:00:00.000Z",
        "attendees": []
      }
    }
  }' | jq .

echo ""
echo "---"
echo ""

# ==============================================================================
# Test 4: Meeting Too Soon (Less than 2 hours)
# ==============================================================================

echo "📋 Test 4: Meeting in 1 hour (Too soon for prep sequence)"
echo "Expected: 202 Accepted, but flow will skip reminders"
echo ""

# Calculate 1 hour from now
MEETING_TIME_SOON=$(date -u -v+1H +"%Y-%m-%dT%H:%M:%S.000Z")

curl -X POST "${BASE_URL}/webhook/calcom-booking" \
  -H "Content-Type: application/json" \
  -d "{
    \"triggerEvent\": \"BOOKING_CREATED\",
    \"payload\": {
      \"booking\": {
        \"id\": 12348,
        \"startTime\": \"${MEETING_TIME_SOON}\",
        \"endTime\": \"${MEETING_TIME_SOON}\",
        \"attendees\": [
          {
            \"email\": \"toosoon@example.com\",
            \"name\": \"Too Soon Test\"
          }
        ]
      }
    }
  }" | jq .

echo ""
echo "---"
echo ""

# ==============================================================================
# Test 5: Valid Booking (Existing Christmas Campaign Customer)
# ==============================================================================

echo "📋 Test 5: Valid Booking (Existing Christmas Campaign Customer)"
echo "Expected: 202 Accepted, reminders scheduled, Notion updated"
echo ""
echo "⚠️  IMPORTANT: Replace 'sarah@example.com' with actual test customer email in Christmas campaign"
echo ""

curl -X POST "${BASE_URL}/webhook/calcom-booking" \
  -H "Content-Type: application/json" \
  -d '{
    "triggerEvent": "BOOKING_CREATED",
    "payload": {
      "booking": {
        "id": 12349,
        "startTime": "2025-11-30T14:00:00.000Z",
        "endTime": "2025-11-30T15:00:00.000Z",
        "attendees": [
          {
            "email": "sarah@example.com",
            "name": "Sarah Test Customer",
            "timeZone": "America/Toronto"
          }
        ]
      }
    }
  }' | jq .

echo ""
echo "---"
echo ""

# ==============================================================================
# Summary
# ==============================================================================

echo "✅ Wave 3 Manual Testing Complete!"
echo ""
echo "Next steps:"
echo "1. Check Prefect UI (http://localhost:4200) for scheduled reminder flows"
echo "2. Check Notion BusinessX Canada DB for updated booking status"
echo "3. Check server logs for detailed execution output"
echo "4. For real Cal.com integration, set up webhook in Cal.com settings"
echo ""
echo "Cal.com Webhook Setup:"
echo "  1. Go to Cal.com Settings → Webhooks"
echo "  2. Add webhook URL: http://your-server.com/webhook/calcom-booking"
echo "  3. Subscribe to 'Booking Created' event"
echo "  4. For local testing, use ngrok: ngrok http 8000"
echo ""
