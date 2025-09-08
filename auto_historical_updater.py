#!/usr/bin/env python3
"""
Automated Historical Data Updater
Automatically fetches and updates historical shares outstanding and BTC holdings data.
"""

import requests
import pandas as pd
import json
import os
import time
from datetime import datetime, timedelta
import yfinance as yf
from bs4 import BeautifulSoup
import re

class AutoHistoricalUpdater:
    def __init__(self):
        self.data_dir = "historical_data"
        self.ensure_data_dir()
        
    def ensure_data_dir(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def fetch_shares_outstanding_history(self, symbol):
        """Fetch historical shares outstanding from multiple sources"""
        print(f"🔄 Fetching shares outstanding history for {symbol}...")
        
        # Try multiple sources
        sources = [
            self.fetch_from_sec_filings,
            self.fetch_from_yahoo_finance,
            self.fetch_from_alpha_vantage,
            self.fetch_from_quandl
        ]
        
        for source_func in sources:
            try:
                data = source_func(symbol)
                if data and len(data) > 0:
                    print(f"✅ Found {len(data)} data points from {source_func.__name__}")
                    return data
            except Exception as e:
                print(f"⚠️ {source_func.__name__} failed: {e}")
                continue
        
        print(f"❌ No shares outstanding history found for {symbol}")
        return []
    
    def fetch_from_sec_filings(self, symbol):
        """Fetch shares outstanding from SEC filings"""
        try:
            # SEC EDGAR API endpoint
            url = f"https://data.sec.gov/submissions/CIK{symbol}.json"
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; MNavBot/1.0)',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Parse SEC filing data for shares outstanding
                # This is a simplified version - would need more complex parsing
                return self.parse_sec_data(data, symbol)
        except Exception as e:
            print(f"SEC API error: {e}")
        
        return []
    
    def fetch_from_yahoo_finance(self, symbol):
        """Fetch shares outstanding from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if 'sharesOutstanding' in info and info['sharesOutstanding']:
                current_shares = info['sharesOutstanding']
                
                # Get historical data to estimate past shares
                hist = ticker.history(period="2y")
                if not hist.empty:
                    # Estimate historical shares based on market cap and price
                    # This is an approximation
                    return self.estimate_historical_shares(hist, current_shares, symbol)
        except Exception as e:
            print(f"Yahoo Finance error: {e}")
        
        return []
    
    def fetch_from_alpha_vantage(self, symbol):
        """Fetch shares outstanding from Alpha Vantage"""
        try:
            # You would need an Alpha Vantage API key
            api_key = os.getenv('ALPHAVANTAGE_API_KEY')
            if not api_key:
                print("⚠️ Alpha Vantage API key not found")
                return []
            
            url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'SharesOutstanding' in data:
                    shares = int(data['SharesOutstanding'])
                    return [{'date': datetime.now().strftime('%Y-%m-%d'), 'shares': shares}]
        except Exception as e:
            print(f"Alpha Vantage error: {e}")
        
        return []
    
    def fetch_from_quandl(self, symbol):
        """Fetch shares outstanding from Quandl (now part of Nasdaq Data Link)"""
        try:
            # You would need a Quandl API key
            api_key = os.getenv('QUANDL_API_KEY')
            if not api_key:
                print("⚠️ Quandl API key not found")
                return []
            
            # Quandl has historical shares outstanding data
            url = f"https://www.quandl.com/api/v3/datasets/SF0/{symbol}_SHARESOUTSTANDING.json?api_key={api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self.parse_quandl_data(data)
        except Exception as e:
            print(f"Quandl error: {e}")
        
        return []
    
    def fetch_btc_holdings_history(self, symbol):
        """Fetch historical BTC holdings from multiple sources"""
        print(f"🔄 Fetching BTC holdings history for {symbol}...")
        
        # Try multiple sources
        sources = [
            self.fetch_from_bitcoin_treasuries,
            self.fetch_from_company_filings,
            self.fetch_from_news_sources
        ]
        
        for source_func in sources:
            try:
                data = source_func(symbol)
                if data and len(data) > 0:
                    print(f"✅ Found {len(data)} BTC data points from {source_func.__name__}")
                    return data
            except Exception as e:
                print(f"⚠️ {source_func.__name__} failed: {e}")
                continue
        
        print(f"❌ No BTC holdings history found for {symbol}")
        return []
    
    def fetch_from_bitcoin_treasuries(self, symbol):
        """Fetch BTC holdings from Bitcoin Treasuries website"""
        try:
            url = "https://bitcointreasuries.net/"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for the company data
                # This would need to be customized based on the website structure
                company_data = self.parse_bitcoin_treasuries(soup, symbol)
                return company_data
        except Exception as e:
            print(f"Bitcoin Treasuries error: {e}")
        
        return []
    
    def fetch_from_company_filings(self, symbol):
        """Fetch BTC holdings from company SEC filings"""
        try:
            # Search for BTC-related filings
            # This would require parsing SEC filings for BTC mentions
            return self.search_sec_filings_for_btc(symbol)
        except Exception as e:
            print(f"SEC filings error: {e}")
        
        return []
    
    def fetch_from_news_sources(self, symbol):
        """Fetch BTC holdings from news sources and press releases"""
        try:
            # Search news APIs for BTC acquisition announcements
            return self.search_news_for_btc(symbol)
        except Exception as e:
            print(f"News search error: {e}")
        
        return []
    
    def auto_update_company(self, symbol):
        """Automatically update all historical data for a company"""
        print(f"🚀 Starting automated update for {symbol}...")
        
        # Fetch shares outstanding history
        shares_data = self.fetch_shares_outstanding_history(symbol)
        
        # Fetch BTC holdings history
        btc_data = self.fetch_btc_holdings_history(symbol)
        
        # Save the data
        if shares_data:
            self.save_shares_data(symbol, shares_data)
        
        if btc_data:
            self.save_btc_data(symbol, btc_data)
        
        # Generate updated code for mnav_backtest.py
        self.generate_updated_code(symbol, shares_data, btc_data)
        
        print(f"✅ Automated update complete for {symbol}")
    
    def save_shares_data(self, symbol, data):
        """Save shares outstanding data to file"""
        filename = os.path.join(self.data_dir, f"shares_{symbol.lower()}.json")
        with open(filename, 'w') as f:
            json.dump({
                'symbol': symbol,
                'data': data,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
        print(f"💾 Saved shares data to {filename}")
    
    def save_btc_data(self, symbol, data):
        """Save BTC holdings data to file"""
        filename = os.path.join(self.data_dir, f"btc_{symbol.lower()}.json")
        with open(filename, 'w') as f:
            json.dump({
                'symbol': symbol,
                'data': data,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
        print(f"💾 Saved BTC data to {filename}")
    
    def generate_updated_code(self, symbol, shares_data, btc_data):
        """Generate updated Python code for mnav_backtest.py"""
        print(f"📝 Generating updated code for {symbol}...")
        
        # Generate shares history code
        if shares_data:
            shares_code = self.generate_shares_code(symbol, shares_data)
            print("📊 Shares outstanding code:")
            print(shares_code)
        
        # Generate BTC history code
        if btc_data:
            btc_code = self.generate_btc_code(symbol, btc_data)
            print("₿ BTC holdings code:")
            print(btc_code)
    
    def generate_shares_code(self, symbol, data):
        """Generate Python code for shares history"""
        code = f"'{symbol}': [\n"
        for item in data:
            code += f"    {{'date': '{item['date']}', 'shares': {item['shares']}}},\n"
        code += "],"
        return code
    
    def generate_btc_code(self, symbol, data):
        """Generate Python code for BTC history"""
        code = f"'{symbol}': [\n"
        for item in data:
            code += f"    {{'date': '{item['date']}', 'btc_owned': {item['btc_owned']}}},\n"
        code += "],"
        return code
    
    def schedule_auto_updates(self):
        """Set up scheduled automatic updates"""
        print("⏰ Setting up scheduled updates...")
        
        # Create a cron job or scheduled task
        # This would depend on your operating system
        
        # For Linux/Mac (cron):
        cron_command = """
