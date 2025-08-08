#!/usr/bin/env python3
"""
Robust Yahoo Finance Client
Handles rate limiting, circuit breaker, and fallback mechanisms
"""

import requests
import time
import json
import os
import pickle
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class RobustYahooClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # Circuit breaker settings
        self.circuit_breaker_failures = 0
        self.circuit_breaker_threshold = 3
        self.circuit_breaker_timeout = 1800  # 30 minutes
        self.circuit_breaker_reset_time = None
        
        # Rate limiting settings
        self.last_request_time = 0
        self.min_request_interval = 2  # 2 seconds between requests
        
        # Cache settings
        self.cache_dir = "cache"
        self.cache_duration = 60  # 60 seconds per symbol
        
        # Ensure cache directory exists
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _get_cache_path(self, key: str) -> str:
        """Get cache file path"""
        return os.path.join(self.cache_dir, f"yahoo_{key}.pkl")
    
    def _save_to_cache(self, data: Any, key: str) -> None:
        """Save data to cache"""
        try:
            cache_path = self._get_cache_path(key)
            with open(cache_path, 'wb') as f:
                pickle.dump({
                    'data': data,
                    'timestamp': time.time()
                }, f)
        except Exception as e:
            print(f"Warning: Could not save to cache: {e}")
    
    def _load_from_cache(self, key: str) -> Optional[Any]:
        """Load data from cache"""
        try:
            cache_path = self._get_cache_path(key)
            if os.path.exists(cache_path):
                with open(cache_path, 'rb') as f:
                    cached = pickle.load(f)
                    cache_age = time.time() - cached['timestamp']
                    if cache_age < self.cache_duration:
                        return cached['data']
        except Exception:
            pass
        return None
    
    def _is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open"""
        if self.circuit_breaker_reset_time and time.time() < self.circuit_breaker_reset_time:
            return True
        return False
    
    def _open_circuit_breaker(self) -> None:
        """Open circuit breaker"""
        self.circuit_breaker_failures += 1
        if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
            self.circuit_breaker_reset_time = time.time() + self.circuit_breaker_timeout
            print(f"🔴 Circuit breaker opened - Yahoo Finance disabled for {self.circuit_breaker_timeout/60:.0f} minutes")
    
    def _close_circuit_breaker(self) -> None:
        """Close circuit breaker"""
        self.circuit_breaker_failures = 0
        self.circuit_breaker_reset_time = None
        print("🟢 Circuit breaker closed - Yahoo Finance re-enabled")
    
    def _is_valid_json_response(self, response: requests.Response) -> bool:
        """Check if response is valid JSON"""
        content_type = response.headers.get('content-type', '').lower()
        if 'application/json' not in content_type:
            return False
        
        text = response.text.strip()
        if text.startswith('<'):
            return False
        
        try:
            json.loads(text)
            return True
        except json.JSONDecodeError:
            return False
    
    def _parse_retry_after(self, response: requests.Response) -> int:
        """Parse Retry-After header"""
        retry_after = response.headers.get('retry-after')
        if retry_after:
            try:
                return int(retry_after)
            except ValueError:
                pass
        return 60  # Default 60 seconds
    
    def _make_request(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Make a rate-limited request with proper error handling"""
        for attempt in range(max_retries):
            # Check circuit breaker
            if self._is_circuit_breaker_open():
                print("🔴 Circuit breaker is open - skipping Yahoo Finance request")
                return None
            
            # Rate limiting
            time_since_last = time.time() - self.last_request_time
            if time_since_last < self.min_request_interval:
                sleep_time = self.min_request_interval - time_since_last
                print(f"⏳ Rate limiting: waiting {sleep_time:.1f}s")
                time.sleep(sleep_time)
            
            try:
                print(f"🔄 Yahoo Finance request (attempt {attempt + 1}/{max_retries})")
                response = self.session.get(url, timeout=10)
                self.last_request_time = time.time()
                
                if response.status_code == 200:
                    if self._is_valid_json_response(response):
                        self._close_circuit_breaker()  # Success resets circuit breaker
                        return response
                    else:
                        print("⚠️ Invalid JSON response - treating as throttled")
                        self._open_circuit_breaker()
                        return None
                
                elif response.status_code == 429:
                    retry_after = self._parse_retry_after(response)
                    print(f"⚠️ Rate limited (429) - waiting {retry_after}s")
                    self._open_circuit_breaker()
                    time.sleep(retry_after)
                    continue
                
                elif response.status_code == 403:
                    print("⚠️ Forbidden (403) - possible IP blocking")
                    self._open_circuit_breaker()
                    return None
                
                else:
                    print(f"⚠️ HTTP {response.status_code} - {response.text[:100]}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Request error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                continue
        
        return None
    
    def get_stock_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get stock data with robust error handling"""
        # Try cache first
        cached_data = self._load_from_cache(symbol)
        if cached_data:
            cache_age = int(time.time() - os.path.getmtime(self._get_cache_path(symbol)))
            print(f"📦 Using cached {symbol} data (age: {cache_age}s)")
            return cached_data
        
        # Make request
        url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{symbol}?modules=financialData,quoteType,defaultKeyStatistics,assetProfile,summaryDetail"
        response = self._make_request(url)
        
        if not response:
            return None
        
        try:
            data = response.json()
            
            # Extract relevant data
            quote_summary = data.get('quoteSummary', {})
            result = quote_summary.get('result', [{}])[0]
            
            # Get price from summary detail
            summary_detail = result.get('summaryDetail', {})
            price = summary_detail.get('regularMarketPrice', {}).get('raw')
            market_cap = summary_detail.get('marketCap', {}).get('raw')
            
            if price:
                stock_data = {
                    'symbol': symbol,
                    'price': price,
                    'market_cap': market_cap,
                    'timestamp': time.time()
                }
                
                # Cache the data
                self._save_to_cache(stock_data, symbol)
                print(f"✅ Fresh {symbol} data: ${price:,.2f}")
                return stock_data
            else:
                print(f"⚠️ No price data found for {symbol}")
                return None
                
        except Exception as e:
            print(f"❌ Error parsing {symbol} data: {e}")
            return None
    
    def get_multiple_stocks(self, symbols: list) -> Dict[str, Optional[Dict[str, Any]]]:
        """Get data for multiple stocks with serialized requests"""
        results = {}
        
        for symbol in symbols:
            print(f"\n📊 Processing {symbol}...")
            data = self.get_stock_data(symbol)
            results[symbol] = data
            
            # Add delay between requests
            if symbol != symbols[-1]:  # Don't delay after last request
                time.sleep(self.min_request_interval)
        
        return results

def main():
    """Test the robust Yahoo client"""
    client = RobustYahooClient()
    
    # Test single stock
    print("Testing single stock...")
    data = client.get_stock_data("MARA")
    if data:
        print(f"✅ Success: {data}")
    else:
        print("❌ Failed to get data")
    
    # Test multiple stocks
    print("\nTesting multiple stocks...")
    symbols = ["MARA", "MSTR", "RIOT"]
    results = client.get_multiple_stocks(symbols)
    
    for symbol, data in results.items():
        if data:
            print(f"✅ {symbol}: ${data['price']:,.2f}")
        else:
            print(f"❌ {symbol}: No data")

if __name__ == "__main__":
    main()
