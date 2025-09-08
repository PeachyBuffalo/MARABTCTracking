#!/usr/bin/env python3
"""
Historical Data Update Utility
Helps update shares outstanding and BTC holdings history for accurate MNav calculations.
"""

import json
import pandas as pd
from datetime import datetime
import os

def update_shares_history():
    """Update shares outstanding history for a company"""
    print("=== Shares Outstanding History Updater ===\n")
    
    symbol = input("Enter stock symbol (e.g., SMLR, MSTR): ").upper()
    company_name = input("Enter company name: ")
    
    print(f"\nEnter shares outstanding changes for {symbol} ({company_name})")
    print("Enter 'done' when finished, or 'cancel' to exit\n")
    
    shares_history = []
    
    while True:
        date_input = input("Date (YYYY-MM-DD): ")
        if date_input.lower() == 'done':
            break
        elif date_input.lower() == 'cancel':
            return
        
        try:
            # Validate date format
            datetime.strptime(date_input, '%Y-%m-%d')
        except ValueError:
            print("❌ Invalid date format. Use YYYY-MM-DD")
            continue
        
        try:
            shares_amount = int(input("Shares outstanding: "))
        except ValueError:
            print("❌ Invalid shares amount. Enter a number.")
            continue
        
        reason = input("Reason for change (e.g., 'stock split', 'offering', 'buyback'): ")
        
        shares_history.append({
            'date': date_input,
            'shares': shares_amount,
            'reason': reason
        })
        
        print(f"✅ Added: {date_input} - {shares_amount:,} shares ({reason})\n")
    
    if not shares_history:
        print("❌ No changes entered.")
        return
    
    # Sort by date
    shares_history.sort(key=lambda x: x['date'])
    
    print(f"\n=== Summary for {symbol} ===")
    for i, change in enumerate(shares_history):
        print(f"{i+1}. {change['date']}: {change['shares']:,} shares ({change['reason']})")
    
    # Save to JSON file
    filename = f"shares_history_{symbol.lower()}.json"
    with open(filename, 'w') as f:
        json.dump({
            'symbol': symbol,
            'company_name': company_name,
            'changes': shares_history
        }, f, indent=2)
    
    print(f"\n✅ Saved to {filename}")
    
    # Generate Python code for mnav_backtest.py
    print(f"\n=== Python Code for mnav_backtest.py ===")
    print(f"'{symbol}': [")
    for change in shares_history:
        print(f"    {{'date': '{change['date']}', 'shares': {change['shares']}}},")
    print("],")

def update_btc_history():
    """Update BTC holdings history for a company"""
    print("=== BTC Holdings History Updater ===\n")
    
    symbol = input("Enter stock symbol (e.g., SMLR, MSTR): ").upper()
    company_name = input("Enter company name: ")
    
    print(f"\nEnter BTC acquisition dates and amounts for {symbol} ({company_name})")
    print("Enter 'done' when finished, or 'cancel' to exit\n")
    
    acquisitions = []
    
    while True:
        date_input = input("Date (YYYY-MM-DD): ")
        if date_input.lower() == 'done':
            break
        elif date_input.lower() == 'cancel':
            return
        
        try:
            # Validate date format
            datetime.strptime(date_input, '%Y-%m-%d')
        except ValueError:
            print("❌ Invalid date format. Use YYYY-MM-DD")
            continue
        
        try:
            btc_amount = int(input("BTC amount: "))
        except ValueError:
            print("❌ Invalid BTC amount. Enter a number.")
            continue
        
        reason = input("Reason for change (e.g., 'purchase', 'mining', 'sale'): ")
        
        acquisitions.append({
            'date': date_input,
            'btc_owned': btc_amount,
            'reason': reason
        })
        
        print(f"✅ Added: {date_input} - {btc_amount:,} BTC ({reason})\n")
    
    if not acquisitions:
        print("❌ No acquisitions entered.")
        return
    
    # Sort by date
    acquisitions.sort(key=lambda x: x['date'])
    
    print(f"\n=== Summary for {symbol} ===")
    for i, acq in enumerate(acquisitions):
        print(f"{i+1}. {acq['date']}: {acq['btc_owned']:,} BTC ({acq['reason']})")
    
    print(f"\nTotal BTC: {acquisitions[-1]['btc_owned']:,}")
    
    # Save to JSON file
    filename = f"btc_history_{symbol.lower()}.json"
    with open(filename, 'w') as f:
        json.dump({
            'symbol': symbol,
            'company_name': company_name,
            'acquisitions': acquisitions
        }, f, indent=2)
    
    print(f"\n✅ Saved to {filename}")
    
    # Generate Python code for mnav_backtest.py
    print(f"\n=== Python Code for mnav_backtest.py ===")
    print(f"'{symbol}': [")
    for acq in acquisitions:
        print(f"    {{'date': '{acq['date']}', 'btc_owned': {acq['btc_owned']}}},")
    print("],")

def view_current_data():
    """View current historical data files"""
    print("=== Current Historical Data Files ===\n")
    
    # Check for shares history files
    shares_files = [f for f in os.listdir('.') if f.startswith('shares_history_') and f.endswith('.json')]
    btc_files = [f for f in os.listdir('.') if f.startswith('btc_history_') and f.endswith('.json')]
    
    if shares_files:
        print("📊 Shares Outstanding History Files:")
        for file in shares_files:
            with open(file, 'r') as f:
                data = json.load(f)
                print(f"  • {file}: {data['company_name']} ({data['symbol']})")
    else:
        print("📊 No shares history files found")
    
    if btc_files:
        print("\n₿ BTC Holdings History Files:")
        for file in btc_files:
            with open(file, 'r') as f:
                data = json.load(f)
                print(f"  • {file}: {data['company_name']} ({data['symbol']})")
    else:
        print("\n₿ No BTC history files found")

def main():
    print("🔧 Historical Data Update Utility")
    print("================================\n")
    
    while True:
        print("Options:")
        print("1. Update Shares Outstanding History")
        print("2. Update BTC Holdings History")
        print("3. View Current Data Files")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            update_shares_history()
        elif choice == '2':
            update_btc_history()
        elif choice == '3':
            view_current_data()
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1-4.")
        
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()
