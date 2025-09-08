#!/usr/bin/env python3
"""
Auto Update Integration
Integrates with existing daily data updater to automatically detect and flag data changes.
"""

import os
import json
import time
from datetime import datetime
import subprocess

class AutoUpdateIntegration:
    def __init__(self):
        self.changes_file = "data_changes.json"
        self.load_changes()
        
    def load_changes(self):
        """Load or create changes tracking file"""
        if os.path.exists(self.changes_file):
            with open(self.changes_file, 'r') as f:
                self.changes = json.load(f)
        else:
            self.changes = {
                'last_check': {},
                'pending_updates': [],
                'auto_detection_enabled': True
            }
            self.save_changes()
    
    def save_changes(self):
        """Save changes tracking file"""
        with open(self.changes_file, 'w') as f:
            json.dump(self.changes, f, indent=2)
    
    def run_daily_update(self):
        """Run the daily data updater and detect changes"""
        print("🔄 Running daily data update...")
        
        try:
            # Run the existing daily data updater
            result = subprocess.run(['python', 'daily_data_updater.py'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ Daily update completed successfully")
                self.analyze_update_output(result.stdout)
            else:
                print(f"❌ Daily update failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("❌ Daily update timed out")
        except Exception as e:
            print(f"❌ Error running daily update: {e}")
    
    def analyze_update_output(self, output):
        """Analyze the daily update output for changes"""
        print("🔍 Analyzing update output for changes...")
        
        # Look for patterns indicating data changes
        changes_detected = []
        
        # Check for BTC data updates
        if "BTC data is up to date" not in output:
            changes_detected.append("BTC data updated")
        
        # Check for stock data updates
        if "Successfully updated" in output:
            # Extract the number of stocks updated
            import re
            match = re.search(r'Successfully updated (\d+) stocks', output)
            if match and int(match.group(1)) > 0:
                changes_detected.append(f"{match.group(1)} stocks updated")
        
        # Check for errors that might indicate data issues
        if "Failed to update" in output:
            failed_stocks = []
            lines = output.split('\n')
            for line in lines:
                if "Failed to update" in line:
                    stock = line.split()[2]  # Extract stock symbol
                    failed_stocks.append(stock)
            if failed_stocks:
                changes_detected.append(f"Failed updates: {', '.join(failed_stocks)}")
        
        if changes_detected:
            self.record_changes(changes_detected)
        else:
            print("📊 No significant changes detected")
    
    def record_changes(self, changes):
        """Record detected changes"""
        timestamp = datetime.now().isoformat()
        
        for change in changes:
            self.changes['pending_updates'].append({
                'timestamp': timestamp,
                'change': change,
                'status': 'pending'
            })
        
        self.save_changes()
        print(f"📝 Recorded {len(changes)} changes")
    
    def check_for_manual_updates_needed(self):
        """Check if manual updates are needed based on detected changes"""
        if not self.changes['pending_updates']:
            print("✅ No pending updates")
            return
        
        print("📋 Pending updates detected:")
        for update in self.changes['pending_updates']:
            if update['status'] == 'pending':
                print(f"  • {update['change']} ({update['timestamp']})")
        
        print("\n💡 Consider running:")
        print("  python update_historical_data.py")
        print("  python mnav_backtest.py SYMBOL --clear-cache")
    
    def auto_run_backtests(self):
        """Automatically run backtests for companies with changes"""
        print("🤖 Auto-running backtests...")
        
        # Get list of companies that might need updates
        companies = ['MSTR', 'MARA', 'RIOT', 'CLSK', 'TSLA', 'HUT', 'COIN', 'SQ', 'SMLR', 'HIVE', 'CIFR']
        
        for symbol in companies:
            print(f"\n{'='*30}")
            print(f"Running backtest for {symbol}...")
            
            try:
                # Run backtest with cache clearing
                result = subprocess.run(['python', 'mnav_backtest.py', symbol, '--clear-cache'], 
                                      capture_output=True, text=True, timeout=600)
                
                if result.returncode == 0:
                    print(f"✅ {symbol} backtest completed")
                else:
                    print(f"❌ {symbol} backtest failed")
                    
            except subprocess.TimeoutExpired:
                print(f"❌ {symbol} backtest timed out")
            except Exception as e:
                print(f"❌ Error running {symbol} backtest: {e}")
            
            time.sleep(2)  # Rate limiting
        
        print("\n✅ Auto-backtest complete!")
    
    def setup_automation(self):
        """Set up automated daily workflow"""
        print("🤖 Setting up automated workflow...")
        
        # Create automation script
        automation_script = """#!/bin/bash
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
"""
        
        with open("automated_workflow.sh", "w") as f:
            f.write(automation_script)
        
        os.chmod("automated_workflow.sh", 0o755)
        
        print("📅 Automation setup instructions:")
        print("1. Open terminal and run: crontab -e")
        print("2. Add this line for daily automation at 9 AM:")
        print("   0 9 * * * /Users/peachybuffalo/GitHubProjects/MARABTCTracking/automated_workflow.sh")
        print("3. Save and exit")
        print("\n💡 The workflow will run automatically every day at 9 AM")
        print("   - Updates data")
        print("   - Checks for changes")
        print("   - Runs backtests")
    
    def generate_status_report(self):
        """Generate a status report of the system"""
        print("📊 MNav System Status Report")
        print("=" * 40)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Check data freshness
        print("📈 Data Freshness:")
        for symbol in ['MSTR', 'MARA', 'SMLR']:
            cache_file = f"cache/mnav_{symbol.lower()}_*.pkl"
            if os.path.exists(cache_file):
                mtime = os.path.getmtime(cache_file)
                age_hours = (time.time() - mtime) / 3600
                print(f"  {symbol}: {age_hours:.1f} hours old")
            else:
                print(f"  {symbol}: No cache found")
        
        print()
        print("🔄 Pending Updates:")
        if self.changes['pending_updates']:
            for update in self.changes['pending_updates'][-5:]:  # Last 5
                print(f"  • {update['change']} ({update['timestamp']})")
        else:
            print("  None")
        
        print()
        print("💡 Recommendations:")
        if self.changes['pending_updates']:
            print("  • Run: python update_historical_data.py")
            print("  • Run: python mnav_backtest.py SYMBOL --clear-cache")
        else:
            print("  • System is up to date")
            print("  • Consider running backtests for latest analysis")

def main():
    integration = AutoUpdateIntegration()
    
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--daily-update':
            integration.run_daily_update()
        elif sys.argv[1] == '--check-changes':
            integration.check_for_manual_updates_needed()
        elif sys.argv[1] == '--auto-backtest':
            integration.auto_run_backtests()
        elif sys.argv[1] == '--setup-automation':
            integration.setup_automation()
        elif sys.argv[1] == '--status':
            integration.generate_status_report()
        else:
            print("❌ Unknown option")
    else:
        print("Auto Update Integration")
        print("======================")
        print()
        print("Usage:")
        print("  python auto_update_integration.py --daily-update    # Run daily update")
        print("  python auto_update_integration.py --check-changes   # Check for updates needed")
        print("  python auto_update_integration.py --auto-backtest   # Run all backtests")
        print("  python auto_update_integration.py --setup-automation # Set up automation")
        print("  python auto_update_integration.py --status          # Generate status report")
        print()
        print("💡 For full automation, use --setup-automation")

if __name__ == "__main__":
    main()

