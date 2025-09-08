#!/bin/bash
# Automated MNav Data Workflow
# Runs daily at 9 AM

cd /Users/peachybuffalo/GitHubProjects/MARABTCTracking

echo "🤖 Starting automated MNav workflow..."
echo "Time: $(date)"

# 1. Run daily data update
echo "📊 Step 1: Running daily data update..."
python daily_data_updater.py

# 2. Check for changes
echo "🔍 Step 2: Checking for data changes..."
python auto_update_integration.py --check-changes

# 3. Run backtests if needed
echo "📈 Step 3: Running backtests..."
python auto_update_integration.py --auto-backtest

echo "✅ Automated workflow complete!"
echo "Time: $(date)"
