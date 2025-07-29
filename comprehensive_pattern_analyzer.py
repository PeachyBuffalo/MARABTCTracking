#!/usr/bin/env python3
"""
Comprehensive Pattern Analyzer for MNav Trading
Analyzes backtesting results and provides detailed pattern predictions.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json
import os
import glob

class ComprehensivePatternAnalyzer:
    def __init__(self):
        self.analysis_results = {}
        
    def analyze_all_symbols(self):
        """Analyze all available symbols with backtest data"""
        print("🔍 Analyzing all available symbols...")
        
        # Find all PNG files to identify available symbols
        png_files = glob.glob("mnav_analysis_*_*.png")
        symbols = set()
        
        for file in png_files:
            # Extract symbol from filename (e.g., mnav_analysis_SMLR_30d.png)
            parts = file.replace('.png', '').split('_')
            if len(parts) >= 3:
                symbol = parts[2]
                symbols.add(symbol)
        
        print(f"📊 Found symbols: {', '.join(sorted(symbols))}")
        
        results = {}
        for symbol in sorted(symbols):
            print(f"\n{'='*50}")
            print(f"Analyzing {symbol}...")
            result = self.analyze_symbol(symbol)
            results[symbol] = result
            
        return results
    
    def analyze_symbol(self, symbol: str) -> dict:
        """Analyze a specific symbol"""
        # Load cached data for different periods
        cache_dir = "cache"
        symbol_lower = symbol.lower()
        
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
            'best_period': None,
            'trading_patterns': [],
            'risk_assessment': 'medium',
            'recommendations': []
        }
        
        total_score = 0
        total_weight = 0
        best_period_score = 0
        
        for period, config in periods.items():
            try:
                cache_file = f"{symbol_lower}_{config['days']}d.pkl"
                cache_path = os.path.join(cache_dir, cache_file)
                
                if os.path.exists(cache_path):
                    import pickle
                    with open(cache_path, 'rb') as f:
                        data = pickle.load(f)
                    
                    period_analysis = self._analyze_period_data(data, period)
                    analysis['periods'][period] = period_analysis
                    
                    # Track best period
                    if period_analysis['score'] > best_period_score:
                        best_period_score = period_analysis['score']
                        analysis['best_period'] = period
                    
                    # Weight the score
                    weighted_score = period_analysis['score'] * config['weight']
                    total_score += weighted_score
                    total_weight += config['weight']
                    
            except Exception as e:
                print(f"⚠️ Could not analyze {period} period for {symbol}: {e}")
                continue
        
        if total_weight > 0:
            analysis['overall_score'] = total_score / total_weight
        
        # Generate trading patterns and recommendations
        analysis['trading_patterns'] = self._identify_patterns(analysis)
        analysis['risk_assessment'] = self._assess_risk(analysis)
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _analyze_period_data(self, data: pd.DataFrame, period: str) -> dict:
        """Analyze data for a specific period"""
        if data.empty:
            return {'score': 0, 'volatility': 0, 'trend': 'neutral', 'opportunities': 0}
        
        mnav_series = data['mnav'].dropna()
        
        if len(mnav_series) < 2:
            return {'score': 0, 'volatility': 0, 'trend': 'neutral', 'opportunities': 0}
        
        # Calculate basic metrics
        mean_mnav = mnav_series.mean()
        std_mnav = mnav_series.std()
        min_mnav = mnav_series.min()
        max_mnav = mnav_series.max()
        
        # Calculate volatility
        volatility = std_mnav / mean_mnav if mean_mnav > 0 else 0
        
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
        
        # Calculate trading opportunities
        range_size = max_mnav - min_mnav
        opportunities = range_size / mean_mnav if mean_mnav > 0 else 0
        
        # Calculate score (0-100)
        score = min((volatility * 40 + opportunities * 30 + (1 if trend == 'neutral' else 0.5) * 30), 100)
        
        return {
            'score': score,
            'mean_mnav': mean_mnav,
            'std_mnav': std_mnav,
            'min_mnav': min_mnav,
            'max_mnav': max_mnav,
            'volatility': volatility,
            'trend': trend,
            'opportunities': opportunities,
            'data_points': len(mnav_series)
        }
    
    def _identify_patterns(self, analysis: dict) -> list:
        """Identify trading patterns"""
        patterns = []
        
        for period, data in analysis.get('periods', {}).items():
            if data.get('score', 0) > 30:  # Only analyze significant periods
                pattern = {
                    'period': period,
                    'type': self._classify_pattern(data),
                    'strength': data.get('score', 0),
                    'trend': data.get('trend', 'neutral'),
                    'volatility': data.get('volatility', 0)
                }
                patterns.append(pattern)
        
        return patterns
    
    def _classify_pattern(self, data: dict) -> str:
        """Classify the trading pattern"""
        volatility = data.get('volatility', 0)
        trend = data.get('trend', 'neutral')
        opportunities = data.get('opportunities', 0)
        
        if volatility > 0.3 and opportunities > 0.5:
            return 'high_volatility_trading'
        elif trend == 'bullish' and volatility < 0.2:
            return 'steady_uptrend'
        elif trend == 'bearish' and volatility < 0.2:
            return 'steady_downtrend'
        elif volatility < 0.1:
            return 'low_volatility_sideways'
        else:
            return 'mixed_pattern'
    
    def _assess_risk(self, analysis: dict) -> str:
        """Assess risk level"""
        overall_score = analysis.get('overall_score', 0)
        volatility_sum = sum(p.get('volatility', 0) for p in analysis.get('periods', {}).values())
        
        if overall_score > 70 or volatility_sum > 2.0:
            return 'high'
        elif overall_score > 40 or volatility_sum > 1.0:
            return 'medium'
        else:
            return 'low'
    
    def _generate_recommendations(self, analysis: dict) -> list:
        """Generate trading recommendations"""
        recommendations = []
        symbol = analysis.get('symbol', '')
        overall_score = analysis.get('overall_score', 0)
        risk_level = analysis.get('risk_assessment', 'medium')
        best_period = analysis.get('best_period', '30d')
        
        # Strategy recommendations
        if overall_score > 60:
            recommendations.append(f"High activity detected - consider aggressive trading strategies")
            recommendations.append(f"Focus on {best_period} timeframe for optimal results")
        elif overall_score > 30:
            recommendations.append(f"Moderate activity - standard trading strategies recommended")
            recommendations.append(f"Use {best_period} period for primary signals")
        else:
            recommendations.append(f"Low activity - consider longer-term positions or different assets")
        
        # Risk management
        if risk_level == 'high':
            recommendations.append("High risk detected - use conservative position sizing")
            recommendations.append("Consider stop-loss orders and smaller position sizes")
        elif risk_level == 'low':
            recommendations.append("Low risk profile - can use larger position sizes")
            recommendations.append("Consider more aggressive entry/exit points")
        
        # Pattern-specific recommendations
        patterns = analysis.get('trading_patterns', [])
        for pattern in patterns:
            if pattern['type'] == 'high_volatility_trading':
                recommendations.append(f"High volatility in {pattern['period']} period - use wider stops")
            elif pattern['type'] == 'steady_uptrend':
                recommendations.append(f"Steady uptrend in {pattern['period']} - consider trend-following strategies")
            elif pattern['type'] == 'steady_downtrend':
                recommendations.append(f"Steady downtrend in {pattern['period']} - consider short positions or wait for reversal")
        
        return recommendations
    
    def generate_comprehensive_report(self, results: dict) -> str:
        """Generate a comprehensive report for all symbols"""
        report = f"""
