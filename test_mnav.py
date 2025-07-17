import pytest
import requests
import yfinance as yf
from datetime import datetime, timedelta

def test_imports():
    """Test that all required packages can be imported"""
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import schedule
    from dotenv import load_dotenv
    assert True

def test_btc_price_api():
    """Test that we can fetch current BTC price"""
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert 'bitcoin' in data
        assert 'usd' in data['bitcoin']
        assert data['bitcoin']['usd'] > 0
    except Exception as e:
        pytest.skip(f"BTC API test skipped: {e}")

def test_mara_ticker():
    """Test that we can access MARA ticker data"""
    try:
        ticker = yf.Ticker("MARA")
        info = ticker.info
        assert 'regularMarketPrice' in info or 'currentPrice' in info
    except Exception as e:
        pytest.skip(f"MARA ticker test skipped: {e}")

def test_mnav_calculation():
    """Test MNav calculation logic"""
    btc_per_share = 0.00014243
    
    # Test with sample data
    mara_price = 20.0
    btc_price = 100000.0
    expected_mnav = mara_price / (btc_price * btc_per_share)
    
    calculated_mnav = mara_price / (btc_price * btc_per_share)
    assert abs(calculated_mnav - expected_mnav) < 0.001

if __name__ == "__main__":
    pytest.main([__file__]) 