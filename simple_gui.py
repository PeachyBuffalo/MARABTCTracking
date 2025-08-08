#!/usr/bin/env python3
"""
Simple Bitcoin Analysis GUI - Fast Loading Version
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image, ImageTk  # For image display
import time # Added for time.time()

# Load environment variables from .env file
load_dotenv()

class SimpleBitcoinGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bitcoin Analysis GUI")
        
        # Configure style for better visibility
        style = ttk.Style()
        style.theme_use('clam')  # Use clam theme for better button visibility
        
        # Configure custom button style
        style.configure('Action.TButton', 
                      font=('Arial', 10, 'bold'),
                      padding=(10, 5),
                      background='#007bff',
                      foreground='white')
        
        # Make window resizable and set minimum size
        self.root.resizable(True, True)
        self.root.minsize(800, 600)
        
        # Configure grid weights for responsive layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # Configure main frame grid weights
        main_frame.columnconfigure(0, weight=1)  # Buttons column
        main_frame.columnconfigure(1, weight=3)  # Results column (3x wider)
        main_frame.rowconfigure(0, weight=1)     # Results row (expandable)
        
        # Create buttons frame - no canvas, direct layout
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.rowconfigure(0, weight=1)
        
        # Create scrollable frame for buttons
        canvas = tk.Canvas(buttons_frame, bg='#f0f0f0')
        scrollbar = ttk.Scrollbar(buttons_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configure scrollable frame to expand
        scrollable_frame.columnconfigure(0, weight=1)
        
        # Bind scrollable frame to canvas
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_reqwidth())
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Configure canvas grid
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        buttons_frame.rowconfigure(0, weight=1)
        buttons_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(scrollable_frame, text="Bitcoin Analysis Tools", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Analysis section
        analysis_frame = ttk.LabelFrame(scrollable_frame, text="Analysis", padding="10")
        analysis_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        analysis_frame.columnconfigure(0, weight=1)
        
        # Force fresh data checkbox
        self.force_fresh_var = tk.BooleanVar()
        fresh_checkbox = ttk.Checkbutton(analysis_frame, text="Force Fresh Data", variable=self.force_fresh_var)
        fresh_checkbox.grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        
        self.create_button(analysis_frame, "Analyze MARA", lambda: self.run_script("analyze_stock.py", ["MARA"] + (["--fresh"] if self.force_fresh_var.get() else [])), 1)
        self.create_button(analysis_frame, "Analyze MSTR", lambda: self.run_script("analyze_stock.py", ["MSTR"] + (["--fresh"] if self.force_fresh_var.get() else [])), 2)
        self.create_button(analysis_frame, "Analyze SMLR", lambda: self.run_script("analyze_stock.py", ["SMLR"] + (["--fresh"] if self.force_fresh_var.get() else [])), 3)
        self.create_button(analysis_frame, "Analyze All Stocks", lambda: self.run_script("analyze_stock.py", ["MARA"] + (["--fresh"] if self.force_fresh_var.get() else [])), 4)
        
        # Alerts section
        alerts_frame = ttk.LabelFrame(scrollable_frame, text="Alerts", padding="10")
        alerts_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        alerts_frame.columnconfigure(0, weight=1)
        
        self.create_button(alerts_frame, "Test Alert", lambda: self.run_script("mnav_alert.py", ["--test-now"]), 0)
        self.create_button(alerts_frame, "Start Monitoring", lambda: self.run_script("mnav_alert.py", []), 1)
        
        # Backtest section
        backtest_frame = ttk.LabelFrame(scrollable_frame, text="Backtesting", padding="10")
        backtest_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        backtest_frame.columnconfigure(0, weight=1)
        
        self.create_button(backtest_frame, "Backtest MARA", lambda: self.run_script("mnav_backtest.py", ["MARA"]), 0)
        self.create_button(backtest_frame, "Backtest MSTR", lambda: self.run_script("mnav_backtest.py", ["MSTR"]), 1)
        self.create_button(backtest_frame, "Backtest SMLR", lambda: self.run_script("mnav_backtest.py", ["SMLR"]), 2)
        
        # Settings section
        settings_frame = ttk.LabelFrame(scrollable_frame, text="Settings", padding="10")
        settings_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(0, weight=1)
        
        self.create_button(settings_frame, "Check Current Price", lambda: self.run_script("check_price.py", ["MARA"]), 0)
        self.create_button(settings_frame, "Update Shares", lambda: self.run_script("update_shares_bitcointreasuries.py", []), 1)
        self.create_button(settings_frame, "Clear Cache", self.clear_cache, 2)
        
        # Results area
        results_frame = ttk.Frame(main_frame)
        results_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        # Results header with tabs
        results_header = ttk.Frame(results_frame)
        results_header.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        results_header.columnconfigure(0, weight=1)
        
        ttk.Label(results_header, text="Results:", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky=tk.W)
        
        # Add image display button
        self.show_image_btn = ttk.Button(results_header, text="Show Latest Image", command=self.show_latest_image)
        self.show_image_btn.grid(row=0, column=1, sticky=tk.E, padx=(10, 0))
        
        # Add image selector dropdown
        self.image_var = tk.StringVar()
        self.image_selector = ttk.Combobox(results_header, textvariable=self.image_var, state="readonly", width=20)
        self.image_selector.grid(row=0, column=2, sticky=tk.E, padx=(5, 0))
        self.image_selector.bind('<<ComboboxSelected>>', self.on_image_selected)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        
        # Text tab
        text_frame = ttk.Frame(self.notebook)
        self.notebook.add(text_frame, text="Output")
        
        # Create results text area with better styling
        self.results_text = scrolledtext.ScrolledText(
            text_frame, 
            height=25, 
            width=70,
            font=("Consolas", 10),
            bg="#f8f9fa",
            fg="#212529"
        )
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        # Image tab
        image_frame = ttk.Frame(self.notebook)
        self.notebook.add(image_frame, text="Images")
        
        # Create a fixed-size canvas for image display
        self.image_canvas = tk.Canvas(image_frame, width=600, height=400, bg='white', relief=tk.SUNKEN, bd=2)
        self.image_canvas.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # Add navigation buttons
        nav_frame = ttk.Frame(image_frame)
        nav_frame.grid(row=1, column=0, columnspan=3, pady=(5, 0))
        
        self.prev_btn = ttk.Button(nav_frame, text="← Previous", command=self.show_previous_image)
        self.prev_btn.grid(row=0, column=0, padx=5)
        
        self.image_info_label = ttk.Label(nav_frame, text="No images available")
        self.image_info_label.grid(row=0, column=1, padx=10)
        
        self.next_btn = ttk.Button(nav_frame, text="Next →", command=self.show_next_image)
        self.next_btn.grid(row=0, column=2, padx=5)
        
        image_frame.columnconfigure(0, weight=1)
        image_frame.rowconfigure(0, weight=1)
        
        # Store current image
        self.current_image = None
        self.current_photo = None
        self.current_image_index = 0
        self.available_images = []
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, padding=(10, 5))
        status_bar.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15, 0))
        
        # Welcome message
        self.results_text.insert(tk.END, "🚀 Welcome to Bitcoin Analysis GUI!\n")
        self.results_text.insert(tk.END, "📊 Click any button to run analysis or tools.\n")
        self.results_text.insert(tk.END, "💡 Results will appear here as scripts run.\n\n")
        
        # Show API key status
        fmp_key = os.getenv("FMP_API_KEY", "")
        av_key = os.getenv("ALPHAVANTAGE_API_KEY", "")
        if fmp_key or av_key:
            self.results_text.insert(tk.END, "✅ API Keys Configured:\n")
            if fmp_key:
                self.results_text.insert(tk.END, "   - FMP API Key: Set\n")
            if av_key:
                self.results_text.insert(tk.END, "   - Alpha Vantage API Key: Set\n")
            self.results_text.insert(tk.END, "   - Using reliable price providers\n\n")
        else:
            self.results_text.insert(tk.END, "⚠️ No API keys set - using fallback providers\n\n")
        
        # Bind mouse wheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Bind canvas resize
        def _on_canvas_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Update canvas window width to match frame
            canvas.itemconfig(canvas.find_withtag("all")[0], width=event.width)
        canvas.bind('<Configure>', _on_canvas_configure)
        
    def create_button(self, parent, text, command, row):
        """Create a styled button that adjusts to window size"""
        btn = ttk.Button(parent, text=text, command=command, style='Action.TButton')
        btn.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=3, padx=(0, 10))
        return btn
        
    def run_script(self, script_name, args):
        """Run a Python script in a separate thread with environment variables"""
        def run():
            self.status_var.set(f"Running {script_name}...")
            self.results_text.insert(tk.END, f"\n[{datetime.now().strftime('%H:%M:%S')}] 🚀 Running {script_name}...\n")
            self.results_text.see(tk.END)
            
            try:
                # Create environment with .env variables
                env = os.environ.copy()
                
                # Load .env file manually if it exists
                if os.path.exists('.env'):
                    with open('.env', 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                env[key] = value.strip('"')
                
                # Use the current Python executable (which has the .env file)
                python_exe = sys.executable
                cmd = [python_exe, script_name] + args
                
                # Debug info
                self.results_text.insert(tk.END, f"🔧 Using Python: {python_exe}\n")
                self.results_text.insert(tk.END, f"🔧 Working directory: {os.getcwd()}\n")
                if env.get('FMP_API_KEY'):
                    self.results_text.insert(tk.END, "🔧 FMP API Key: Set\n")
                if env.get('ALPHAVANTAGE_API_KEY'):
                    self.results_text.insert(tk.END, "🔧 Alpha Vantage API Key: Set\n")
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=env, cwd=os.getcwd())
                
                if result.stdout:
                    self.results_text.insert(tk.END, f"✅ Output:\n{result.stdout}\n")
                if result.stderr:
                    self.results_text.insert(tk.END, f"⚠️ Errors:\n{result.stderr}\n")
                
                # Check for new images after script completion
                self.check_for_new_images()
                
                self.status_var.set(f"✅ {script_name} completed")
                self.results_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {script_name} completed\n")
                self.results_text.see(tk.END)
                
            except subprocess.TimeoutExpired:
                self.results_text.insert(tk.END, f"❌ Error: {script_name} timed out after 5 minutes\n")
                self.status_var.set(f"❌ {script_name} timed out")
            except Exception as e:
                self.results_text.insert(tk.END, f"❌ Error running {script_name}: {e}\n")
                self.status_var.set(f"❌ Error running {script_name}")
        
        threading.Thread(target=run, daemon=True).start()
    
    def check_for_new_images(self):
        """Check for new images and show all newly generated ones"""
        try:
            # Look for PNG files in current directory and subdirectories
            png_files = []
            for root, dirs, files in os.walk('.'):
                # Skip system directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
                for file in files:
                    if file.lower().endswith('.png'):
                        # Only include analysis-related images
                        if any(keyword in file.lower() for keyword in ['mnav_analysis', 'pattern_analysis', 'comprehensive_pattern', 'robust_pattern']):
                            png_files.append(os.path.join(root, file))
            
            if png_files:
                # Update the dropdown with available images
                self.update_image_dropdown(png_files)
                
                # Find all new files (created in the last 30 seconds)
                new_files = []
                for png_file in png_files:
                    if time.time() - os.path.getctime(png_file) < 30:
                        new_files.append(png_file)
                
                if new_files:
                    # Sort by creation time (oldest first for logical progression)
                    new_files.sort(key=os.path.getctime)
                    
                    self.results_text.insert(tk.END, f"🖼️ Generated {len(new_files)} new analysis images:\n")
                    for i, file_path in enumerate(new_files, 1):
                        filename = os.path.basename(file_path)
                        self.results_text.insert(tk.END, f"   {i}. {filename}\n")
                    
                    self.results_text.insert(tk.END, "💡 Use the dropdown to view each image\n")
                    self.results_text.see(tk.END)
                    
                    # Show the first new image
                    if new_files:
                        self.display_image(new_files[0])
                    
        except Exception as e:
            self.results_text.insert(tk.END, f"⚠️ Error checking for images: {e}\n")
    
    def show_previous_image(self):
        """Show the previous image"""
        if self.available_images and self.current_image_index > 0:
            self.current_image_index -= 1
            self.display_image(self.available_images[self.current_image_index])
    
    def show_next_image(self):
        """Show the next image"""
        if self.available_images and self.current_image_index < len(self.available_images) - 1:
            self.current_image_index += 1
            self.display_image(self.available_images[self.current_image_index])
    
    def update_image_dropdown(self, png_files):
        """Update the image selector dropdown"""
        try:
            # Sort files by creation time (newest first)
            sorted_files = sorted(png_files, key=os.path.getctime, reverse=True)
            
            # Store available images for navigation
            self.available_images = sorted_files
            
            # Create display names for dropdown
            dropdown_items = []
            for file_path in sorted_files:
                filename = os.path.basename(file_path)
                # Extract meaningful name from filename
                if 'mnav_analysis' in filename:
                    # Extract stock and period from filename like "mnav_analysis_MARA_30d.png"
                    parts = filename.replace('.png', '').split('_')
                    if len(parts) >= 4:
                        stock = parts[2]  # e.g., "MARA"
                        period = parts[3]  # e.g., "30d"
                        dropdown_items.append(f"MNav {stock} ({period})")
                    else:
                        dropdown_items.append(f"MNav Analysis - {filename}")
                elif 'pattern_analysis' in filename:
                    dropdown_items.append(f"Pattern Analysis - {filename}")
                elif 'comprehensive_pattern' in filename:
                    dropdown_items.append(f"Comprehensive Pattern - {filename}")
                elif 'robust_pattern' in filename:
                    dropdown_items.append(f"Robust Pattern - {filename}")
                else:
                    dropdown_items.append(filename)
            
            # Update dropdown
            self.image_selector['values'] = dropdown_items
            if dropdown_items:
                self.image_selector.set(dropdown_items[0])  # Set to most recent
                self.image_files = sorted_files  # Store the file paths
                
        except Exception as e:
            self.results_text.insert(tk.END, f"⚠️ Error updating image dropdown: {e}\n")
    
    def on_image_selected(self, event=None):
        """Handle image selection from dropdown"""
        try:
            selection = self.image_var.get()
            if selection and hasattr(self, 'image_files'):
                # Find the corresponding file
                dropdown_items = list(self.image_selector['values'])
                if selection in dropdown_items:
                    index = dropdown_items.index(selection)
                    selected_file = self.image_files[index]
                    self.display_image(selected_file)
                    
        except Exception as e:
            self.results_text.insert(tk.END, f"❌ Error selecting image: {e}\n")
    
    def display_image(self, image_path):
        """Display an image in the image tab"""
        try:
            # Load image
            image = Image.open(image_path)
            
            # Get canvas dimensions
            canvas_width = 600
            canvas_height = 400
            
            # Calculate resize ratio to fit the canvas
            img_width, img_height = image.size
            ratio = min(canvas_width / img_width, canvas_height / img_height, 1.0)
            
            # Resize image to fit canvas
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(resized_image)
            
            # Clear canvas and display image
            self.image_canvas.delete("all")
            # Center the image in the canvas
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            self.image_canvas.create_image(x, y, anchor=tk.NW, image=photo)
            self.image_canvas.image = photo  # Keep a reference
            
            # Update current index
            if hasattr(self, 'available_images') and image_path in self.available_images:
                self.current_image_index = self.available_images.index(image_path)
            
            # Update navigation info
            if self.available_images:
                filename = os.path.basename(image_path)
                self.image_info_label.config(text=f"Image {self.current_image_index + 1} of {len(self.available_images)}: {filename}")
                
                # Update button states
                self.prev_btn.config(state="normal" if self.current_image_index > 0 else "disabled")
                self.next_btn.config(state="normal" if self.current_image_index < len(self.available_images) - 1 else "disabled")
            else:
                self.image_info_label.config(text=f"Image: {os.path.basename(image_path)}")
                self.prev_btn.config(state="disabled")
                self.next_btn.config(state="disabled")
            
            # Switch to image tab
            self.notebook.select(1)
            
            self.results_text.insert(tk.END, f"✅ Image displayed: {os.path.basename(image_path)}\n")
            self.results_text.see(tk.END)
            
        except Exception as e:
            self.results_text.insert(tk.END, f"❌ Error displaying image: {e}\n")
            self.results_text.see(tk.END)
    
    def clear_cache(self):
        """Clear the cache directory"""
        def run():
            self.status_var.set("Clearing cache...")
            self.results_text.insert(tk.END, f"\n[{datetime.now().strftime('%H:%M:%S')}] 🗑️ Clearing cache...\n")
            
            try:
                if os.path.exists('cache'):
                    for file in os.listdir('cache'):
                        os.remove(os.path.join('cache', file))
                    self.results_text.insert(tk.END, "✅ Cache cleared successfully\n")
                else:
                    self.results_text.insert(tk.END, "⚠️ Cache directory not found\n")
                
                self.status_var.set("✅ Cache cleared")
            except Exception as e:
                self.results_text.insert(tk.END, f"❌ Error clearing cache: {e}\n")
                self.status_var.set("❌ Error clearing cache")

    def show_latest_image(self):
        """Display the latest image from the available files"""
        try:
            # Get all PNG files (filtered for analysis images)
            png_files = []
            for root, dirs, files in os.walk('.'):
                # Skip system directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
                for file in files:
                    if file.lower().endswith('.png'):
                        # Only include analysis-related images
                        if any(keyword in file.lower() for keyword in ['mnav_analysis', 'pattern_analysis', 'comprehensive_pattern', 'robust_pattern']):
                            png_files.append(os.path.join(root, file))
            
            if png_files:
                # Get the most recent file
                latest_png = max(png_files, key=os.path.getctime)
                self.display_image(latest_png)
                
                # Update dropdown if not already done
                self.update_image_dropdown(png_files)
                
            else:
                self.results_text.insert(tk.END, "⚠️ No analysis images found\n")
                self.results_text.see(tk.END)
                
        except Exception as e:
            self.results_text.insert(tk.END, f"❌ Error loading latest image: {e}\n")
            self.results_text.see(tk.END)

def main():
    root = tk.Tk()
    app = SimpleBitcoinGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