🔮 COMPREHENSIVE PATTERN ANALYSIS REPORT
{'='*80}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 SUMMARY STATISTICS
• Total Symbols Analyzed: {len(results)}
• Average Overall Score: {np.mean([r.get('overall_score', 0) for r in results.values()]):.1f}
• High Activity Symbols: {len([r for r in results.values() if r.get('overall_score', 0) > 60])}
• Medium Activity Symbols: {len([r for r in results.values() if 30 <= r.get('overall_score', 0) <= 60])}
• Low Activity Symbols: {len([r for r in results.values() if r.get('overall_score', 0) < 30])}

"""
        
        # Sort symbols by overall score
        sorted_symbols = sorted(results.items(), key=lambda x: x[1].get('overall_score', 0), reverse=True)
        
        for symbol, analysis in sorted_symbols:
            report += f"""
{'='*60}
📈 {symbol} ANALYSIS
{'='*60}
• Overall Score: {analysis.get('overall_score', 0):.1f}/100
• Risk Level: {analysis.get('risk_assessment', 'medium').upper()}
• Best Period: {analysis.get('best_period', 'N/A')}
• Trading Patterns: {len(analysis.get('trading_patterns', []))}

📊 PERIOD BREAKDOWN:
"""
            
            for period, data in analysis.get('periods', {}).items():
                report += f"  {period.upper()}: Score {data.get('score', 0):.1f}, Volatility {data.get('volatility', 0):.3f}, Trend {data.get('trend', 'neutral').upper()}\n"
            
            report += f"""
🎯 PATTERNS IDENTIFIED:
"""
            
            for pattern in analysis.get('trading_patterns', []):
                report += f"  • {pattern['period'].upper()}: {pattern['type'].replace('_', ' ').title()} (Strength: {pattern['strength']:.1f})\n"
            
            report += f"""
💡 RECOMMENDATIONS:
"""
            
            for rec in analysis.get('recommendations', []):
                report += f"  • {rec}\n"
        
        return report
    
    def save_results(self, results: dict):
        """Save analysis results to JSON file"""
        filename = f"comprehensive_pattern_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert numpy types to native Python types for JSON serialization
        def convert_numpy(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj
        
        # Recursively convert numpy types
        def clean_dict(d):
            if isinstance(d, dict):
                return {k: clean_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [clean_dict(v) for v in d]
            else:
                return convert_numpy(d)
        
        clean_results = clean_dict(results)
        
        with open(filename, 'w') as f:
            json.dump(clean_results, f, indent=2)
        
        print(f"✅ Comprehensive analysis saved to {filename}")

def main():
    """Main function to run comprehensive pattern analysis"""
    analyzer = ComprehensivePatternAnalyzer()
    
    print("🔮 Starting comprehensive pattern analysis...")
    
    # Analyze all available symbols
    results = analyzer.analyze_all_symbols()
    
    # Generate comprehensive report
    report = analyzer.generate_comprehensive_report(results)
    print(report)
    
    # Save results
    analyzer.save_results(results)
    
    print("✅ Comprehensive pattern analysis complete!")

if __name__ == "__main__":
    main() 