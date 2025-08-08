#!/usr/bin/env python3
"""
Bitcoin Analysis GUI
User-friendly interface for Bitcoin NAV and MNav analysis
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import subprocess
import sys
import os
import json
from datetime import datetime
import webbrowser

class BitcoinAnalysisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bitcoin Analysis Suite")
        self.root.geometry("1000x700")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_analysis_tab()
        self.create_alerts_tab()
        self.create_backtest_tab()
        self.create_settings_tab()
        self.create_logs_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief='sunken')
        self.status_bar.pack(side='bottom', fill='x')

    def create_analysis_tab(self):
        """Create the main analysis tab"""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="📊 Analysis")
        
        # Stock selection
        stock_frame = ttk.LabelFrame(analysis_frame, text="Stock Selection", padding=10)
        stock_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(stock_frame, text="Select Stock:").pack(side='left')
        self.stock_var = tk.StringVar(value="MSTR")
        stock_combo = ttk.Combobox(stock_frame, textvariable=self.stock_var, 
                                  values=["MSTR", "MARA", "RIOT", "CLSK", "TSLA", "COIN", "SQ", "SMLR"])
        stock_combo.pack(side='left', padx=5)
        
        ttk.Button(stock_frame, text="Analyze", command=self.run_analysis).pack(side='left', padx=5)
        ttk.Button(stock_frame, text="Analyze All", command=self.run_analysis_all).pack(side='left', padx=5)
        
        # Results area
        results_frame = ttk.LabelFrame(analysis_frame, text="Analysis Results", padding=10)
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=20)
        self.results_text.pack(fill='both', expand=True)

    def create_alerts_tab(self):
        """Create the alerts tab"""
        alerts_frame = ttk.Frame(self.notebook)
        self.notebook.add(alerts_frame, text="🔔 Alerts")
        
        # Alert controls
        controls_frame = ttk.LabelFrame(alerts_frame, text="Alert Controls", padding=10)
        controls_frame.pack(fill='x', padx=10, pady=5)
        
        # Test alerts
        ttk.Button(controls_frame, text="Test Alert Now", 
                  command=self.test_alert).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Start Alert Monitor", 
                  command=self.start_alert_monitor).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Stop Alert Monitor", 
                  command=self.stop_alert_monitor).pack(side='left', padx=5)
        
        # Alert status
        status_frame = ttk.LabelFrame(alerts_frame, text="Alert Status", padding=10)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.alert_status_var = tk.StringVar(value="Stopped")
        ttk.Label(status_frame, text="Status:").pack(side='left')
        ttk.Label(status_frame, textvariable=self.alert_status_var).pack(side='left', padx=5)
        
        # Alert log
        log_frame = ttk.LabelFrame(alerts_frame, text="Alert Log", padding=10)
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.alert_log = scrolledtext.ScrolledText(log_frame, height=15)
        self.alert_log.pack(fill='both', expand=True)

    def create_backtest_tab(self):
        """Create the backtest tab"""
        backtest_frame = ttk.Frame(self.notebook)
        self.notebook.add(backtest_frame, text="📈 Backtest")
        
        # Backtest controls
        controls_frame = ttk.LabelFrame(backtest_frame, text="Backtest Controls", padding=10)
        controls_frame.pack(fill='x', padx=10, pady=5)
        
        # Period selection
        ttk.Label(controls_frame, text="Period:").pack(side='left')
        self.period_var = tk.StringVar(value="90d")
        period_combo = ttk.Combobox(controls_frame, textvariable=self.period_var,
                                   values=["1d", "7d", "30d", "90d", "180d", "365d"])
        period_combo.pack(side='left', padx=5)
        
        ttk.Button(controls_frame, text="Run Backtest", 
                  command=self.run_backtest).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="View Results", 
                  command=self.view_backtest_results).pack(side='left', padx=5)
        
        # Backtest results
        results_frame = ttk.LabelFrame(backtest_frame, text="Backtest Results", padding=10)
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.backtest_text = scrolledtext.ScrolledText(results_frame, height=20)
        self.backtest_text.pack(fill='both', expand=True)

    def create_settings_tab(self):
        """Create the settings tab"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # Data update settings
        data_frame = ttk.LabelFrame(settings_frame, text="Data Management", padding=10)
        data_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(data_frame, text="Update Shares Outstanding", 
                  command=self.update_shares).pack(side='left', padx=5)
        ttk.Button(data_frame, text="Clear Cache", 
                  command=self.clear_cache).pack(side='left', padx=5)
        ttk.Button(data_frame, text="View GitHub Actions", 
                  command=self.open_github_actions).pack(side='left', padx=5)
        
        # Configuration
        config_frame = ttk.LabelFrame(settings_frame, text="Configuration", padding=10)
        config_frame.pack(fill='x', padx=10, pady=5)
        
        # Alert threshold
        ttk.Label(config_frame, text="Alert Threshold (%):").pack(side='left')
        self.threshold_var = tk.StringVar(value="5.0")
        threshold_entry = ttk.Entry(config_frame, textvariable=self.threshold_var, width=10)
        threshold_entry.pack(side='left', padx=5)
        
        ttk.Button(config_frame, text="Save Settings", 
                  command=self.save_settings).pack(side='left', padx=5)
        
        # System info
        info_frame = ttk.LabelFrame(settings_frame, text="System Information", padding=10)
        info_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=10)
        self.info_text.pack(fill='both', expand=True)
        
        # Load system info
        self.load_system_info()

    def create_logs_tab(self):
        """Create the logs tab"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="📋 Logs")
        
        # Log controls
        controls_frame = ttk.LabelFrame(logs_frame, text="Log Controls", padding=10)
        controls_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(controls_frame, text="Refresh Logs", 
                  command=self.refresh_logs).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Clear Logs", 
                  command=self.clear_logs).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Export Logs", 
                  command=self.export_logs).pack(side='left', padx=5)
        
        # Log display
        log_frame = ttk.LabelFrame(logs_frame, text="Application Logs", padding=10)
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.logs_text = scrolledtext.ScrolledText(log_frame, height=20)
        self.logs_text.pack(fill='both', expand=True)
        
        # Load initial logs
        self.refresh_logs()

    def run_analysis(self):
        """Run analysis for selected stock"""
        stock = self.stock_var.get()
        self.status_var.set(f"Analyzing {stock}...")
        
        def run():
            try:
                result = subprocess.run([sys.executable, "analyze_stock.py", stock], 
                                      capture_output=True, text=True, timeout=30)
                
                self.root.after(0, lambda: self.display_results(result.stdout, result.stderr))
            except Exception as e:
                self.root.after(0, lambda: self.display_results("", f"Error: {e}"))
        
        threading.Thread(target=run, daemon=True).start()

    def run_analysis_all(self):
        """Run analysis for all stocks"""
        stocks = ["MSTR", "MARA", "RIOT", "CLSK", "TSLA", "COIN", "SQ", "SMLR"]
        self.status_var.set("Analyzing all stocks...")
        
        def run():
            all_results = ""
            for stock in stocks:
                try:
                    result = subprocess.run([sys.executable, "analyze_stock.py", stock], 
                                          capture_output=True, text=True, timeout=30)
                    all_results += f"\n{'='*60}\n{stock} Analysis\n{'='*60}\n"
                    all_results += result.stdout
                    if result.stderr:
                        all_results += f"Errors: {result.stderr}\n"
                except Exception as e:
                    all_results += f"Error analyzing {stock}: {e}\n"
            
            self.root.after(0, lambda: self.display_results(all_results, ""))
        
        threading.Thread(target=run, daemon=True).start()

    def test_alert(self):
        """Test the alert system"""
        self.status_var.set("Testing alert...")
        
        def run():
            try:
                result = subprocess.run([sys.executable, "mnav_alert.py", "--test-now"], 
                                      capture_output=True, text=True, timeout=30)
                
                self.root.after(0, lambda: self.log_alert(result.stdout, result.stderr))
            except Exception as e:
                self.root.after(0, lambda: self.log_alert("", f"Error: {e}"))
        
        threading.Thread(target=run, daemon=True).start()

    def start_alert_monitor(self):
        """Start the alert monitor"""
        self.alert_status_var.set("Running")
        self.status_var.set("Starting alert monitor...")
        
        def run():
            try:
                # Start the alert monitor in background
                self.alert_process = subprocess.Popen([sys.executable, "mnav_alert.py"], 
                                                    stdout=subprocess.PIPE, 
                                                    stderr=subprocess.PIPE,
                                                    text=True)
                
                self.root.after(0, lambda: self.log_alert("Alert monitor started successfully", ""))
            except Exception as e:
                self.root.after(0, lambda: self.log_alert("", f"Error starting alert monitor: {e}"))
        
        threading.Thread(target=run, daemon=True).start()

    def stop_alert_monitor(self):
        """Stop the alert monitor"""
        self.alert_status_var.set("Stopped")
        self.status_var.set("Stopping alert monitor...")
        
        try:
            if hasattr(self, 'alert_process'):
                self.alert_process.terminate()
                self.log_alert("Alert monitor stopped", "")
        except Exception as e:
            self.log_alert("", f"Error stopping alert monitor: {e}")

    def run_backtest(self):
        """Run backtest for selected period"""
        period = self.period_var.get()
        self.status_var.set(f"Running backtest for {period}...")
        
        def run():
            try:
                result = subprocess.run([sys.executable, "mnav_backtest.py"], 
                                      capture_output=True, text=True, timeout=60)
                
                self.root.after(0, lambda: self.display_backtest_results(result.stdout, result.stderr))
            except Exception as e:
                self.root.after(0, lambda: self.display_backtest_results("", f"Error: {e}"))
        
        threading.Thread(target=run, daemon=True).start()

    def view_backtest_results(self):
        """View backtest results"""
        try:
            # Look for analysis images
            image_files = [f for f in os.listdir('.') if f.endswith('.png') and 'analysis' in f]
            if image_files:
                # Open the most recent one
                latest_image = max(image_files, key=os.path.getctime)
                os.system(f"open {latest_image}")
            else:
                messagebox.showinfo("No Results", "No backtest results found. Run a backtest first.")
        except Exception as e:
            messagebox.showerror("Error", f"Error viewing results: {e}")

    def update_shares(self):
        """Update shares outstanding"""
        self.status_var.set("Updating shares outstanding...")
        
        def run():
            try:
                result = subprocess.run([sys.executable, "update_shares_bitcointreasuries.py"], 
                                      capture_output=True, text=True, timeout=30)
                
                self.root.after(0, lambda: self.log_alert(result.stdout, result.stderr))
            except Exception as e:
                self.root.after(0, lambda: self.log_alert("", f"Error: {e}"))
        
        threading.Thread(target=run, daemon=True).start()

    def clear_cache(self):
        """Clear cache files"""
        try:
            import shutil
            if os.path.exists('cache'):
                shutil.rmtree('cache')
                os.makedirs('cache')
            messagebox.showinfo("Success", "Cache cleared successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Error clearing cache: {e}")

    def open_github_actions(self):
        """Open GitHub Actions page"""
        webbrowser.open("https://github.com/PeachyBuffalo/MARABTCTracking/actions")

    def save_settings(self):
        """Save settings"""
        try:
            settings = {
                'alert_threshold': float(self.threshold_var.get()),
                'last_updated': datetime.now().isoformat()
            }
            
            with open('gui_settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
            
            messagebox.showinfo("Success", "Settings saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving settings: {e}")

    def load_system_info(self):
        """Load system information"""
        info = f"""
