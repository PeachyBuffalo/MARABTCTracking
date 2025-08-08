#!/usr/bin/env python3
"""
Simple launcher for the Bitcoin Analysis GUI
"""

import sys
import os

def check_dependencies():
    """Check if required dependencies are installed"""
    # Built-in packages that don't need pip installation
    builtin_packages = ['tkinter']
    
    # External packages that need pip installation
    external_packages = ['requests', 'yfinance', 'pandas', 'numpy']
    
    missing_packages = []
    
    # Check built-in packages
    for package in builtin_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    # Check external packages
    for package in external_packages:
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
    
    # Try simple GUI first (faster loading)
    if os.path.exists('simple_gui.py'):
        print("📱 Using Simple GUI (fast loading)")
        try:
            import simple_gui
            simple_gui.main()
            return
        except Exception as e:
            print(f"⚠️ Simple GUI failed: {e}")
            print("🔄 Falling back to full GUI...")
    
    # Fall back to full GUI
    if os.path.exists('bitcoin_analysis_gui.py'):
        print("🖥️ Using Full GUI")
        try:
            import bitcoin_analysis_gui
            bitcoin_analysis_gui.main()
        except Exception as e:
            print(f"❌ Error launching GUI: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print("❌ No GUI files found")
        sys.exit(1)

if __name__ == "__main__":
    main()
