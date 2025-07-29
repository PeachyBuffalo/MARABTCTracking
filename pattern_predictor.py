#!/usr/bin/env python3
"""
Pattern Prediction System for MNav Trading
Analyzes backtesting results to identify patterns and predict future trading opportunities.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Tuple, Optional

class MNavPatternPredictor:
    def __init__(self):
        self.patterns = {}
        self.predictions = {}
        self.backtest_results = {}
        
    def analyze_backtest_results(self, symbol: str) -> Dict:
        """Analyze backtest results for a given symbol"""
        print(f"🔍 Analyzing patterns for {symbol}...")
        
        # Load backtest data from cache
        cache_dir = "cache"
        symbol_lower = symbol.lower()
        
        # Analyze different time periods
        periods = {
            '1d': {'days': 1, 'weight': 0.1},
            '7d': {'days': 7, 'weight': 0.2},
            '30d': {'days': 30, 'weight': 0.3},
            '90d': {'days': 90, 'weight': 0.25},
            '180d': {'days': 180, 'weight': 0.1},
            '365d': {'days': 365, 'weight': 0.05}
        }
        
        analysis = {
            'symbol': symbol,
            'periods': {},
            'overall_score': 0,
            'trading_opportunities': [],
            'risk_level': 'medium',
            'recommended_strategy': 'moderate'
        }
        
        total_score = 0
        total_weight = 0
        
        for period, config in periods.items():
            try:
                # Load cached data
                cache_file = f"{symbol_lower}_{config['days']}d.pkl"
                cache_path = os.path.join(cache_dir, cache_file)
                
                if os.path.exists(cache_path):
                    import pickle
                    with open(cache_path, 'rb') as f:
                        data = pickle.load(f)
                    
                    period_analysis = self._analyze_period(data, period, config)
                    analysis['periods'][period] = period_analysis
                    
                    # Weight the score
                    weighted_score = period_analysis['score'] * config['weight']
                    total_score += weighted_score
                    total_weight += config['weight']
                    
            except Exception as e:
                print(f"⚠️ Could not analyze {period} period: {e}")
                continue
        
        if total_weight > 0:
            analysis['overall_score'] = total_score / total_weight
        
        # Determine risk level and recommended strategy
        analysis['risk_level'] = self._determine_risk_level(analysis)
        analysis['recommended_strategy'] = self._determine_strategy(analysis)
        
        return analysis
    
    def _analyze_period(self, data: pd.DataFrame, period: str, config: Dict) -> Dict:
        """Analyze a specific time period"""
        if data.empty:
            return {'score': 0, 'trades': 0, 'volatility': 0, 'trend': 'neutral'}
        
        mnav_series = data['mnav'].dropna()
        
        if len(mnav_series) < 2:
            return {'score': 0, 'trades': 0, 'volatility': 0, 'trend': 'neutral'}
        
        # Calculate metrics
        mean_mnav = mnav_series.mean()
        std_mnav = mnav_series.std()
        min_mnav = mnav_series.min()
        max_mnav = mnav_series.max()
        
        # Determine trend
        if len(mnav_series) >= 5:
            recent_avg = mnav_series.tail(5).mean()
            earlier_avg = mnav_series.head(5).mean()
            if recent_avg > earlier_avg * 1.05:
                trend = 'bullish'
            elif recent_avg < earlier_avg * 0.95:
                trend = 'bearish'
            else:
                trend = 'neutral'
        else:
            trend = 'neutral'
        
        # Calculate volatility score (0-1)
        volatility = min(std_mnav / mean_mnav if mean_mnav > 0 else 0, 1.0)
        
        # Calculate trading opportunity score
        range_size = max_mnav - min_mnav
        opportunity_score = min(range_size / mean_mnav if mean_mnav > 0 else 0, 2.0)
        
        # Overall score (0-100)
        score = min((volatility * 40 + opportunity_score * 30 + (1 if trend == 'neutral' else 0.5) * 30), 100)
        
        return {
            'score': score,
            'mean_mnav': mean_mnav,
            'std_mnav': std_mnav,
            'min_mnav': min_mnav,
            'max_mnav': max_mnav,
            'volatility': volatility,
            'trend': trend,
            'opportunity_score': opportunity_score,
            'data_points': len(mnav_series)
        }
    
    def _determine_risk_level(self, analysis: Dict) -> str:
        """Determine risk level based on analysis"""
        overall_score = analysis.get('overall_score', 0)
        volatility_sum = sum(p.get('volatility', 0) for p in analysis.get('periods', {}).values())
        
        if overall_score > 70 or volatility_sum > 2.0:
            return 'high'
        elif overall_score > 40 or volatility_sum > 1.0:
            return 'medium'
        else:
            return 'low'
    
    def _determine_strategy(self, analysis: Dict) -> str:
        """Determine recommended trading strategy"""
        overall_score = analysis.get('overall_score', 0)
        risk_level = analysis.get('risk_level', 'medium')
        
        if risk_level == 'high' and overall_score > 60:
            return 'conservative'
        elif risk_level == 'low' and overall_score < 30:
            return 'aggressive'
        else:
            return 'moderate'
    
    def predict_opportunities(self, symbol: str, analysis: Dict) -> List[Dict]:
        """Predict future trading opportunities"""
        predictions = []
        
        # Get current market data
        try:
            import yfinance as yf
            import requests
            
            # Get current stock price
            ticker = yf.Ticker(symbol)
            current_price = ticker.info.get("currentPrice", 0)
            
            # Get current BTC price
            response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
            btc_price = float(response.json()['bitcoin']['usd'])
            
            # Get current BTC holdings
            from mnav_backtest import get_btc_holdings_over_time
            btc_holdings = get_btc_holdings_over_time(symbol)
            current_btc = btc_holdings.iloc[-1]['btc_owned'] if not btc_holdings.empty else 0
            
            # Calculate current MNav
            from mnav_backtest import get_shares_outstanding
            shares = get_shares_outstanding()
            btc_per_share = current_btc / shares
            current_mnav = current_price / (btc_price * btc_per_share)
            
            # Analyze patterns and make predictions
            for period, period_data in analysis.get('periods', {}).items():
                if period_data.get('score', 0) > 30:  # Only analyze periods with sufficient activity
                    mean_mnav = period_data.get('mean_mnav', 1.0)
                    std_mnav = period_data.get('std_mnav', 0.1)
                    trend = period_data.get('trend', 'neutral')
                    
                    # Calculate thresholds
                    conservative_buy = mean_mnav - 1.5 * std_mnav
                    conservative_sell = mean_mnav + 1.5 * std_mnav
                    moderate_buy = mean_mnav - std_mnav
                    moderate_sell = mean_mnav + std_mnav
                    
                    # Determine current position relative to thresholds
                    position = 'neutral'
                    if current_mnav < conservative_buy:
                        position = 'strong_buy'
                    elif current_mnav < moderate_buy:
                        position = 'buy'
                    elif current_mnav > conservative_sell:
                        position = 'strong_sell'
                    elif current_mnav > moderate_sell:
                        position = 'sell'
                    
                    # Calculate confidence based on distance from mean
                    distance_from_mean = abs(current_mnav - mean_mnav) / std_mnav if std_mnav > 0 else 0
                    confidence = min(distance_from_mean * 20, 100)
                    
                    predictions.append({
                        'period': period,
                        'current_mnav': current_mnav,
                        'mean_mnav': mean_mnav,
                        'position': position,
                        'confidence': confidence,
                        'trend': trend,
                        'conservative_buy': conservative_buy,
                        'conservative_sell': conservative_sell,
                        'moderate_buy': moderate_buy,
                        'moderate_sell': moderate_sell
                    })
            
        except Exception as e:
            print(f"⚠️ Error predicting opportunities for {symbol}: {e}")
        
        return predictions
    
    def generate_report(self, symbol: str) -> str:
        """Generate a comprehensive pattern prediction report"""
        analysis = self.analyze_backtest_results(symbol)
        predictions = self.predict_opportunities(symbol, analysis)
        
        report = f"""
