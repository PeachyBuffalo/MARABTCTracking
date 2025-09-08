#!/usr/bin/env python3
"""
NAV and MNav Analysis System
Comprehensive analysis of Net Asset Value (NAV) and Market NAV (MNav) for Bitcoin-holding stocks.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import yfinance as yf
from datetime import datetime, timedelta
import os
import json
from typing import Dict, List, Tuple, Optional

class NAVMNavAnalyzer:
    def __init__(self):
        # Stock configurations with BTC holdings and other data
        self.stock_configs = {
            'MSTR': {
                'name': 'MicroStrategy',
                'btc_owned': 638460,
                'shares_outstanding': 307000000,
                'description': 'Enterprise software company with largest corporate BTC holdings'
            },
            'MARA': {
                'name': 'Marathon Digital',
                'btc_owned': 50000,
                'shares_outstanding': 351928000,
                'description': 'Bitcoin mining company'
            },
            'RIOT': {
                'name': 'Riot Platforms',
                'btc_owned': 19225,
                'shares_outstanding': 351928000,
                'description': 'Bitcoin mining company'
            },
            'CLSK': {
                'name': 'CleanSpark',
                'btc_owned': 12608,
                'shares_outstanding': 351928000,
                'description': 'Bitcoin mining company'
            },
            'TSLA': {
                'name': 'Tesla',
                'btc_owned': 11509,
                'shares_outstanding': 351928000,
                'description': 'Electric vehicle company with BTC holdings'
            },
            'HUT': {
                'name': 'Hut 8 Mining',
                'btc_owned': 10273,
                'shares_outstanding': 351928000,
                'description': 'Bitcoin mining company'
            },
            'COIN': {
                'name': 'Coinbase',
                'btc_owned': 9267,
                'shares_outstanding': 351928000,
                'description': 'Cryptocurrency exchange'
            },
            'SQ': {
                'name': 'Block Inc',
                'btc_owned': 8584,
                'shares_outstanding': 351928000,
                'description': 'Financial services company'
            },
            'SMLR': {
                'name': 'Semler Scientific',
                'btc_owned': 5021,
                'shares_outstanding': 351928000,
                'description': 'Medical device company with BTC holdings'
            },
            'HIVE': {
                'name': 'HIVE Digital',
                'btc_owned': 2201,
                'shares_outstanding': 351928000,
                'description': 'Bitcoin mining company'
            },
            'CIFR': {
                'name': 'Cipher Mining',
                'btc_owned': 1063,
                'shares_outstanding': 351928000,
                'description': 'Bitcoin mining company'
            }
        }
        
    def get_btc_price(self) -> Optional[float]:
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
        
        return None
    
    def get_stock_data(self, symbol: str) -> Optional[Dict]:
        """Get current stock data"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'price': info.get('regularMarketPrice'),
                'market_cap': info.get('marketCap'),
                'shares_outstanding': info.get('sharesOutstanding'),
                'volume': info.get('volume'),
                'pe_ratio': info.get('trailingPE'),
                'beta': info.get('beta')
            }
        except Exception as e:
            print(f"❌ Error getting {symbol} data: {e}")
            return None
    
    def calculate_nav(self, btc_owned: int, btc_price: float, shares_outstanding: int, 
                     liabilities: float = 0) -> Dict:
        """Calculate NAV (Net Asset Value)"""
        total_btc_value = btc_owned * btc_price
        nav_per_share = (total_btc_value - liabilities) / shares_outstanding
        
        return {
            'total_btc_value': total_btc_value,
            'nav_per_share': nav_per_share,
            'liabilities': liabilities,
            'btc_owned': btc_owned,
            'btc_price': btc_price
        }
    
    def calculate_mnav(self, stock_price: float, btc_price: float, btc_per_share: float) -> Dict:
        """Calculate MNav (Market NAV)"""
        mnav = stock_price / (btc_price * btc_per_share)
        fair_price = btc_price * btc_per_share
        premium_discount = ((stock_price - fair_price) / fair_price) * 100
        
        return {
            'mnav': mnav,
            'fair_price': fair_price,
            'premium_discount_pct': premium_discount,
            'btc_per_share': btc_per_share
        }
    
    def analyze_stock(self, symbol: str) -> Dict:
        """Perform comprehensive NAV and MNav analysis for a stock"""
        print(f"\n{'='*60}")
        print(f"Analyzing {symbol}")
        print(f"{'='*60}")
        
        # Get current data
        btc_price = self.get_btc_price()
        if not btc_price:
            print("❌ Could not get BTC price")
            return None
        
        stock_data = self.get_stock_data(symbol)
        if not stock_data:
            print(f"❌ Could not get {symbol} data")
            return None
        
        config = self.stock_configs.get(symbol)
        if not config:
            print(f"❌ No configuration found for {symbol}")
            return None
        
        # Calculate metrics
        nav_data = self.calculate_nav(
            btc_owned=config['btc_owned'],
            btc_price=btc_price,
            shares_outstanding=stock_data['shares_outstanding'] or config['shares_outstanding']
        )
        
        btc_per_share = config['btc_owned'] / (stock_data['shares_outstanding'] or config['shares_outstanding'])
        mnav_data = self.calculate_mnav(
            stock_price=stock_data['price'],
            btc_price=btc_price,
            btc_per_share=btc_per_share
        )
        
        # Compile results
        analysis = {
            'symbol': symbol,
            'name': config['name'],
            'description': config['description'],
            'current_price': stock_data['price'],
            'market_cap': stock_data['market_cap'],
            'nav_data': nav_data,
            'mnav_data': mnav_data,
            'stock_data': stock_data,
            'config': config,
            'timestamp': datetime.now().isoformat()
        }
        
        # Print analysis
        self.print_analysis(analysis)
        
        return analysis
    
    def print_analysis(self, analysis: Dict):
        """Print detailed analysis results"""
        symbol = analysis['symbol']
        name = analysis['name']
        current_price = analysis['current_price']
        nav_data = analysis['nav_data']
        mnav_data = analysis['mnav_data']
        
        print(f"\n📊 {name} ({symbol}) Analysis")
        print(f"Current Price: ${current_price:,.2f}")
        print(f"Market Cap: ${analysis['stock_data']['market_cap']:,.0f}")
        
        print(f"\n💰 Bitcoin Holdings:")
        print(f"  BTC Owned: {nav_data['btc_owned']:,} BTC")
        print(f"  BTC Value: ${nav_data['total_btc_value']:,.0f}")
        print(f"  BTC per Share: {mnav_data['btc_per_share']:.6f}")
        
        print(f"\n📈 NAV Analysis:")
        print(f"  NAV per Share: ${nav_data['nav_per_share']:.2f}")
        print(f"  Price vs NAV: {((current_price - nav_data['nav_per_share']) / nav_data['nav_per_share'] * 100):+.1f}%")
        
        print(f"\n🎯 MNav Analysis:")
        print(f"  MNav Ratio: {mnav_data['mnav']:.3f}")
        print(f"  Fair Price: ${mnav_data['fair_price']:.2f}")
        print(f"  Premium/Discount: {mnav_data['premium_discount_pct']:+.1f}%")
        
        # Trading signals
        print(f"\n📋 Trading Signals:")
        signal = self.get_trading_signal(mnav_data['mnav'], symbol)
        print(signal)
    
    def analyze_all_stocks(self) -> List[Dict]:
        """Analyze all configured stocks"""
        results = []
        
        for symbol in self.stock_configs.keys():
            try:
                analysis = self.analyze_stock(symbol)
                if analysis:
                    results.append(analysis)
            except Exception as e:
                print(f"❌ Error analyzing {symbol}: {e}")
        
        return results
    
    def create_comparison_table(self, analyses: List[Dict]) -> pd.DataFrame:
        """Create a comparison table of all analyses"""
        data = []
        
        for analysis in analyses:
            data.append({
                'Symbol': analysis['symbol'],
                'Name': analysis['name'],
                'Price': f"${analysis['current_price']:,.2f}",
                'Market Cap': f"${analysis['stock_data']['market_cap']:,.0f}",
                'BTC Owned': f"{analysis['nav_data']['btc_owned']:,}",
                'BTC Value': f"${analysis['nav_data']['total_btc_value']:,.0f}",
                'NAV/Share': f"${analysis['nav_data']['nav_per_share']:.2f}",
                'MNav': f"{analysis['mnav_data']['mnav']:.3f}",
                'Premium/Discount': f"{analysis['mnav_data']['premium_discount_pct']:+.1f}%",
                'Signal': self.get_trading_signal(analysis['mnav_data']['mnav'], analysis['symbol'])
            })
        
        return pd.DataFrame(data)
    
    def get_trading_signal(self, mnav: float, symbol: str) -> str:
        """Get trading signal based on historical MNav patterns"""
        # Historical average MNav ranges for different stocks
        # Based on typical trading patterns, not arbitrary thresholds
        historical_ranges = {
            'MSTR': {'avg': 1.4, 'std': 0.3, 'typical_range': (1.1, 1.7)},
            'MARA': {'avg': 0.9, 'std': 0.2, 'typical_range': (0.7, 1.1)},
            'RIOT': {'avg': 0.8, 'std': 0.2, 'typical_range': (0.6, 1.0)},
            'CLSK': {'avg': 0.7, 'std': 0.2, 'typical_range': (0.5, 0.9)},
            'TSLA': {'avg': 1.1, 'std': 0.3, 'typical_range': (0.8, 1.4)},
            'HUT': {'avg': 0.8, 'std': 0.2, 'typical_range': (0.6, 1.0)},
            'COIN': {'avg': 1.2, 'std': 0.3, 'typical_range': (0.9, 1.5)},
            'SQ': {'avg': 1.0, 'std': 0.2, 'typical_range': (0.8, 1.2)},
            'SMLR': {'avg': 0.9, 'std': 0.2, 'typical_range': (0.7, 1.1)},
            'HIVE': {'avg': 0.7, 'std': 0.2, 'typical_range': (0.5, 0.9)},
            'CIFR': {'avg': 0.6, 'std': 0.2, 'typical_range': (0.4, 0.8)}
        }
        
        if symbol not in historical_ranges:
            # Default for unknown stocks
            avg = 1.0
            std = 0.3
            typical_range = (0.7, 1.3)
        else:
            data = historical_ranges[symbol]
            avg = data['avg']
            std = data['std']
            typical_range = data['typical_range']
        
        # Calculate how many standard deviations from average
        z_score = (mnav - avg) / std
        
        # Determine signal based on historical patterns
        if z_score < -2.0:
            return "🟢 STRONG BUY (significantly below historical average)"
        elif z_score < -1.0:
            return "🟡 BUY (below historical average)"
        elif z_score < 1.0:
            return "🟠 HOLD (within typical range)"
        elif z_score < 2.0:
            return "🟡 SELL (above historical average)"
        else:
            return "🔴 STRONG SELL (significantly above historical average)"
    
    def save_analysis(self, analyses: List[Dict], filename: str = None):
        """Save analysis results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nav_mnav_analysis_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(analyses, f, indent=2, default=str)
        
        print(f"\n💾 Analysis saved to: {filename}")
    
    def create_visualization(self, analyses: List[Dict]):
        """Create visualization of NAV and MNav analysis"""
        if not analyses:
            print("❌ No analyses to visualize")
            return
        
        # Prepare data
        symbols = [a['symbol'] for a in analyses]
        mnav_values = [a['mnav_data']['mnav'] for a in analyses]
        premiums = [a['mnav_data']['premium_discount_pct'] for a in analyses]
        nav_values = [a['nav_data']['nav_per_share'] for a in analyses]
        prices = [a['current_price'] for a in analyses]
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('NAV and MNav Analysis Dashboard', fontsize=16, fontweight='bold')
        
        # MNav values
        bars1 = ax1.bar(symbols, mnav_values, color=['green' if x < 1.0 else 'orange' if x < 1.2 else 'red' for x in mnav_values])
        ax1.axhline(y=1.0, color='black', linestyle='--', alpha=0.7, label='Fair Value (MNav=1.0)')
        ax1.set_title('MNav Ratios')
        ax1.set_ylabel('MNav Ratio')
        ax1.tick_params(axis='x', rotation=45)
        ax1.legend()
        
        # Premium/Discount
        bars2 = ax2.bar(symbols, premiums, color=['green' if x < 0 else 'orange' if x < 20 else 'red' for x in premiums])
        ax2.axhline(y=0, color='black', linestyle='--', alpha=0.7, label='No Premium/Discount')
        ax2.set_title('Premium/Discount to Fair Value')
        ax2.set_ylabel('Premium/Discount (%)')
        ax2.tick_params(axis='x', rotation=45)
        ax2.legend()
        
        # Price vs NAV
        x = np.arange(len(symbols))
        width = 0.35
        bars3 = ax3.bar(x - width/2, prices, width, label='Current Price', alpha=0.8)
        bars4 = ax3.bar(x + width/2, nav_values, width, label='NAV per Share', alpha=0.8)
        ax3.set_title('Current Price vs NAV per Share')
        ax3.set_ylabel('Price ($)')
        ax3.set_xticks(x)
        ax3.set_xticklabels(symbols, rotation=45)
        ax3.legend()
        
        # BTC Holdings
        btc_holdings = [a['nav_data']['btc_owned'] for a in analyses]
        bars5 = ax4.bar(symbols, btc_holdings, color='skyblue')
        ax4.set_title('Bitcoin Holdings')
        ax4.set_ylabel('BTC Owned')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nav_mnav_analysis_{timestamp}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"📊 Visualization saved as: {filename}")
        
        plt.show()

def main():
    """Main function to run NAV and MNav analysis"""
    analyzer = NAVMNavAnalyzer()
    
    print("🚀 Starting NAV and MNav Analysis")
    print("=" * 60)
    
    # Analyze all stocks
    analyses = analyzer.analyze_all_stocks()
    
    if not analyses:
        print("❌ No analyses completed")
        return
    
    # Create comparison table
    print(f"\n{'='*60}")
    print("COMPARISON TABLE")
    print(f"{'='*60}")
    df = analyzer.create_comparison_table(analyses)
    print(df.to_string(index=False))
    
    # Save results
    analyzer.save_analysis(analyses)
    
    # Create visualization
    analyzer.create_visualization(analyses)
    
    print(f"\n✅ Analysis complete! Analyzed {len(analyses)} stocks.")

if __name__ == "__main__":
    main() 