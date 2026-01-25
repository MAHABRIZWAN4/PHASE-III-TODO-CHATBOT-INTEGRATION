#!/bin/bash

echo "════════════════════════════════════════════════════════════════════════════"
echo "                    Testing Backend Chat API Directly"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

# You need to replace these values
USER_ID="YOUR_USER_ID"  # Get from: JSON.parse(localStorage.getItem('auth_user')).id
AUTH_TOKEN="YOUR_TOKEN"  # Get from: JSON.parse(localStorage.getItem('auth_token')).token

if [ "$USER_ID" = "YOUR_USER_ID" ]; then
    echo "⚠️  ERROR: Please edit this script and set USER_ID and AUTH_TOKEN"
    echo ""
    echo "To get these values:"
    echo "1. Open browser console (F12)"
    echo "2. Run: JSON.parse(localStorage.getItem('auth_user')).id"
    echo "3. Copy the user ID"
    echo "4. Run: JSON.parse(localStorage.getItem('auth_token')).token"
    echo "5. Copy the token"
    echo "6. Edit this script and replace USER_ID and AUTH_TOKEN"
    echo ""
    exit 1
fi

echo "📤 Test 1: Initial message - 'Add task to buy groceries'"
echo ""

RESPONSE1=$(curl -s -X POST "http://localhost:8001/api/$USER_ID/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d '{"message": "Add task to buy groceries"}')

echo "Response:"
echo "$RESPONSE1" | python3 -m json.tool
echo ""

# Extract conversation_id
CONV_ID=$(echo "$RESPONSE1" | python3 -c "import sys, json; print(json.load(sys.stdin)['conversation_id'])" 2>/dev/null)

if [ -z "$CONV_ID" ]; then
    echo "❌ Failed to get conversation_id"
    exit 1
fi

echo "✓ Conversation ID: $CONV_ID"
echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

sleep 2

echo "📤 Test 2: Structured format - 'Task Title: Buy groceries'"
echo ""

RESPONSE2=$(curl -s -X POST "http://localhost:8001/api/$USER_ID/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d "{\"message\": \"Task Title: Buy groceries\", \"conversation_id\": \"$CONV_ID\"}")

echo "Response:"
echo "$RESPONSE2" | python3 -m json.tool
echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

sleep 2

echo "📤 Test 3: Due date - 'Due date: Tomorrow'"
echo ""

RESPONSE3=$(curl -s -X POST "http://localhost:8001/api/$USER_ID/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d "{\"message\": \"Due date: Tomorrow\", \"conversation_id\": \"$CONV_ID\"}")

echo "Response:"
echo "$RESPONSE3" | python3 -m json.tool
echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

sleep 2

echo "📤 Test 4: Priority - 'Priority: Medium'"
echo ""

RESPONSE4=$(curl -s -X POST "http://localhost:8001/api/$USER_ID/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d "{\"message\": \"Priority: Medium\", \"conversation_id\": \"$CONV_ID\"}")

echo "Response:"
echo "$RESPONSE4" | python3 -m json.tool
echo ""

# Check for tool_calls
TOOL_CALLS=$(echo "$RESPONSE4" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('metadata', {}).get('tool_calls', []))" 2>/dev/null)

echo "Tool calls in response: $TOOL_CALLS"
echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

sleep 2

echo "📤 Test 5: Category - 'Category: Shopping'"
echo ""

RESPONSE5=$(curl -s -X POST "http://localhost:8001/api/$USER_ID/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d "{\"message\": \"Category: Shopping\", \"conversation_id\": \"$CONV_ID\"}")

echo "Response:"
echo "$RESPONSE5" | python3 -m json.tool
echo ""

# Check for tool_calls
TOOL_CALLS=$(echo "$RESPONSE5" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('metadata', {}).get('tool_calls', []))" 2>/dev/null)

echo "Tool calls in response: $TOOL_CALLS"
echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo "                                TEST COMPLETE"
echo "════════════════════════════════════════════════════════════════════════════"

