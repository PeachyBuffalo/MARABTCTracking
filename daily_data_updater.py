#!/usr/bin/env python3
"""
Daily Data Updater for MNav Trading
Downloads and stores stock and BTC data locally, updating daily to avoid rate limiting.
"""

import os
import sys
import pandas as pd
import numpy as np
import yfinance as yf
import requests
from datetime import datetime, timedelta
import pickle
import json
import time

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configuration
DATA_DIR = "local_data"
CACHE_DIR = "cache"
STOCKS = ['MSTR', 'MARA', 'RIOT', 'CLSK', 'TSLA', 'HUT', 'COIN', 'SQ', 'HIVE', 'CIFR']

def ensure_directories():
    """Ensure data directories exist"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, "stocks"), exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, "btc"), exist_ok=True)

def get_stock_data_yahoo(symbol, days=365):
    """Get stock data from Yahoo Finance"""
    try:
        print(f"📊 Fetching {symbol} data from Yahoo Finance...")
        ticker = yf.Ticker(symbol)
        
        # Get historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        df = ticker.history(start=start_date, end=end_date)
        
        if df.empty:
            print(f"⚠️ No data returned for {symbol}")
            return None
            
        # Select only relevant columns and rename to lowercase
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"⚠️ Missing columns for {symbol}: {missing_columns}")
            return None
            
        df = df[required_columns]
        df.columns = [c.lower() for c in df.columns]
        
        print(f"✅ Retrieved {len(df)} data points for {symbol}")
        return df
        
    except Exception as e:
        print(f"❌ Error fetching {symbol} data: {e}")
        return None

def get_btc_data_coingecko(days=365):
    """Get BTC data from CoinGecko"""
    try:
        print("📊 Fetching BTC data from CoinGecko...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        from_timestamp = int(start_date.timestamp())
        to_timestamp = int(end_date.timestamp())
        
        url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range?vs_currency=usd&from={from_timestamp}&to={to_timestamp}"
        response = requests.get(url, timeout=30)
        data = response.json()
        
        if 'prices' in data:
            prices = data['prices']
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            print(f"✅ Retrieved {len(df)} BTC data points")
            return df
        else:
            print(f"❌ CoinGecko error: {data}")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching BTC data: {e}")
        return None

def get_btc_data_binance(days=365):
    """Get BTC data from Binance as fallback"""
    try:
        print("📊 Fetching BTC data from Binance...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        url = "https://api.binance.com/api/v3/klines"
        params = {
            'symbol': 'BTCUSDT',
            'interval': '1d',
            'startTime': int(start_date.timestamp() * 1000),
            'endTime': int(end_date.timestamp() * 1000)
        }
        
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        
        if not data:
            print("❌ No data from Binance")
            return None
        
        # Convert to DataFrame
        df_data = []
        for candle in data:
            df_data.append({
                'price': float(candle[4])  # Close price
            })
        
        df = pd.DataFrame(df_data)
        df.index = pd.date_range(start=start_date, end=end_date, freq='D')[:len(df)]
        
        print(f"✅ Retrieved {len(df)} BTC data points from Binance")
        return df
        
    except Exception as e:
        print(f"❌ Error fetching BTC data from Binance: {e}")
        return None

def save_data_locally(data, filename, data_type="stock"):
    """Save data to local storage"""
    filepath = os.path.join(DATA_DIR, data_type, filename)
    
    # Save as pickle for fast loading
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)
    
    # Also save as CSV for easy inspection
    csv_filepath = filepath.replace('.pkl', '.csv')
    data.to_csv(csv_filepath)
    
    # Save metadata
    metadata = {
        'last_updated': datetime.now().isoformat(),
        'data_points': len(data),
        'date_range': {
            'start': data.index.min().isoformat(),
            'end': data.index.max().isoformat()
        },
        'columns': list(data.columns)
    }
    
    meta_filepath = filepath.replace('.pkl', '_metadata.json')
    with open(meta_filepath, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"💾 Saved {data_type} data to {filepath}")
    return filepath

def load_data_locally(filename, data_type="stock"):
    """Load data from local storage"""
    filepath = os.path.join(DATA_DIR, data_type, filename)
    
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        # Check if data is recent (within 24 hours)
        meta_filepath = filepath.replace('.pkl', '_metadata.json')
        if os.path.exists(meta_filepath):
            with open(meta_filepath, 'r') as f:
                metadata = json.load(f)
            
            last_updated = datetime.fromisoformat(metadata['last_updated'])
            if datetime.now() - last_updated < timedelta(hours=24):
                print(f"✅ Using recent local {data_type} data (updated {last_updated.strftime('%Y-%m-%d %H:%M')})")
                return data
            else:
                print(f"⚠️ Local {data_type} data is outdated (updated {last_updated.strftime('%Y-%m-%d %H:%M')})")
                return None
        else:
            print(f"⚠️ No metadata found for {data_type} data")
            return None
            
    except Exception as e:
        print(f"❌ Error loading local {data_type} data: {e}")
        return None

def update_stock_data(symbol):
    """Update stock data for a specific symbol"""
    print(f"\n🔄 Updating {symbol} data...")
    
    # Check if we have recent local data
    local_data = load_data_locally(f"{symbol.lower()}.pkl", "stocks")
    if local_data is not None:
        print(f"✅ {symbol} data is up to date")
        return local_data
    
    # Fetch new data
    data = get_stock_data_yahoo(symbol)
    if data is not None:
        save_data_locally(data, f"{symbol.lower()}.pkl", "stocks")
        return data
    else:
        print(f"❌ Failed to update {symbol} data")
        return None

def update_btc_data():
    """Update BTC data"""
    print(f"\n🔄 Updating BTC data...")
    
    # Check if we have recent local data
    local_data = load_data_locally("btc.pkl", "btc")
    if local_data is not None:
        print(f"✅ BTC data is up to date")
        return local_data
    
    # Try CoinGecko first
    data = get_btc_data_coingecko()
    if data is None:
        # Fallback to Binance
        data = get_btc_data_binance()
    
    if data is not None:
        save_data_locally(data, "btc.pkl", "btc")
        return data
    else:
        print(f"❌ Failed to update BTC data")
        return None

def update_all_data():
    """Update all stock and BTC data"""
    print("🚀 Starting daily data update...")
    ensure_directories()
    
    # Update BTC data
    btc_data = update_btc_data()
    
    # Update stock data
    successful_stocks = []
    for symbol in STOCKS:
        try:
            data = update_stock_data(symbol)
            if data is not None:
                successful_stocks.append(symbol)
            time.sleep(1)  # Rate limiting
        except Exception as e:
            print(f"❌ Error updating {symbol}: {e}")
    
    print(f"\n✅ Data update complete!")
    print(f"📊 Successfully updated {len(successful_stocks)} stocks: {', '.join(successful_stocks)}")
    print(f"₿ BTC data: {'✅ Updated' if btc_data is not None else '❌ Failed'}")
    
    return successful_stocks, btc_data is not None

def get_data_summary():
    """Get summary of local data"""
    print("📊 Local Data Summary")
    print("=" * 50)
    
    # Check BTC data
    btc_file = os.path.join(DATA_DIR, "btc", "btc.pkl")
    if os.path.exists(btc_file):
        with open(btc_file.replace('.pkl', '_metadata.json'), 'r') as f:
            btc_meta = json.load(f)
        print(f"₿ BTC: {btc_meta['data_points']} points, updated {btc_meta['last_updated'][:10]}")
    else:
        print("₿ BTC: Not available")
    
    # Check stock data
    stocks_dir = os.path.join(DATA_DIR, "stocks")
    if os.path.exists(stocks_dir):
        stock_files = [f for f in os.listdir(stocks_dir) if f.endswith('.pkl')]
        print(f"📈 Stocks: {len(stock_files)} available")
        
        for stock_file in sorted(stock_files):
            symbol = stock_file.replace('.pkl', '').upper()
            meta_file = stock_file.replace('.pkl', '_metadata.json')
            meta_path = os.path.join(stocks_dir, meta_file)
            
            if os.path.exists(meta_path):
                with open(meta_path, 'r') as f:
                    meta = json.load(f)
                print(f"  {symbol}: {meta['data_points']} points, updated {meta['last_updated'][:10]}")
            else:
                print(f"  {symbol}: No metadata")
    else:
        print("📈 Stocks: No data available")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--summary':
            get_data_summary()
            return
        elif sys.argv[1] == '--help':
            print("Usage: python daily_data_updater.py [--summary] [--help]")
            print("  --summary: Show local data summary")
            print("  --help: Show this help")
            return
    
    # Update all data
    update_all_data()
    
    print("\n💡 Tips:")
    print("• Run this script daily to keep data fresh")
    print("• Use --summary to check data status")
    print("• Data is stored in 'local_data/' directory")
    print("• The system will automatically use local data when available")

if __name__ == "__main__":
    main() 