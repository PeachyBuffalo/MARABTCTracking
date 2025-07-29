#!/usr/bin/env python3
"""
Setup Daily Data Updates
Helps configure automated daily data updates to avoid rate limiting.
"""

import os
import sys
import platform
from datetime import datetime

def create_cron_job():
    """Create a cron job for daily data updates"""
    print("🕐 Setting up automated daily data updates...")
    print()
    
    # Get the current directory
    current_dir = os.getcwd()
    python_path = sys.executable
    script_path = os.path.join(current_dir, "daily_data_updater.py")
    
    print(f"📁 Current directory: {current_dir}")
    print(f"🐍 Python path: {python_path}")
    print(f"📜 Script path: {script_path}")
    print()
    
    # Create the cron command
    cron_command = f"0 9 * * * cd {current_dir} && {python_path} {script_path} >> daily_update.log 2>&1"
    
    print("📋 Cron job command:")
    print(f"   {cron_command}")
    print()
    
    # Instructions for different platforms
    system = platform.system()
    
    if system == "Darwin":  # macOS
        print("🍎 macOS Instructions:")
        print("1. Open Terminal")
        print("2. Run: crontab -e")
        print("3. Add this line:")
        print(f"   {cron_command}")
        print("4. Save and exit (Ctrl+X, Y, Enter)")
        print("5. Verify with: crontab -l")
        
    elif system == "Linux":
        print("🐧 Linux Instructions:")
        print("1. Open terminal")
        print("2. Run: crontab -e")
        print("3. Add this line:")
        print(f"   {cron_command}")
        print("4. Save and exit (Ctrl+X, Y, Enter)")
        print("5. Verify with: crontab -l")
        
    elif system == "Windows":
        print("🪟 Windows Instructions:")
        print("1. Open Task Scheduler (taskschd.msc)")
        print("2. Create Basic Task")
        print("3. Name: 'Daily Data Update'")
        print("4. Trigger: Daily at 9:00 AM")
        print("5. Action: Start a program")
        print(f"6. Program: {python_path}")
        print(f"7. Arguments: {script_path}")
        print(f"8. Start in: {current_dir}")
        
    else:
        print("❓ Unknown system, manual setup required")
        print("Add this cron job to run daily at 9:00 AM:")
        print(f"   {cron_command}")
    
    print()
    print("💡 The job will run daily at 9:00 AM")
    print("💡 Logs will be saved to 'daily_update.log'")
    print("💡 Check logs with: tail -f daily_update.log")

def create_systemd_service():
    """Create a systemd service for Linux systems"""
    if platform.system() != "Linux":
        print("❌ systemd services are only available on Linux")
        return
    
    print("🐧 Creating systemd service for Linux...")
    
    current_dir = os.getcwd()
    python_path = sys.executable
    script_path = os.path.join(current_dir, "daily_data_updater.py")
    
    service_content = f"""[Unit]
Description=Daily Data Updater for MNav Trading
After=network.target

[Service]
Type=oneshot
User={os.getenv('USER', 'root')}
WorkingDirectory={current_dir}
ExecStart={python_path} {script_path}
StandardOutput=append:/var/log/daily-updater.log
StandardError=append:/var/log/daily-updater.log

[Install]
WantedBy=multi-user.target
"""
    
    timer_content = f"""[Unit]
Description=Run Daily Data Updater at 9:00 AM
Requires=daily-updater.service

[Timer]
OnCalendar=*-*-* 09:00:00
Persistent=true

[Install]
WantedBy=timers.target
"""
    
    print("📄 Service file content:")
    print(service_content)
    print()
    print("📄 Timer file content:")
    print(timer_content)
    print()
    print("📝 Installation instructions:")
    print("1. Create service file: sudo nano /etc/systemd/system/daily-updater.service")
    print("2. Paste the service content above")
    print("3. Create timer file: sudo nano /etc/systemd/system/daily-updater.timer")
    print("4. Paste the timer content above")
    print("5. Enable and start: sudo systemctl enable daily-updater.timer")
    print("6. Start timer: sudo systemctl start daily-updater.timer")
    print("7. Check status: sudo systemctl status daily-updater.timer")

def test_daily_updater():
    """Test the daily updater script"""
    print("🧪 Testing daily data updater...")
    print()
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, "daily_data_updater.py", "--summary"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Daily updater script is working!")
            print("📊 Current data status:")
            print(result.stdout)
        else:
            print("❌ Daily updater script has issues:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Error testing daily updater: {e}")

def main():
    """Main function"""
    print("🔄 Daily Data Update Setup")
    print("=" * 40)
    print()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--cron':
            create_cron_job()
            return
        elif sys.argv[1] == '--systemd':
            create_systemd_service()
            return
        elif sys.argv[1] == '--test':
            test_daily_updater()
            return
        elif sys.argv[1] == '--help':
            print("Usage: python setup_daily_updates.py [--cron] [--systemd] [--test] [--help]")
            print("  --cron: Setup cron job (macOS/Linux)")
            print("  --systemd: Setup systemd service (Linux)")
            print("  --test: Test the daily updater")
            print("  --help: Show this help")
            return
    
    print("Choose your setup method:")
    print("1. Cron job (recommended for macOS/Linux)")
    print("2. systemd service (Linux only)")
    print("3. Test the daily updater")
    print()
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == "1":
        create_cron_job()
    elif choice == "2":
        create_systemd_service()
    elif choice == "3":
        test_daily_updater()
    else:
        print("❌ Invalid choice")
        return
    
    print()
    print("🎉 Setup complete!")
    print("💡 Run 'python daily_data_updater.py --summary' to check data status")

if __name__ == "__main__":
    main() 