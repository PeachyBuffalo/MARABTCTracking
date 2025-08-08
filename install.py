#!/usr/bin/env python3
"""
Installation script for Bitcoin Analysis Suite
For non-technical users
"""

import os
import sys
import subprocess
import platform

def print_banner():
    print("=" * 60)
    print("🚀 Bitcoin Analysis Suite - Installation")
    print("=" * 60)

def check_python():
    """Check if Python is installed"""
    print("🔍 Checking Python installation...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} is installed")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        # Upgrade pip
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        print("✅ Upgraded pip")
        
        # Install requirements
        if os.path.exists('requirements.txt'):
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                          check=True, capture_output=True)
            print("✅ Installed Python dependencies")
        else:
            print("⚠️ requirements.txt not found, installing basic dependencies...")
            basic_deps = ['requests', 'yfinance', 'pandas', 'numpy', 'matplotlib', 'schedule', 'python-dotenv', 'beautifulsoup4']
            for dep in basic_deps:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                              check=True, capture_output=True)
            print("✅ Installed basic dependencies")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_terminal_notifier():
    """Check if terminal-notifier is installed (macOS)"""
    if platform.system() == "Darwin":  # macOS
        print("\n🔔 Checking terminal-notifier (for notifications)...")
        
        try:
            result = subprocess.run(['which', 'terminal-notifier'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ terminal-notifier is installed")
                return True
            else:
                print("⚠️ terminal-notifier not found")
                print("💡 Install with: brew install terminal-notifier")
                print("   Or download from: https://github.com/julienXX/terminal-notifier")
                return False
        except FileNotFoundError:
            print("⚠️ Could not check for terminal-notifier")
            return False
    else:
        print("ℹ️ terminal-notifier check skipped (not macOS)")
        return True

def create_cache_directory():
    """Create cache directory"""
    print("\n📁 Creating cache directory...")
    
    try:
        os.makedirs('cache', exist_ok=True)
        print("✅ Cache directory created")
        return True
    except Exception as e:
        print(f"❌ Error creating cache directory: {e}")
        return False

def test_installation():
    """Test the installation"""
    print("\n🧪 Testing installation...")
    
    # Test imports
    try:
        import requests
        import yfinance
        import pandas
        import numpy
        print("✅ All Python packages imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test GUI
    try:
        import tkinter
        print("✅ GUI framework available")
    except ImportError:
        print("❌ tkinter not available (GUI won't work)")
        return False
    
    return True

def main():
    print_banner()
    
    # Check Python
    if not check_python():
        print("\n❌ Installation failed: Python version issue")
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Installation failed: Dependency installation error")
        return False
    
    # Check terminal-notifier
    check_terminal_notifier()
    
    # Create cache directory
    if not create_cache_directory():
        print("\n❌ Installation failed: Could not create cache directory")
        return False
    
    # Test installation
    if not test_installation():
        print("\n❌ Installation failed: Test failed")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Installation completed successfully!")
    print("=" * 60)
    
    print("\n🚀 To launch the GUI:")
    print("   python launch_gui.py")
    
    print("\n💻 To use command line tools:")
    print("   python analyze_stock.py MSTR")
    print("   python mnav_alert.py --test-now")
    
    print("\n📚 For more information, see README.md")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
