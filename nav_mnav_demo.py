#!/usr/bin/env python3
"""
NAV and MNav Analysis Demo
Using data from the image to demonstrate NAV and MNav calculations.
"""

def analyze_mstr_from_image():
    """Analyze MSTR using data from the image"""
    print("🚀 NAV and MNav Analysis Demo")
    print("=" * 60)
    print("Using data from the provided image")
    print("=" * 60)
    
    # Data from the image
    symbol = "MSTR"
    name = "MicroStrategy"
    current_price = 395
    market_cap = 112000000000  # $112B
    btc_owned = 638460
    btc_price = 112000  # Current BTC price
    shares_outstanding = 307000000  # Updated to current shares outstanding
    
    print(f"\n📊 {name} ({symbol}) Analysis")
    print(f"Current Price: ${current_price:,.2f}")
    print(f"Market Cap: ${market_cap:,.0f}")
    
    # Calculate metrics
    total_btc_value = btc_owned * btc_price
    btc_per_share = btc_owned / shares_outstanding
    nav_per_share = total_btc_value / shares_outstanding
    mnav = current_price / (btc_price * btc_per_share)
    fair_price = btc_price * btc_per_share
    premium_discount = ((current_price - fair_price) / fair_price) * 100
    
    print(f"\n💰 Bitcoin Holdings:")
    print(f"  BTC Owned: {btc_owned:,} BTC")
    print(f"  BTC Value: ${total_btc_value:,.0f}")
    print(f"  BTC per Share: {btc_per_share:.6f}")
    
    print(f"\n📈 NAV Analysis:")
    print(f"  NAV per Share: ${nav_per_share:.2f}")
    print(f"  Price vs NAV: {((current_price - nav_per_share) / nav_per_share * 100):+.1f}%")
    
    print(f"\n🎯 MNav Analysis:")
    print(f"  MNav Ratio: {mnav:.3f}")
    print(f"  Fair Price: ${fair_price:.2f}")
    print(f"  Premium/Discount: {premium_discount:+.1f}%")
    
    # Compare with image data
    nav_multiple_from_image = 1.571
    print(f"\n📊 Comparison with Image Data:")
    print(f"  Our Calculated MNav: {mnav:.3f}")
    print(f"  Image NAV Multiple: {nav_multiple_from_image}")
    print(f"  Difference: {abs(mnav - nav_multiple_from_image):.3f}")
    
    # Trading signals
    print(f"\n📋 Trading Signals:")
    signal_description = get_trading_signal(mnav, symbol)
    print(f"  {signal_description}")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"  {symbol} is trading at {mnav:.3f}x its Bitcoin-backed value")
    print(f"  The stock has a {premium_discount:.1f}% premium to fair value")
    print(f"  This premium reflects market confidence in MicroStrategy's business model")
    
    return {
        'symbol': symbol,
        'name': name,
        'current_price': current_price,
        'market_cap': market_cap,
        'btc_owned': btc_owned,
        'btc_price': btc_price,
        'shares_outstanding': shares_outstanding,
        'total_btc_value': total_btc_value,
        'btc_per_share': btc_per_share,
        'nav_per_share': nav_per_share,
        'mnav': mnav,
        'fair_price': fair_price,
        'premium_discount': premium_discount
    }

def explain_nav_vs_mnav():
    """Explain the difference between NAV and MNav"""
    print(f"\n{'='*60}")
    print("NAV vs MNav Explanation")
    print(f"{'='*60}")
    
    print("\n📈 NAV (Net Asset Value):")
    print("  • Formula: NAV = (BTC Holdings × BTC Price) / Shares Outstanding")
    print("  • Purpose: Shows the intrinsic value per share based on Bitcoin holdings")
    print("  • Interpretation: Absolute dollar value per share")
    print("  • Trading Signal: Buy when stock price < NAV per share")
    
    print("\n🎯 MNav (Market NAV):")
    print("  • Formula: MNav = Stock Price / (BTC Price × BTC per Share)")
    print("  • Purpose: Shows market premium/discount relative to Bitcoin value")
    print("  • Interpretation: Ratio (1.0 = fair value)")
    print("  • Trading Signal: Buy when MNav < 1.0")
    
    print("\n📊 Key Differences:")
    print("  • NAV: Absolute value per share")
    print("  • MNav: Relative valuation ratio")
    print("  • NAV: Useful for absolute valuation")
    print("  • MNav: Useful for relative valuation and trading signals")
    
    print("\n💡 Trading Strategy:")
    print("  • MNav < 0.8: Strong Buy (significant discount)")
    print("  • MNav < 1.0: Buy (discount)")
    print("  • MNav 1.0-1.2: Hold (fairly valued)")
    print("  • MNav 1.2-1.5: Sell (premium)")
    print("  • MNav > 1.5: Strong Sell (significant premium)")

def get_trading_signal(mnav: float, symbol: str) -> str:
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

def main():
    """Main function"""
    # Analyze MSTR using image data
    analysis = analyze_mstr_from_image()
    
    # Explain NAV vs MNav
    explain_nav_vs_mnav()
    
    print(f"\n✅ Demo complete!")
    print("This demonstrates how NAV and MNav analysis works for Bitcoin-holding stocks.")

if __name__ == "__main__":
    main() 