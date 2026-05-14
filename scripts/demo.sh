#!/bin/bash

echo "🎬 AgriAI Demo Script"
echo "===================="
echo ""

API_URL="http://localhost:8000"

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "⚠️  jq is not installed. Install it for better output formatting."
    echo "   Mac: brew install jq"
    echo "   Ubuntu: sudo apt-get install jq"
    echo ""
fi

echo "📊 Demo 1: Tra cứu giá Cà chua tại Hà Nội"
echo "----------------------------------------"
curl -s -X POST "$API_URL/api/pricing/current" \
    -H "Content-Type: application/json" \
    -d '{"crop_name":"Cà chua","region":"Hà Nội","quality_grade":"grade_1"}' | jq '.'
echo ""

echo "📈 Demo 2: Dự báo giá Cà chua 7 ngày tới"
echo "----------------------------------------"
curl -s -X POST "$API_URL/api/pricing/forecast" \
    -H "Content-Type: application/json" \
    -d '{"crop_name":"Cà chua","region":"Hà Nội","days":7}' | jq '.forecast_data[0:3]'
echo "... (showing first 3 days)"
echo ""

echo "🗺️  Demo 3: So sánh giá Cà chua các vùng"
echo "----------------------------------------"
curl -s "$API_URL/api/pricing/compare-regions/Cà%20chua" | jq '.regions[0:3]'
echo "... (showing first 3 regions)"
echo ""

echo "📋 Demo 4: Phân loại chất lượng"
echo "----------------------------------------"
curl -s "$API_URL/api/quality/grades" | jq '.grades'
echo ""

echo "✅ Demo complete!"
echo ""
echo "🌐 Try the web interface:"
echo "   Frontend: http://localhost:5173"
echo "   API Docs: http://localhost:8000/docs"
