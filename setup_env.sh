#!/bin/bash
"""
Environment Setup Script for Bitcoin Analysis
Sets up API keys and environment variables
"""

echo "🔧 Setting up environment for Bitcoin Analysis"
echo "=============================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# API Keys for Price Data Providers
# Get free API keys from the links below

# Financial Modeling Prep (FMP) - 250 requests/day free
# https://financialmodelingprep.com/developer/docs/
FMP_API_KEY=""

# Alpha Vantage - 25 requests/day free  
# https://www.alphavantage.co/support/#api-key
ALPHAVANTAGE_API_KEY=""

# Optional: Yahoo Finance (no key needed, but rate limited)
# Used as last resort if other providers fail

# Cache settings
CACHE_TTL_SECONDS=30
FORCE_FRESH_DATA=false
EOF
    echo "✅ Created .env file"
else
    echo "📝 .env file already exists"
fi

echo ""
echo "🔑 API Key Setup Instructions:"
echo "=============================="
echo ""
echo "1. Get FMP API Key (Recommended):"
echo "   - Go to: https://financialmodelingprep.com/developer/docs/"
echo "   - Sign up for free account"
echo "   - Copy your API key"
echo "   - Add to .env file: FMP_API_KEY=\"your_key_here\""
echo ""
echo "2. Get Alpha Vantage API Key (Optional):"
echo "   - Go to: https://www.alphavantage.co/support/#api-key"
echo "   - Sign up for free account"
echo "   - Copy your API key"
echo "   - Add to .env file: ALPHAVANTAGE_API_KEY=\"your_key_here\""
echo ""
echo "3. Load environment variables:"
echo "   source .env"
echo ""
echo "4. Test the setup:"
echo "   python test_providers.py"
echo ""
echo "💡 Benefits of API keys:"
echo "   - FMP: 250 requests/day (vs Yahoo's rate limits)"
echo "   - Alpha Vantage: 25 requests/day (backup provider)"
echo "   - More reliable price data"
echo "   - Better for backtesting and frequent analysis"
echo ""
echo "🚀 Ready to use without API keys:"
echo "   python analyze_stock.py MARA"
echo "   python run_gui.py"
