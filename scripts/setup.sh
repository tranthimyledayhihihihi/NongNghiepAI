#!/bin/bash

echo "🔧 Setting up AgriAI Development Environment..."

# Create .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env file"
fi

# Create necessary directories
mkdir -p backend/uploads/quality_check
mkdir -p backend/ai_models/weights
mkdir -p backend/ai_models/price_forecast/saved_models
mkdir -p backend/ai_models/harvest_forecast/saved_models

echo "✓ Created directories"

# Make scripts executable
chmod +x scripts/*.sh

echo "✓ Made scripts executable"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your configuration"
echo "2. Run: ./scripts/start.sh"
