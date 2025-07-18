import requests
import yfinance as yf
import schedule
import time
import os
import pickle
from dotenv import load_dotenv
import sys
import subprocess

# Load environment variables from .env file if present
load_dotenv()

CACHE_DIR = "cache"
MARA_BTC_OWNED = 50000  # Update this as needed (from MARA's latest report)

def ensure_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def get_cache_path(filename):
    return os.path.join(CACHE_DIR, filename)

def save_to_cache(data, filename):
    ensure_cache_dir()
    cache_path = get_cache_path(filename)
    with open(cache_path, 'wb') as f:
        pickle.dump(data, f)

def load_from_cache(filename):
    cache_path = get_cache_path(filename)
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception:
            pass
    return None

def get_shares_outstanding(symbol):
    cache_key = f"shares_outstanding_{symbol}.pkl"
    cached = load_from_cache(cache_key)
    if cached is not None:
        return cached
    
    # Check if we're in a CI environment
    if os.environ.get('CI') == 'true':
        print("CI environment detected, using default shares outstanding")
        return 351928000
    
    try:
        ticker = yf.Ticker(symbol)
        shares = ticker.info.get("sharesOutstanding", 351928000)
        save_to_cache(shares, cache_key)
        return shares
    except Exception as e:
        print(f"Error fetching shares outstanding for {symbol}: {e}")
        return 351928000

# Configuration
THRESHOLD = 0.05  # 5% change triggers alert

# Multi-stock configuration
STOCKS_TO_MONITOR = [
    {
        'symbol': 'MSTR',
        'name': 'MicroStrategy',
        'btc_owned': 601550,
        'threshold': 0.05
    },
    {
        'symbol': 'MARA',
        'name': 'Marathon Digital',
        'btc_owned': 50000,
        'threshold': 0.05
    },
    {
        'symbol': 'RIOT',
        'name': 'Riot Platforms', 
        'btc_owned': 19225,
        'threshold': 0.05
    },
    {
        'symbol': 'CLSK',
        'name': 'CleanSpark',
        'btc_owned': 12608,
        'threshold': 0.05
    },
    {
        'symbol': 'TSLA',
        'name': 'Tesla',
        'btc_owned': 11509,
        'threshold': 0.05
    },
    {
        'symbol': 'HUT',
        'name': 'Hut 8 Mining',
        'btc_owned': 10273,
        'threshold': 0.05
    },
    {
        'symbol': 'COIN',
        'name': 'Coinbase',
        'btc_owned': 9267,
        'threshold': 0.05
    },
    {
        'symbol': 'SQ',  # Block Inc. (formerly Square)
        'name': 'Block Inc',
        'btc_owned': 8584,
        'threshold': 0.05
    },
    {
        'symbol': 'HIVE',
        'name': 'HIVE Digital',
        'btc_owned': 2201,
        'threshold': 0.05
    },
    {
        'symbol': 'CIFR',
        'name': 'Cipher Mining',
        'btc_owned': 1063,
        'threshold': 0.05
    }
]

# Global variable to store previous MNav for each stock
previous_mnav = {}

def get_btc_price():
    # Try multiple APIs for reliability
    apis = [
        "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
        "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",
        "https://api.coindesk.com/v1/bpi/currentprice/USD.json"
    ]
    
    for api in apis:
        try:
            response = requests.get(api, timeout=10)
            if api == "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd":
                return float(response.json()['bitcoin']['usd'])
            elif api == "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT":
                return float(response.json()['price'])
            elif api == "https://api.coindesk.com/v1/bpi/currentprice/USD.json":
                return float(response.json()['bpi']['USD']['rate'].replace(",", ""))
        except Exception as e:
            print(f"Failed to fetch from {api}: {e}")
            continue
    
    raise Exception("All Bitcoin price APIs failed")

def get_stock_price(symbol):
    try:
        ticker = yf.Ticker(symbol)
        price = ticker.info.get("currentPrice", 0)
        return price
    except Exception as e:
        print(f"Error fetching {symbol} price: {e}")
        return 0

def calculate_mnav(stock_price, btc_price, btc_per_share):
    return stock_price / (btc_price * btc_per_share)

