#!/usr/bin/env python3
"""
Robust Pattern Analyzer for MNav Trading
Analyzes backtesting results and provides detailed pattern predictions.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json
import os
import glob
import pickle

class RobustPatternAnalyzer:
    def __init__(self):
        self.analysis_results = {}
        
    def analyze_symbol(self, symbol: str) -> dict:
        """Analyze a specific symbol using available cache data"""
        print(f"🔍 Analyzing {symbol}...")
        
        cache_dir = "cache"
        symbol_lower = symbol.lower()
        
        # Find all cache files for this symbol (both stock data and MNav data)
        cache_files = glob.glob(os.path.join(cache_dir, f"{symbol_lower}_*.pkl"))
        mnav_cache_files = glob.glob(os.path.join(cache_dir, f"mnav_{symbol_lower}_*.pkl"))
        
        # Prefer MNav cache files if available
        if mnav_cache_files:
            cache_files = mnav_cache_files
            print(f"📊 Found {len(cache_files)} MNav cache files for {symbol}")
        else:
            print(f"📊 Found {len(cache_files)} stock cache files for {symbol}")
        
        if not cache_files:
            print(f"⚠️ No cache files found for {symbol}")
            return self._create_empty_analysis(symbol)
        
        print(f"📊 Found {len(cache_files)} cache files for {symbol}")
        
        # Analyze each cache file
        period_analyses = {}
        total_score = 0
        total_weight = 0
        best_period_score = 0
        best_period = None
        
        for cache_file in cache_files:
            try:
                # Extract period from filename
                filename = os.path.basename(cache_file)
                period = self._extract_period_from_filename(filename)
                
                if not period:
                    continue
                
                # Load and analyze data
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                
                analysis = self._analyze_data(data, period)
                period_analyses[period] = analysis
                
                # Track best period
                if analysis['score'] > best_period_score:
                    best_period_score = analysis['score']
                    best_period = period
                
                # Weight by period importance
                weight = self._get_period_weight(period)
                total_score += analysis['score'] * weight
                total_weight += weight
                
            except Exception as e:
                print(f"⚠️ Error analyzing {cache_file}: {e}")
                continue
        
        # Create comprehensive analysis
        analysis = {
            'symbol': symbol,
            'periods': period_analyses,
            'overall_score': total_score / total_weight if total_weight > 0 else 0,
            'best_period': best_period,
            'trading_patterns': self._identify_patterns(period_analyses),
            'risk_assessment': self._assess_risk(period_analyses),
            'recommendations': self._generate_recommendations(symbol, period_analyses, best_period)
        }
        
        return analysis
    
    def _extract_period_from_filename(self, filename: str) -> str:
        """Extract period from cache filename"""
        # Examples: smlr_20240728_20250728.pkl -> 365d
        #          smlr_20250129_20250728.pkl -> 180d
        #          smlr_20250727_20250728.pkl -> 1d
        
        try:
            # Extract date range from filename
            parts = filename.replace('.pkl', '').split('_')
            
            if len(parts) >= 4:  # mnav_mstr_20240729_20250729.pkl
                start_date_str = parts[2]
                end_date_str = parts[3]
            elif len(parts) >= 3:  # mstr_20240729_20250729.pkl
                start_date_str = parts[1]
                end_date_str = parts[2]
            else:
                return None
            
            start_date = datetime.strptime(start_date_str, '%Y%m%d')
            end_date = datetime.strptime(end_date_str, '%Y%m%d')
            
            days_diff = (end_date - start_date).days
            
            # Map to standard periods
            if days_diff <= 1:
                return '1d'
            elif days_diff <= 7:
                return '7d'
            elif days_diff <= 30:
                return '30d'
            elif days_diff <= 90:
                return '90d'
            elif days_diff <= 180:
                return '180d'
            else:
                return '365d'
        except Exception as e:
            return None
    
    def _get_period_weight(self, period: str) -> float:
        """Get weight for period importance"""
        weights = {
            '1d': 0.05,
            '7d': 0.15,
            '30d': 0.35,
            '90d': 0.25,
            '180d': 0.15,
            '365d': 0.05
        }
        return weights.get(period, 0.1)
    
    def _analyze_data(self, data: pd.DataFrame, period: str) -> dict:
        """Analyze data for a specific period"""
        if data.empty:
            return {'score': 0, 'volatility': 0, 'trend': 'neutral', 'opportunities': 0}
        
        # Check if data has mnav column
        if 'mnav' not in data.columns:
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
    
    def _identify_patterns(self, period_analyses: dict) -> list:
        """Identify trading patterns"""
        patterns = []
        
        for period, data in period_analyses.items():
            if data.get('score', 0) > 20:  # Lower threshold for pattern detection
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
    
    def _assess_risk(self, period_analyses: dict) -> str:
        """Assess risk level"""
        overall_score = np.mean([p.get('score', 0) for p in period_analyses.values()])
        volatility_sum = sum(p.get('volatility', 0) for p in period_analyses.values())
        
        if overall_score > 50 or volatility_sum > 1.5:
            return 'high'
        elif overall_score > 25 or volatility_sum > 0.8:
            return 'medium'
        else:
            return 'low'
    
    def _generate_recommendations(self, symbol: str, period_analyses: dict, best_period: str) -> list:
        """Generate trading recommendations"""
        recommendations = []
        overall_score = np.mean([p.get('score', 0) for p in period_analyses.values()])
        risk_level = self._assess_risk(period_analyses)
        
        # Strategy recommendations
        if overall_score > 40:
            recommendations.append(f"High activity detected for {symbol} - consider aggressive trading strategies")
            if best_period:
                recommendations.append(f"Focus on {best_period} timeframe for optimal results")
        elif overall_score > 20:
            recommendations.append(f"Moderate activity for {symbol} - standard trading strategies recommended")
            if best_period:
                recommendations.append(f"Use {best_period} period for primary signals")
        else:
            recommendations.append(f"Low activity for {symbol} - consider longer-term positions or different assets")
        
        # Risk management
        if risk_level == 'high':
            recommendations.append("High risk detected - use conservative position sizing")
            recommendations.append("Consider stop-loss orders and smaller position sizes")
        elif risk_level == 'low':
            recommendations.append("Low risk profile - can use larger position sizes")
            recommendations.append("Consider more aggressive entry/exit points")
        
        # Pattern-specific recommendations
        patterns = self._identify_patterns(period_analyses)
        for pattern in patterns:
            if pattern['type'] == 'high_volatility_trading':
                recommendations.append(f"High volatility in {pattern['period']} period - use wider stops")
            elif pattern['type'] == 'steady_uptrend':
                recommendations.append(f"Steady uptrend in {pattern['period']} - consider trend-following strategies")
            elif pattern['type'] == 'steady_downtrend':
                recommendations.append(f"Steady downtrend in {pattern['period']} - consider short positions or wait for reversal")
        
        return recommendations
    
    def _create_empty_analysis(self, symbol: str) -> dict:
        """Create empty analysis for symbols without data"""
        return {
            'symbol': symbol,
            'periods': {},
            'overall_score': 0,
            'best_period': None,
            'trading_patterns': [],
            'risk_assessment': 'low',
            'recommendations': [
                f"No data available for {symbol}",
                "Consider running backtest first",
                "Low risk profile due to lack of data"
            ]
        }
    
    def analyze_all_symbols(self) -> dict:
        """Analyze all available symbols"""
        print("🔍 Analyzing all available symbols...")
        
        # Find all cache files to identify symbols
        cache_dir = "cache"
        cache_files = glob.glob(os.path.join(cache_dir, "*.pkl"))
        
        symbols = set()
        for file in cache_files:
            filename = os.path.basename(file)
            if '_' in filename and not filename.startswith('btc_') and not filename.startswith('shares_'):
                parts = filename.split('_')
                if len(parts) >= 2:
                    symbol = parts[0].upper()
                    symbols.add(symbol)
        
        print(f"📊 Found symbols: {', '.join(sorted(symbols))}")
        
        results = {}
        for symbol in sorted(symbols):
            result = self.analyze_symbol(symbol)
            results[symbol] = result
        
        return results
    
    def generate_report(self, results: dict) -> str:
        """Generate comprehensive report"""
        report = f"""
