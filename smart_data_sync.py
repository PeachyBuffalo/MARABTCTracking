#!/usr/bin/env python3
"""
Smart Data Synchronization
Automatically syncs historical data from reliable sources and updates the backtest system.
"""

import requests
import json
import os
import time
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd

class SmartDataSync:
    def __init__(self):
        self.config_file = "data_sync_config.json"
        self.load_config()
        
    def load_config(self):
        """Load or create configuration file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                'last_update': {},
                'auto_sync_enabled': True,
                'sync_interval_hours': 24,
                'data_sources': {
                    'shares_outstanding': ['yahoo_finance', 'alpha_vantage'],
                    'btc_holdings': ['bitcoin_treasuries', 'company_filings']
                }
            }
            self.save_config()
    
    def save_config(self):
        """Save configuration file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def should_update(self, symbol):
        """Check if data should be updated based on last update time"""
        if not self.config['auto_sync_enabled']:
            return False
            
        last_update = self.config['last_update'].get(symbol, '1970-01-01')
        last_update_dt = datetime.fromisoformat(last_update)
        hours_since_update = (datetime.now() - last_update_dt).total_seconds() / 3600
        
        return hours_since_update >= self.config['sync_interval_hours']
    
    def sync_shares_outstanding(self, symbol):
        """Sync shares outstanding data from multiple sources"""
        print(f"🔄 Syncing shares outstanding for {symbol}...")
        
        # Try Yahoo Finance first (most reliable)
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if 'sharesOutstanding' in info and info['sharesOutstanding']:
                shares = info['sharesOutstanding']
                print(f"✅ Yahoo Finance: {shares:,} shares")
                
                # Check if this is different from our current data
                current_data = self.get_current_shares_data(symbol)
                if current_data != shares:
                    print(f"📊 Shares changed: {current_data:,} → {shares:,}")
                    self.update_shares_data(symbol, shares)
                    return True
                else:
                    print("📊 Shares unchanged")
                    return False
        except Exception as e:
            print(f"❌ Yahoo Finance error: {e}")
        
        return False
    
    def sync_btc_holdings(self, symbol):
        """Sync BTC holdings data from Bitcoin Treasuries"""
        print(f"🔄 Syncing BTC holdings for {symbol}...")
        
        try:
            # Fetch from Bitcoin Treasuries
            url = "https://bitcointreasuries.net/"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                # Parse the HTML to find company data
                btc_data = self.parse_bitcoin_treasuries(response.text, symbol)
                if btc_data:
                    current_btc = self.get_current_btc_data(symbol)
                    if current_btc != btc_data:
                        print(f"₿ BTC changed: {current_btc:,} → {btc_data:,}")
                        self.update_btc_data(symbol, btc_data)
                        return True
                    else:
                        print("₿ BTC unchanged")
                        return False
        except Exception as e:
            print(f"❌ Bitcoin Treasuries error: {e}")
        
        return False
    
    def parse_bitcoin_treasuries(self, html_content, symbol):
        """Parse Bitcoin Treasuries HTML for company BTC holdings"""
        try:
            # This is a simplified parser - you'd need to customize based on the actual HTML structure
            # Look for the company in the HTML table
            lines = html_content.split('\n')
            for line in lines:
                if symbol.upper() in line.upper() and 'BTC' in line:
                    # Extract BTC amount from the line
                    # This is a placeholder - actual parsing would depend on HTML structure
                    import re
                    btc_match = re.search(r'(\d{1,3}(?:,\d{3})*)', line)
                    if btc_match:
                        btc_str = btc_match.group(1).replace(',', '')
                        return int(btc_str)
        except Exception as e:
            print(f"❌ HTML parsing error: {e}")
        
        return None
    
    def get_current_shares_data(self, symbol):
        """Get current shares outstanding from our data"""
        # This would read from the current data in mnav_backtest.py
        # For now, return a placeholder
        default_shares = {
            'MSTR': 307000000,
            'MARA': 351928000,
            'RIOT': 351928000,
            'CLSK': 351928000,
            'TSLA': 351928000,
            'HUT': 351928000,
            'COIN': 351928000,
            'SQ': 351928000,
            'SMLR': 14800000,
            'HIVE': 351928000,
            'CIFR': 351928000
        }
        return default_shares.get(symbol, 351928000)
    
    def get_current_btc_data(self, symbol):
        """Get current BTC holdings from our data"""
        # This would read from the current data in mnav_backtest.py
        default_btc = {
            'MSTR': 638460,
            'MARA': 50000,
            'RIOT': 19225,
            'CLSK': 12608,
            'TSLA': 11509,
            'HUT': 10273,
            'COIN': 9267,
            'SQ': 8584,
            'SMLR': 5021,
            'HIVE': 2201,
            'CIFR': 1063
        }
        return default_btc.get(symbol, 50000)
    
    def update_shares_data(self, symbol, new_shares):
        """Update shares outstanding data"""
        print(f"📝 Updating shares data for {symbol}...")
        
        # Generate the updated code
        code = self.generate_shares_update_code(symbol, new_shares)
        
        # Save to a file for manual review
        filename = f"shares_update_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        with open(filename, 'w') as f:
            f.write(code)
        
        print(f"💾 Update code saved to {filename}")
        print("📋 Review the file and manually update mnav_backtest.py if needed")
        
        # Update last sync time
        self.config['last_update'][symbol] = datetime.now().isoformat()
        self.save_config()
    
    def update_btc_data(self, symbol, new_btc):
        """Update BTC holdings data"""
        print(f"📝 Updating BTC data for {symbol}...")
        
        # Generate the updated code
        code = self.generate_btc_update_code(symbol, new_btc)
        
        # Save to a file for manual review
        filename = f"btc_update_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        with open(filename, 'w') as f:
            f.write(code)
        
        print(f"💾 Update code saved to {filename}")
        print("📋 Review the file and manually update mnav_backtest.py if needed")
        
        # Update last sync time
        self.config['last_update'][symbol] = datetime.now().isoformat()
        self.save_config()
    
    def generate_shares_update_code(self, symbol, new_shares):
        """Generate Python code to update shares outstanding"""
        code = f"""# Auto-generated shares outstanding update for {symbol}
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# New shares outstanding: {new_shares:,}

# Add this to the shares_history dictionary in mnav_backtest.py:
'{symbol}': [
    {{'date': '{datetime.now().strftime('%Y-%m-%d')}', 'shares': {new_shares}}},
],

# Instructions:
# 1. Open mnav_backtest.py
# 2. Find the shares_history dictionary
# 3. Add or update the entry for {symbol}
# 4. Save the file
"""
        return code
    
    def generate_btc_update_code(self, symbol, new_btc):
        """Generate Python code to update BTC holdings"""
        code = f"""# Auto-generated BTC holdings update for {symbol}
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# New BTC holdings: {new_btc:,}

# Add this to the btc_history dictionary in mnav_backtest.py:
'{symbol}': [
    {{'date': '{datetime.now().strftime('%Y-%m-%d')}', 'btc_owned': {new_btc}}},
],

# Instructions:
# 1. Open mnav_backtest.py
# 2. Find the btc_history dictionary
# 3. Add or update the entry for {symbol}
# 4. Save the file
"""
        return code
    
    def auto_sync_company(self, symbol):
        """Automatically sync all data for a company"""
        print(f"🚀 Auto-syncing {symbol}...")
        
        if not self.should_update(symbol):
            print(f"⏰ {symbol} was updated recently, skipping...")
            return
        
        shares_updated = self.sync_shares_outstanding(symbol)
        btc_updated = self.sync_btc_holdings(symbol)
        
        if shares_updated or btc_updated:
            print(f"✅ {symbol} data updated successfully")
        else:
            print(f"📊 {symbol} data unchanged")
    
    def auto_sync_all(self):
        """Auto-sync all tracked companies"""
        companies = ['MSTR', 'MARA', 'RIOT', 'CLSK', 'TSLA', 'HUT', 'COIN', 'SQ', 'SMLR', 'HIVE', 'CIFR']
        
        print("🤖 Starting auto-sync for all companies...")
        
        for symbol in companies:
            print(f"\n{'='*40}")
            self.auto_sync_company(symbol)
            time.sleep(1)  # Rate limiting
        
        print(f"\n✅ Auto-sync complete!")
    
    def setup_cron_job(self):
        """Set up automatic cron job for daily sync"""
        print("⏰ Setting up automatic sync...")
        
        # Create a simple script for cron
        cron_script = """#!/bin/bash
cd /Users/peachybuffalo/GitHubProjects/MARABTCTracking
python smart_data_sync.py --auto-sync
"""
        
        with open("auto_sync.sh", "w") as f:
            f.write(cron_script)
        
        os.chmod("auto_sync.sh", 0o755)
        
        print("📅 Cron setup instructions:")
        print("1. Open terminal and run: crontab -e")
        print("2. Add this line for daily sync at 9 AM:")
        print("   0 9 * * * /Users/peachybuffalo/GitHubProjects/MARABTCTracking/auto_sync.sh")
        print("3. Save and exit")
        print("\n💡 The script will run automatically every day at 9 AM")

def main():
    sync = SmartDataSync()
    
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--auto-sync':
            sync.auto_sync_all()
        elif sys.argv[1] == '--setup-cron':
            sync.setup_cron_job()
        else:
            symbol = sys.argv[1].upper()
            sync.auto_sync_company(symbol)
    else:
        print("Smart Data Synchronization")
        print("=========================")
        print()
        print("Usage:")
        print("  python smart_data_sync.py SYMBOL      # Sync specific company")
        print("  python smart_data_sync.py --auto-sync # Sync all companies")
        print("  python smart_data_sync.py --setup-cron # Set up automatic sync")
        print()
        print("Configuration:")
        print(f"  Auto-sync enabled: {sync.config['auto_sync_enabled']}")
        print(f"  Sync interval: {sync.config['sync_interval_hours']} hours")
        print(f"  Config file: {sync.config_file}")

if __name__ == "__main__":
    main()