def send_mnav_alert(stock_config, prev, curr, change, stock_price, btc_price):
    title = f"🔔 {stock_config['name']} MNav Alert"
    message = f"MNav changed by {change:.2f}%\nPrevious: {prev:.3f} → Current: {curr:.3f}\n{stock_config['symbol']}: ${stock_price:.2f} | BTC: ${btc_price:,.0f}"
    send_mac_notification(title, message)

def check_mnav():
    btc_price = get_btc_price()
    
    for stock_config in STOCKS_TO_MONITOR:
        symbol = stock_config['symbol']
        stock_price = get_stock_price(symbol)
        
        if stock_price == 0:
            print(f"⚠️ Skipping {symbol} - price fetch failed")
            continue
            
        btc_per_share = stock_config['btc_owned'] / get_shares_outstanding(symbol)
        current_mnav = calculate_mnav(stock_price, btc_price, btc_per_share)

        if symbol not in previous_mnav:
            previous_mnav[symbol] = current_mnav
            print(f"Initialized {symbol} MNav: {current_mnav:.3f}")
            continue

        change = (current_mnav - previous_mnav[symbol]) / previous_mnav[symbol]
        print(f"{symbol} MNav: {current_mnav:.3f}, Change: {change*100:.2f}%")

        if abs(change) >= stock_config['threshold']:
            send_mnav_alert(stock_config, previous_mnav[symbol], current_mnav, change * 100, stock_price, btc_price)

        previous_mnav[symbol] = current_mnav

def send_mac_notification(title, message):
    """Send a native macOS notification using terminal-notifier"""
    try:
        subprocess.run([
            'terminal-notifier',
            '-title', title,
            '-message', message
        ], check=True)
        print("✅ Mac notification sent (terminal-notifier)!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to send Mac notification: {e}")
    except Exception as e:
        print(f"❌ Error sending notification: {e}")

def send_test_notification():
    send_mac_notification("Test MNav Alert", "This is a test notification from your MNav alert script!")

# Schedule it every hour
schedule.every(1).hours.do(check_mnav)

def run_check_once():
    """Run a single check and always send a notification with current status"""
    btc_price = get_btc_price()
    
    for stock_config in STOCKS_TO_MONITOR:
        symbol = stock_config['symbol']
        stock_price = get_stock_price(symbol)
        
        if stock_price == 0:
            print(f"⚠️ Skipping {symbol} - price fetch failed")
            continue
            
        btc_per_share = stock_config['btc_owned'] / get_shares_outstanding(symbol)
        current_mnav = calculate_mnav(stock_price, btc_price, btc_per_share)

        if symbol not in previous_mnav:
            previous_mnav[symbol] = current_mnav
            print(f"Initialized {symbol} MNav: {current_mnav:.3f}")
            # Send notification for first run
            send_mac_notification(f"🔔 {stock_config['name']} Monitor Started", f"Current {stock_config['name']} MNav: {current_mnav:.3f}\n{stock_config['symbol']}: ${stock_price:.2f} | BTC: ${btc_price:,.0f}")
            continue

        change = (current_mnav - previous_mnav[symbol]) / previous_mnav[symbol]
        print(f"{symbol} MNav: {current_mnav:.3f}, Change: {change*100:.2f}%")

        # Always send notification for test-now
        if abs(change) >= stock_config['threshold']:
            title = f"🔔 {stock_config['name']} Alert - Significant Change"
            message = f"MNav changed by {change*100:.2f}%\nPrevious: {previous_mnav[symbol]:.3f} → Current: {current_mnav:.3f}\n{stock_config['symbol']}: ${stock_price:.2f} | BTC: ${btc_price:,.0f}"
        else:
            title = f"📊 {stock_config['name']} Status Check"
            message = f"Current {stock_config['name']} MNav: {current_mnav:.3f} (Change: {change*100:.2f}%)\n{stock_config['symbol']}: ${stock_price:.2f} | BTC: ${btc_price:,.0f}"

        send_mac_notification(title, message)
        previous_mnav[symbol] = current_mnav

if __name__ == "__main__":
    if "--send-test-notification" in sys.argv:
        send_test_notification()
    elif "--test-now" in sys.argv:
        run_check_once()
    else:
        print("🚀 MNav monitor started. Waiting for next interval...")
        while True:
            schedule.run_pending()
            time.sleep(60) 