🔮 ROBUST PATTERN ANALYSIS REPORT
{'='*80}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 SUMMARY STATISTICS
• Total Symbols Analyzed: {len(results)}
• Average Overall Score: {np.mean([r.get('overall_score', 0) for r in results.values()]):.1f}
• High Activity Symbols: {len([r for r in results.values() if r.get('overall_score', 0) > 40])}
• Medium Activity Symbols: {len([r for r in results.values() if 20 <= r.get('overall_score', 0) <= 40])}
• Low Activity Symbols: {len([r for r in results.values() if r.get('overall_score', 0) < 20])}

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
        """Save analysis results"""
        filename = f"robust_pattern_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert numpy types for JSON serialization
        def clean_dict(d):
            if isinstance(d, dict):
                return {k: clean_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [clean_dict(v) for v in d]
            elif isinstance(d, np.integer):
                return int(d)
            elif isinstance(d, np.floating):
                return float(d)
            elif isinstance(d, np.ndarray):
                return d.tolist()
            return d
        
        clean_results = clean_dict(results)
        
        with open(filename, 'w') as f:
            json.dump(clean_results, f, indent=2)
        
        print(f"✅ Robust analysis saved to {filename}")

def main():
    """Main function"""
    analyzer = RobustPatternAnalyzer()
    
    print("🔮 Starting robust pattern analysis...")
    
    # Analyze all symbols
    results = analyzer.analyze_all_symbols()
    
    # Generate report
    report = analyzer.generate_report(results)
    print(report)
    
    # Save results
    analyzer.save_results(results)
    
    print("✅ Robust pattern analysis complete!")

if __name__ == "__main__":
    main() 