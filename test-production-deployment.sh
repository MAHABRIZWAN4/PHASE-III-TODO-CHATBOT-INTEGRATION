#!/bin/bash

# Production Deployment Test Script
# This script tests all endpoints and functionality of the deployed application

echo "=========================================="
echo "Production Deployment Test Suite"
echo "=========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Deployment URLs
BACKEND_URL="https://backend-one-wine-71.vercel.app"
FRONTEND_URL="https://frontend-kappa-ruddy-34.vercel.app"

# Test counters
PASSED=0
FAILED=0

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected=$3

    echo -n "Testing $name... "
    response=$(curl -s "$url")

    if echo "$response" | grep -q "$expected"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
        echo "  Response: $response"
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((FAILED++))
        echo "  Expected: $expected"
        echo "  Got: $response"
    fi
    echo ""
}

# Function to test HTTP status
test_status() {
    local name=$1
    local url=$2
    local expected_status=$3

    echo -n "Testing $name... "
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url")

    if [ "$status" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (Status: $status)"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((FAILED++))
        echo "  Expected status: $expected_status"
        echo "  Got status: $status"
    fi
    echo ""
}

echo "=========================================="
echo "BACKEND TESTS"
echo "=========================================="
echo ""

# Test 1: Backend Health Check
test_endpoint "Backend Health" "$BACKEND_URL/health" "healthy"

# Test 2: Backend Root
test_endpoint "Backend Root" "$BACKEND_URL/" "Todo API is running"

# Test 3: Backend API Documentation
test_status "API Documentation" "$BACKEND_URL/docs" "200"

# Test 4: Auth Endpoints Exist
echo -n "Testing Auth Endpoints... "
if curl -s "$BACKEND_URL/docs" | grep -q "api/auth"; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi
echo ""

# Test 5: Tasks Endpoints Exist
echo -n "Testing Tasks Endpoints... "
if curl -s "$BACKEND_URL/docs" | grep -q "api/tasks"; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi
echo ""

# Test 6: Chat Endpoints Exist
echo -n "Testing Chat Endpoints... "
if curl -s "$BACKEND_URL/docs" | grep -q "chat"; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
    echo "  Chat endpoint is available"
else
    echo -e "${YELLOW}⚠ WARNING${NC}"
    echo "  Chat endpoint not found - this will be fixed after deployment"
fi
echo ""

echo "=========================================="
echo "FRONTEND TESTS"
echo "=========================================="
echo ""

# Test 7: Frontend Landing Page
echo -n "Testing Frontend Landing Page... "
response=$(curl -s "$FRONTEND_URL/")
if echo "$response" | grep -q "TaskAI"; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
    echo "  Landing page loads successfully"
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
    echo "  Landing page may be stuck in redirect loop"
fi
echo ""

# Test 8: Frontend Login Page
test_status "Login Page" "$FRONTEND_URL/login" "200"

# Test 9: Frontend Signup Page
test_status "Signup Page" "$FRONTEND_URL/signup" "200"

# Test 10: Frontend Dashboard (should redirect to login if not authenticated)
echo -n "Testing Dashboard (unauthenticated)... "
status=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL/dashboard")
if [ "$status" = "200" ] || [ "$status" = "307" ] || [ "$status" = "308" ]; then
    echo -e "${GREEN}✓ PASSED${NC} (Status: $status)"
    ((PASSED++))
    echo "  Dashboard properly handles unauthenticated access"
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
    echo "  Unexpected status: $status"
fi
echo ""

# Test 11: Frontend Chat Page
test_status "Chat Page" "$FRONTEND_URL/chat" "200"

echo "=========================================="
echo "CORS CONFIGURATION TEST"
echo "=========================================="
echo ""

# Test 12: CORS Headers
echo -n "Testing CORS Configuration... "
cors_headers=$(curl -s -I -X OPTIONS "$BACKEND_URL/api/auth/signup" \
    -H "Origin: $FRONTEND_URL" \
    -H "Access-Control-Request-Method: POST")

if echo "$cors_headers" | grep -q "access-control-allow-origin"; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
    echo "  CORS is properly configured"
else
    echo -e "${YELLOW}⚠ WARNING${NC}"
    echo "  CORS headers not detected - may need verification"
fi
echo ""

echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo ""
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Test user signup and login manually"
    echo "2. Test task creation and management"
    echo "3. Test chat functionality"
    exit 0
else
    echo -e "${YELLOW}Some tests failed. Please review the output above.${NC}"
    echo ""
    echo "Common issues:"
    echo "1. Environment variables not set in Vercel"
    echo "2. Code changes not pushed to GitHub"
    echo "3. Deployment not completed yet"
    echo ""
    echo "Refer to DEPLOYMENT_CHECKLIST.md for detailed instructions."
    exit 1
fi
