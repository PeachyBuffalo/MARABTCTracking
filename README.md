# Bitcoin-Holding Stocks MNav Tracking & Backtesting

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/PeachyBuffalo/MARABTCTracking/actions/workflows/python-app.yml/badge.svg)](https://github.com/PeachyBuffalo/MARABTCTracking/actions/workflows/python-app.yml)

## Overview
This project provides a robust system for:
- **Monitoring and alerting** on MNav (Market NAV) changes for multiple Bitcoin-holding stocks
- **Backtesting** MNav-based trading strategies across multiple timeframes
- **Analyzing historical relationships** between Bitcoin-holding stocks and BTC

## Features
- **Multi-Stock Monitoring**: Tracks 10+ major Bitcoin-holding companies (MSTR, MARA, RIOT, CLSK, TSLA, HUT, COIN, SQ, HIVE, CIFR)
- **Real-time Alerts**: Native macOS notifications for significant MNav changes
- **Historical Analysis**: Fetches historical stock prices (yfinance) and BTC prices (multiple APIs with fallbacks)
- **Multi-period Backtesting**: 1 day, 1 week, 1 month, 3 months, 6 months, 1 year
- **Buy/sell threshold suggestions** based on MNav distribution
- **Caching system** for fast, rate-limit-free repeated runs
- **Fallback APIs** for BTC prices if primary sources are rate-limited
- **Dynamic Data**: Automatically fetches current shares outstanding for accurate MNav calculation

## Screenshots

### Backtest Results
![Backtest Output](mnav_analysis_MSTR_365d.png)
*MNav historical analysis showing trading thresholds and distribution over time*

### Multi-Stock Monitoring
The system monitors multiple Bitcoin-holding stocks simultaneously:
- **MicroStrategy (MSTR)** - 601,550 BTC
- **Marathon Digital (MARA)** - 50,000 BTC  
- **Riot Platforms (RIOT)** - 19,225 BTC
- **CleanSpark (CLSK)** - 12,608 BTC
- **Tesla (TSLA)** - 11,509 BTC
- **Hut 8 Mining (HUT)** - 10,273 BTC
- **Coinbase (COIN)** - 9,267 BTC
- **Block Inc (SQ)** - 8,584 BTC
- **HIVE Digital (HIVE)** - 2,201 BTC
- **Cipher Mining (CIFR)** - 1,063 BTC

## Setup
1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Install terminal-notifier** (for macOS notifications):
   ```bash
   brew install terminal-notifier
   ```
4. **Set up your environment** (optional):
   - Copy `.env.example` to `.env` and fill in any API keys if needed:
     ```bash
     cp .env.example .env
     # Edit .env with your API keys (optional)
     ```
   - **Never commit your `.env` file!**
5. *(Optional but recommended)*: Use a Python virtual environment

## Usage

### Live Multi-Stock MNav Monitoring
Start monitoring all Bitcoin-holding stocks:
```bash
python mnav_alert.py
```

**Test the notification system immediately:**
```bash
python mnav_alert.py --test-now
```

**Send a test notification:**
```bash
python mnav_alert.py --send-test-notification
```

- The script checks MNav every hour and sends native macOS notifications for significant changes
- Monitors all configured stocks simultaneously
- Each stock has its own threshold (default: 5% change)

### Backtesting Individual Stocks
Run backtest for a specific stock:
```bash
python mnav_backtest.py MSTR    # MicroStrategy
python mnav_backtest.py MARA    # Marathon Digital
python mnav_backtest.py RIOT    # Riot Platforms
python mnav_backtest.py CLSK    # CleanSpark
python mnav_backtest.py TSLA    # Tesla
```

**Force refresh all data (clear cache):**
```bash
python mnav_backtest.py MSTR --clear-cache
```

**View available stocks:**
```bash
python mnav_backtest.py --help
```

- Results and suggested thresholds will be printed for each period
- Cached data is stored in the `cache/` directory for 24 hours by default
- Plots are saved with stock-specific names (e.g., `mnav_analysis_MSTR_1d.png`)

## Configuration
- **Cache duration**: Change `CACHE_DURATION_HOURS` in `mnav_backtest.py` to adjust cache expiry
- **BTC price APIs**: The script automatically tries CoinGecko, Binance, and CoinDesk for BTC prices
- **Alert thresholds**: Modify the `threshold` values in `STOCKS_TO_MONITOR` in `mnav_alert.py`
- **Monitoring interval**: Change `schedule.every(1).hours.do(check_mnav)` in `mnav_alert.py`

## MNav Calculation
MNav (Market NAV) = Stock Price / (BTC Price × BTC per Share)

Where BTC per Share = Company's BTC Holdings / Shares Outstanding

This ratio helps identify when a stock is trading at a premium or discount relative to its Bitcoin holdings.

## Notes
- **API Rate Limits**: CoinGecko has a free tier rate limit. The script will use cached data or fallback APIs if needed
- **Data Freshness**: Cached data is valid for 24 hours. Use `--clear-cache` to force a refresh
- **macOS Notifications**: Requires `terminal-notifier` to be installed via Homebrew
- **Dynamic Shares**: Shares outstanding are fetched in real-time for accurate calculations
- **.env file**: Never commit your `.env` file. Use `.env.example` as a template for sharing

## Requirements
- Python 3.8+
- macOS (for notifications)
- `terminal-notifier` (install via `brew install terminal-notifier`)
- See `requirements.txt` for Python dependencies

## License
MIT License