import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import time
import yfinance as yf
import os
import json
import pickle

# Configuration
CACHE_DIR = "cache"
CACHE_DURATION_HOURS = 24  # Cache data for 24 hours

# Stock configuration - will be set based on command line argument
STOCK_SYMBOL = "MARA"  # Default
STOCK_NAME = "Marathon Digital"  # Default
STOCK_BTC_OWNED = 50000  # Default

def get_stock_config():
    """Get stock configuration based on symbol"""
    stock_configs = {
        'MSTR': {'name': 'MicroStrategy', 'btc_owned': 601550},
        'MARA': {'name': 'Marathon Digital', 'btc_owned': 50000},
        'RIOT': {'name': 'Riot Platforms', 'btc_owned': 19225},
        'CLSK': {'name': 'CleanSpark', 'btc_owned': 12608},
        'TSLA': {'name': 'Tesla', 'btc_owned': 11509},
        'HUT': {'name': 'Hut 8 Mining', 'btc_owned': 10273},
        'COIN': {'name': 'Coinbase', 'btc_owned': 9267},
        'SQ': {'name': 'Block Inc', 'btc_owned': 8584},
        'HIVE': {'name': 'HIVE Digital', 'btc_owned': 2201},
        'CIFR': {'name': 'Cipher Mining', 'btc_owned': 1063}
    }
    return stock_configs.get(STOCK_SYMBOL, {'name': STOCK_SYMBOL, 'btc_owned': 50000})

