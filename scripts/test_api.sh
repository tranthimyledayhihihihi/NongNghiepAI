#!/bin/bash

echo "🧪 Testing AgriAI API Endpoints..."
echo ""

API_URL="http://localhost:8000"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    
    echo -n "Testing $name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$API_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $http_code)"
        echo "   Response: $(echo $body | jq -c '.' 2>/dev/null || echo $body | head -c 100)"
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $http_code)"
        echo "   Error: $body"
    fi
    echo ""
}

# Check if server is running
echo "Checking if server is running..."
if ! curl -s "$API_URL/health" > /dev/null; then
    echo -e "${RED}✗ Server is not running!${NC}"
    echo "Please start the server first: docker-compose up -d"
    exit 1
fi
echo -e "${GREEN}✓ Server is running${NC}"
echo ""

# Run tests
echo "Running API tests..."
echo "===================="
echo ""

# Test 1: Health check
test_endpoint "Health Check" "GET" "/health"

# Test 2: Root endpoint
test_endpoint "Root Endpoint" "GET" "/"

# Test 3: Quality grades
test_endpoint "Quality Grades" "GET" "/api/quality/grades"

# Test 4: Current price
test_endpoint "Current Price" "POST" "/api/pricing/current" \
    '{"crop_name":"Cà chua","region":"Hà Nội","quality_grade":"grade_1"}'

# Test 5: Price forecast
test_endpoint "Price Forecast (7 days)" "POST" "/api/pricing/forecast" \
    '{"crop_name":"Cà chua","region":"Hà Nội","days":7}'

# Test 6: Price history
test_endpoint "Price History" "GET" "/api/pricing/history/Cà%20chua/Hà%20Nội?days=30"

# Test 7: Compare regions
test_endpoint "Compare Regions" "GET" "/api/pricing/compare-regions/Cà%20chua"

echo "===================="
echo "✅ API testing complete!"
echo ""
echo "📚 View full API documentation at: $API_URL/docs"
