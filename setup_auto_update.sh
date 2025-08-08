#!/bin/bash
# Setup automatic shares outstanding updates

echo "🔄 Setting up automatic shares outstanding updates..."

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create a cron job to update shares outstanding weekly
(crontab -l 2>/dev/null; echo "0 9 * * 1 cd $SCRIPT_DIR && python update_shares_bitcointreasuries.py >> logs/shares_update.log 2>&1") | crontab -

echo "✅ Added weekly shares update to cron (Mondays at 9 AM)"
echo "📁 Logs will be saved to logs/shares_update.log"

# Create logs directory
mkdir -p logs

echo "💡 To view the cron job: crontab -l"
echo "💡 To remove the cron job: crontab -r"
