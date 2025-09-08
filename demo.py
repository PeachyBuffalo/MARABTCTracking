#!/usr/bin/env python3
"""
Bitcoin-Holding Stocks MNav Tracker - Demo Script
Quick demonstration of the system's capabilities
"""

import sys
import os
import time
from datetime import datetime

def print_banner():
    """Print a nice banner"""
    print("=" * 70)
    print("₿  Bitcoin-Holding Stocks MNav Tracker - DEMO")
    print("=" * 70)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def demo_analyze_stock():
    """Demo the stock analysis functionality"""
    print("📊 DEMO: Stock Analysis")
    print("-" * 30)
    
    try:
        # Import and run a quick analysis
        from analyze_stock import analyze_stock
        
        # Demo with MARA (Marathon Digital)
        print("🔍 Analyzing MARA (Marathon Digital)...")
        result = analyze_stock('MARA', 50639, 320000000)
        
        if result:
            print(f"✅ Analysis complete!")
            print(f"   Stock Price: ${result['stock_price']:,.2f}")
            print(f"   NAV: ${result['nav']:.4f}")
            print(f"   MNav: {result['mnav']:.4f}")
            print(f"   Signal: {result['signal']}")
        
    except Exception as e:
        print(f"⚠️ Demo analysis failed: {e}")
        print("💡 This is normal if APIs are rate-limited")

def demo_btc_price():
    """Demo BTC price fetching"""
    print("\n₿ DEMO: Bitcoin Price")
    print("-" * 25)
    
    try:
        from analyze_stock import get_btc_price
        price = get_btc_price()
        if price:
            print(f"✅ Current BTC Price: ${price:,.2f}")
        else:
            print("⚠️ Could not fetch BTC price (API rate limited)")
    except Exception as e:
        print(f"⚠️ BTC price demo failed: {e}")

def demo_backtest():
    """Demo backtesting functionality"""
    print("\n📈 DEMO: Backtesting")
    print("-" * 25)
    
    try:
        # Check if backtest module exists
        import mnav_backtest
        print("✅ Backtesting module loaded successfully")
        print("💡 Run 'python mnav_backtest.py' for full backtesting")
    except ImportError as e:
        print(f"⚠️ Backtesting module not available: {e}")

def demo_gui():
    """Demo GUI availability"""
    print("\n🖥️ DEMO: GUI Interface")
    print("-" * 25)
    
    try:
        import tkinter
        print("✅ GUI support available")
        print("💡 Run 'python launch_gui.py' to start the GUI")
    except ImportError:
        print("⚠️ GUI not available (tkinter not installed)")
        print("💡 Install tkinter: brew install python-tk (macOS)")

def show_usage_examples():
    """Show usage examples"""
    print("\n📚 USAGE EXAMPLES")
    print("-" * 20)
    print("1. Quick stock analysis:")
    print("   python analyze_stock.py MARA")
    print()
    print("2. Launch GUI interface:")
    print("   python launch_gui.py")
    print()
    print("3. Run backtesting:")
    print("   python mnav_backtest.py")
    print()
    print("4. Check alerts:")
    print("   python mnav_alert.py")

def show_company_info():
    """Show supported companies"""
    print("\n🏢 SUPPORTED COMPANIES")
    print("-" * 25)
    companies = [
        ("MSTR", "MicroStrategy", "607,770 BTC"),
        ("MARA", "Marathon Digital", "50,639 BTC"),
        ("RIOT", "Riot Platforms", "19,225 BTC"),
        ("CLSK", "CleanSpark", "12,608 BTC"),
        ("TSLA", "Tesla", "11,509 BTC"),
        ("COIN", "Coinbase", "9,267 BTC"),
        ("SQ", "Block Inc", "8,584 BTC"),
        ("SMLR", "Semler Scientific", "5,021 BTC"),
    ]
    
    for symbol, name, btc in companies:
        print(f"   {symbol:4} - {name:20} ({btc})")

def main():
    """Main demo function"""
    print_banner()
    
    # Run demos
    demo_btc_price()
    demo_analyze_stock()
    demo_backtest()
    demo_gui()
    
    # Show information
    show_company_info()
    show_usage_examples()
    
    print("\n" + "=" * 70)
    print("🎉 Demo complete! Check the examples above to get started.")
    print("📖 For more info, visit: https://github.com/PeachyBuffalo/MARABTCTracking")
    print("=" * 70)

if __name__ == "__main__":
    main()
