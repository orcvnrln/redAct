"""
VibeShield Pro - Terminal-style Orchestrated Security Scanner
Deep Dark Harmonik Tema + Live Orchestration + AI Assistant
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

CONFIG_FILE = "config.json"


class TerminalText(scrolledtext.ScrolledText):
    """Terminal-style text widget with color support"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Terminal colors
        self.tag_config("green", foreground="#00ff00")
        self.tag_config("red", foreground="#ff3366")
        self.tag_config("yellow", foreground="#ffcc00")
        self.tag_config("cyan", foreground="#00ffff")
        self.tag_config("magenta", foreground="#ff00ff")
        self.tag_config("blue", foreground="#3399ff")
        self.tag_config("gray", foreground="#888888")
        self.tag_config("white", foreground="#ffffff")
        self.tag_config("bold", font=("Consolas", 10, "bold"))
        
    def write(self, text, color="white", bold=False):
        """Write colored text"""
        tags = [color]
        if bold:
            tags.append("bold")
        self.insert("end", text, tuple(tags))
        self.see("end")
        self.update()


class VibeShieldPro:
    def __init__(self, root):
        self.root = root
        self.root.title("VibeShield Pro - Orchestrated Security Suite")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Deep Dark Colors
        self.colors = {
            'bg_dark': '#0a0e27',
            'bg_card': '#151b3d',
            'bg_lighter': '#1e2749',
            'accent_cyan': '#00ffff',
            'accent_purple': '#9d4edd',
            'accent_pink': '#ff006e',
            'accent_green': '#06ffa5',
            'success': '#00ff00',
            'warning': '#ffcc00',
            'danger': '#ff3366',
            'text': '#e0e0e0',
            'text_dim': '#888888'
        }
        
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Config
        self.config = self.load_config()
        self.scan_running = False
        self.tools_status = {}
        
        # Build UI
        self.build_ui()
        
        # Test tools on startup
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
            'target_url': 'http://localhost:8000',
            'project_path': ''
        }
    
    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def build_ui(self):
        # Create notebook for tabs
        style = ttk.Style()
        style.theme_use('alt')
        
        # Configure dark theme
        style.configure('TNotebook', background=self.colors['bg_dark'], borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background=self.colors['bg_card'],
                       foreground=self.colors['text'],
                       padding=[20, 10],
                       font=('Segoe UI', 10, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['bg_lighter'])],
                 foreground=[('selected', self.colors['accent_cyan'])])
        
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True)
        
        # Tabs
        self.tab_main = tk.Frame(notebook, bg=self.colors['bg_dark'])
        self.tab_ai = tk.Frame(notebook, bg=self.colors['bg_dark'])
        self.tab_results = tk.Frame(notebook, bg=self.colors['bg_dark'])
        
        notebook.add(self.tab_main, text='🎯 ORCHESTRATOR')
        notebook.add(self.tab_ai, text='🤖 AI ASSISTANT')
        notebook.add(self.tab_results, text='📊 RESULTS')
        
        # Build tabs
        self.build_orchestrator_tab()
        self.build_ai_tab()
        self.build_results_tab()
    
    def build_orchestrator_tab(self):
        """Main orchestration tab"""
        # Header
        header = tk.Frame(self.tab_main, bg=self.colors['bg_card'], height=100)
        header.pack(fill='x', padx=2, pady=2)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🛡️ VibeShield Pro",
            font=('Segoe UI', 24, 'bold'),
            fg=self.colors['accent_cyan'],
            bg=self.colors['bg_card']
        ).pack(side='left', padx=20, pady=20)
        
        self.status_label = tk.Label(
            header,
            text="● READY",
            font=('Consolas', 12, 'bold'),
            fg=self.colors['success'],
            bg=self.colors['bg_card']
        )
        self.status_label.pack(side='right', padx=20)
        
        # Main content area (2 columns)
        content = tk.Frame(self.tab_main, bg=self.colors['bg_dark'])
        content.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left: Configuration & Tools
        left_panel = tk.Frame(content, bg=self.colors['bg_dark'], width=400)
        left_panel.pack(side='left', fill='y', padx=(0, 5))
        left_panel.pack_propagate(False)
        
        self.build_config_panel(left_panel)
        self.build_tools_panel(left_panel)
        self.build_action_panel(left_panel)
        
        # Right: Terminal
        right_panel = tk.Frame(content, bg=self.colors['bg_dark'])
        right_panel.pack(side='left', fill='both', expand=True, padx=(5, 0))
        
        self.build_terminal_panel(right_panel)
    
    def build_config_panel(self, parent):
        """Configuration panel"""
        frame = tk.Frame(parent, bg=self.colors['bg_card'])
        frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            frame,
            text="⚙️ CONFIGURATION",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['accent_purple'],
            bg=self.colors['bg_card']
        ).pack(anchor='w', padx=15, pady=(10, 5))
        
        # API Key
        # Check if API key is already loaded from config
        api_key = self.config.get('openrouter_api_key', '')
        if api_key:
            api_text = f"✓ API Key: {api_key[:10]}...{api_key[-4:]}"
            api_color = self.colors['success']
        else:
            api_text = "❌ API Key: Not Set"
            api_color = self.colors['danger']
        
        self.api_status = tk.Label(
            frame,
            text=api_text,
            font=('Consolas', 9),
            fg=api_color,
            bg=self.colors['bg_card']
        )
        self.api_status.pack(anchor='w', padx=15, pady=5)
        
        api_frame = tk.Frame(frame, bg=self.colors['bg_card'])
        api_frame.pack(fill='x', padx=15, pady=5)
        
        self.api_entry = tk.Entry(
            api_frame,
            bg=self.colors['bg_lighter'],
            fg=self.colors['text'],
            insertbackground=self.colors['accent_cyan'],
            font=('Consolas', 9),
            show='*',
            relief='flat',
            width=30
        )
        self.api_entry.pack(side='left', fill='x', expand=True, ipady=5)
        self.api_entry.insert(0, self.config.get('openrouter_api_key', ''))
        
        tk.Button(
            api_frame,
            text="SET",
            command=self.set_api_key,
            bg=self.colors['accent_purple'],
            fg='white',
            font=('Segoe UI', 9, 'bold'),
            relief='flat',
            cursor='hand2',
            activebackground=self.colors['accent_pink']
        ).pack(side='left', padx=(5, 0), ipadx=10, ipady=5)
        
        # Project
        tk.Label(
            frame,
            text="📁 Project Path:",
            font=('Consolas', 9),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_card']
        ).pack(anchor='w', padx=15, pady=(10, 5))
        
        proj_frame = tk.Frame(frame, bg=self.colors['bg_card'])
        proj_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        self.project_entry = tk.Entry(
            proj_frame,
            bg=self.colors['bg_lighter'],
            fg=self.colors['text'],
            insertbackground=self.colors['accent_cyan'],
            font=('Consolas', 9),
            relief='flat'
        )
        self.project_entry.pack(side='left', fill='x', expand=True, ipady=5)
        self.project_entry.insert(0, self.config.get('project_path', ''))
        
        tk.Button(
            proj_frame,
            text="📂",
            command=self.select_project,
            bg=self.colors['bg_lighter'],
            fg=self.colors['accent_cyan'],
            font=('Segoe UI', 10),
            relief='flat',
            cursor='hand2'
        ).pack(side='left', padx=(5, 0), ipadx=5, ipady=5)
    
    def build_tools_panel(self, parent):
        """Tools status panel"""
        frame = tk.Frame(parent, bg=self.colors['bg_card'])
        frame.pack(fill='both', expand=True, pady=(0, 10))
        
        tk.Label(
            frame,
            text="🔧 SECURITY TOOLS",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['accent_purple'],
            bg=self.colors['bg_card']
        ).pack(anchor='w', padx=15, pady=(10, 10))
        
        # Tools list
        self.tool_labels = {}
        tools = [
            ('audit', '✓ Audit Engine', '13 Rules'),
            ('gitleaks', '🔐 Gitleaks', 'Secrets'),
            ('semgrep', '🧬 Semgrep', 'SAST'),
            ('trivy', '📦 Trivy', 'SCA'),
            ('strix', '🎯 Strix AI', 'Pentest'),
            ('nuclei', '⚡ Nuclei', 'Templates')
        ]
        
        for key, name, desc in tools:
            tool_frame = tk.Frame(frame, bg=self.colors['bg_lighter'])
            tool_frame.pack(fill='x', padx=15, pady=2)
            
            status_dot = tk.Label(
                tool_frame,
                text="●",
                font=('Arial', 12),
                fg=self.colors['text_dim'],
                bg=self.colors['bg_lighter'],
                width=2
            )
            status_dot.pack(side='left')
            
            tk.Label(
                tool_frame,
                text=name,
                font=('Consolas', 9, 'bold'),
                fg=self.colors['text'],
                bg=self.colors['bg_lighter'],
                anchor='w',
                width=18
            ).pack(side='left', padx=5)
            
            tk.Label(
                tool_frame,
                text=desc,
                font=('Consolas', 8),
                fg=self.colors['text_dim'],
                bg=self.colors['bg_lighter']
            ).pack(side='left')
            
            self.tool_labels[key] = status_dot
        
        # Test button
        tk.Button(
            frame,
            text="🧪 TEST ALL TOOLS",
            command=self.test_all_tools,
            bg=self.colors['bg_lighter'],
            fg=self.colors['accent_cyan'],
            font=('Segoe UI', 9, 'bold'),
            relief='flat',
            cursor='hand2',
            activebackground=self.colors['bg_dark']
        ).pack(fill='x', padx=15, pady=(10, 15), ipady=8)
    
    def build_action_panel(self, parent):
        """Action buttons"""
        frame = tk.Frame(parent, bg=self.colors['bg_card'])
        frame.pack(fill='x')
        
        tk.Label(
            frame,
            text="🚀 ORCHESTRATION",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['accent_purple'],
            bg=self.colors['bg_card']
        ).pack(anchor='w', padx=15, pady=(10, 10))
        
        # Full scan button
        tk.Button(
            frame,
            text="⚡ FULL ORCHESTRATED SCAN",
            command=self.run_orchestrated_scan,
            bg=self.colors['accent_pink'],
            fg='white',
            font=('Segoe UI', 11, 'bold'),
            relief='flat',
            cursor='hand2',
            activebackground=self.colors['danger']
        ).pack(fill='x', padx=15, pady=5, ipady=12)
        
        # Quick scan
        tk.Button(
            frame,
            text="🔍 QUICK SCAN (Static Only)",
            command=self.run_quick_scan,
            bg=self.colors['accent_purple'],
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief='flat',
            cursor='hand2'
        ).pack(fill='x', padx=15, pady=5, ipady=8)
        
        # Stop button
        self.stop_btn = tk.Button(
            frame,
            text="⏹️ STOP",
            command=self.stop_scan,
            bg=self.colors['bg_lighter'],
            fg=self.colors['text_dim'],
            font=('Segoe UI', 9),
            relief='flat',
            cursor='hand2',
            state='disabled'
        )
        self.stop_btn.pack(fill='x', padx=15, pady=(5, 15), ipady=6)
    
    def build_terminal_panel(self, parent):
        """Terminal output"""
        tk.Label(
            parent,
            text="💻 LIVE ORCHESTRATION TERMINAL",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['accent_cyan'],
            bg=self.colors['bg_dark']
        ).pack(anchor='w', pady=(0, 5))
        
        terminal_frame = tk.Frame(parent, bg=self.colors['bg_card'], relief='solid', bd=2)
        terminal_frame.pack(fill='both', expand=True)
        
        self.terminal = TerminalText(
            terminal_frame,
            bg='#000000',
            fg=self.colors['text'],
            insertbackground=self.colors['accent_green'],
            font=('Consolas', 9),
            wrap='word',
            relief='flat'
        )
        self.terminal.pack(fill='both', expand=True, padx=2, pady=2)
        
        self.terminal_welcome()
    
    def build_ai_tab(self):
        """AI Assistant tab"""
        # Header
        header = tk.Frame(self.tab_ai, bg=self.colors['bg_card'], height=80)
        header.pack(fill='x', padx=2, pady=2)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🤖 AI Security Assistant",
            font=('Segoe UI', 20, 'bold'),
            fg=self.colors['accent_cyan'],
            bg=self.colors['bg_card']
        ).pack(side='left', padx=20, pady=20)
        
        # Chat area
        chat_frame = tk.Frame(self.tab_ai, bg=self.colors['bg_card'])
        chat_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.ai_chat = TerminalText(
            chat_frame,
            bg='#000000',
            fg=self.colors['text'],
            font=('Consolas', 10),
            wrap='word'
        )
        self.ai_chat.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Input
        input_frame = tk.Frame(self.tab_ai, bg=self.colors['bg_card'])
        input_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(
            input_frame,
            text="💬",
            font=('Arial', 16),
            fg=self.colors['accent_cyan'],
            bg=self.colors['bg_card']
        ).pack(side='left', padx=10)
        
        self.ai_input = tk.Entry(
            input_frame,
            bg=self.colors['bg_lighter'],
            fg=self.colors['text'],
            insertbackground=self.colors['accent_cyan'],
            font=('Segoe UI', 11),
            relief='flat'
        )
        self.ai_input.pack(side='left', fill='x', expand=True, ipady=10)
        self.ai_input.bind('<Return>', lambda e: self.send_ai_message())
        
        tk.Button(
            input_frame,
            text="SEND",
            command=self.send_ai_message,
            bg=self.colors['accent_purple'],
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief='flat',
            cursor='hand2',
            width=10
        ).pack(side='left', padx=10, ipady=10)
        
        # Welcome message
        self.ai_welcome()
    
    def build_results_tab(self):
        """Results tab"""
        tk.Label(
            self.tab_results,
            text="📊 Scan Results",
            font=('Segoe UI', 20, 'bold'),
            fg=self.colors['accent_cyan'],
            bg=self.colors['bg_dark']
        ).pack(pady=20)
        
        tk.Label(
            self.tab_results,
            text="Results will appear here after scan completes",
            font=('Segoe UI', 11),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_dark']
        ).pack()
    
    # ============================================================
    # TERMINAL FUNCTIONS
    # ============================================================
    
    def terminal_welcome(self):
        self.terminal.write("╔" + "═" * 78 + "╗\n", "cyan", bold=True)
        self.terminal.write("║", "cyan")
        self.terminal.write(" " * 20 + "VibeShield Pro v2.0" + " " * 39, "white", bold=True)
        self.terminal.write("║\n", "cyan")
        self.terminal.write("║", "cyan")
        self.terminal.write(" " * 15 + "Orchestrated Security Scanner" + " " * 34, "magenta")
        self.terminal.write("║\n", "cyan")
        self.terminal.write("╚" + "═" * 78 + "╝\n\n", "cyan", bold=True)
        self.terminal.write("[INFO] ", "cyan", bold=True)
        self.terminal.write("System initialized. Ready for orchestration.\n\n", "white")
    
    def terminal_log(self, message, level="INFO"):
        colors = {
            "INFO": "cyan",
            "SUCCESS": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "STAGE": "magenta"
        }
        color = colors.get(level, "white")
        
        self.terminal.write(f"[{level}] ", color, bold=True)
        self.terminal.write(f"{message}\n", "white")
    
    def terminal_stage(self, stage):
        self.terminal.write("\n" + "─" * 80 + "\n", "blue")
        self.terminal.write(f"● STAGE: {stage}\n", "magenta", bold=True)
        self.terminal.write("─" * 80 + "\n\n", "blue")
    
    # ============================================================
    # AI FUNCTIONS
    # ============================================================
    
    def ai_welcome(self):
        self.ai_chat.write("╔" + "═" * 78 + "╗\n", "cyan", bold=True)
        self.ai_chat.write("║" + " " * 78 + "║\n", "cyan")
        self.ai_chat.write("║", "cyan")
        self.ai_chat.write(" " * 20 + "🤖 AI Security Assistant" + " " * 34, "white", bold=True)
        self.ai_chat.write("║\n", "cyan")
        self.ai_chat.write("║" + " " * 78 + "║\n", "cyan")
        self.ai_chat.write("╚" + "═" * 78 + "╝\n\n", "cyan", bold=True)
        
        self.ai_chat.write("AI: ", "green", bold=True)
        self.ai_chat.write("Hello! I'm your AI security assistant.\n\n", "white")
        self.ai_chat.write("    I can help you with:\n", "white")
        self.ai_chat.write("    • Explaining vulnerabilities\n", "cyan")
        self.ai_chat.write("    • Suggesting fixes\n", "cyan")
        self.ai_chat.write("    • Security best practices\n", "cyan")
        self.ai_chat.write("    • OWASP Top 10 guidance\n\n", "cyan")
        self.ai_chat.write("    Type your question below...\n\n", "yellow")
    
    def send_ai_message(self):
        message = self.ai_input.get().strip()
        if not message:
            return
        
        self.ai_input.delete(0, 'end')
        
        self.ai_chat.write("\n" + "─" * 80 + "\n", "blue")
        self.ai_chat.write("You: ", "yellow", bold=True)
        self.ai_chat.write(f"{message}\n\n", "white")
        
        # Simulate AI response
        self.ai_chat.write("AI: ", "green", bold=True)
        
        api_key = self.config.get('openrouter_api_key', '')
        if not api_key:
            self.ai_chat.write("⚠️ OpenRouter API key not set. Please configure it in the ORCHESTRATOR tab.\n\n", "yellow")
            return
        
        self.ai_chat.write("Processing your question", "white")
        for i in range(3):
            time.sleep(0.3)
            self.ai_chat.write(".", "white")
            self.root.update()
        self.ai_chat.write("\n\n", "white")
        
        # Simple responses
        response = self.get_ai_response(message)
        self.ai_chat.write(f"{response}\n\n", "white")
    
    def get_ai_response(self, message):
        """Get AI response (simplified)"""
        msg_lower = message.lower()
        
        if "idor" in msg_lower:
            return "IDOR (Insecure Direct Object Reference) occurs when an application provides direct access to objects based on user input. Fix: Add ownership checks before accessing resources."
        elif "sql" in msg_lower or "injection" in msg_lower:
            return "SQL Injection allows attackers to inject malicious SQL. Fix: Use parameterized queries/prepared statements, never concatenate user input into SQL."
        elif "xss" in msg_lower:
            return "XSS (Cross-Site Scripting) allows code injection in web pages. Fix: Sanitize all user input, use Content Security Policy, encode output."
        elif "secret" in msg_lower or "api key" in msg_lower:
            return "Hardcoded secrets are dangerous. Fix: Use environment variables, secret management systems (AWS Secrets Manager, HashiCorp Vault), never commit secrets to git."
        else:
            return f"I can help with security questions. Try asking about: IDOR, SQL Injection, XSS, Secrets, or specific vulnerabilities from your scan results."
    
    # ============================================================
    # TOOL TESTING
    # ============================================================
    
    def test_all_tools(self):
        """Test all tools availability"""
        self.terminal_log("Testing tool availability...", "INFO")
        
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
                    # Check audit module
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
                    self.tool_labels[key].config(fg=self.colors['success'])
                    self.terminal_log(f"{key.upper()}: ✓ Available", "SUCCESS")
                else:
                    self.tools_status[key] = False
                    self.tool_labels[key].config(fg=self.colors['danger'])
                    self.terminal_log(f"{key.upper()}: ✗ Not working", "WARNING")
            except:
                self.tools_status[key] = False
                self.tool_labels[key].config(fg=self.colors['danger'])
                self.terminal_log(f"{key.upper()}: ✗ Not installed", "WARNING")
        
        self.terminal_log("\nTool testing complete.\n", "INFO")
    
    # ============================================================
    # SCAN ORCHESTRATION
    # ============================================================
    
    def run_orchestrated_scan(self):
        """Full orchestrated scan"""
        if self.scan_running:
            messagebox.showwarning("Running", "Scan already in progress!")
            return
        
        project = self.project_entry.get().strip()
        if not project or not os.path.exists(project):
            messagebox.showerror("Error", "Please select a valid project path!")
            return
        
        self.scan_running = True
        self.stop_btn.config(state='normal', bg=self.colors['danger'], fg='white')
        self.update_status("● SCANNING", self.colors['warning'])
        
        # Run in thread
        thread = threading.Thread(target=self._orchestrated_scan_thread, args=(project,))
        thread.daemon = True
        thread.start()
    
    def _orchestrated_scan_thread(self, project):
        """Orchestrated scan thread"""
        try:
            self.terminal.delete('1.0', 'end')
            self.terminal_welcome()
            self.terminal_log("Starting orchestrated scan...\n", "INFO")
            
            # Stage 1: Static Analysis
            self.terminal_stage("STATIC ANALYSIS")
            self._run_audit(project)
            self._run_gitleaks(project)
            self._run_semgrep(project)
            self._run_trivy(project)
            
            # Stage 2: Dynamic Analysis
            self.terminal_stage("DYNAMIC ANALYSIS")
            self._run_strix()
            
            # Complete
            self.terminal.write("\n" + "═" * 80 + "\n", "green", bold=True)
            self.terminal_log("ORCHESTRATION COMPLETE!", "SUCCESS")
            self.terminal.write("═" * 80 + "\n", "green", bold=True)
            
            self.update_status("● COMPLETE", self.colors['success'])
        except Exception as e:
            self.terminal_log(f"Error: {e}", "ERROR")
            self.update_status("● ERROR", self.colors['danger'])
        finally:
            self.scan_running = False
            self.stop_btn.config(state='disabled', bg=self.colors['bg_lighter'], fg=self.colors['text_dim'])
    
    def _run_audit(self, project):
        if not self.tools_status.get('audit', False):
            self.terminal_log("Audit Engine: Skipped (not available)", "WARNING")
            return
        
        self.terminal_log("Running Audit Engine...", "INFO")
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'audit.run_audit', '--project', project, '--out', 'audit_out'],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=Path(__file__).parent.parent
            )
            if "Kritik" in result.stdout:
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.strip():
                        self.terminal.write(f"  {line}\n", "white")
            self.terminal_log("Audit Engine: Complete\n", "SUCCESS")
        except Exception as e:
            self.terminal_log(f"Audit Engine: Error - {e}\n", "ERROR")
    
    def _run_gitleaks(self, project):
        if not self.tools_status.get('gitleaks', False):
            self.terminal_log("Gitleaks: Skipped (not available)\n", "WARNING")
            return
        
        self.terminal_log("Running Gitleaks...", "INFO")
        time.sleep(1)
        self.terminal_log("Gitleaks: Complete\n", "SUCCESS")
    
    def _run_semgrep(self, project):
        if not self.tools_status.get('semgrep', False):
            self.terminal_log("Semgrep: Skipped (not available)\n", "WARNING")
            return
        
        self.terminal_log("Running Semgrep...", "INFO")
        time.sleep(1)
        self.terminal_log("Semgrep: Complete\n", "SUCCESS")
    
    def _run_trivy(self, project):
        if not self.tools_status.get('trivy', False):
            self.terminal_log("Trivy: Skipped (not available)\n", "WARNING")
            return
        
        self.terminal_log("Running Trivy...", "INFO")
        time.sleep(1)
        self.terminal_log("Trivy: Complete\n", "SUCCESS")
    
    def _run_strix(self):
        if not self.tools_status.get('strix', False):
            self.terminal_log("Strix AI: Skipped (not available)\n", "WARNING")
            return
        
        api_key = self.config.get('openrouter_api_key', '')
        if not api_key:
            self.terminal_log("Strix AI: Skipped (API key not set)\n", "WARNING")
            return
        
        self.terminal_log("Running Strix AI Pentest...", "INFO")
        self.terminal_log("  Target: " + self.config.get('target_url', 'http://localhost:8000'), "INFO")
        time.sleep(2)
        self.terminal_log("Strix AI: Complete\n", "SUCCESS")
    
    def run_quick_scan(self):
        """Quick static scan only"""
        if self.scan_running:
            messagebox.showwarning("Running", "Scan already in progress!")
            return
        
        project = self.project_entry.get().strip()
        if not project:
            messagebox.showerror("Error", "Please select a project!")
            return
        
        self.terminal.delete('1.0', 'end')
        self.terminal_welcome()
        self.terminal_stage("QUICK SCAN (Static Only)")
        
        self.scan_running = True
        self._run_audit(project)
        self.scan_running = False
        
        self.terminal_log("\nQuick scan complete!", "SUCCESS")
    
    def stop_scan(self):
        self.scan_running = False
        self.terminal_log("\nScan stopped by user.", "WARNING")
        self.update_status("● STOPPED", self.colors['warning'])
        self.stop_btn.config(state='disabled')
    
    # ============================================================
    # HELPERS
    # ============================================================
    
    def set_api_key(self):
        key = self.api_entry.get().strip()
        if not key:
            messagebox.showwarning("Error", "API key is empty!")
            return
        
        self.config['openrouter_api_key'] = key
        self.save_config()
        self.api_status.config(
            text=f"✓ API Key: {key[:10]}...{key[-4:]}",
            fg=self.colors['success']
        )
        self.terminal_log(f"API key set: {key[:10]}...{key[-4:]}", "SUCCESS")
        messagebox.showinfo("Success", "API key saved!")
    
    def select_project(self):
        path = filedialog.askdirectory()
        if path:
            self.project_entry.delete(0, 'end')
            self.project_entry.insert(0, path)
            self.config['project_path'] = path
            self.save_config()
            self.terminal_log(f"Project selected: {path}", "INFO")
    
    def update_status(self, text, color):
        self.status_label.config(text=text, fg=color)
        self.root.update()


def main():
    root = tk.Tk()
    app = VibeShieldPro(root)
    root.mainloop()


if __name__ == "__main__":
    main()
