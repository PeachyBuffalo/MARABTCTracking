# Outputs Directory

This directory contains all generated analysis files organized by type:

## Directory Structure

- **`analysis_charts/`** - Contains all MNAV analysis chart PNG files
  - Files are named with pattern: `mnav_analysis_{TICKER}_{TIMEFRAME}.png`
  - Examples: `mnav_analysis_MARA_365d.png`, `mnav_analysis_TSLA_30d.png`

- **`pattern_analysis/`** - Contains all JSON pattern analysis files
  - Pattern prediction files: `pattern_prediction_*.json`
  - Comprehensive analysis files: `comprehensive_pattern_analysis_*.json`
  - Robust analysis files: `robust_pattern_analysis_*.json`

- **`nav_analysis/`** - Contains NAV/MNAV analysis specific files
  - NAV analysis charts and data files

## File Naming Conventions

### Analysis Charts
- Format: `mnav_analysis_{TICKER}_{TIMEFRAME}.png`
- Timeframes: 1d, 7d, 30d, 90d, 180d, 365d
- Tickers: MARA, SMLR, MSTR, GME, TSLA, RIOT, etc.

### Pattern Analysis Files
- Format: `{analysis_type}_{ticker}_{timestamp}.json`
- Analysis types: pattern_prediction, comprehensive_pattern_analysis, robust_pattern_analysis
- Timestamps: YYYYMMDD_HHMMSS format

## Note
These files are generated automatically by the analysis scripts and are excluded from version control via `.gitignore`.
