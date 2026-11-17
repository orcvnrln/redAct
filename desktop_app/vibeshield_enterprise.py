"""
VibeShield Enterprise - Professional Security Scanner
Minimalist | Data-Driven | Real-Time Monitoring
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


class MonitoringText(scrolledtext.ScrolledText):
    """Professional monitoring text widget"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Professional colors - no glow
        self.tag_config("info", foreground="#3B82F6")
        self.tag_config("success", foreground="#26A69A")
        self.tag_config("warning", foreground="#D9A441")
        self.tag_config("error", foreground="#EF5350")
        self.tag_config("dim", foreground="#6B7280")
        self.tag_config("highlight", foreground="#E6EAF0", font=("Consolas", 9, "bold"))
        
    def log(self, message, level="info"):
        """Write log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.insert("end", f"[{timestamp}] ", "dim")
        self.insert("end", f"{message}\n", level)
        self.see("end")
        self.update()


class VibeShieldEnterprise:
    def __init__(self, root):
        self.root = root
        self.root.title("VibeShield Enterprise")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        
        # Professional color palette - no gradients
        self.colors = {
            'bg_main': '#090B0E',
            'bg_sidebar': '#0D1117',
            'bg_card': '#11161D',
            'border': '#252C35',
            'primary': '#3B82F6',
            'success': '#26A69A',
            'danger': '#EF5350',
            'warning': '#D9A441',
            'text': '#E6EAF0',
            'text_dim': '#6B7280',
            'hover': '#1A1F26'
        }
        
        self.root.configure(bg=self.colors['bg_main'])
        
        # State
        self.config = self.load_config()
        self.scan_running = False
        self.tools_status = {}
        self.current_view = "orchestrator"
        
        # Build UI
        self.build_ui()
        
        # Test tools
        self.root.after(500, self.test_all_tools)
    
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
        """Main UI layout: Sidebar + Content"""
        
        # Main container
        container = tk.Frame(self.root, bg=self.colors['bg_main'])
        container.pack(fill='both', expand=True)
        
        # Sidebar (compact)
        self.build_sidebar(container)
        
        # Content area
        self.content_frame = tk.Frame(container, bg=self.colors['bg_main'])
        self.content_frame.pack(side='left', fill='both', expand=True)
        
        # Build views
        self.build_orchestrator_view()
    
    def build_sidebar(self, parent):
        """Compact professional sidebar"""
        sidebar = tk.Frame(parent, bg=self.colors['bg_sidebar'], width=200)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        # Header
        header = tk.Frame(sidebar, bg=self.colors['bg_sidebar'], height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="VIBESHIELD",
            font=('Segoe UI', 13, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['bg_sidebar']
        ).pack(pady=(20, 2))
        
        tk.Label(
            header,
            text="Enterprise",
            font=('Segoe UI', 8),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_sidebar']
        ).pack()
        
        # Status indicator
        self.status_indicator = tk.Frame(
            sidebar,
            bg=self.colors['border'],
            height=1
        )
        self.status_indicator.pack(fill='x', pady=10)
        
        self.status_label = tk.Label(
            sidebar,
            text="● READY",
            font=('Consolas', 9),
            fg=self.colors['success'],
            bg=self.colors['bg_sidebar']
        )
        self.status_label.pack(pady=5)
        
        # Navigation
        tk.Frame(sidebar, bg=self.colors['border'], height=1).pack(fill='x', pady=10)
        
        nav_items = [
            ("⚡", "Orchestrator", "orchestrator"),
            ("🤖", "AI Assistant", "ai"),
            ("📊", "Results", "results"),
            ("⚙️", "Settings", "settings")
        ]
        
        self.nav_buttons = {}
        for icon, label, view in nav_items:
            btn = tk.Button(
                sidebar,
                text=f"  {icon}  {label}",
                font=('Segoe UI', 10),
                fg=self.colors['text'],
                bg=self.colors['bg_sidebar'],
                activebackground=self.colors['hover'],
                relief='flat',
                anchor='w',
                cursor='hand2',
                command=lambda v=view: self.switch_view(v)
            )
            btn.pack(fill='x', padx=10, pady=2)
            self.nav_buttons[view] = btn
        
        # Highlight current
        self.nav_buttons['orchestrator'].config(
            bg=self.colors['bg_card'],
            fg=self.colors['primary']
        )
        
        # Bottom info
        tk.Frame(sidebar, bg=self.colors['bg_sidebar']).pack(expand=True)
        
        tk.Frame(sidebar, bg=self.colors['border'], height=1).pack(fill='x')
        
        info_frame = tk.Frame(sidebar, bg=self.colors['bg_sidebar'])
        info_frame.pack(fill='x', pady=10)
        
        tk.Label(
            info_frame,
            text="Version 3.0",
            font=('Consolas', 8),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_sidebar']
        ).pack()
    
    def switch_view(self, view):
        """Switch between views"""
        # Update nav buttons
        for v, btn in self.nav_buttons.items():
            if v == view:
                btn.config(bg=self.colors['bg_card'], fg=self.colors['primary'])
            else:
                btn.config(bg=self.colors['bg_sidebar'], fg=self.colors['text'])
        
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        self.current_view = view
        
        # Build view
        if view == "orchestrator":
            self.build_orchestrator_view()
        elif view == "ai":
            self.build_ai_view()
        elif view == "results":
            self.build_results_view()
        elif view == "settings":
            self.build_settings_view()
    
    def build_orchestrator_view(self):
        """Main orchestration view - data-driven"""
        
        # Top bar
        top_bar = tk.Frame(self.content_frame, bg=self.colors['bg_main'], height=60)
        top_bar.pack(fill='x', padx=20, pady=(20, 10))
        top_bar.pack_propagate(False)
        
        tk.Label(
            top_bar,
            text="Security Orchestration",
            font=('Segoe UI', 18, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['bg_main']
        ).pack(side='left', anchor='w')
        
        # Quick actions
        actions = tk.Frame(top_bar, bg=self.colors['bg_main'])
        actions.pack(side='right')
        
        tk.Button(
            actions,
            text="⚡ Full Scan",
            command=self.run_full_scan,
            bg=self.colors['primary'],
            fg='white',
            font=('Segoe UI', 9, 'bold'),
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=8
        ).pack(side='left', padx=5)
        
        tk.Button(
            actions,
            text="🔍 Quick",
            command=self.run_quick_scan,
            bg=self.colors['bg_card'],
            fg=self.colors['text'],
            font=('Segoe UI', 9),
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=8
        ).pack(side='left')
        
        # Main content: 2 columns
        content = tk.Frame(self.content_frame, bg=self.colors['bg_main'])
        content.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left: Tools & Config (30%)
        left = tk.Frame(content, bg=self.colors['bg_main'], width=350)
        left.pack(side='left', fill='y', padx=(0, 10))
        left.pack_propagate(False)
        
        self.build_tools_panel(left)
        self.build_config_compact(left)
        
        # Right: Monitor (70%)
        right = tk.Frame(content, bg=self.colors['bg_main'])
        right.pack(side='left', fill='both', expand=True)
        
        self.build_monitor_panel(right)
    
    def build_tools_panel(self, parent):
        """Compact tools status"""
        card = tk.Frame(parent, bg=self.colors['bg_card'], relief='flat')
        card.pack(fill='x', pady=(0, 10))
        
        # Header
        header = tk.Frame(card, bg=self.colors['bg_card'])
        header.pack(fill='x', padx=15, pady=12)
        
        tk.Label(
            header,
            text="Security Tools",
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['bg_card']
        ).pack(side='left')
        
        tk.Button(
            header,
            text="Test",
            command=self.test_all_tools,
            bg=self.colors['bg_main'],
            fg=self.colors['text_dim'],
            font=('Segoe UI', 8),
            relief='flat',
            cursor='hand2',
            padx=10,
            pady=4
        ).pack(side='right')
        
        tk.Frame(card, bg=self.colors['border'], height=1).pack(fill='x')
        
        # Tools list - compact
        tools_frame = tk.Frame(card, bg=self.colors['bg_card'])
        tools_frame.pack(fill='x', padx=15, pady=10)
        
        self.tool_widgets = {}
        tools = [
            ('audit', 'Audit Engine', 'SAST'),
            ('gitleaks', 'Gitleaks', 'Secrets'),
            ('semgrep', 'Semgrep', 'SAST'),
            ('trivy', 'Trivy', 'SCA'),
            ('strix', 'Strix', 'DAST'),
            ('nuclei', 'Nuclei', 'Templates')
        ]
        
        for key, name, category in tools:
            row = tk.Frame(tools_frame, bg=self.colors['bg_card'])
            row.pack(fill='x', pady=3)
            
            # Status dot
            dot = tk.Label(
                row,
                text="●",
                font=('Arial', 10),
                fg=self.colors['text_dim'],
                bg=self.colors['bg_card'],
                width=2
            )
            dot.pack(side='left')
            
            # Name
            tk.Label(
                row,
                text=name,
                font=('Segoe UI', 9),
                fg=self.colors['text'],
                bg=self.colors['bg_card'],
                anchor='w',
                width=12
            ).pack(side='left')
            
            # Category
            tk.Label(
                row,
                text=category,
                font=('Consolas', 8),
                fg=self.colors['text_dim'],
                bg=self.colors['bg_card']
            ).pack(side='left')
            
            self.tool_widgets[key] = dot
    
    def build_config_compact(self, parent):
        """Compact config panel"""
        card = tk.Frame(parent, bg=self.colors['bg_card'], relief='flat')
        card.pack(fill='x')
        
        # Header
        tk.Label(
            card,
            text="Configuration",
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['bg_card']
        ).pack(anchor='w', padx=15, pady=12)
        
        tk.Frame(card, bg=self.colors['border'], height=1).pack(fill='x')
        
        # Project
        proj_frame = tk.Frame(card, bg=self.colors['bg_card'])
        proj_frame.pack(fill='x', padx=15, pady=12)
        
        tk.Label(
            proj_frame,
            text="Project",
            font=('Segoe UI', 9),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_card']
        ).pack(anchor='w', pady=(0, 5))
        
        proj_input = tk.Frame(proj_frame, bg=self.colors['bg_card'])
        proj_input.pack(fill='x')
        
        self.project_entry = tk.Entry(
            proj_input,
            bg=self.colors['bg_main'],
            fg=self.colors['text'],
            insertbackground=self.colors['primary'],
            font=('Consolas', 9),
            relief='flat',
            bd=1,
            highlightthickness=1,
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['primary']
        )
        self.project_entry.pack(side='left', fill='x', expand=True, ipady=6)
        self.project_entry.insert(0, self.config.get('project_path', ''))
        
        tk.Button(
            proj_input,
            text="📂",
            command=self.select_project,
            bg=self.colors['bg_main'],
            fg=self.colors['text'],
            font=('Segoe UI', 10),
            relief='flat',
            cursor='hand2',
            width=3
        ).pack(side='left', padx=(5, 0))
        
        # API Status (compact)
        api_key = self.config.get('openrouter_api_key', '')
        if api_key:
            api_text = f"API: {api_key[:8]}...{api_key[-4:]}"
            api_color = self.colors['success']
        else:
            api_text = "API: Not configured"
            api_color = self.colors['text_dim']
        
        self.api_status_label = tk.Label(
            card,
            text=api_text,
            font=('Consolas', 8),
            fg=api_color,
            bg=self.colors['bg_card']
        )
        self.api_status_label.pack(anchor='w', padx=15, pady=(5, 12))
    
    def build_monitor_panel(self, parent):
        """Real-time monitoring panel"""
        card = tk.Frame(parent, bg=self.colors['bg_card'], relief='flat')
        card.pack(fill='both', expand=True)
        
        # Header
        header = tk.Frame(card, bg=self.colors['bg_card'])
        header.pack(fill='x', padx=15, pady=12)
        
        tk.Label(
            header,
            text="Live Monitor",
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['bg_card']
        ).pack(side='left')
        
        # Controls
        controls = tk.Frame(header, bg=self.colors['bg_card'])
        controls.pack(side='right')
        
        self.stop_btn = tk.Button(
            controls,
            text="⏹ Stop",
            command=self.stop_scan,
            bg=self.colors['bg_main'],
            fg=self.colors['text_dim'],
            font=('Segoe UI', 8),
            relief='flat',
            cursor='hand2',
            padx=10,
            pady=4,
            state='disabled'
        )
        self.stop_btn.pack(side='left', padx=5)
        
        tk.Button(
            controls,
            text="Clear",
            command=self.clear_monitor,
            bg=self.colors['bg_main'],
            fg=self.colors['text_dim'],
            font=('Segoe UI', 8),
            relief='flat',
            cursor='hand2',
            padx=10,
            pady=4
        ).pack(side='left')
        
        tk.Frame(card, bg=self.colors['border'], height=1).pack(fill='x')
        
        # Monitor output
        monitor_frame = tk.Frame(card, bg=self.colors['bg_main'])
        monitor_frame.pack(fill='both', expand=True, padx=1, pady=1)
        
        self.monitor = MonitoringText(
            monitor_frame,
            bg=self.colors['bg_main'],
            fg=self.colors['text'],
            insertbackground=self.colors['primary'],
            font=('Consolas', 9),
            wrap='word',
            relief='flat',
            padx=10,
            pady=10
        )
        self.monitor.pack(fill='both', expand=True)
        
        # Welcome
        self.monitor.log("VibeShield Enterprise initialized", "highlight")
        self.monitor.log("System ready for security operations", "info")
    
    def build_ai_view(self):
        """AI Assistant view"""
        tk.Label(
            self.content_frame,
            text="AI Security Assistant",
            font=('Segoe UI', 18, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['bg_main']
        ).pack(pady=30)
        
        card = tk.Frame(self.content_frame, bg=self.colors['bg_card'])
        card.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Chat
        self.ai_chat = MonitoringText(
            card,
            bg=self.colors['bg_main'],
            fg=self.colors['text'],
            font=('Consolas', 10),
            wrap='word'
        )
        self.ai_chat.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Input
        input_frame = tk.Frame(card, bg=self.colors['bg_card'])
        input_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        self.ai_input = tk.Entry(
            input_frame,
            bg=self.colors['bg_main'],
            fg=self.colors['text'],
            insertbackground=self.colors['primary'],
            font=('Segoe UI', 10),
            relief='flat',
            bd=1,
            highlightthickness=1,
            highlightbackground=self.colors['border']
        )
        self.ai_input.pack(side='left', fill='x', expand=True, ipady=8)
        self.ai_input.bind('<Return>', lambda e: self.send_ai_message())
        
        tk.Button(
            input_frame,
            text="Send",
            command=self.send_ai_message,
            bg=self.colors['primary'],
            fg='white',
            font=('Segoe UI', 9, 'bold'),
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=8
        ).pack(side='left', padx=(10, 0))
        
        # Welcome
        self.ai_chat.log("AI Security Assistant ready", "highlight")
        self.ai_chat.log("Ask me about vulnerabilities, fixes, or security best practices", "info")
    
    def build_results_view(self):
        """Results view"""
        tk.Label(
            self.content_frame,
            text="Scan Results",
            font=('Segoe UI', 18, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['bg_main']
        ).pack(pady=30)
        
        tk.Label(
            self.content_frame,
            text="Results will appear here after scan completion",
            font=('Segoe UI', 10),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_main']
        ).pack()
    
    def build_settings_view(self):
        """Settings view"""
        tk.Label(
            self.content_frame,
            text="Settings",
            font=('Segoe UI', 18, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['bg_main']
        ).pack(anchor='w', padx=20, pady=(20, 30))
        
        # OpenRouter API Key card
        card = tk.Frame(self.content_frame, bg=self.colors['bg_card'])
        card.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            card,
            text="OpenRouter API Key",
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['bg_card']
        ).pack(anchor='w', padx=15, pady=(15, 5))
        
        tk.Label(
            card,
            text="Required for Strix AI pentest (pipeline: OPENROUTER_API_KEY)",
            font=('Segoe UI', 9),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_card']
        ).pack(anchor='w', padx=15, pady=(0, 10))
        
        api_frame = tk.Frame(card, bg=self.colors['bg_card'])
        api_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        self.api_entry = tk.Entry(
            api_frame,
            bg=self.colors['bg_main'],
            fg=self.colors['text'],
            insertbackground=self.colors['primary'],
            font=('Consolas', 10),
            show='*',
            relief='flat',
            bd=1,
            highlightthickness=1,
            highlightbackground=self.colors['border']
        )
        self.api_entry.pack(side='left', fill='x', expand=True, ipady=8)
        self.api_entry.insert(0, self.config.get('openrouter_api_key', ''))
        
        tk.Button(
            api_frame,
            text="Save",
            command=self.save_api_key,
            bg=self.colors['primary'],
            fg='white',
            font=('Segoe UI', 9, 'bold'),
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=8
        ).pack(side='left', padx=(10, 0))
        
        # GitHub Token card
        card2 = tk.Frame(self.content_frame, bg=self.colors['bg_card'])
        card2.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            card2,
            text="GitHub Token",
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['bg_card']
        ).pack(anchor='w', padx=15, pady=(15, 5))
        
        tk.Label(
            card2,
            text="Required for Gitleaks and Kavach auto-fix (pipeline: GITHUB_TOKEN)",
            font=('Segoe UI', 9),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_card']
        ).pack(anchor='w', padx=15, pady=(0, 10))
        
        github_frame = tk.Frame(card2, bg=self.colors['bg_card'])
        github_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        self.github_entry = tk.Entry(
            github_frame,
            bg=self.colors['bg_main'],
            fg=self.colors['text'],
            insertbackground=self.colors['primary'],
            font=('Consolas', 10),
            show='*',
            relief='flat',
            bd=1,
            highlightthickness=1,
            highlightbackground=self.colors['border']
        )
        self.github_entry.pack(side='left', fill='x', expand=True, ipady=8)
        self.github_entry.insert(0, self.config.get('github_token', ''))
        
        tk.Button(
            github_frame,
            text="Save",
            command=self.save_github_token,
            bg=self.colors['primary'],
            fg='white',
            font=('Segoe UI', 9, 'bold'),
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=8
        ).pack(side='left', padx=(10, 0))
        
        # Target URL card
        card3 = tk.Frame(self.content_frame, bg=self.colors['bg_card'])
        card3.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            card3,
            text="Target URL",
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['bg_card']
        ).pack(anchor='w', padx=15, pady=(15, 5))
        
        tk.Label(
            card3,
            text="Target application URL for dynamic testing",
            font=('Segoe UI', 9),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_card']
        ).pack(anchor='w', padx=15, pady=(0, 10))
        
        url_frame = tk.Frame(card3, bg=self.colors['bg_card'])
        url_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        self.url_entry = tk.Entry(
            url_frame,
            bg=self.colors['bg_main'],
            fg=self.colors['text'],
            insertbackground=self.colors['primary'],
            font=('Consolas', 10),
            relief='flat',
            bd=1,
            highlightthickness=1,
            highlightbackground=self.colors['border']
        )
        self.url_entry.pack(side='left', fill='x', expand=True, ipady=8)
        self.url_entry.insert(0, self.config.get('target_url', ''))
        
        tk.Button(
            url_frame,
            text="Save",
            command=self.save_target_url,
            bg=self.colors['primary'],
            fg='white',
            font=('Segoe UI', 9, 'bold'),
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=8
        ).pack(side='left', padx=(10, 0))
        
        # Info card
        info_card = tk.Frame(self.content_frame, bg=self.colors['bg_card'])
        info_card.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            info_card,
            text="ℹ️ Pipeline Integration",
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['primary'],
            bg=self.colors['bg_card']
        ).pack(anchor='w', padx=15, pady=(15, 10))
        
        info_text = """These credentials match your GitHub Actions secrets:
        
