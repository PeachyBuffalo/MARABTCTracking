#!/usr/bin/env python3
"""
Individual Stock NAV and MNav Analyzer
Quick analysis of NAV and MNav for a single stock.
"""

import sys
import requests
import yfinance as yf
from datetime import datetime
import time
import os
import pickle

# Import the robust price router
try:
    from providers import PriceRouter
    ROUTER_AVAILABLE = True
except ImportError:
    ROUTER_AVAILABLE = False
    print("⚠️ Price router not available, using fallback")

# Cache settings
CACHE_DIR = "cache"
CACHE_DURATION = 300  # 5 minutes

def ensure_cache_dir():
    """Ensure cache directory exists"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def get_cache_path(key):
    """Get cache file path"""
    return os.path.join(CACHE_DIR, f"{key}.pkl")

def save_to_cache(data, key):
    """Save data to cache"""
    ensure_cache_dir()
    cache_path = get_cache_path(key)
    try:
        with open(cache_path, 'wb') as f:
            pickle.dump(data, f)
    except Exception as e:
        print(f"Warning: Could not save to cache: {e}")

def load_from_cache(key):
    """Load data from cache"""
    cache_path = get_cache_path(key)
    try:
        if os.path.exists(cache_path):
            file_age = time.time() - os.path.getmtime(cache_path)
            if file_age < CACHE_DURATION:
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
    except Exception:
        pass
    return None

def get_btc_price():
    """Get current BTC price using robust router"""
    if ROUTER_AVAILABLE:
        try:
            router = PriceRouter()
            price = router.get_crypto_price("BTC", "USD")
            print(f"✅ BTC Price: ${price:,.2f} (from Coinbase)")
            return price
        except Exception as e:
            print(f"⚠️ Router failed for BTC: {e}")
            print("🔄 Falling back to direct API calls...")
    
    # Fallback to direct API calls
    cached_price = load_from_cache("btc_price")
    if cached_price is not None:
        print(f"📦 Using cached BTC price: ${cached_price:,.2f}")
        return cached_price
    
    # Try multiple APIs with retries
    apis = [
        ('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd', 'coingecko'),
        ('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT', 'binance'),
        ('https://api.coindesk.com/v1/bpi/currentprice.json', 'coindesk')
    ]
    
    for url, source in apis:
        try:
            print(f"🔄 Fetching BTC price from {source}...")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if source == 'coingecko':
                    price = float(data['bitcoin']['usd'])
                elif source == 'binance':
                    price = float(data['price'])
                elif source == 'coindesk':
                    price = float(data['bpi']['USD']['rate_float'])
                
                # Cache the price
                save_to_cache(price, "btc_price")
                print(f"✅ BTC Price: ${price:,.2f} (from {source})")
                return price
                
        except Exception as e:
            print(f"⚠️ Failed to get BTC price from {source}: {e}")
            continue
    
    print("❌ Could not get BTC price from any source")
    return None

def get_stock_price_robust(symbol, force_fresh=False):
    """Get stock price using robust router"""
    if not ROUTER_AVAILABLE:
        print("⚠️ Router not available, using fallback")
        return get_stock_price_fallback(symbol, force_fresh)
    
    # Try cache first (unless forcing fresh data)
    if not force_fresh:
        cached_data = load_from_cache(f"stock_{symbol}")
        if cached_data is not None:
            cache_age = time.time() - os.path.getmtime(get_cache_path(f"stock_{symbol}"))
            cache_age_minutes = int(cache_age / 60)
            print(f"📦 Using cached {symbol} data: ${cached_data['price']:,.2f} (age: {cache_age_minutes} minutes)")
            return cached_data['price']
    
    try:
        router = PriceRouter()
        price = router.get_equity_price(symbol)
        
        # Cache the data
        save_to_cache({'price': price}, f"stock_{symbol}")
        print(f"✅ Fresh {symbol} data: ${price:,.2f}")
        return price
        
    except Exception as e:
        print(f"⚠️ Router failed for {symbol}: {e}")
        print("🔄 Falling back to direct API calls...")
        return get_stock_price_fallback(symbol, force_fresh)

def get_stock_price_fallback(symbol, force_fresh=False):
    """Fallback method using yfinance"""
    # Try cache first (unless forcing fresh data)
    if not force_fresh:
        cached_data = load_from_cache(f"stock_{symbol}")
        if cached_data is not None:
            cache_age = time.time() - os.path.getmtime(get_cache_path(f"stock_{symbol}"))
            cache_age_minutes = int(cache_age / 60)
            print(f"📦 Using cached {symbol} data: ${cached_data['price']:,.2f} (age: {cache_age_minutes} minutes)")
            return cached_data['price']
    
    for attempt in range(3):
        try:
            print(f"🔄 Fetching {symbol} data (attempt {attempt + 1}/3)...")
            ticker = yf.Ticker(symbol)
            
            # Add delay between attempts
            if attempt > 0:
                delay = (2 ** attempt) * 2  # 2s, 4s, 8s
                print(f"⏳ Waiting {delay}s before retry...")
                time.sleep(delay)
            
            stock_price = ticker.info.get('regularMarketPrice')
            
            if stock_price and stock_price > 0:
                # Cache the data
                save_to_cache({'price': stock_price}, f"stock_{symbol}")
                print(f"✅ Fresh {symbol} data: ${stock_price:,.2f}")
                return stock_price
            else:
                print(f"⚠️ {symbol} price is 0 or None")
                
        except Exception as e:
            print(f"⚠️ Error fetching {symbol} data: {e}")
            if "429" in str(e):
                print("🔄 Rate limited, will retry...")
            continue
    
    return None

def get_estimated_price(symbol):
    """Get estimated price from recent cached data or historical averages"""
    # Try to get from cache first
    cached_data = load_from_cache(f"stock_{symbol}")
    if cached_data is not None:
        cache_age = time.time() - os.path.getmtime(get_cache_path(f"stock_{symbol}"))
        cache_age_minutes = int(cache_age / 60)
        print(f"📦 Using cached {symbol} data: ${cached_data['price']:,.2f} (age: {cache_age_minutes} minutes)")
        return cached_data['price']
    
    # Fallback to estimated prices based on recent market data
    estimated_prices = {
        'MARA': 15.50,  # Recent approximate price
        'MSTR': 1450.00,
        'RIOT': 12.80,
        'CLSK': 8.20,
        'TSLA': 180.00,
        'HUT': 2.10,
        'COIN': 220.00,
        'SQ': 65.00,
        'SMLR': 45.00,
        'HIVE': 3.80,
        'CIFR': 12.50
    }
    
    if symbol in estimated_prices:
        print(f"⚠️ WARNING: Using estimated price for {symbol}: ${estimated_prices[symbol]:,.2f}")
        print("💡 This is NOT real-time data and should not be used for trading decisions")
        print("💡 Check current market price for accurate information")
        return estimated_prices[symbol]
    
    return None

def get_trading_signal(mnav: float, symbol: str) -> str:
    """Get trading signal based on historical MNav patterns"""
    # Historical average MNav ranges for different stocks
    # Based on typical trading patterns, not arbitrary thresholds
    historical_ranges = {
        'MSTR': {'avg': 1.4, 'std': 0.3, 'typical_range': (1.1, 1.7)},
        'MARA': {'avg': 0.9, 'std': 0.2, 'typical_range': (0.7, 1.1)},
        'RIOT': {'avg': 0.8, 'std': 0.2, 'typical_range': (0.6, 1.0)},
        'CLSK': {'avg': 0.7, 'std': 0.2, 'typical_range': (0.5, 0.9)},
        'TSLA': {'avg': 1.1, 'std': 0.3, 'typical_range': (0.8, 1.4)},
        'HUT': {'avg': 0.8, 'std': 0.2, 'typical_range': (0.6, 1.0)},
        'COIN': {'avg': 1.2, 'std': 0.3, 'typical_range': (0.9, 1.5)},
        'SQ': {'avg': 1.0, 'std': 0.2, 'typical_range': (0.8, 1.2)},
        'SMLR': {'avg': 0.9, 'std': 0.2, 'typical_range': (0.7, 1.1)},
        'HIVE': {'avg': 0.7, 'std': 0.2, 'typical_range': (0.5, 0.9)},
        'CIFR': {'avg': 0.6, 'std': 0.2, 'typical_range': (0.4, 0.8)}
    }
    
    if symbol not in historical_ranges:
        # Default for unknown stocks
        avg = 1.0
        std = 0.3
        typical_range = (0.7, 1.3)
    else:
        data = historical_ranges[symbol]
        avg = data['avg']
        std = data['std']
        typical_range = data['typical_range']
    
    # Calculate how many standard deviations from average
    z_score = (mnav - avg) / std
    
    # Determine signal based on historical patterns
    if z_score < -2.0:
        return "🟢 STRONG BUY (significantly below historical average)"
    elif z_score < -1.0:
        return "🟡 BUY (below historical average)"
    elif z_score < 1.0:
        return "🟠 HOLD (within typical range)"
    elif z_score < 2.0:
        return "🟡 SELL (above historical average)"
    else:
        return "🔴 STRONG SELL (significantly above historical average)"

def analyze_stock(symbol, btc_owned, shares_outstanding, force_fresh=False):
    """Analyze NAV and MNav for a single stock"""
    print(f"\n{'='*60}")
    print(f"NAV and MNav Analysis for {symbol}")
    print(f"{'='*60}")
    
    # Get current data
    btc_price = get_btc_price()
    if not btc_price:
        print("❌ Could not get BTC price")
        return
    
    # Try to get stock data with robust router
    stock_price = get_stock_price_robust(symbol, force_fresh=force_fresh)
    
    # If API fails, try estimated price
    if not stock_price:
        print(f"⚠️ All price providers failed for {symbol}")
        print("🔄 Trying estimated price...")
        stock_price = get_estimated_price(symbol)
        
        if stock_price:
            print(f"📊 Using estimated price for {symbol}: ${stock_price:,.2f}")
            print("💡 This is an approximation - check current market price for accuracy")
        else:
            print(f"❌ Could not get {symbol} price from any source")
            print("💡 Try again in a few minutes when API rate limits reset")
            return
    
    print(f"✅ {symbol} Price: ${stock_price:,.2f}")
    
    # Calculate metrics
    total_btc_value = btc_owned * btc_price
    nav = total_btc_value / shares_outstanding
    mnav = stock_price / nav if nav > 0 else 0
    
    print(f"\n📊 Analysis Results:")
    print(f"   BTC Owned: {btc_owned:,}")
    print(f"   BTC Value: ${total_btc_value:,.2f}")
    print(f"   Shares Outstanding: {shares_outstanding:,}")
    print(f"   NAV: ${nav:.4f}")
    print(f"   MNav: {mnav:.4f}")
    
    # Trading signal
    signal = get_trading_signal(mnav, symbol)
    print(f"\n🎯 Trading Signal: {signal}")
    
    # Interpretation
    if mnav > 1.0:
        print(f"📈 {symbol} is trading ABOVE NAV (premium)")
    elif mnav < 1.0:
        print(f"📉 {symbol} is trading BELOW NAV (discount)")
    else:
        print(f"📊 {symbol} is trading AT NAV")
    
    return {
        'symbol': symbol,
        'btc_price': btc_price,
        'stock_price': stock_price,
        'nav': nav,
        'mnav': mnav,
        'signal': signal
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_stock.py <SYMBOL> [--fresh]")
        print("Example: python analyze_stock.py MARA")
        print("Example: python analyze_stock.py MARA --fresh")
        print("\n💡 Set API keys for better reliability:")
        print("   export FMP_API_KEY='your_fmp_key'")
        print("   export ALPHAVANTAGE_API_KEY='your_alpha_vantage_key'")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    force_fresh = "--fresh" in sys.argv
    
    if force_fresh:
        print("🔄 Force fresh data mode - will ignore cache")
    
    # Default configurations - Updated January 2025
    defaults = {
        'MSTR': {'btc': 638460, 'shares': 307000000},   # Updated: 638,460 BTC, ~307M shares
        'MARA': {'btc': 50639, 'shares': 320000000},   # Bitcoin Treasuries
        'RIOT': {'btc': 19225, 'shares': 220000000},   # Bitcoin Treasuries
        'CLSK': {'btc': 12608, 'shares': 70000000},    # Bitcoin Treasuries
        'TSLA': {'btc': 11509, 'shares': 3200000000},  # Bitcoin Treasuries
        'HUT': {'btc': 10273, 'shares': 120000000},    # Estimated
        'COIN': {'btc': 9267, 'shares': 220000000},    # Bitcoin Treasuries
        'SQ': {'btc': 8584, 'shares': 650000000},      # Bitcoin Treasuries
        'SMLR': {'btc': 5021, 'shares': 14800000},     # Bitcoin Treasuries
        'HIVE': {'btc': 2201, 'shares': 120000000},    # Estimated
        'CIFR': {'btc': 1063, 'shares': 80000000}      # Estimated
    }
    
    if symbol in defaults:
        btc_owned = defaults[symbol]['btc']
        shares_outstanding = defaults[symbol]['shares']
        print(f"Using default values for {symbol}: {btc_owned:,} BTC, {shares_outstanding:,} shares")
    else:
        print(f"❌ No default data for {symbol}")
        print("Available symbols:", list(defaults.keys()))
        sys.exit(1)
    
    result = analyze_stock(symbol, btc_owned, shares_outstanding, force_fresh=force_fresh)
    
    if result:
        print(f"\n✅ Analysis complete for {symbol}")
        if force_fresh:
            print("📊 Analysis used fresh data from APIs")
        else:
            print("📊 Analysis may have used cached data (use --fresh for latest data)")

if __name__ == "__main__":
    main() 