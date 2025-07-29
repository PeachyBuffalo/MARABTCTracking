#!/usr/bin/env python3
"""
Utility script to help add BTC acquisition history for companies.
This helps make MNav analysis more accurate by tracking when companies acquired their BTC.
"""

import json
from datetime import datetime

def add_btc_history():
    """Interactive script to add BTC acquisition history"""
    print("=== BTC Acquisition History Adder ===\n")
    
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
        
        acquisitions.append({
            'date': date_input,
            'btc_owned': btc_amount
        })
        
        print(f"✅ Added: {date_input} - {btc_amount:,} BTC\n")
    
    if not acquisitions:
        print("❌ No acquisitions entered.")
        return
    
    # Sort by date
    acquisitions.sort(key=lambda x: x['date'])
    
    print(f"\n=== Summary for {symbol} ===")
    for i, acq in enumerate(acquisitions):
        print(f"{i+1}. {acq['date']}: {acq['btc_owned']:,} BTC")
    
    print(f"\nTotal BTC: {acquisitions[-1]['btc_owned']:,}")
    
    # Generate Python code
    print(f"\n=== Python Code for {symbol} ===")
    print(f"'{symbol}': [")
    for acq in acquisitions:
        print(f"    {{'date': '{acq['date']}', 'btc_owned': {acq['btc_owned']}}},")
    print("],")
    
    # Save to JSON file
    filename = f"btc_history_{symbol.lower()}.json"
    with open(filename, 'w') as f:
        json.dump({
            'symbol': symbol,
            'company_name': company_name,
            'acquisitions': acquisitions
        }, f, indent=2)
    
    print(f"\n✅ Saved to {filename}")

if __name__ == "__main__":
    add_btc_history() 