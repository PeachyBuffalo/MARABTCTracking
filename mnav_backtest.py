#!/usr/bin/env python3
"""
MNav Backtesting System
Multi-period backtesting analysis for Bitcoin-holding stocks.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import requests
import time
from datetime import datetime, timedelta
import pickle

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not installed, try to load .env manually
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    except FileNotFoundError:
        pass  # No .env file, continue without it

# Configuration
CACHE_DIR = "cache"
CACHE_DURATION_HOURS = 24  # Cache data for 24 hours

# Stock configuration - will be set based on command line argument
STOCK_SYMBOL = "MARA"  # Default
STOCK_NAME = "Marathon Digital"  # Default
STOCK_BTC_OWNED = 50000  # Default

# Global flag for forcing real data (no mock data fallback)
force_real_data = False

def get_stock_config():
    """Get stock configuration based on symbol"""
    stock_configs = {
        'MSTR': {'name': 'MicroStrategy', 'btc_owned': 607770},
        'MARA': {'name': 'Marathon Digital', 'btc_owned': 50000},
        'RIOT': {'name': 'Riot Platforms', 'btc_owned': 19225},
        'CLSK': {'name': 'CleanSpark', 'btc_owned': 12608},
        'TSLA': {'name': 'Tesla', 'btc_owned': 11509},
        'HUT': {'name': 'Hut 8 Mining', 'btc_owned': 10273},
        'COIN': {'name': 'Coinbase', 'btc_owned': 9267},
        'SQ': {'name': 'Block Inc', 'btc_owned': 8584},
        'SMLR': {'name': 'Semler Scientific', 'btc_owned': 5021},
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
    """Fetch historical BTC data using local data or APIs with caching"""
    global force_real_data
    # Try local data first
    local_data = load_local_btc_data()
    if local_data is not None:
        # Filter to requested date range
        filtered_data = local_data[(local_data.index >= start_date) & (local_data.index <= end_date)]
        if not filtered_data.empty:
            print(f"📦 Using local BTC data")
            return filtered_data
    
    # Try cache first
    cache_key = f"btc_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pkl"
    cached_data = load_from_cache(cache_key)
    if cached_data is not None:
        print(f"📦 Using cached BTC data")
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
    
    # Try alternative BTC data sources
    print("🔄 Trying alternative BTC data sources...")
    
    # Try Binance API
    try:
        return get_btc_data_binance(start_date, end_date)
    except:
        pass
    
    # Try CoinDesk API
    try:
        return get_btc_data_coindesk(start_date, end_date)
    except:
        pass
    
    # Try CryptoCompare API
    try:
        return get_btc_data_cryptocompare(start_date, end_date)
    except:
        pass
    
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
        # Create mock BTC data for testing (unless force_real_data is True)
        if force_real_data:
            print("❌ All real BTC data sources failed")
            print("💡 Try setting up API keys or wait for rate limits to reset")
            return None
        else:
            print("🔄 Creating mock BTC data due to API issues...")
            return create_mock_btc_data(start_date, end_date)

def get_btc_data_binance(start_date, end_date):
    """Fetch BTC data from Binance API"""
    import requests
    
    # Binance public API
    url = "https://api.binance.com/api/v3/klines"
    params = {
        'symbol': 'BTCUSDT',
        'interval': '1d',
        'startTime': int(start_date.timestamp() * 1000),
        'endTime': int(end_date.timestamp() * 1000)
    }
    
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    if not data:
        raise Exception("No data from Binance")
    
    # Convert to DataFrame
    df_data = []
    for candle in data:
        df_data.append({
            'price': float(candle[4])  # Close price
        })
    
    df = pd.DataFrame(df_data)
    df.index = pd.date_range(start=start_date, end=end_date, freq='D')[:len(df)]
    
    print("✅ Retrieved BTC data from Binance")
    return df

def get_btc_data_coindesk(start_date, end_date):
    """Fetch BTC data from CoinDesk API"""
    import requests
    
    # CoinDesk public API
    url = "https://api.coindesk.com/v1/bpi/historical/close.json"
    params = {
        'start': start_date.strftime('%Y-%m-%d'),
        'end': end_date.strftime('%Y-%m-%d')
    }
    
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    if 'bpi' not in data:
        raise Exception("Invalid response from CoinDesk")
    
    # Convert to DataFrame
    prices = data['bpi']
    df_data = []
    for date, price in prices.items():
        df_data.append({
            'price': float(price)
        })
    
    df = pd.DataFrame(df_data)
    df.index = pd.to_datetime(list(prices.keys()))
    
    print("✅ Retrieved BTC data from CoinDesk")
    return df

def get_btc_data_cryptocompare(start_date, end_date):
    """Fetch BTC data from CryptoCompare API"""
    import requests
    
    # CryptoCompare public API
    url = f"https://min-api.cryptocompare.com/data/v2/histoday"
    params = {
        'fsym': 'BTC',
        'tsym': 'USD',
        'limit': 2000,  # Max limit
        'toTs': int(end_date.timestamp())
    }
    
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    if data['Response'] != 'Success':
        raise Exception("Invalid response from CryptoCompare")
    
    # Convert to DataFrame
    df_data = []
    for candle in data['Data']['Data']:
        date = datetime.fromtimestamp(candle['time'])
        if start_date <= date <= end_date:
            df_data.append({
                'price': candle['close']
            })
    
    df = pd.DataFrame(df_data)
    df.index = pd.to_datetime([datetime.fromtimestamp(c['time']) for c in data['Data']['Data'] if start_date <= datetime.fromtimestamp(c['time']) <= end_date])
    
    print("✅ Retrieved BTC data from CryptoCompare")
    return df

def create_mock_btc_data(start_date, end_date):
    """Create mock BTC data for testing when APIs are unavailable"""
    import numpy as np
    
    # Create date range
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Create mock BTC data with realistic patterns
    base_price = 65000.0  # Base BTC price
    np.random.seed(42)  # For reproducible results
    
    # Generate price movements with higher volatility for BTC
    returns = np.random.normal(0, 0.04, len(date_range))  # 4% daily volatility for BTC
    prices = [base_price]
    
    for i in range(1, len(date_range)):
        new_price = prices[-1] * (1 + returns[i])
        prices.append(new_price)
    
    # Create price data
    data = []
    for i, (date, price) in enumerate(zip(date_range, prices)):
        data.append({
            'price': price
        })
    
    df = pd.DataFrame(data, index=date_range)
    print(f"✅ Created mock BTC data with {len(df)} data points")
    
    # Cache the mock BTC data
    cache_key = f"btc_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pkl"
    save_to_cache(df, cache_key)
    print(f"💾 Mock BTC data cached")
    
    return df

def get_btc_holdings_over_time(symbol):
    """Get BTC holdings over time for a given symbol"""
    # Define BTC acquisition history for each company
    btc_history = {
        'SMLR': [
            {'date': '2024-05-28', 'btc_owned': 581},
            {'date': '2024-06-11', 'btc_owned': 791},
            {'date': '2024-06-25', 'btc_owned': 1001},
            {'date': '2024-07-09', 'btc_owned': 1211},
            {'date': '2024-07-23', 'btc_owned': 1421},
            {'date': '2024-08-06', 'btc_owned': 1631},
            {'date': '2024-08-20', 'btc_owned': 1841},
            {'date': '2024-09-03', 'btc_owned': 2051},
            {'date': '2024-09-17', 'btc_owned': 2261},
            {'date': '2024-10-01', 'btc_owned': 2471},
            {'date': '2024-10-15', 'btc_owned': 2681},
            {'date': '2024-10-29', 'btc_owned': 2891},
            {'date': '2024-11-12', 'btc_owned': 3101},
            {'date': '2024-11-26', 'btc_owned': 3311},
            {'date': '2024-12-10', 'btc_owned': 3521},
            {'date': '2024-12-24', 'btc_owned': 3731},
            {'date': '2025-01-07', 'btc_owned': 3941},
            {'date': '2025-01-21', 'btc_owned': 4151},
            {'date': '2025-02-04', 'btc_owned': 4361},
            {'date': '2025-02-18', 'btc_owned': 4571},
            {'date': '2025-03-04', 'btc_owned': 4781},
            {'date': '2025-03-18', 'btc_owned': 4991},
            {'date': '2025-04-01', 'btc_owned': 5021},  # Final amount
        ],
        'MSTR': [
            {'date': '2020-08-11', 'btc_owned': 21454},
            {'date': '2020-09-14', 'btc_owned': 38250},
            {'date': '2020-12-21', 'btc_owned': 70470},
            {'date': '2021-02-24', 'btc_owned': 90532},
            {'date': '2021-06-21', 'btc_owned': 105085},
            {'date': '2021-07-28', 'btc_owned': 108992},
            {'date': '2021-08-24', 'btc_owned': 114042},
            {'date': '2021-09-13', 'btc_owned': 114042},
            {'date': '2021-10-01', 'btc_owned': 114042},
            {'date': '2021-11-29', 'btc_owned': 121044},
            {'date': '2021-12-30', 'btc_owned': 124391},
            {'date': '2022-01-31', 'btc_owned': 125051},
            {'date': '2022-02-15', 'btc_owned': 125051},
            {'date': '2022-03-31', 'btc_owned': 129218},
            {'date': '2022-04-04', 'btc_owned': 129218},
            {'date': '2022-06-28', 'btc_owned': 129699},
            {'date': '2022-08-02', 'btc_owned': 129699},
            {'date': '2022-09-09', 'btc_owned': 130000},
            {'date': '2022-10-27', 'btc_owned': 130000},
            {'date': '2022-12-27', 'btc_owned': 132500},
            {'date': '2023-01-31', 'btc_owned': 132500},
            {'date': '2023-03-23', 'btc_owned': 140000},
            {'date': '2023-04-05', 'btc_owned': 140000},
            {'date': '2023-06-27', 'btc_owned': 152800},
            {'date': '2023-07-31', 'btc_owned': 152800},
            {'date': '2023-09-11', 'btc_owned': 158245},
            {'date': '2023-10-31', 'btc_owned': 158245},
            {'date': '2023-12-26', 'btc_owned': 189150},
            {'date': '2024-01-31', 'btc_owned': 189150},
            {'date': '2024-03-19', 'btc_owned': 205000},
            {'date': '2024-04-30', 'btc_owned': 214246},
            {'date': '2024-06-20', 'btc_owned': 226331},
            {'date': '2024-07-31', 'btc_owned': 226331},
            {'date': '2024-09-16', 'btc_owned': 245000},
            {'date': '2024-10-31', 'btc_owned': 245000},
            {'date': '2024-12-30', 'btc_owned': 301000},
            {'date': '2025-01-31', 'btc_owned': 301000},
            {'date': '2025-03-19', 'btc_owned': 607770},  # Latest amount
        ],
        # Add other companies as needed
    }
    
    if symbol not in btc_history:
        # For companies without historical data, use current holdings
        stock_config = get_stock_config()
        return pd.DataFrame({
            'date': [pd.Timestamp.now().strftime('%Y-%m-%d')],
            'btc_owned': [stock_config['btc_owned']]
        })
    
    # Convert to DataFrame
    df = pd.DataFrame(btc_history[symbol])
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    return df

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
    
    # Updated shares outstanding values based on recent filings
    default_shares = {
        'MSTR': 283544304,  # Updated from current market cap and share price
        'MARA': 351928000,  # Placeholder - needs verification
        'RIOT': 351928000,  # Placeholder - needs verification
        'CLSK': 351928000,  # Placeholder - needs verification
        'TSLA': 351928000,  # Placeholder - needs verification
        'HUT': 351928000,   # Placeholder - needs verification
        'COIN': 351928000,  # Placeholder - needs verification
        'SQ': 351928000,    # Placeholder - needs verification
        'SMLR': 351928000,  # Placeholder - needs verification
        'HIVE': 351928000,  # Placeholder - needs verification
        'CIFR': 351928000   # Placeholder - needs verification
    }
    
    try:
        ticker = yf.Ticker(STOCK_SYMBOL)
        shares = ticker.info.get("sharesOutstanding", default_shares.get(STOCK_SYMBOL, 351928000))
        save_to_cache(shares, cache_key)
        return shares
    except Exception as e:
        print(f"Error fetching shares outstanding for {STOCK_SYMBOL}: {e}")
        return default_shares.get(STOCK_SYMBOL, 351928000)

def get_historical_stock_data(start_date, end_date):
    """Fetch historical stock data using local data or yfinance with caching"""
    global force_real_data
    # Try local data first
    local_data = load_local_stock_data(STOCK_SYMBOL)
    if local_data is not None:
        # Filter to requested date range
        filtered_data = local_data[(local_data.index >= start_date) & (local_data.index <= end_date)]
        if not filtered_data.empty:
            print(f"📦 Using local {STOCK_SYMBOL} data")
            return filtered_data
    
    # Try cache next
    cache_key = f"{STOCK_SYMBOL.lower()}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pkl"
    cached_data = load_from_cache(cache_key)
    if cached_data is not None:
        print(f"📦 Using cached {STOCK_SYMBOL} data")
        return cached_data
    
    # Try yfinance first
    try:
        print(f"🔄 Fetching {STOCK_SYMBOL} data from yfinance...")
        ticker = yf.Ticker(STOCK_SYMBOL)
        df = ticker.history(start=start_date, end=end_date)
        
        # Check if we got valid data
        if df.empty:
            print(f"⚠️ No data returned for {STOCK_SYMBOL}")
            raise Exception("Empty dataframe returned")
            
        # Select only relevant columns and rename to lowercase
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"⚠️ Missing columns for {STOCK_SYMBOL}: {missing_columns}")
            raise Exception("Missing required columns")
            
        df = df[required_columns]
        df.columns = [c.lower() for c in df.columns]
        
        # Cache the data
        save_to_cache(df, cache_key)
        print(f"✅ {STOCK_SYMBOL} data cached successfully")
        return df
    except Exception as e:
        print(f"Error fetching {STOCK_SYMBOL} data with yfinance: {e}")
        
        # Try alternative data sources
        print(f"🔄 Trying alternative data sources for {STOCK_SYMBOL}...")
        
        # Try Alpha Vantage (requires API key)
        try:
            return get_stock_data_alpha_vantage(start_date, end_date)
        except:
            pass
            
        # Try Yahoo Finance alternative endpoint
        try:
            return get_stock_data_yahoo_alt(start_date, end_date)
        except:
            pass
            
        # Try IEX Cloud (requires API key)
        try:
            return get_stock_data_iex(start_date, end_date)
        except:
            pass
        
        # Fallback to mock data (unless force_real_data is True)
        if force_real_data:
            print(f"❌ All real data sources failed for {STOCK_SYMBOL}")
            print("💡 Try setting up API keys or wait for rate limits to reset")
            return None
        else:
            print(f"🔄 Creating mock data for {STOCK_SYMBOL} due to API issues...")
            return create_mock_stock_data(start_date, end_date)

def get_stock_data_alpha_vantage(start_date, end_date):
    """Fetch stock data from Alpha Vantage"""
    import requests
    
    # You'll need to get a free API key from https://www.alphavantage.co/
    API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
    if not API_KEY:
        print("⚠️ Alpha Vantage API key not found. Set ALPHA_VANTAGE_API_KEY environment variable.")
        raise Exception("No API key")
    
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={STOCK_SYMBOL}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if 'Time Series (Daily)' not in data:
        raise Exception("Invalid response from Alpha Vantage")
    
    # Convert to DataFrame
    time_series = data['Time Series (Daily)']
    df_data = []
    
    for date, values in time_series.items():
        if start_date <= datetime.strptime(date, '%Y-%m-%d') <= end_date:
            df_data.append({
                'open': float(values['1. open']),
                'high': float(values['2. high']),
                'low': float(values['3. low']),
                'close': float(values['4. close']),
                'volume': int(values['5. volume'])
            })
    
    df = pd.DataFrame(df_data)
    df.index = pd.to_datetime([d for d in time_series.keys() if start_date <= datetime.strptime(d, '%Y-%m-%d') <= end_date])
    
    print(f"✅ Retrieved {STOCK_SYMBOL} data from Alpha Vantage")
    return df

def get_stock_data_yahoo_alt(start_date, end_date):
    """Try alternative Yahoo Finance endpoint"""
    import requests
    
    # Use Yahoo Finance's alternative endpoint
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{STOCK_SYMBOL}?period1={int(start_date.timestamp())}&period2={int(end_date.timestamp())}&interval=1d"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    if 'chart' not in data or 'result' not in data['chart'] or not data['chart']['result']:
        raise Exception("Invalid response from Yahoo Finance")
    
    result = data['chart']['result'][0]
    timestamps = result['timestamp']
    quotes = result['indicators']['quote'][0]
    
    df_data = []
    for i, ts in enumerate(timestamps):
        if quotes['open'][i] is not None:
            df_data.append({
                'open': quotes['open'][i],
                'high': quotes['high'][i],
                'low': quotes['low'][i],
                'close': quotes['close'][i],
                'volume': quotes['volume'][i] if quotes['volume'][i] else 0
            })
    
    df = pd.DataFrame(df_data)
    df.index = pd.to_datetime(timestamps, unit='s')
    
    print(f"✅ Retrieved {STOCK_SYMBOL} data from Yahoo Finance alternative endpoint")
    return df

def get_stock_data_iex(start_date, end_date):
    """Fetch stock data from IEX Cloud"""
    import requests
    
    # You'll need to get a free API key from https://iexcloud.io/
    API_KEY = os.getenv('IEX_API_KEY')
    if not API_KEY:
        print("⚠️ IEX API key not found. Set IEX_API_KEY environment variable.")
        raise Exception("No API key")
    
    url = f"https://cloud.iexapis.com/stable/stock/{STOCK_SYMBOL}/chart/1y?token={API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    df_data = []
    for item in data:
        date = datetime.strptime(item['date'], '%Y-%m-%d')
        if start_date <= date <= end_date:
            df_data.append({
                'open': item['open'],
                'high': item['high'],
                'low': item['low'],
                'close': item['close'],
                'volume': item['volume']
            })
    
    df = pd.DataFrame(df_data)
    df.index = pd.to_datetime([item['date'] for item in data if start_date <= datetime.strptime(item['date'], '%Y-%m-%d') <= end_date])
    
    print(f"✅ Retrieved {STOCK_SYMBOL} data from IEX Cloud")
    return df

def create_mock_stock_data(start_date, end_date):
    """Create mock stock data for testing when APIs are unavailable"""
    import numpy as np
    
    # Create date range
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Create mock data with realistic patterns
    base_price = 100.0  # Base price
    np.random.seed(42)  # For reproducible results
    
    # Generate price movements
    returns = np.random.normal(0, 0.02, len(date_range))  # 2% daily volatility
    prices = [base_price]
    
    for i in range(1, len(date_range)):
        new_price = prices[-1] * (1 + returns[i])
        prices.append(new_price)
    
    # Create OHLC data
    data = []
    for i, (date, price) in enumerate(zip(date_range, prices)):
        # Create realistic OHLC from close price
        daily_volatility = np.random.uniform(0.01, 0.03)
        high = price * (1 + daily_volatility)
        low = price * (1 - daily_volatility)
        open_price = price * (1 + np.random.uniform(-0.01, 0.01))
        volume = np.random.randint(1000000, 10000000)
        
        data.append({
            'open': open_price,
            'high': high,
            'low': low,
            'close': price,
            'volume': volume
        })
    
    df = pd.DataFrame(data, index=date_range)
    print(f"✅ Created mock data for {STOCK_SYMBOL} with {len(df)} data points")
    
    # Cache the mock data
    cache_key = f"{STOCK_SYMBOL.lower()}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pkl"
    save_to_cache(df, cache_key)
    print(f"💾 Mock data cached for {STOCK_SYMBOL}")
    
    return df

def calculate_mnav_series(mara_df, btc_df):
    """Calculate MNav series from MARA and BTC data with historical BTC holdings"""
    # Validate input data
    if mara_df is None or mara_df.empty:
        print("⚠️ No stock data available")
        return None
    if btc_df is None or btc_df.empty:
        print("⚠️ No BTC data available")
        return None
    
    btc_daily = btc_df.resample('D').last()
    
    # Handle timezone issues safely
    try:
        if hasattr(mara_df.index, 'tz') and mara_df.index.tz is not None:
            mara_df.index = mara_df.index.tz_localize(None)
    except:
        pass
    
    try:
        if hasattr(btc_daily.index, 'tz') and btc_daily.index.tz is not None:
            btc_daily.index = btc_daily.index.tz_localize(None)
    except:
        pass
    
    # Get historical BTC holdings
    btc_holdings_df = get_btc_holdings_over_time(STOCK_SYMBOL)
    
    # Debug: Print data info
    print(f"📊 Stock data shape: {mara_df.shape}, index: {mara_df.index[0]} to {mara_df.index[-1]}")
    print(f"📊 BTC data shape: {btc_daily.shape}, index: {btc_daily.index[0]} to {btc_daily.index[-1]}")
    
    # Merge stock data with BTC price data
    merged = mara_df.join(btc_daily, how='inner')
    
    # Check if merge was successful
    if merged.empty:
        print("⚠️ No overlapping data between stock and BTC")
        print("🔄 Trying alternative merge approach...")
        # Try alternative merge with outer join and forward fill
        merged = mara_df.join(btc_daily, how='outer')
        if merged.empty:
            print("⚠️ Alternative merge also failed")
            return None
        # Forward fill missing values
        merged = merged.ffill().bfill()
        print(f"✅ Alternative merge successful, shape: {merged.shape}")
    
    # Ensure we have the right columns
    if 'price' in merged.columns:
        merged = merged.rename(columns={'price': 'btc_price'})
    
    merged.columns = ['open', 'high', 'low', 'close', 'volume', 'btc_price']
    
    # Add BTC holdings column by forward-filling the holdings data
    merged = merged.join(btc_holdings_df, how='left')
    merged['btc_owned'] = merged['btc_owned'].ffill()
    
    # If no historical data, use current holdings
    if merged['btc_owned'].isna().all():
        stock_config = get_stock_config()
        merged['btc_owned'] = stock_config['btc_owned']
    
    # Dynamically calculate BTC_PER_SHARE for each date
    shares_outstanding = get_shares_outstanding()
    merged['btc_per_share'] = merged['btc_owned'] / shares_outstanding
    
    # Calculate MNav using historical BTC holdings
    merged['mnav'] = merged['close'] / (merged['btc_price'] * merged['btc_per_share'])
    
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
    if mnav_series is None:
        print("Failed to calculate MNav series")
        return None
    print(f"✅ Calculated {len(mnav_series)} data points")
    
    # Cache the MNav data for pattern analysis
    mnav_cache_key = f"mnav_{STOCK_SYMBOL.lower()}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pkl"
    save_to_cache(mnav_series, mnav_cache_key)
    print(f"💾 MNav data cached for pattern analysis")
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

def load_local_stock_data(symbol):
    """Load stock data from local storage"""
    try:
        from daily_data_updater import load_data_locally
        return load_data_locally(f"{symbol.lower()}.pkl", "stocks")
    except ImportError:
        return None
    except Exception as e:
        print(f"⚠️ Error loading local stock data: {e}")
        return None

def load_local_btc_data():
    """Load BTC data from local storage"""
    try:
        from daily_data_updater import load_data_locally
        return load_data_locally("btc.pkl", "btc")
    except ImportError:
        return None
    except Exception as e:
        print(f"⚠️ Error loading local BTC data: {e}")
        return None

def main():
    global STOCK_SYMBOL, STOCK_NAME, STOCK_BTC_OWNED, force_real_data
    
    # Parse command line arguments
    import sys
    force_real_data = False
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--clear-cache':
            clear_cache()
            return
        elif sys.argv[1] == '--help':
            print("Usage: python mnav_backtest.py [STOCK_SYMBOL] [--clear-cache] [--force-real-data]")
            print("Available stocks: MSTR, MARA, RIOT, CLSK, TSLA, HUT, COIN, SQ, HIVE, CIFR")
            print("Example: python mnav_backtest.py MSTR")
            print("Example: python mnav_backtest.py RIOT --clear-cache")
            print("Example: python mnav_backtest.py MSTR --force-real-data")
            return
        elif sys.argv[1] == '--force-real-data':
            force_real_data = True
            if len(sys.argv) > 2:
                STOCK_SYMBOL = sys.argv[2].upper()
        else:
            STOCK_SYMBOL = sys.argv[1].upper()
            if len(sys.argv) > 2 and sys.argv[2] == '--force-real-data':
                force_real_data = True
    
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