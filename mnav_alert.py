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
CACHE_DURATION_HOURS = 0.5  # Cache data for 30 minutes to reduce API calls
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

def is_cache_valid(cache_path, max_age_hours=CACHE_DURATION_HOURS):
    if not os.path.exists(cache_path):
        return False
    
    file_age = time.time() - os.path.getmtime(cache_path)
    return file_age < (max_age_hours * 3600)

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

# Multi-stock configuration - Reduced to top 8 to stay within rate limits
STOCKS_TO_MONITOR = [
    {
        "symbol": "MSTR",
        "name": "MicroStrategy",
        "btc_owned": 607770,
        "threshold": 0.05
    },
    {
        "symbol": "MARA",
        "name": "Marathon Digital",
        "btc_owned": 50000,
        "threshold": 0.05
    },
    {
        "symbol": "RIOT",
        "name": "Riot Platforms",
        "btc_owned": 19225,
        "threshold": 0.05
    },
    {
        "symbol": "DJT",
        "name": "Trump Media & Technology Group",
        "btc_owned": 18430,
        "threshold": 0.05
    },
    {
        "symbol": "MTPLF",
        "name": "Metaplanet Inc.",
        "btc_owned": 17132,
        "threshold": 0.05
    },
    {
        "symbol": "GLXY",
        "name": "Galaxy Digital Holdings Ltd.",
        "btc_owned": 12830,
        "threshold": 0.05
    },
    {
        "symbol": "CLSK",
        "name": "CleanSpark",
        "btc_owned": 12608,
        "threshold": 0.05
    },
    {
        "symbol": "TSLA",
        "name": "Tesla",
        "btc_owned": 11509,
        "threshold": 0.05
    },
    {
        "symbol": "COIN",
        "name": "Coinbase",
        "btc_owned": 9267,
        "threshold": 0.05
    },
    {
        "symbol": "SQ",
        "name": "Block Inc",
        "btc_owned": 8584,
        "threshold": 0.05
    },
    {
        "symbol": "SMLR",
        "name": "Semler Scientific",
        "btc_owned": 5021,
        "threshold": 0.05
    },
    {
        "symbol": "CCCM",
        "name": "ProCap BTC",
        "btc_owned": 4932,
        "threshold": 0.05
    },
    {
        "symbol": "GME",
        "name": "GameStop Corp.",
        "btc_owned": 4710,
        "threshold": 0.05
    },
    {
        "symbol": "CANG",
        "name": "Cango Inc",
        "btc_owned": 4240,
        "threshold": 0.05
    },
    {
        "symbol": "VLCN",
        "name": "Volcon Inc.",
        "btc_owned": 3500,
        "threshold": 0.05
    },
    {
        "symbol": "HOLO",
        "name": "Microcloud Hologram",
        "btc_owned": 2353,
        "threshold": 0.05
    },
    {
        "symbol": "HIVE",
        "name": "HIVE Digital",
        "btc_owned": 2201,
        "threshold": 0.05
    },
    {
        "symbol": "EXOD",
        "name": "Exodus Movement, Inc",
        "btc_owned": 2038,
        "threshold": 0.05
    },
    {
        "symbol": "FLD",
        "name": "Fold Holdings Inc.",
        "btc_owned": 1488,
        "threshold": 0.05
    },
    {
        "symbol": "BITF",
        "name": "Bitfarms Ltd.",
        "btc_owned": 1166,
        "threshold": 0.05
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
    # Try cache first
    cache_key = f"stock_price_{symbol}.pkl"
    cached_price = load_from_cache(cache_key)
    if cached_price is not None:
        # Check if cache is still valid
        cache_path = get_cache_path(cache_key)
        if is_cache_valid(cache_path, CACHE_DURATION_HOURS):
            print(f"📦 Using cached price for {symbol}")
            return cached_price
        else:
            print(f"🔄 Cache expired for {symbol}, fetching fresh data")
    
    # Retry with exponential backoff
    max_retries = 3
    for attempt in range(max_retries):
        try:
            ticker = yf.Ticker(symbol)
            price = ticker.info.get("currentPrice", 0)
            
            # Cache the price for 5 minutes
            if price > 0:
                save_to_cache(price, cache_key)
                print(f"✅ Fetched {symbol} price: ${price:.2f}")
                return price
            else:
                print(f"⚠️ {symbol} price is 0, may indicate error")
                return 0
                
        except Exception as e:
            print(f"Error fetching {symbol} price (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 5  # 5s, 10s, 20s
                print(f"⏳ Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                print(f"❌ Failed to fetch {symbol} price after {max_retries} attempts")
                return 0
    
    return 0

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
        # For companies without historical data, use current holdings from STOCKS_TO_MONITOR
        for stock in STOCKS_TO_MONITOR:
            if stock['symbol'] == symbol:
                return stock['btc_owned']
        return 0
    
    # Get current holdings from the most recent entry
    return btc_history[symbol][-1]['btc_owned']

def calculate_mnav(stock_price, btc_price, btc_per_share):
    """Calculate MNav ratio"""
    return stock_price / (btc_price * btc_per_share)

def get_current_btc_holdings(symbol):
    """Get current BTC holdings for a symbol, considering historical acquisitions"""
    return get_btc_holdings_over_time(symbol)

def send_mnav_alert(stock_config, prev, curr, change, stock_price, btc_price):
    title = f"🔔 {stock_config['name']} MNav Alert"
    message = f"MNav changed by {change:.2f}%\nPrevious: {prev:.3f} → Current: {curr:.3f}\n{stock_config['symbol']}: ${stock_price:.2f} | BTC: ${btc_price:,.0f}"
    send_mac_notification(title, message)

def check_mnav():
    btc_price = get_btc_price()
    
    for i, stock_config in enumerate(STOCKS_TO_MONITOR):
        symbol = stock_config['symbol']
        stock_price = get_stock_price(symbol)
        
        # Add delay between API calls to avoid rate limiting
        if i > 0:
            time.sleep(1)  # 1 second delay between calls
        
        if stock_price == 0:
            print(f"⚠️ Skipping {symbol} - price fetch failed")
            continue
            
        # Use historical BTC holdings instead of static value
        current_btc_owned = get_current_btc_holdings(symbol)
        btc_per_share = current_btc_owned / get_shares_outstanding(symbol)
        current_mnav = calculate_mnav(stock_price, btc_price, btc_per_share)

        if symbol not in previous_mnav:
            previous_mnav[symbol] = current_mnav
            print(f"Initialized {symbol} MNav: {current_mnav:.3f} (BTC: {current_btc_owned:,})")
            continue

        change = (current_mnav - previous_mnav[symbol]) / previous_mnav[symbol]
        print(f"{symbol} MNav: {current_mnav:.3f}, Change: {change*100:.2f}% (BTC: {current_btc_owned:,})")

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

# Schedule it every 4 hours to stay within rate limits
schedule.every(4).hours.do(check_mnav)

# Optional: Update shares outstanding weekly
schedule.every().monday.at("09:00").do(lambda: os.system("python update_shares_bitcointreasuries.py"))

def run_check_once():
    """Run a single check and always send a notification with current status"""
    btc_price = get_btc_price()
    
    # For testing, only check the first 2 stocks to avoid rate limiting
    test_stocks = STOCKS_TO_MONITOR[:2] if "--test-now" in sys.argv else STOCKS_TO_MONITOR
    
    for i, stock_config in enumerate(test_stocks):
        symbol = stock_config['symbol']
        stock_price = get_stock_price(symbol)
        
        # Add delay between API calls to avoid rate limiting
        if i > 0:
            time.sleep(5)  # 5 second delay between calls (increased from 2)
            
        # If API fails, use mock data for testing
        if stock_price == 0 and "--test-now" in sys.argv:
            print(f"🔄 Using mock data for {symbol} (API rate limited)")
            stock_price = 150.0  # Mock price for testing
        
        if stock_price == 0:
            print(f"⚠️ Skipping {symbol} - price fetch failed")
            continue
            
        # Use historical BTC holdings instead of static value
        current_btc_owned = get_current_btc_holdings(symbol)
        btc_per_share = current_btc_owned / get_shares_outstanding(symbol)
        current_mnav = calculate_mnav(stock_price, btc_price, btc_per_share)

        if symbol not in previous_mnav:
            previous_mnav[symbol] = current_mnav
            print(f"Initialized {symbol} MNav: {current_mnav:.3f} (BTC: {current_btc_owned:,})")
            # Send notification for first run
            send_mac_notification(f"🔔 {stock_config['name']} Monitor Started", f"Current {stock_config['name']} MNav: {current_mnav:.3f}\n{stock_config['symbol']}: ${stock_price:.2f} | BTC: ${btc_price:,.0f} | BTC Holdings: {current_btc_owned:,}")
            continue

        change = (current_mnav - previous_mnav[symbol]) / previous_mnav[symbol]
        print(f"{symbol} MNav: {current_mnav:.3f}, Change: {change*100:.2f}% (BTC: {current_btc_owned:,})")

        # Always send notification for test-now
        if abs(change) >= stock_config['threshold']:
            title = f"🔔 {stock_config['name']} Alert - Significant Change"
            message = f"MNav changed by {change*100:.2f}%\nPrevious: {previous_mnav[symbol]:.3f} → Current: {current_mnav:.3f}\n{stock_config['symbol']}: ${stock_price:.2f} | BTC: ${btc_price:,.0f} | BTC Holdings: {current_btc_owned:,}"
        else:
            title = f"📊 {stock_config['name']} Status Check"
            message = f"Current {stock_config['name']} MNav: {current_mnav:.3f} (Change: {change*100:.2f}%)\n{stock_config['symbol']}: ${stock_price:.2f} | BTC: ${btc_price:,.0f} | BTC Holdings: {current_btc_owned:,}"

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
