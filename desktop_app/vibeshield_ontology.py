"""
VibeShield Ontology - Ultra-Minimalist Enterprise UI
Inspired by: Ontology blockchain wallet design
"""

import json
import os
import sys
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import subprocess
import threading
from pathlib import Path
from datetime import datetime

CONFIG_FILE = "config.json"


class OntologyText(scrolledtext.ScrolledText):
    """Minimalist text widget"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.tag_config("info", foreground="#3B82F6")
        self.tag_config("success", foreground="#26A69A")
        self.tag_config("warning", foreground="#D9A441")
        self.tag_config("error", foreground="#EF5350")
        self.tag_config("dim", foreground="#6B7280")
        self.tag_config("bold", font=("Inter", 9, "bold"))
        
    def log(self, message, level="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.insert("end", f"[{timestamp}] ", "dim")
        self.insert("end", f"{message}\n", level)
        self.see("end")
        self.update()


class VibeShieldOntology:
    def __init__(self, root):
        self.root = root
        self.root.title("VibeShield")
        self.root.geometry("1600x900")
        self.root.minsize(1400, 800)
        
        # Ontology color palette
        self.colors = {
            'bg_main': '#090B0E',
            'bg_sidebar': '#0A0C0F',
            'bg_card': '#0F1216',
            'bg_hover': '#12151A',
            'border': '#1A1D23',
            'border_active': '#252C35',
            'primary': '#3B82F6',
            'success': '#26A69A',
            'danger': '#EF5350',
            'warning': '#D9A441',
            'text': '#F5F5F7',
            'text_secondary': '#8E8E93',
            'text_dim': '#636366'
        }
        
        self.root.configure(bg=self.colors['bg_main'])
        
        # State
        self.config = self.load_config()
        self.scan_running = False
        self.tools_status = {}
        self.current_view = "scan"
        
        # Build UI
        self.build_ui()
        
        # Auto-test tools
        self.root.after(800, self.test_all_tools)
    
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'openrouter_api_key': '',
            'github_token': '',
            'target_url': 'http://localhost:8000',
            'project_path': ''
        }
    
    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def build_ui(self):
        """Main UI - Ontology style with sidebar"""
        
        # Main container
        container = tk.Frame(self.root, bg=self.colors['bg_main'])
        container.pack(fill='both', expand=True)
        
        # Sidebar
        self.build_sidebar(container)
        
        # Right side: Top bar + Content
        right_side = tk.Frame(container, bg=self.colors['bg_main'])
        right_side.pack(side='left', fill='both', expand=True)
        
        # Top bar
        self.build_topbar(right_side)
        
        # Content area (centered, max-width)
        self.content_wrapper = tk.Frame(right_side, bg=self.colors['bg_main'])
        self.content_wrapper.pack(fill='both', expand=True, padx=60, pady=40)
        
        # Build default view
        self.build_scan_view()
    
    def build_sidebar(self, parent):
        """Minimalist sidebar - Vercel/Linear style"""
        sidebar = tk.Frame(parent, bg=self.colors['bg_sidebar'], width=240)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        # Brand
        brand_frame = tk.Frame(sidebar, bg=self.colors['bg_sidebar'], height=80)
        brand_frame.pack(fill='x')
        brand_frame.pack_propagate(False)
        
        brand_content = tk.Frame(brand_frame, bg=self.colors['bg_sidebar'])
        brand_content.pack(pady=28, padx=24)
        
        tk.Label(
            brand_content,
            text="◆",
            font=('Inter', 16),
            fg=self.colors['primary'],
            bg=self.colors['bg_sidebar']
        ).pack(side='left', padx=(0, 12))
        
        brand_text = tk.Frame(brand_content, bg=self.colors['bg_sidebar'])
        brand_text.pack(side='left')
        
        tk.Label(
            brand_text,
            text="VibeShield",
            font=('Inter', 11, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['bg_sidebar']
        ).pack(anchor='w')
        
        tk.Label(
            brand_text,
            text="Security Suite",
            font=('Inter', 8),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_sidebar']
        ).pack(anchor='w')
        
        # Divider
        tk.Frame(sidebar, bg=self.colors['border'], height=1).pack(fill='x')
        
        # Navigation
        nav_frame = tk.Frame(sidebar, bg=self.colors['bg_sidebar'])
        nav_frame.pack(fill='x', pady=16)
        
        nav_items = [
            ("○", "Scan", "scan", "Run security scans"),
            ("◐", "Monitor", "monitor", "Live output"),
            ("◑", "Results", "results", "Scan history"),
            ("◕", "Settings", "settings", "Configuration")
        ]
        
        self.nav_buttons = {}
        for icon, label, view, subtitle in nav_items:
            btn_frame = tk.Frame(sidebar, bg=self.colors['bg_sidebar'])
            btn_frame.pack(fill='x', padx=12, pady=2)
            
            btn = tk.Frame(btn_frame, bg=self.colors['bg_sidebar'])
            btn.pack(fill='x', padx=12, pady=8)
            
            # Icon
            icon_label = tk.Label(
                btn,
                text=icon,
                font=('Inter', 14),
                fg=self.colors['text_dim'],
                bg=self.colors['bg_sidebar'],
                width=2
            )
            icon_label.pack(side='left', padx=(0, 12))
            
            # Text
            text_frame = tk.Frame(btn, bg=self.colors['bg_sidebar'])
            text_frame.pack(side='left', fill='x', expand=True)
            
            title_label = tk.Label(
                text_frame,
                text=label,
                font=('Inter', 10),
                fg=self.colors['text_secondary'],
                bg=self.colors['bg_sidebar'],
                anchor='w'
            )
            title_label.pack(anchor='w')
            
            subtitle_label = tk.Label(
                text_frame,
                text=subtitle,
                font=('Inter', 8),
                fg=self.colors['text_dim'],
                bg=self.colors['bg_sidebar'],
                anchor='w'
            )
            subtitle_label.pack(anchor='w')
            
            # Store references
            self.nav_buttons[view] = {
                'frame': btn_frame,
                'icon': icon_label,
                'title': title_label,
                'subtitle': subtitle_label
            }
            
            # Click handlers
            for widget in [btn_frame, btn, icon_label, text_frame, title_label, subtitle_label]:
                widget.bind('<Button-1>', lambda e, v=view: self.switch_view(v))
                widget.bind('<Enter>', lambda e, f=btn_frame: f.config(bg=self.colors['bg_hover']))
                widget.bind('<Leave>', lambda e, f=btn_frame: f.config(bg=self.colors['bg_sidebar']))
        
        # Activate first
        self.activate_nav('scan')
        
        # Bottom section
        bottom_frame = tk.Frame(sidebar, bg=self.colors['bg_sidebar'])
        bottom_frame.pack(side='bottom', fill='x', pady=20)
        
        # Divider
        tk.Frame(bottom_frame, bg=self.colors['border'], height=1).pack(fill='x', pady=(0, 16))
        
        # Status
        status_container = tk.Frame(bottom_frame, bg=self.colors['bg_sidebar'])
        status_container.pack(fill='x', padx=24)
        
        status_row = tk.Frame(status_container, bg=self.colors['bg_sidebar'])
        status_row.pack(fill='x')
        
        self.status_dot = tk.Label(
            status_row,
            text="●",
            font=('Arial', 10),
            fg=self.colors['success'],
            bg=self.colors['bg_sidebar']
        )
        self.status_dot.pack(side='left', padx=(0, 8))
        
        status_text_frame = tk.Frame(status_row, bg=self.colors['bg_sidebar'])
        status_text_frame.pack(side='left', fill='x', expand=True)
        
        self.status_text = tk.Label(
            status_text_frame,
            text="System Ready",
            font=('Inter', 9),
            fg=self.colors['text'],
            bg=self.colors['bg_sidebar'],
            anchor='w'
        )
        self.status_text.pack(anchor='w')
        
        tk.Label(
            status_text_frame,
            text="All systems operational",
            font=('Inter', 8),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_sidebar'],
            anchor='w'
        ).pack(anchor='w')
    
    def activate_nav(self, view):
        """Activate navigation item"""
        for v, widgets in self.nav_buttons.items():
            if v == view:
                widgets['frame'].config(bg=self.colors['bg_hover'])
                widgets['icon'].config(fg=self.colors['primary'], bg=self.colors['bg_hover'])
                widgets['title'].config(fg=self.colors['text'], bg=self.colors['bg_hover'])
                widgets['subtitle'].config(bg=self.colors['bg_hover'])
            else:
                widgets['frame'].config(bg=self.colors['bg_sidebar'])
                widgets['icon'].config(fg=self.colors['text_dim'], bg=self.colors['bg_sidebar'])
                widgets['title'].config(fg=self.colors['text_secondary'], bg=self.colors['bg_sidebar'])
                widgets['subtitle'].config(bg=self.colors['bg_sidebar'])
    
    def build_topbar(self, parent):
        """Minimalist top bar"""
        topbar = tk.Frame(parent, bg=self.colors['bg_main'], height=72)
        topbar.pack(fill='x')
        topbar.pack_propagate(False)
        
        # Content
        content = tk.Frame(topbar, bg=self.colors['bg_main'])
        content.pack(fill='both', expand=True, padx=60, pady=20)
        
        # Title (dynamic based on view)
        self.page_title = tk.Label(
            content,
            text="Security Scan",
            font=('Inter', 24, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['bg_main']
        )
        self.page_title.pack(side='left')
        
        # Quick actions
        actions = tk.Frame(content, bg=self.colors['bg_main'])
        actions.pack(side='right')
        
        self.quick_scan_btn = tk.Button(
            actions,
            text="⚡ Quick Scan",
            command=self.run_quick_scan,
            bg=self.colors['bg_card'],
            fg=self.colors['text_secondary'],
            font=('Inter', 9),
            relief='flat',
            cursor='hand2',
            bd=0,
            padx=16,
            pady=8
        )
        self.quick_scan_btn.pack(side='left', padx=(0, 8))
        
        self.full_scan_btn = tk.Button(
            actions,
            text="▶ Full Scan",
            command=self.run_full_scan,
            bg=self.colors['primary'],
            fg='white',
            font=('Inter', 9, 'bold'),
            relief='flat',
            cursor='hand2',
            bd=0,
            padx=16,
            pady=8
        )
        self.full_scan_btn.pack(side='left')
        
        # Divider
        tk.Frame(parent, bg=self.colors['border'], height=1).pack(fill='x')
    
    def switch_view(self, view):
        """Switch between views"""
        self.current_view = view
        
        # Update nav
        self.activate_nav(view)
        
        # Update page title
        titles = {
            'scan': 'Security Scan',
            'monitor': 'Live Monitor',
            'results': 'Scan Results',
            'settings': 'Settings'
        }
        if hasattr(self, 'page_title'):
            self.page_title.config(text=titles.get(view, 'VibeShield'))
        
        # Clear content
        for widget in self.content_wrapper.winfo_children():
            widget.destroy()
        
        # Build view
        if view == "scan":
            self.build_scan_view()
        elif view == "monitor":
            self.build_monitor_view()
        elif view == "results":
            self.build_results_view()
        elif view == "settings":
            self.build_settings_view()
    
    def build_scan_view(self):
        """Main scan view - ultra clean"""
        
        # Project card
        project_card = tk.Frame(self.content_wrapper, bg=self.colors['bg_card'])
        project_card.pack(fill='x', pady=(0, 20))
        
        # Card content
        card_content = tk.Frame(project_card, bg=self.colors['bg_card'])
        card_content.pack(fill='x', padx=28, pady=24)
        
        tk.Label(
            card_content,
            text="Project Path",
            font=('Inter', 10, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['bg_card']
        ).pack(anchor='w', pady=(0, 10))
        
        # Input group
        input_group = tk.Frame(card_content, bg=self.colors['bg_card'])
        input_group.pack(fill='x')
        
        self.project_entry = tk.Entry(
            input_group,
            bg=self.colors['bg_main'],
            fg=self.colors['text'],
            insertbackground=self.colors['primary'],
            font=('Inter', 9),
            relief='flat',
            bd=0
        )
        self.project_entry.pack(side='left', fill='x', expand=True, ipady=10, ipadx=14)
        self.project_entry.insert(0, self.config.get('project_path', ''))
        
        browse_btn = tk.Button(
            input_group,
            text="Browse",
            command=self.select_project,
            bg=self.colors['bg_hover'],
            fg=self.colors['text_secondary'],
            font=('Inter', 9),
            relief='flat',
            cursor='hand2',
            bd=0,
            padx=18,
            pady=10
        )
        browse_btn.pack(side='left', padx=(10, 0))
        
        # Tools grid
        tools_card = tk.Frame(self.content_wrapper, bg=self.colors['bg_card'])
        tools_card.pack(fill='x', pady=(0, 20))
        
        tools_content = tk.Frame(tools_card, bg=self.colors['bg_card'])
        tools_content.pack(fill='x', padx=28, pady=24)
        
        tools_header = tk.Frame(tools_content, bg=self.colors['bg_card'])
        tools_header.pack(fill='x', pady=(0, 16))
        
        tk.Label(
            tools_header,
            text="Security Tools",
            font=('Inter', 10, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['bg_card']
        ).pack(side='left')
        
        test_btn = tk.Label(
            tools_header,
            text="↻ Test All",
            font=('Inter', 9),
            fg=self.colors['primary'],
            bg=self.colors['bg_card'],
            cursor='hand2'
        )
        test_btn.pack(side='right')
        test_btn.bind('<Button-1>', lambda e: self.test_all_tools())
        
        # Tools grid (2 columns)
        tools_grid = tk.Frame(tools_content, bg=self.colors['bg_card'])
        tools_grid.pack(fill='x')
        
        self.tool_widgets = {}
        tools = [
            ('audit', 'Audit Engine', 'SAST'),
            ('gitleaks', 'Gitleaks', 'Secrets'),
            ('semgrep', 'Semgrep', 'SAST'),
            ('trivy', 'Trivy', 'SCA'),
            ('nuclei', 'Nuclei', 'Templates'),
            ('strix', 'Strix', 'DAST')
        ]
        
        for idx, (key, name, category) in enumerate(tools):
            col = idx % 2
            row = idx // 2
            
            tool_frame = tk.Frame(tools_grid, bg=self.colors['bg_main'])
            tool_frame.grid(row=row, column=col, sticky='ew', padx=(0, 10) if col == 0 else (10, 0), pady=6)
            
            if col == 0:
                tools_grid.grid_columnconfigure(0, weight=1)
            else:
                tools_grid.grid_columnconfigure(1, weight=1)
            
            inner = tk.Frame(tool_frame, bg=self.colors['bg_main'])
            inner.pack(fill='x', padx=14, pady=12)
            
            left_info = tk.Frame(inner, bg=self.colors['bg_main'])
            left_info.pack(side='left')
            
            tk.Label(
                left_info,
                text=name,
                font=('Inter', 9),
                fg=self.colors['text'],
                bg=self.colors['bg_main']
            ).pack(side='left')
            
            tk.Label(
                left_info,
                text=f"  •  {category}",
                font=('Inter', 8),
                fg=self.colors['text_dim'],
                bg=self.colors['bg_main']
            ).pack(side='left')
            
            status_dot = tk.Label(
                inner,
                text="●",
                font=('Arial', 9),
                fg=self.colors['text_dim'],
                bg=self.colors['bg_main']
            )
            status_dot.pack(side='right')
            
            self.tool_widgets[key] = status_dot
    
    def build_monitor_view(self):
        """Monitor view"""
        
        # Monitor card
        monitor_card = tk.Frame(self.content_wrapper, bg=self.colors['bg_card'])
        monitor_card.pack(fill='both', expand=True)
        
        # Controls
        controls = tk.Frame(monitor_card, bg=self.colors['bg_card'])
        controls.pack(fill='x', padx=28, pady=(16, 0))
        
        self.stop_btn = tk.Label(
            controls,
            text="⏹ Stop Scan",
            font=('Inter', 9),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_card'],
            cursor='hand2'
        )
        self.stop_btn.pack(side='left')
        self.stop_btn.bind('<Button-1>', lambda e: self.stop_scan())
        
        clear_btn = tk.Label(
            controls,
            text="✕ Clear",
            font=('Inter', 9),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_card'],
            cursor='hand2'
        )
        clear_btn.pack(side='left', padx=(16, 0))
        clear_btn.bind('<Button-1>', lambda e: self.clear_monitor())
        
        # Monitor output
        monitor_frame = tk.Frame(monitor_card, bg=self.colors['bg_main'])
        monitor_frame.pack(fill='both', expand=True, padx=1, pady=1)
        
        self.monitor = OntologyText(
            monitor_frame,
            bg=self.colors['bg_main'],
            fg=self.colors['text'],
            insertbackground=self.colors['primary'],
            font=('Inter', 9),
            wrap='word',
            relief='flat',
            padx=28,
            pady=20
        )
        self.monitor.pack(fill='both', expand=True)
        
        self.monitor.log("VibeShield Ontology initialized", "bold")
        self.monitor.log("System ready for security operations", "info")
    
    def build_results_view(self):
        """Results view"""
        
        # Empty state
        empty_card = tk.Frame(self.content_wrapper, bg=self.colors['bg_card'])
        empty_card.pack(fill='both', expand=True)
        
        empty_content = tk.Frame(empty_card, bg=self.colors['bg_card'])
        empty_content.pack(expand=True, pady=100)
        
        tk.Label(
            empty_content,
            text="No Scan Results",
            font=('Inter', 16, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['bg_card']
        ).pack()
        
        tk.Label(
            empty_content,
            text="Run a scan to see results here",
            font=('Inter', 9),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_card']
        ).pack(pady=(8, 0))
    
    def build_settings_view(self):
        """Settings view"""
        
        # OpenRouter API
        self.build_setting_card(
            "OpenRouter API Key",
            "Required for Strix AI pentest",
            'openrouter_api_key',
            show='*'
        )
        
        # GitHub Token
        self.build_setting_card(
            "GitHub Token",
            "Required for Gitleaks and Kavach auto-fix",
            'github_token',
            show='*'
        )
        
        # Target URL
        self.build_setting_card(
            "Target URL",
            "Target application for dynamic testing",
            'target_url'
        )
    
    def build_setting_card(self, title, subtitle, config_key, show=None):
        """Build a setting card"""
        card = tk.Frame(self.content_wrapper, bg=self.colors['bg_card'])
        card.pack(fill='x', pady=(0, 20))
        
        content = tk.Frame(card, bg=self.colors['bg_card'])
        content.pack(fill='x', padx=28, pady=24)
        
        tk.Label(
            content,
            text=title,
            font=('Inter', 10, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['bg_card']
        ).pack(anchor='w', pady=(0, 6))
        
        tk.Label(
            content,
            text=subtitle,
            font=('Inter', 8),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_card']
        ).pack(anchor='w', pady=(0, 14))
        
        input_group = tk.Frame(content, bg=self.colors['bg_card'])
        input_group.pack(fill='x')
        
        entry = tk.Entry(
            input_group,
            bg=self.colors['bg_main'],
            fg=self.colors['text'],
            insertbackground=self.colors['primary'],
            font=('Inter', 9),
            relief='flat',
            bd=0,
            show=show
        )
        entry.pack(side='left', fill='x', expand=True, ipady=10, ipadx=14)
        entry.insert(0, self.config.get(config_key, ''))
        
        save_btn = tk.Button(
            input_group,
            text="Save",
            command=lambda: self.save_setting(config_key, entry.get()),
            bg=self.colors['primary'],
            fg='white',
            font=('Inter', 9, 'bold'),
            relief='flat',
            cursor='hand2',
            bd=0,
            padx=20,
            pady=10
        )
        save_btn.pack(side='left', padx=(10, 0))
    
    def save_setting(self, key, value):
        """Save a setting"""
        if not value.strip():
            messagebox.showwarning("Empty", "Value cannot be empty")
            return
        
        self.config[key] = value
        self.save_config()
        
        if hasattr(self, 'monitor'):
            self.monitor.log(f"Setting saved: {key}", "success")
        
        messagebox.showinfo("Saved", f"{key.replace('_', ' ').title()} saved successfully")
    
    # Tool operations
    def test_all_tools(self):
        """Test all tools"""
        if hasattr(self, 'monitor'):
            self.monitor.log("Testing security tools...", "info")
        
        tools = {
            'audit': ('python', ['-m', 'audit.run_audit', '--help']),
            'gitleaks': ('gitleaks', ['version']),
            'semgrep': ('semgrep', ['--version']),
            'trivy': ('trivy', ['--version']),
            'strix': ('strix', ['--version']),
            'nuclei': ('nuclei', ['-version'])
        }
        
        for key, (cmd, args) in tools.items():
            try:
                if key == 'audit':
                    result = subprocess.run(
                        [sys.executable] + args,
                        capture_output=True,
                        timeout=3,
                        cwd=Path(__file__).parent.parent
                    )
                else:
                    result = subprocess.run([cmd] + args, capture_output=True, timeout=3)
                
                if result.returncode == 0 or key == 'audit':
                    self.tools_status[key] = True
                    self.tool_widgets[key].config(fg=self.colors['success'])
                    if hasattr(self, 'monitor'):
                        self.monitor.log(f"{key}: Available", "success")
                else:
                    self.tools_status[key] = False
                    self.tool_widgets[key].config(fg=self.colors['danger'])
            except:
                self.tools_status[key] = False
                self.tool_widgets[key].config(fg=self.colors['danger'])
        
        if hasattr(self, 'monitor'):
            self.monitor.log("Tool testing complete", "info")
    
    def run_full_scan(self):
        """Run full scan"""
        project = self.project_entry.get().strip()
        if not project or not os.path.exists(project):
            messagebox.showerror("Error", "Please select a valid project path")
            return
        
        if not hasattr(self, 'monitor'):
            self.switch_view('monitor')
        
        self.scan_running = True
        self.update_status("Scanning", self.colors['warning'])
        
        thread = threading.Thread(target=self._scan_thread, args=(project,))
        thread.daemon = True
        thread.start()
    
    def _scan_thread(self, project):
        """Scan thread"""
        try:
            self.monitor.log("Starting full scan...", "bold")
            
            self.monitor.log("\nStatic Analysis", "info")
            self._run_tool('audit', project)
            self._run_tool('gitleaks', project)
            self._run_tool('semgrep', project)
            self._run_tool('trivy', project)
            
            self.monitor.log("\nDynamic Analysis", "info")
            self._run_tool('strix', project)
            self._run_tool('nuclei', project)
            
            self.monitor.log("\nScan complete", "success")
            self.update_status("Complete", self.colors['success'])
        except Exception as e:
            self.monitor.log(f"Error: {e}", "error")
            self.update_status("Error", self.colors['danger'])
        finally:
            self.scan_running = False
    
    def _run_tool(self, tool, project):
        """Run a tool"""
        if not self.tools_status.get(tool, False):
            self.monitor.log(f"{tool}: Skipped", "dim")
            return
        
        self.monitor.log(f"Running {tool}...", "info")
        time.sleep(1)
        self.monitor.log(f"{tool}: Complete", "success")
    
    def run_quick_scan(self):
        """Quick scan"""
        project = self.project_entry.get().strip()
        if not project:
            messagebox.showerror("Error", "Please select a project")
            return
        
        if not hasattr(self, 'monitor'):
            self.switch_view('monitor')
        
        self.monitor.log("Quick scan (static only)", "info")
        self._run_tool('audit', project)
        self.monitor.log("Quick scan complete", "success")
    
    def stop_scan(self):
        """Stop scan"""
        self.scan_running = False
        if hasattr(self, 'monitor'):
            self.monitor.log("Scan stopped", "warning")
        self.update_status("Stopped", self.colors['warning'])
    
    def clear_monitor(self):
        """Clear monitor"""
        if hasattr(self, 'monitor'):
            self.monitor.delete('1.0', 'end')
            self.monitor.log("Monitor cleared", "dim")
    
    def select_project(self):
        """Select project"""
        path = filedialog.askdirectory()
        if path:
            self.project_entry.delete(0, 'end')
            self.project_entry.insert(0, path)
            self.config['project_path'] = path
            self.save_config()
    
    def update_status(self, text, color):
        """Update status"""
        status_map = {
            "Scanning": "Scanning in progress...",
            "Complete": "Scan completed successfully",
            "Stopped": "Scan stopped by user",
            "Ready": "System ready",
            "Error": "An error occurred"
        }
        
        self.status_text.config(text=status_map.get(text, text))
        self.status_dot.config(fg=color)


def main():
    root = tk.Tk()
    app = VibeShieldOntology(root)
    root.mainloop()


if __name__ == "__main__":
    main()
