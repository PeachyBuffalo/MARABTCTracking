#!/usr/bin/env python3
"""
Quick Stock Price Checker
Gets current stock prices from multiple sources when Yahoo Finance is rate limited
"""

import requests
import time
import sys

def get_price_from_alpha_vantage(symbol):
    """Get price from Alpha Vantage (free tier available)"""
    try:
        # Note: You'd need to get a free API key from https://www.alphavantage.co/
        # For now, this is a placeholder
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=DEMO"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'Global Quote' in data and data['Global Quote']:
                price = float(data['Global Quote']['05. price'])
                return price
    except Exception as e:
        print(f"Alpha Vantage error: {e}")
    return None

def get_price_from_finnhub(symbol):
    """Get price from Finnhub (free tier available)"""
    try:
        # Note: You'd need to get a free API key from https://finnhub.io/
        # For now, this is a placeholder
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token=DEMO"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'c' in data and data['c'] > 0:
                return data['c']
    except Exception as e:
        print(f"Finnhub error: {e}")
    return None

def get_price_from_web_scraping(symbol):
    """Get price from web scraping (fallback)"""
    try:
        # This is a simple example - in practice you'd need more robust scraping
        url = f"https://finance.yahoo.com/quote/{symbol}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            # This is a simplified example - real implementation would parse the HTML
            print(f"⚠️ Web scraping not implemented for {symbol}")
            return None
    except Exception as e:
        print(f"Web scraping error: {e}")
    return None

def check_price(symbol):
    """Check current price from multiple sources"""
    print(f"🔍 Checking current price for {symbol}...")
    
    # Try multiple sources
    sources = [
        ("Alpha Vantage", lambda: get_price_from_alpha_vantage(symbol)),
        ("Finnhub", lambda: get_price_from_finnhub(symbol)),
        ("Web Scraping", lambda: get_price_from_web_scraping(symbol))
    ]
    
    for source_name, source_func in sources:
        try:
            print(f"🔄 Trying {source_name}...")
            price = source_func()
            if price:
                print(f"✅ {source_name} price for {symbol}: ${price:,.2f}")
                return price
            else:
                print(f"❌ {source_name} failed")
        except Exception as e:
            print(f"❌ {source_name} error: {e}")
    
    print(f"❌ Could not get current price for {symbol} from any source")
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python check_price.py <SYMBOL>")
        print("Example: python check_price.py MARA")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    price = check_price(symbol)
    
    if price:
        print(f"\n📊 Current {symbol} price: ${price:,.2f}")
        print("💡 Use this price for accurate analysis")
    else:
        print(f"\n❌ Could not get current price for {symbol}")
        print("💡 Try again later or check manually on Yahoo Finance")

if __name__ == "__main__":
    main()
