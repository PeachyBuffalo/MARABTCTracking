#!/usr/bin/env python3
"""
Test script for the robust price provider system
"""

from providers import PriceRouter
import os

def test_providers():
    """Test the price provider system"""
    print("🧪 Testing Price Provider System")
    print("=" * 40)
    
    # Check if API keys are set
    fmp_key = os.getenv("FMP_API_KEY", "")
    av_key = os.getenv("ALPHAVANTAGE_API_KEY", "")
    
    print(f"🔑 FMP API Key: {'✅ Set' if fmp_key else '❌ Not set'}")
    print(f"🔑 Alpha Vantage API Key: {'✅ Set' if av_key else '❌ Not set'}")
    print()
    
    # Create router
    router = PriceRouter()
    print(f"📡 Available equity providers: {len(router.providers_equity)}")
    for i, provider in enumerate(router.providers_equity):
        provider_name = provider.__class__.__name__
        print(f"   {i+1}. {provider_name}")
    print()
    
    # Test BTC price
    print("🪙 Testing BTC price...")
    try:
        btc_price = router.get_crypto_price("BTC", "USD")
        print(f"✅ BTC Price: ${btc_price:,.2f}")
    except Exception as e:
        print(f"❌ BTC price failed: {e}")
    print()
    
    # Test equity price
    print("📈 Testing equity price (MARA)...")
    try:
        mara_price = router.get_equity_price("MARA")
        print(f"✅ MARA Price: ${mara_price:,.2f}")
    except Exception as e:
        print(f"❌ MARA price failed: {e}")
        print("💡 This is expected without API keys - Yahoo Finance is rate limited")
    print()
    
    # Show setup instructions
    print("💡 To improve reliability, set API keys:")
    print("   export FMP_API_KEY='your_fmp_key'")
    print("   export ALPHAVANTAGE_API_KEY='your_alpha_vantage_key'")
    print()
    print("🔗 Get free API keys from:")
    print("   - FMP: https://financialmodelingprep.com/developer/docs/")
    print("   - Alpha Vantage: https://www.alphavantage.co/support/#api-key")

if __name__ == "__main__":
    test_providers()
