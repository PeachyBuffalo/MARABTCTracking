import requests
import yfinance as yf
import smtplib
from email.message import EmailMessage
import schedule
import time
import os
import pickle
from dotenv import load_dotenv

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
        except:
            pass
    return None

def get_shares_outstanding():
    cache_key = "shares_outstanding.pkl"
    cached = load_from_cache(cache_key)
    if cached is not None:
        return cached
    try:
        ticker = yf.Ticker("MARA")
        shares = ticker.info.get("sharesOutstanding", 351928000)
        save_to_cache(shares, cache_key)
        return shares
    except Exception as e:
        print(f"Error fetching shares outstanding: {e}")
        return 351928000

# Configuration
THRESHOLD = 0.05  # 5% change triggers alert
EMAIL_TO = os.environ.get("EMAIL_TO", "your_email@example.com")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "alertsender@example.com")
EMAIL_PASS = os.environ.get("EMAIL_PASS", "your_app_password")

# Global variable to store previous MNav
previous_mnav = None

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

def get_mara_price():
    try:
        ticker = yf.Ticker("MARA")
        mara_price = ticker.info.get("currentPrice", 0)
        return mara_price
    except Exception as e:
        print(f"Error fetching MARA price: {e}")
        return 0

def calculate_mnav(mara_price, btc_price):
    btc_per_share = MARA_BTC_OWNED / get_shares_outstanding()
    return mara_price / (btc_price * btc_per_share)

def send_email_alert(prev, curr, change, mara_price, btc_price):
    msg = EmailMessage()
    msg["Subject"] = "🔔 MNav Drastic Change Alert"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.set_content(f"""
    ALERT: MNav changed by {change:.2f}%\n\n    Previous MNav: {prev:.3f}\n    Current MNav: {curr:.3f}\n\n    MARA Price: ${mara_price:.2f}\n    BTC Price: ${btc_price:,.2f}\n    """)
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_FROM, EMAIL_PASS)
        smtp.send_message(msg)

def check_mnav():
    global previous_mnav
    btc_price = get_btc_price()
    mara_price = get_mara_price()
    current_mnav = calculate_mnav(mara_price, btc_price)

    if previous_mnav is None:
        previous_mnav = current_mnav
        print("Initialized MNav:", round(current_mnav, 3))
        return

    change = (current_mnav - previous_mnav) / previous_mnav
    print(f"Current MNav: {current_mnav:.3f}, Change: {change*100:.2f}%")

    if abs(change) >= THRESHOLD:
        send_email_alert(previous_mnav, current_mnav, change * 100, mara_price, btc_price)

    previous_mnav = current_mnav

# Schedule it every hour
schedule.every(1).hours.do(check_mnav)

print("🚀 MNav monitor started. Waiting for next interval...")
while True:
    schedule.run_pending()
    time.sleep(60) 