🔮 PATTERN PREDICTION REPORT FOR {symbol}
{'='*60}

📊 OVERALL ANALYSIS
• Overall Score: {analysis['overall_score']:.1f}/100
• Risk Level: {analysis['risk_level'].upper()}
• Recommended Strategy: {analysis['recommended_strategy'].upper()}

📈 PERIOD ANALYSIS
"""
        
        for period, data in analysis.get('periods', {}).items():
            report += f"""
{period.upper()} Period:
• Score: {data.get('score', 0):.1f}/100
• Mean MNav: {data.get('mean_mnav', 0):.3f}
• Volatility: {data.get('volatility', 0):.3f}
• Trend: {data.get('trend', 'neutral').upper()}
• Data Points: {data.get('data_points', 0)}
"""
        
        report += f"""
🎯 TRADING PREDICTIONS
"""
        
        for pred in predictions:
            report += f"""
{pred['period'].upper()} Prediction:
• Current MNav: {pred['current_mnav']:.3f}
• Position: {pred['position'].replace('_', ' ').upper()}
• Confidence: {pred['confidence']:.1f}%
• Trend: {pred['trend'].upper()}
• Conservative Buy: {pred['conservative_buy']:.3f}
• Conservative Sell: {pred['conservative_sell']:.3f}
• Moderate Buy: {pred['moderate_buy']:.3f}
• Moderate Sell: {pred['moderate_sell']:.3f}
"""
        
        # Add recommendations
        report += f"""