def ensure_cache_dir():
    """Ensure cache directory exists"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def get_cache_path(filename):
    """Get full path for cache file"""
    return os.path.join(CACHE_DIR, filename)

def is_cache_valid(cache_path, max_age_hours=CACHE_DURATION_HOURS):
    """Check if cache file is still valid"""
    if not os.path.exists(cache_path):
        return False
    
    file_age = time.time() - os.path.getmtime(cache_path)
    return file_age < (max_age_hours * 3600)

def save_to_cache(data, filename):
    """Save data to cache"""
    ensure_cache_dir()
    cache_path = get_cache_path(filename)
    with open(cache_path, 'wb') as f:
        pickle.dump(data, f)

def load_from_cache(filename):
    """Load data from cache if valid"""
    cache_path = get_cache_path(filename)
    if is_cache_valid(cache_path):
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except:
            pass
    return None

def get_btc_price_current():
    """Get current BTC price from multiple sources"""
    apis = [
        {
            'name': 'CoinGecko',
            'url': 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd',
            'parser': lambda r: float(r.json()['bitcoin']['usd'])
        },
        {
            'name': 'Binance',
            'url': 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT',
            'parser': lambda r: float(r.json()['price'])
        },
        {
            'name': 'CoinDesk',
            'url': 'https://api.coindesk.com/v1/bpi/currentprice/USD.json',
            'parser': lambda r: float(r.json()['bpi']['USD']['rate'].replace(',', ''))
        }
    ]
    
    for api in apis:
        try:
            response = requests.get(api['url'], timeout=10)
            if response.status_code == 200:
                price = api['parser'](response)
                print(f"✅ Got BTC price from {api['name']}: ${price:,.2f}")
                return price
        except Exception as e:
            print(f"❌ {api['name']} failed: {e}")
            continue
    
    raise Exception("All BTC price APIs failed")

def get_btc_historical_data(start_date, end_date):
    """Fetch historical BTC data with caching and fallbacks"""
    # Try cache first
    cache_key = f"btc_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pkl"
    cached_data = load_from_cache(cache_key)
    if cached_data is not None:
        print("📦 Using cached BTC data")
        return cached_data
    
    # Try CoinGecko first (most reliable for historical data)
    try:
        print("🔄 Fetching BTC data from CoinGecko...")
        from_timestamp = int(start_date.timestamp())
        to_timestamp = int(end_date.timestamp())
        url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range?vs_currency=usd&from={from_timestamp}&to={to_timestamp}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'prices' in data:
            prices = data['prices']
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Cache the data
            save_to_cache(df, cache_key)
            print("✅ BTC data cached successfully")
            return df
        else:
            print(f"CoinGecko error: {data}")
    except Exception as e:
        print(f"CoinGecko failed: {e}")
    
    # Fallback: Use current price and simulate historical data
    print("⚠️ Using fallback method: current BTC price for historical simulation")
    try:
        current_price = get_btc_price_current()
        
        # Create historical series with current price
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        df = pd.DataFrame({'price': current_price}, index=date_range)
        
        # Cache the fallback data
        save_to_cache(df, cache_key)
        print(f"📊 Created historical BTC series with current price: ${current_price:,.2f}")
        return df
        
    except Exception as e:
        print(f"All BTC data sources failed: {e}")
        return None

def get_shares_outstanding():
    """Fetch and cache stock shares outstanding using yfinance"""
    cache_key = f"shares_outstanding_{STOCK_SYMBOL}.pkl"
    cached = load_from_cache(cache_key)
    if cached is not None:
        return cached
    
    # Check if we're in a CI environment
    if os.environ.get('CI') == 'true':
        print("CI environment detected, using default shares outstanding")
        return 351928000
    
    try:
        ticker = yf.Ticker(STOCK_SYMBOL)
        shares = ticker.info.get("sharesOutstanding", 351928000)
        save_to_cache(shares, cache_key)
        return shares
    except Exception as e:
        print(f"Error fetching shares outstanding for {STOCK_SYMBOL}: {e}")
        return 351928000

def get_historical_stock_data(start_date, end_date):
    """Fetch historical stock data using yfinance with caching"""
    # Try cache first
    cache_key = f"{STOCK_SYMBOL.lower()}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pkl"
    cached_data = load_from_cache(cache_key)
    if cached_data is not None:
        print(f"📦 Using cached {STOCK_SYMBOL} data")
        return cached_data
    
    try:
        print(f"🔄 Fetching {STOCK_SYMBOL} data from yfinance...")
        ticker = yf.Ticker(STOCK_SYMBOL)
        df = ticker.history(start=start_date, end=end_date)
        # Select only relevant columns and rename to lowercase
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        df.columns = [c.lower() for c in df.columns]
        
        # Cache the data
        save_to_cache(df, cache_key)
        print(f"✅ {STOCK_SYMBOL} data cached successfully")
        return df
    except Exception as e:
        print(f"Error fetching {STOCK_SYMBOL} data with yfinance: {e}")
        return None

def calculate_mnav_series(mara_df, btc_df):
    """Calculate MNav series from MARA and BTC data"""
    btc_daily = btc_df.resample('D').last()
    if mara_df.index.tz is not None:
        mara_df.index = mara_df.index.tz_localize(None)
    if btc_daily.index.tz is not None:
        btc_daily.index = btc_daily.index.tz_localize(None)
    merged = mara_df.join(btc_daily, how='inner')
    merged.columns = ['open', 'high', 'low', 'close', 'volume', 'btc_price']
    # Dynamically calculate BTC_PER_SHARE
    shares_outstanding = get_shares_outstanding()
    btc_per_share = STOCK_BTC_OWNED / shares_outstanding
    merged['mnav'] = merged['close'] / (merged['btc_price'] * btc_per_share)
    return merged

def analyze_mnav_distribution(mnav_series):
    mnav_values = mnav_series['mnav'].dropna()
    stats = {
        'mean': mnav_values.mean(),
        'median': mnav_values.median(),
        'std': mnav_values.std(),
        'min': mnav_values.min(),
        'max': mnav_values.max(),
        'q25': mnav_values.quantile(0.25),
        'q75': mnav_values.quantile(0.75),
        'q10': mnav_values.quantile(0.10),
        'q90': mnav_values.quantile(0.90)
    }
    print("\n=== MNav Distribution Analysis ===")
    print(f"Mean MNav: {stats['mean']:.3f}")
    print(f"Median MNav: {stats['median']:.3f}")
    print(f"Standard Deviation: {stats['std']:.3f}")
    print(f"Range: {stats['min']:.3f} - {stats['max']:.3f}")
    print(f"25th Percentile: {stats['q25']:.3f}")
    print(f"75th Percentile: {stats['q75']:.3f}")
    print(f"10th Percentile: {stats['q10']:.3f}")
    print(f"90th Percentile: {stats['q90']:.3f}")
    return stats

def suggest_thresholds(stats):
    print("\n=== Suggested Trading Thresholds ===")
    conservative_buy = stats['q10']
    conservative_sell = stats['q90']
    moderate_buy = stats['q25']
    moderate_sell = stats['q75']
    mean_buy = stats['mean'] - stats['std']
    mean_sell = stats['mean'] + stats['std']
    print(f"Conservative Strategy:")
    print(f"  Buy when MNav < {conservative_buy:.3f} (10th percentile)")
    print(f"  Sell when MNav > {conservative_sell:.3f} (90th percentile)")
    print(f"\nModerate Strategy:")
    print(f"  Buy when MNav < {moderate_buy:.3f} (25th percentile)")
    print(f"  Sell when MNav > {moderate_sell:.3f} (75th percentile)")
    print(f"\nMean-based Strategy:")
    print(f"  Buy when MNav < {mean_buy:.3f} (mean - 1 std)")
    print(f"  Sell when MNav > {mean_sell:.3f} (mean + 1 std)")
    return {
        'conservative': (conservative_buy, conservative_sell),
        'moderate': (moderate_buy, moderate_sell),
        'mean_based': (mean_buy, mean_sell)
    }

def backtest_strategy(mnav_series, buy_threshold, sell_threshold):
    """Backtest a simple buy/sell strategy"""
    mnav_values = mnav_series['mnav'].dropna()
    mara_prices = mnav_series['close'].dropna()
    position = 0
    trades = []
    current_price = None
    for date, row in mnav_series.iterrows():
        if pd.isna(row['mnav']) or pd.isna(row['close']):
            continue
        mnav = row['mnav']
        price = row['close']
        if position == 0:
            if mnav < buy_threshold:
                position = 1
                current_price = price
                trades.append({
                    'date': date,
                    'action': 'BUY',
                    'price': price,
                    'mnav': mnav
                })
        elif position == 1:
            if mnav > sell_threshold:
                position = 0
                trades.append({
                    'date': date,
                    'action': 'SELL',
                    'price': price,
                    'mnav': mnav,
                    'return': (price - current_price) / current_price * 100
                })
                current_price = None
    return trades

def analyze_trades(trades):
    if not trades:
        print("No trades executed")
        return
    buy_trades = [t for t in trades if t['action'] == 'BUY']
    sell_trades = [t for t in trades if t['action'] == 'SELL']
    print(f"\n=== Trading Performance ===")
    print(f"Total trades: {len(buy_trades)}")
    print(f"Completed trades: {len(sell_trades)}")
    if sell_trades:
        returns = [t['return'] for t in sell_trades]
        total_return = sum(returns)
        avg_return = np.mean(returns)
        print(f"Total return: {total_return:.2f}%")
        print(f"Average return per trade: {avg_return:.2f}%")
        print(f"Best trade: {max(returns):.2f}%")
        print(f"Worst trade: {min(returns):.2f}%")
    return trades

def plot_mnav_analysis(mnav_series, thresholds, filename='mnav_analysis.png'):
    """Plot MNav analysis with thresholds"""
    try:
        plt.figure(figsize=(15, 10))
        
        # Plot MNav over time
        plt.subplot(2, 1, 1)
        mnav_values = mnav_series['mnav'].dropna()
        plt.plot(mnav_values.index, mnav_values.values, label='MNav', alpha=0.7)
        
        # Add threshold lines
        for strategy, (buy_thresh, sell_thresh) in thresholds.items():
            plt.axhline(y=buy_thresh, color='green', linestyle='--', alpha=0.5, 
                       label=f'{strategy.title()} Buy ({buy_thresh:.3f})')
            plt.axhline(y=sell_thresh, color='red', linestyle='--', alpha=0.5,
                       label=f'{strategy.title()} Sell ({sell_thresh:.3f})')
        
        plt.title('MNav Historical Analysis with Trading Thresholds')
        plt.ylabel('MNav')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Plot MNav distribution
        plt.subplot(2, 1, 2)
        plt.hist(mnav_values.values, bins=50, alpha=0.7, edgecolor='black')
        plt.axvline(mnav_values.mean(), color='red', linestyle='-', label=f'Mean: {mnav_values.mean():.3f}')
        plt.axvline(mnav_values.median(), color='blue', linestyle='-', label=f'Median: {mnav_values.median():.3f}')
        
        plt.title('MNav Distribution')
        plt.xlabel('MNav')
        plt.ylabel('Frequency')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()  # Close the figure to free memory
        print(f"📊 Plot saved as: {filename}")
    except Exception as e:
        print(f"❌ Error creating plot: {e}")
        plt.close()  # Make sure to close any open figures

def run_backtest_for_period(days, label):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    print(f"\n===== {label} Backtest: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} =====")
    print(f"📊 Fetching {STOCK_SYMBOL} historical data (yfinance)...")
    stock_df = get_historical_stock_data(start_date, end_date)
    if stock_df is None:
        print(f"Failed to fetch {STOCK_SYMBOL} data")
        return None
    print("📊 Fetching BTC historical data (CoinGecko)...")
    btc_df = get_btc_historical_data(start_date, end_date)
    if btc_df is None:
        print("Failed to fetch BTC data")
        return None
    mnav_series = calculate_mnav_series(stock_df, btc_df)
    print(f"✅ Calculated {len(mnav_series)} data points")
    stats = analyze_mnav_distribution(mnav_series)
    thresholds = suggest_thresholds(stats)
    
    # Generate plot for this period
    filename = f"mnav_analysis_{STOCK_SYMBOL}_{days}d.png"
    plot_mnav_analysis(mnav_series, thresholds, filename)
    
    results = {}
    for strategy, (buy_thresh, sell_thresh) in thresholds.items():
        print(f"\n--- Testing {strategy.title()} Strategy ---")
        trades = backtest_strategy(mnav_series, buy_thresh, sell_thresh)
        analyze_trades(trades)
        results[strategy] = trades
    return mnav_series, thresholds, results

def clear_cache():
    """Clear all cached data"""
    if os.path.exists(CACHE_DIR):
        import shutil
        shutil.rmtree(CACHE_DIR)
        print("🗑️ Cache cleared")
    # Also remove shares outstanding cache
    shares_cache = get_cache_path("shares_outstanding.pkl")
    if os.path.exists(shares_cache):
        os.remove(shares_cache)
        print("🗑️ Shares outstanding cache cleared")

def main():
    global STOCK_SYMBOL, STOCK_NAME, STOCK_BTC_OWNED
    
    # Parse command line arguments
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == '--clear-cache':
            clear_cache()
            return
        elif sys.argv[1] == '--help':
            print("Usage: python mnav_backtest.py [STOCK_SYMBOL] [--clear-cache]")
            print("Available stocks: MSTR, MARA, RIOT, CLSK, TSLA, HUT, COIN, SQ, HIVE, CIFR")
            print("Example: python mnav_backtest.py MSTR")
            print("Example: python mnav_backtest.py RIOT --clear-cache")
            return
        else:
            STOCK_SYMBOL = sys.argv[1].upper()
    
    # Get stock configuration
    stock_config = get_stock_config()
    STOCK_NAME = stock_config['name']
    STOCK_BTC_OWNED = stock_config['btc_owned']
    
    print(f"🚀 Starting {STOCK_NAME} ({STOCK_SYMBOL}) Multi-Period Backtesting Analysis...")
    print(f"Using: yfinance ({STOCK_SYMBOL}), CoinGecko (BTC) with caching and fallbacks")
    print(f"BTC Holdings: {STOCK_BTC_OWNED:,} BTC")
    print("💡 Tip: Use --clear-cache to refresh data")
    print("💡 Tip: Use --help to see available stocks")
    
    periods = [
        (1, "1 Day"),
        (7, "1 Week"),
        (30, "1 Month"),
        (90, "3 Months"),
        (180, "6 Months"),
        (365, "1 Year")
    ]
    
    for days, label in periods:
        try:
            print(f"\n{'='*60}")
            print(f"Processing {label} period...")
            print(f"{'='*60}")
            result = run_backtest_for_period(days, label)
            if result is None:
                print(f"⚠️ Skipping {label} due to data fetch issues")
            else:
                print(f"✅ {label} analysis completed successfully")
        except Exception as e:
            print(f"❌ Error processing {label}: {e}")
            print(f"Continuing with next period...")
            continue
    
    print("\n✅ Multi-period backtesting complete!")
    print("💾 Data cached in 'cache/' directory for faster future runs")
    print("📊 Check the generated PNG files for visual analysis")

if __name__ == "__main__":
    main()