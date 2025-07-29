#!/usr/bin/env python3
"""
Individual Stock NAV and MNav Analyzer
Quick analysis of NAV and MNav for a single stock.
"""

import sys
import requests
import yfinance as yf
from datetime import datetime

def get_btc_price():
    """Get current BTC price"""
    try:
        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd', timeout=10)
        if response.status_code == 200:
            return float(response.json()['bitcoin']['usd'])
    except:
        pass
    
    try:
        response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT', timeout=10)
        if response.status_code == 200:
            return float(response.json()['price'])
    except:
        pass
    
    return None

def analyze_stock(symbol, btc_owned, shares_outstanding):
    """Analyze NAV and MNav for a single stock"""
    print(f"\n{'='*60}")
    print(f"NAV and MNav Analysis for {symbol}")
    print(f"{'='*60}")
    
    # Get current data
    btc_price = get_btc_price()
    if not btc_price:
        print("❌ Could not get BTC price")
        return
    
    try:
        ticker = yf.Ticker(symbol)
        stock_price = ticker.info.get('regularMarketPrice')
        market_cap = ticker.info.get('marketCap')
        
        if not stock_price:
            print(f"❌ Could not get {symbol} price")
            return
        
        print(f"✅ Current BTC Price: ${btc_price:,.2f}")
        print(f"✅ {symbol} Price: ${stock_price:,.2f}")
        print(f"✅ Market Cap: ${market_cap:,.0f}")
        
        # Calculate metrics
        total_btc_value = btc_owned * btc_price
        btc_per_share = btc_owned / shares_outstanding
        nav_per_share = total_btc_value / shares_outstanding
        mnav = stock_price / (btc_price * btc_per_share)
        fair_price = btc_price * btc_per_share
        premium_discount = ((stock_price - fair_price) / fair_price) * 100
        
        # Print results
        print(f"\n💰 Bitcoin Holdings:")
        print(f"  BTC Owned: {btc_owned:,} BTC")
        print(f"  BTC Value: ${total_btc_value:,.0f}")
        print(f"  BTC per Share: {btc_per_share:.6f}")
        
        print(f"\n📈 NAV Analysis:")
        print(f"  NAV per Share: ${nav_per_share:.2f}")
        print(f"  Price vs NAV: {((stock_price - nav_per_share) / nav_per_share * 100):+.1f}%")
        
        print(f"\n🎯 MNav Analysis:")
        print(f"  MNav Ratio: {mnav:.3f}")
        print(f"  Fair Price: ${fair_price:.2f}")
        print(f"  Premium/Discount: {premium_discount:+.1f}%")
        
        # Trading signals
        print(f"\n📋 Trading Signals:")
        if mnav < 0.8:
            print(f"  🟢 STRONG BUY: MNav < 0.8 (trading at significant discount)")
        elif mnav < 1.0:
            print(f"  🟡 BUY: MNav < 1.0 (trading at discount)")
        elif mnav < 1.2:
            print(f"  🟠 HOLD: MNav between 1.0-1.2 (fairly valued)")
        elif mnav < 1.5:
            print(f"  🟡 SELL: MNav between 1.2-1.5 (trading at premium)")
        else:
            print(f"  🔴 STRONG SELL: MNav > 1.5 (trading at significant premium)")
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"  {symbol} is trading at {mnav:.3f}x its Bitcoin-backed value")
        if premium_discount > 0:
            print(f"  The stock has a {premium_discount:.1f}% premium to fair value")
        else:
            print(f"  The stock has a {abs(premium_discount):.1f}% discount to fair value")
        
    except Exception as e:
        print(f"❌ Error analyzing {symbol}: {e}")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python analyze_stock.py SYMBOL [BTC_OWNED] [SHARES_OUTSTANDING]")
        print("\nExamples:")
        print("  python analyze_stock.py MSTR")
        print("  python analyze_stock.py MSTR 607770 283544304")
        print("  python analyze_stock.py MARA 50000 351928000")
        return
    
    symbol = sys.argv[1].upper()
    
    # Default configurations
    defaults = {
        'MSTR': {'btc': 607770, 'shares': 283544304},
        'MARA': {'btc': 50000, 'shares': 351928000},
        'RIOT': {'btc': 19225, 'shares': 351928000},
        'CLSK': {'btc': 12608, 'shares': 351928000},
        'TSLA': {'btc': 11509, 'shares': 351928000},
        'HUT': {'btc': 10273, 'shares': 351928000},
        'COIN': {'btc': 9267, 'shares': 351928000},
        'SQ': {'btc': 8584, 'shares': 351928000},
        'SMLR': {'btc': 5021, 'shares': 351928000},
        'HIVE': {'btc': 2201, 'shares': 351928000},
        'CIFR': {'btc': 1063, 'shares': 351928000}
    }
    
    if symbol in defaults:
        btc_owned = defaults[symbol]['btc']
        shares_outstanding = defaults[symbol]['shares']
        print(f"Using default values for {symbol}: {btc_owned:,} BTC, {shares_outstanding:,} shares")
    else:
        if len(sys.argv) < 4:
            print(f"❌ No default configuration for {symbol}")
            print("Please provide BTC_OWNED and SHARES_OUTSTANDING as arguments")
            return
        btc_owned = int(sys.argv[2])
        shares_outstanding = int(sys.argv[3])
    
    analyze_stock(symbol, btc_owned, shares_outstanding)

if __name__ == "__main__":
    main() 