💡 RECOMMENDATIONS
"""
        
        if analysis['overall_score'] > 60:
            report += "• HIGH ACTIVITY: This stock shows significant MNav volatility\n"
            report += "• Consider multiple timeframes for trading decisions\n"
        elif analysis['overall_score'] > 30:
            report += "• MODERATE ACTIVITY: Standard trading strategies may work\n"
            report += "• Focus on moderate strategy thresholds\n"
        else:
            report += "• LOW ACTIVITY: Limited trading opportunities\n"
            report += "• Consider longer-term positions or different assets\n"
        
        if analysis['risk_level'] == 'high':
            report += "• HIGH RISK: Use conservative thresholds\n"
            report += "• Consider smaller position sizes\n"
        elif analysis['risk_level'] == 'low':
            report += "• LOW RISK: Can use more aggressive strategies\n"
            report += "• Consider larger position sizes\n"
        
        return report
    
    def save_analysis(self, symbol: str, analysis: Dict, predictions: List[Dict]):
        """Save analysis results to JSON file"""
        results = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis,
            'predictions': predictions
        }
        
        filename = f"pattern_analysis_{symbol.lower()}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✅ Analysis saved to {filename}")

def main():
    """Main function to run pattern prediction"""
    predictor = MNavPatternPredictor()
    
    # Get symbol from command line or use default
    import sys
    if len(sys.argv) > 1:
        symbol = sys.argv[1].upper()
    else:
        symbol = input("Enter stock symbol to analyze: ").upper()
    
    print(f"🔮 Starting pattern prediction for {symbol}...")
    
    # Generate analysis and predictions
    analysis = predictor.analyze_backtest_results(symbol)
    predictions = predictor.predict_opportunities(symbol, analysis)
    
    # Generate and display report
    report = predictor.generate_report(symbol)
    print(report)
    
    # Save results
    predictor.save_analysis(symbol, analysis, predictions)
    
    print(f"✅ Pattern prediction complete for {symbol}")

if __name__ == "__main__":
    main() 