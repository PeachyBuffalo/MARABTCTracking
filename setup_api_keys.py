#!/usr/bin/env python3
"""
API Key Setup Script for Bitcoin Analysis
Helps users set up API keys for better price data reliability
"""

import os
import sys

def create_env_file():
    """Create .env file with API key placeholders"""
    env_content = """# API Keys for Price Data Providers
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
"""
    
    if os.path.exists('.env'):
        print("📝 .env file already exists")
        return False
    else:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
        return True

def check_api_keys():
    """Check if API keys are set"""
    fmp_key = os.getenv("FMP_API_KEY", "")
    av_key = os.getenv("ALPHAVANTAGE_API_KEY", "")
    
    print("🔑 API Key Status:")
    print(f"   FMP API Key: {'✅ Set' if fmp_key else '❌ Not set'}")
    print(f"   Alpha Vantage API Key: {'✅ Set' if av_key else '❌ Not set'}")
    
    return bool(fmp_key or av_key)

def main():
    print("🔧 API Key Setup for Bitcoin Analysis")
    print("=" * 40)
    
    # Create .env file if it doesn't exist
    created = create_env_file()
    
    print("\n🔑 API Key Setup Instructions:")
    print("==============================")
    print()
    print("1. Get FMP API Key (Recommended):")
    print("   - Go to: https://financialmodelingprep.com/developer/docs/")
    print("   - Sign up for free account")
    print("   - Copy your API key")
    print("   - Edit .env file: FMP_API_KEY=\"your_key_here\"")
    print()
    print("2. Get Alpha Vantage API Key (Optional):")
    print("   - Go to: https://www.alphavantage.co/support/#api-key")
    print("   - Sign up for free account")
    print("   - Copy your API key")
    print("   - Edit .env file: ALPHAVANTAGE_API_KEY=\"your_key_here\"")
    print()
    print("3. Load environment variables:")
    print("   source .env")
    print()
    print("4. Test the setup:")
    print("   python test_providers.py")
    print()
    print("💡 Benefits of API keys:")
    print("   - FMP: 250 requests/day (vs Yahoo's rate limits)")
    print("   - Alpha Vantage: 25 requests/day (backup provider)")
    print("   - More reliable price data")
    print("   - Better for backtesting and frequent analysis")
    print()
    print("🚀 Ready to use without API keys:")
    print("   python analyze_stock.py MARA")
    print("   python run_gui.py")
    
    # Check current status
    print("\n📊 Current Status:")
    if check_api_keys():
        print("✅ API keys are configured!")
    else:
        print("⚠️ No API keys set - will use fallback providers")

if __name__ == "__main__":
    main() 