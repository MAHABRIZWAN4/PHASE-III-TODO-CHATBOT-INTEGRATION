#!/bin/bash
# Comprehensive Testing Script for Railway Backend
# Usage: ./test-railway-backend.sh <RAILWAY_URL>

BACKEND_URL=$1

if [ -z "$BACKEND_URL" ]; then
    echo "Usage: ./test-railway-backend.sh <RAILWAY_URL>"
    echo "Example: ./test-railway-backend.sh https://backend-production-xxxx.up.railway.app"
    exit 1
fi

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           TESTING RAILWAY BACKEND DEPLOYMENT                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Backend URL: $BACKEND_URL"
echo ""

# Test 1: Health Check
echo "1️⃣  Testing Health Endpoint..."
HEALTH=$(curl -s "$BACKEND_URL/health")
if echo "$HEALTH" | grep -q "healthy"; then
    echo "   ✅ Health check passed"
else
    echo "   ❌ Health check failed: $HEALTH"
    exit 1
fi

# Test 2: Root Endpoint
echo "2️⃣  Testing Root Endpoint..."
ROOT=$(curl -s "$BACKEND_URL/")
if echo "$ROOT" | grep -q "Todo API is running"; then
    echo "   ✅ Root endpoint working"
else
    echo "   ❌ Root endpoint failed: $ROOT"
fi

# Test 3: Signup
echo "3️⃣  Testing Signup..."
SIGNUP_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/auth/signup" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"test$(date +%s)@example.com\",\"password\":\"testpass123\",\"name\":\"Test User\"}")

if echo "$SIGNUP_RESPONSE" | grep -q "token"; then
    echo "   ✅ Signup successful"
    TOKEN=$(echo "$SIGNUP_RESPONSE" | grep -o '"token":"[^"]*' | cut -d'"' -f4)
    USER_ID=$(echo "$SIGNUP_RESPONSE" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
    echo "   Token: ${TOKEN:0:50}..."
    echo "   User ID: $USER_ID"
else
    echo "   ❌ Signup failed: $SIGNUP_RESPONSE"
    exit 1
fi

# Test 4: Get Tasks (with auth)
echo "4️⃣  Testing Get Tasks..."
TASKS=$(curl -s "$BACKEND_URL/api/tasks" -H "Authorization: Bearer $TOKEN")
if echo "$TASKS" | grep -q "\["; then
    echo "   ✅ Get tasks working (empty list expected)"
else
    echo "   ❌ Get tasks failed: $TASKS"
fi

# Test 5: Create Task
echo "5️⃣  Testing Create Task..."
CREATE_TASK=$(curl -s -X POST "$BACKEND_URL/api/tasks" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"title":"Test Task from Script","description":"Testing Railway deployment","completed":false}')

if echo "$CREATE_TASK" | grep -q "Test Task from Script"; then
    echo "   ✅ Task created successfully"
    TASK_ID=$(echo "$CREATE_TASK" | grep -o '"id":[0-9]*' | cut -d':' -f2)
    echo "   Task ID: $TASK_ID"
else
    echo "   ❌ Task creation failed: $CREATE_TASK"
fi

# Test 6: Chat Endpoint (if available)
echo "6️⃣  Testing Chat Endpoint..."
CHAT_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/$USER_ID/chat" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"message":"Hello, show me my tasks"}')

if echo "$CHAT_RESPONSE" | grep -q "conversation_id"; then
    echo "   ✅ Chat endpoint working!"
else
    echo "   ⚠️  Chat endpoint response: $CHAT_RESPONSE"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    TESTING COMPLETE                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Summary:"
echo "  Backend URL: $BACKEND_URL"
echo "  Test User Token: ${TOKEN:0:50}..."
echo "  Test User ID: $USER_ID"
echo "  Test Task ID: $TASK_ID"