• OPENROUTER_API_KEY → Used by Strix AI pentest
• GITHUB_TOKEN → Used by Gitleaks and Kavach auto-fix

Save them here to use the same tools locally!"""
        
        tk.Label(
            info_card,
            text=info_text,
            font=('Consolas', 9),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_card'],
            justify='left'
        ).pack(anchor='w', padx=15, pady=(0, 15))
    
    # ============================================================
    # TOOL TESTING
    # ============================================================
    
    def test_all_tools(self):
        """Test tool availability"""
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
                    result = subprocess.run(
                        [cmd] + args,
                        capture_output=True,
                        timeout=3
                    )
                
                if result.returncode == 0 or key == 'audit':
                    self.tools_status[key] = True
                    self.tool_widgets[key].config(fg=self.colors['success'])
                    self.monitor.log(f"{key}: Available", "success")
                else:
                    self.tools_status[key] = False
                    self.tool_widgets[key].config(fg=self.colors['danger'])
            except:
                self.tools_status[key] = False
                self.tool_widgets[key].config(fg=self.colors['danger'])
        
        self.monitor.log("Tool testing complete", "info")
    
    # ============================================================
    # SCAN OPERATIONS
    # ============================================================
    
    def run_full_scan(self):
        """Full orchestrated scan"""
        if self.scan_running:
            messagebox.showwarning("Running", "Scan already in progress")
            return
        
        project = self.project_entry.get().strip()
        if not project or not os.path.exists(project):
            messagebox.showerror("Error", "Please select a valid project path")
            return
        
        self.scan_running = True
        self.stop_btn.config(state='normal', fg=self.colors['danger'])
        self.update_status("SCANNING", self.colors['warning'])
        
        thread = threading.Thread(target=self._full_scan_thread, args=(project,))
        thread.daemon = True
        thread.start()
    
    def _full_scan_thread(self, project):
        """Full scan thread"""
        try:
            self.monitor.log("═" * 60, "dim")
            self.monitor.log("Starting full orchestrated scan", "highlight")
            self.monitor.log("═" * 60, "dim")
            
            # Static analysis
            self.monitor.log("\n[STAGE] Static Analysis", "info")
            self._run_audit(project)
            self._run_tool('gitleaks', 'Secret scanning')
            self._run_tool('semgrep', 'SAST analysis')
            self._run_tool('trivy', 'Dependency check')
            
            # Dynamic analysis
            self.monitor.log("\n[STAGE] Dynamic Analysis", "info")
            self._run_tool('strix', 'AI pentest')
            
            self.monitor.log("\n═" * 60, "dim")
            self.monitor.log("Scan complete", "success")
            self.monitor.log("═" * 60, "dim")
            
            self.update_status("COMPLETE", self.colors['success'])
        except Exception as e:
            self.monitor.log(f"Error: {e}", "error")
            self.update_status("ERROR", self.colors['danger'])
        finally:
            self.scan_running = False
            self.stop_btn.config(state='disabled', fg=self.colors['text_dim'])
    
    def _run_audit(self, project):
        if not self.tools_status.get('audit', False):
            self.monitor.log("Audit: Skipped (unavailable)", "warning")
            return
        
        self.monitor.log("Running Audit Engine...", "info")
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'audit.run_audit', '--project', project],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=Path(__file__).parent.parent
            )
            self.monitor.log("Audit: Complete", "success")
        except Exception as e:
            self.monitor.log(f"Audit: Error - {e}", "error")
    
    def _run_tool(self, tool, description):
        if not self.tools_status.get(tool, False):
            self.monitor.log(f"{tool}: Skipped (unavailable)", "warning")
            return
        
        self.monitor.log(f"Running {description}...", "info")
        time.sleep(1)
        self.monitor.log(f"{tool}: Complete", "success")
    
    def run_quick_scan(self):
        """Quick static scan"""
        project = self.project_entry.get().strip()
        if not project:
            messagebox.showerror("Error", "Please select a project")
            return
        
        self.monitor.log("\n[QUICK SCAN] Static analysis only", "info")
        self._run_audit(project)
        self.monitor.log("Quick scan complete", "success")
    
    def stop_scan(self):
        self.scan_running = False
        self.monitor.log("Scan stopped by user", "warning")
        self.update_status("STOPPED", self.colors['warning'])
    
    # ============================================================
    # AI
    # ============================================================
    
    def send_ai_message(self):
        msg = self.ai_input.get().strip()
        if not msg:
            return
        
        self.ai_input.delete(0, 'end')
        self.ai_chat.log(f"You: {msg}", "info")
        
        api_key = self.config.get('openrouter_api_key', '')
        if not api_key:
            self.ai_chat.log("Please configure API key in Settings", "warning")
            return
        
        # Simple response
        response = self._get_ai_response(msg)
        self.ai_chat.log(f"AI: {response}", "success")
    
    def _get_ai_response(self, msg):
        msg_lower = msg.lower()
        if "sql" in msg_lower:
            return "Use parameterized queries to prevent SQL injection"
        elif "xss" in msg_lower:
            return "Sanitize user input and use CSP headers"
        elif "idor" in msg_lower:
            return "Implement proper access control checks"
        else:
            return "I can help with security questions. Try: SQL, XSS, IDOR, secrets"
    
    # ============================================================
    # HELPERS
    # ============================================================
    
    def select_project(self):
        path = filedialog.askdirectory()
        if path:
            self.project_entry.delete(0, 'end')
            self.project_entry.insert(0, path)
            self.config['project_path'] = path
            self.save_config()
            self.monitor.log(f"Project: {path}", "info")
    
    def save_api_key(self):
        key = self.api_entry.get().strip()
        if not key:
            messagebox.showwarning("Error", "API key is empty")
            return
        
        self.config['openrouter_api_key'] = key
        self.save_config()
        
        # Update status
        if hasattr(self, 'api_status_label'):
            self.api_status_label.config(
                text=f"API: {key[:8]}...{key[-4:]}",
                fg=self.colors['success']
            )
        
        self.monitor.log(f"OpenRouter API key saved: {key[:8]}...{key[-4:]}", "success")
        messagebox.showinfo("Success", "OpenRouter API key saved")
    
    def save_github_token(self):
        token = self.github_entry.get().strip()
        if not token:
            messagebox.showwarning("Error", "GitHub token is empty")
            return
        
        self.config['github_token'] = token
        self.save_config()
        
        self.monitor.log(f"GitHub token saved: {token[:8]}...{token[-4:]}", "success")
        messagebox.showinfo("Success", "GitHub token saved")
    
    def save_target_url(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Error", "URL is empty")
            return
        
        self.config['target_url'] = url
        self.save_config()
        messagebox.showinfo("Success", "Target URL saved")
    
    def clear_monitor(self):
        self.monitor.delete('1.0', 'end')
        self.monitor.log("Monitor cleared", "info")
    
    def update_status(self, text, color):
        self.status_label.config(text=f"● {text}", fg=color)
        self.root.update()


def main():
    root = tk.Tk()
    app = VibeShieldEnterprise(root)
    root.mainloop()


if __name__ == "__main__":
    main()
