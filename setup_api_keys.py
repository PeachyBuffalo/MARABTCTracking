#!/usr/bin/env python3
"""
Setup API Keys for Alternative Data Sources
This script helps you configure API keys for real data sources.
"""

import os
import sys

def setup_api_keys():
    """Interactive setup for API keys"""
    print("🔑 API Key Setup for Alternative Data Sources")
    print("=" * 50)
    print()
    print("This will help you set up API keys to use real data instead of mock data.")
    print("All APIs mentioned here offer free tiers.")
    print()
    
    # Check current environment
    print("📊 Current API Keys Status:")
    alpha_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    iex_key = os.getenv('IEX_API_KEY')
    
    print(f"Alpha Vantage: {'✅ Set' if alpha_key else '❌ Not set'}")
    print(f"IEX Cloud: {'✅ Set' if iex_key else '❌ Not set'}")
    print()
    
    # Alpha Vantage setup
    print("1️⃣ Alpha Vantage (Recommended)")
    print("   • Free tier: 5 API calls per minute, 500 per day")
    print("   • Get key at: https://www.alphavantage.co/support/#api-key")
    print("   • Provides reliable stock data")
    print()
    
    # IEX Cloud setup
    print("2️⃣ IEX Cloud")
    print("   • Free tier: 50,000 API calls per month")
    print("   • Get key at: https://iexcloud.io/cloud-login#/register")
    print("   • High-quality financial data")
    print()
    
    # Instructions
    print("📝 Setup Instructions:")
    print("1. Get free API keys from the websites above")
    print("2. Set environment variables:")
    print()
    print("   For macOS/Linux:")
    print("   export ALPHA_VANTAGE_API_KEY='your_key_here'")
    print("   export IEX_API_KEY='your_key_here'")
    print()
    print("   For Windows:")
    print("   set ALPHA_VANTAGE_API_KEY=your_key_here")
    print("   set IEX_API_KEY=your_key_here")
    print()
    print("3. Or create a .env file in this directory:")
    print("   ALPHA_VANTAGE_API_KEY=your_key_here")
    print("   IEX_API_KEY=your_key_here")
    print()
    
    # Test current setup
    print("🧪 Testing Current Setup:")
    print("Running a quick test to see if real data sources work...")
    print()
    
    try:
        # Test yfinance (no API key needed)
        print("Testing yfinance...")
        import yfinance as yf
        ticker = yf.Ticker('AAPL')
        info = ticker.info
        if info.get('regularMarketPrice'):
            print("✅ yfinance is working!")
        else:
            print("⚠️ yfinance may be rate limited")
    except Exception as e:
        print(f"❌ yfinance error: {e}")
    
    # Test Binance (no API key needed)
    try:
        print("Testing Binance API...")
        import requests
        response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5)
        if response.status_code == 200:
            print("✅ Binance API is working!")
        else:
            print("❌ Binance API error")
    except Exception as e:
        print(f"❌ Binance API error: {e}")
    
    print()
    print("💡 Tips:")
    print("• Start with Alpha Vantage - it's the most reliable")
    print("• If you're still getting rate limited, wait 15-30 minutes")
    print("• The system will automatically try multiple sources")
    print("• Mock data is still available for testing")
    print()
    print("🚀 Ready to test? Run:")
    print("   python mnav_backtest.py MSTR --clear-cache")

if __name__ == "__main__":
    setup_api_keys() 