import requests
import yfinance as yf

def get_btc_price():
    try:
        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd')
        return float(response.json()['bitcoin']['usd'])
    except:
        return 118000  # Fallback price

def get_mara_info():
    try:
        ticker = yf.Ticker('MARA')
        info = ticker.info
        return {
            'market_cap': info.get('marketCap', 0),
            'shares_outstanding': info.get('sharesOutstanding', 0),
            'current_price': info.get('regularMarketPrice', 0)
        }
    except:
        return {
            'market_cap': 7008576000,
            'shares_outstanding': 351928000,
            'current_price': 20.0
        }

def calculate_btc_per_share(btc_holdings, shares_outstanding):
    return btc_holdings / shares_outstanding

def main():
    print("=== MARA BTC Holdings Analysis ===\n")
    
    # Get current data
    btc_price = get_btc_price()
    mara_info = get_mara_info()
    
    print(f"Current BTC Price: ${btc_price:,.2f}")
    print(f"MARA Market Cap: ${mara_info['market_cap']:,.0f}")
    print(f"MARA Shares Outstanding: {mara_info['shares_outstanding']:,.0f}")
    print(f"MARA Current Price: ${mara_info['current_price']:.2f}")
    print()
    
    # MARA's actual BTC holdings (as of latest reports)
    # Note: This should be updated based on MARA's latest quarterly reports
    actual_btc_holdings = 50000  # Update this based on latest MARA reports
    
    # Calculate BTC_PER_SHARE for different scenarios
    scenarios = [
        (f"{actual_btc_holdings:,} BTC (Current holdings)", actual_btc_holdings),
        ("50,000 BTC (Original assumption)", 50000),
        ("25,000 BTC", 25000),
        ("10,000 BTC", 10000),
        ("5,000 BTC", 5000),
        ("1,000 BTC", 1000)
    ]
    
    print("BTC_PER_SHARE ratios:")
    print("-" * 50)
    for scenario, btc_holdings in scenarios:
        btc_per_share = calculate_btc_per_share(btc_holdings, mara_info['shares_outstanding'])
        print(f"{scenario}: {btc_per_share:.8f}")
    
    print()
    print("Current BTC_PER_SHARE in code: 0.00014243")
    print()
    
    # Calculate what BTC holdings would give us the current ratio
    current_ratio = 0.00014243
    implied_btc_holdings = current_ratio * mara_info['shares_outstanding']
    print(f"Implied BTC holdings for current ratio: {implied_btc_holdings:,.0f} BTC")
    
    # Check if this makes sense
    implied_btc_value = implied_btc_holdings * btc_price
    print(f"Implied BTC value: ${implied_btc_value:,.0f}")
    print(f"Percentage of market cap: {(implied_btc_value / mara_info['market_cap']) * 100:.1f}%")
    
    print()
    print("=== RECOMMENDATION ===")
    print(f"Use BTC_PER_SHARE = {calculate_btc_per_share(actual_btc_holdings, mara_info['shares_outstanding']):.8f}")
    print("(Update actual_btc_holdings variable based on MARA's latest quarterly reports)")

if __name__ == "__main__":
    main() 