# Add to crontab (crontab -e):
# Update historical data weekly
0 9 * * 1 cd /path/to/MARABTCTracking && python auto_historical_updater.py --update-all
        """
        
        # For Windows (Task Scheduler):
        windows_command = """
# Create scheduled task in Windows Task Scheduler:
# Program: python
# Arguments: auto_historical_updater.py --update-all
# Schedule: Weekly on Monday at 9:00 AM
        """
        
        print("📅 Scheduled update commands:")
        print(cron_command)
        print(windows_command)
    
    def update_all_companies(self):
        """Update all tracked companies"""
        companies = ['MSTR', 'MARA', 'RIOT', 'CLSK', 'TSLA', 'HUT', 'COIN', 'SQ', 'SMLR', 'HIVE', 'CIFR']
        
        for symbol in companies:
            print(f"\n{'='*50}")
            self.auto_update_company(symbol)
            time.sleep(2)  # Rate limiting
    
    def parse_sec_data(self, data, symbol):
        """Parse SEC filing data for shares outstanding"""
        # This would need to be implemented based on SEC data structure
        # For now, return empty list
        return []
    
    def estimate_historical_shares(self, hist, current_shares, symbol):
        """Estimate historical shares based on market cap and price"""
        # This is a simplified estimation
        # In reality, you'd need more sophisticated analysis
        data = []
        for date, row in hist.iterrows():
            # Estimate shares based on price and market cap
            # This is just a placeholder
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'shares': current_shares  # Simplified - would need actual calculation
            })
        return data
    
    def parse_quandl_data(self, data):
        """Parse Quandl data for shares outstanding"""
        # This would need to be implemented based on Quandl data structure
        return []
    
    def parse_bitcoin_treasuries(self, soup, symbol):
        """Parse Bitcoin Treasuries website for company data"""
        # This would need to be implemented based on website structure
        return []
    
    def search_sec_filings_for_btc(self, symbol):
        """Search SEC filings for BTC-related information"""
        # This would need to be implemented
        return []
    
    def search_news_for_btc(self, symbol):
        """Search news sources for BTC acquisition announcements"""
        # This would need to be implemented
        return []

def main():
    updater = AutoHistoricalUpdater()
    
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--update-all':
            updater.update_all_companies()
        elif sys.argv[1] == '--schedule':
            updater.schedule_auto_updates()
        else:
            symbol = sys.argv[1].upper()
            updater.auto_update_company(symbol)
    else:
        print("Usage:")
        print("  python auto_historical_updater.py SYMBOL    # Update specific company")
        print("  python auto_historical_updater.py --update-all  # Update all companies")
        print("  python auto_historical_updater.py --schedule    # Set up scheduled updates")

if __name__ == "__main__":
    main()

