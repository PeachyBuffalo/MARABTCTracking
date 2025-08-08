#!/usr/bin/env python3
"""
Smart GUI Launcher - Automatically handles Python environment issues
"""

import sys
import os
import subprocess

def check_tkinter():
    """Check if tkinter is available"""
    try:
        import tkinter
        return True
    except ImportError:
        return False

def find_working_python():
    """Find a Python installation that has tkinter"""
    # Try current Python first
    if check_tkinter():
        return sys.executable
    
    # Try system Python (Anaconda)
    try:
        result = subprocess.run(['/opt/anaconda3/bin/python', '-c', 'import tkinter'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return '/opt/anaconda3/bin/python'
    except:
        pass
    
    # Try python3
    try:
        result = subprocess.run(['python3', '-c', 'import tkinter'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return 'python3'
    except:
        pass
    
    return None

def main():
    print("🚀 Smart GUI Launcher")
    print("=" * 30)
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if in_venv:
        print("⚠️  Detected virtual environment")
        print("💡 Virtual environments often have tkinter issues")
        print("🔄 Trying to find system Python with tkinter...")
    
    # Find working Python
    python_exe = find_working_python()
    
    if not python_exe:
        print("❌ No Python installation with tkinter found")
        print("\n💡 Solutions:")
        print("   1. Install tkinter: brew install python-tk")
        print("   2. Use system Python instead of virtual environment")
        print("   3. Recreate virtual environment with tkinter support")
        sys.exit(1)
    
    if python_exe != sys.executable:
        print(f"✅ Found working Python: {python_exe}")
        print("🔄 Launching GUI with system Python...")
        
        # Launch GUI with the working Python
        try:
            subprocess.run([python_exe, 'simple_gui.py'])
        except KeyboardInterrupt:
            print("\n👋 GUI closed by user")
        except Exception as e:
            print(f"❌ Error launching GUI: {e}")
            sys.exit(1)
    else:
        print("✅ Current Python has tkinter")
        print("🔄 Launching GUI...")
        
        # Launch GUI with current Python
        try:
            import simple_gui
            simple_gui.main()
        except KeyboardInterrupt:
            print("\n👋 GUI closed by user")
        except Exception as e:
            print(f"❌ Error launching GUI: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