System Information:
==================
Python Version: {sys.version}
Working Directory: {os.getcwd()}
Files Available:
"""
        
        # List available scripts
        scripts = ['analyze_stock.py', 'mnav_alert.py', 'mnav_backtest.py', 
                  'update_shares_bitcointreasuries.py']
        
        for script in scripts:
            if os.path.exists(script):
                info += f"✅ {script}\n"
            else:
                info += f"❌ {script}\n"
        
        # Check cache
        if os.path.exists('cache'):
            cache_size = len(os.listdir('cache'))
            info += f"\nCache: {cache_size} files\n"
        else:
            info += "\nCache: Not found\n"
        
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info)

    def refresh_logs(self):
        """Refresh logs display"""
        log_content = "Application Logs:\n"
        log_content += "=" * 50 + "\n\n"
        
        # Add recent activity
        log_content += f"GUI Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        log_content += f"Current Directory: {os.getcwd()}\n"
        log_content += f"Python Executable: {sys.executable}\n\n"
        
        # Check for log files
        log_files = [f for f in os.listdir('.') if f.endswith('.log')]
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    log_content += f"=== {log_file} ===\n"
                    log_content += f.read() + "\n"
            except:
                log_content += f"Could not read {log_file}\n"
        
        self.logs_text.delete(1.0, tk.END)
        self.logs_text.insert(1.0, log_content)

    def clear_logs(self):
        """Clear logs display"""
        self.logs_text.delete(1.0, tk.END)
        self.logs_text.insert(1.0, "Logs cleared\n")

    def export_logs(self):
        """Export logs to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.logs_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Logs exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error exporting logs: {e}")

    def display_results(self, stdout, stderr):
        """Display analysis results"""
        self.results_text.delete(1.0, tk.END)
        if stdout:
            self.results_text.insert(1.0, stdout)
        if stderr:
            self.results_text.insert(tk.END, f"\nErrors:\n{stderr}")
        self.status_var.set("Analysis complete")

    def display_backtest_results(self, stdout, stderr):
        """Display backtest results"""
        self.backtest_text.delete(1.0, tk.END)
        if stdout:
            self.backtest_text.insert(1.0, stdout)
        if stderr:
            self.backtest_text.insert(tk.END, f"\nErrors:\n{stderr}")
        self.status_var.set("Backtest complete")

    def log_alert(self, stdout, stderr):
        """Log alert activity"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] "
        
        if stdout:
            log_entry += stdout
        if stderr:
            log_entry += f"\nError: {stderr}"
        
        self.alert_log.insert(tk.END, log_entry + "\n")
        self.alert_log.see(tk.END)
        self.status_var.set("Alert operation complete")

def main():
    root = tk.Tk()
    app = BitcoinAnalysisGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
