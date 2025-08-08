#!/usr/bin/env python3
"""
Simple launcher for the Bitcoin Analysis GUI
"""

import sys
import os

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['tkinter', 'requests', 'yfinance', 'pandas', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def main():
    print("🚀 Launching Bitcoin Analysis GUI...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check if GUI file exists
    if not os.path.exists('bitcoin_analysis_gui.py'):
        print("❌ GUI file not found: bitcoin_analysis_gui.py")
        sys.exit(1)
    
    # Launch GUI
    try:
        import bitcoin_analysis_gui
        bitcoin_analysis_gui.main()
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
