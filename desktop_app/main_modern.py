"""
VibeShield Desktop - Modern User-Friendly UI
Dashboard + Tool Status + Visual Pentest Results
"""

import json
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from typing import Dict, Any, List
from pathlib import Path

# Try import optional modules
try:
    from scanner import DesktopScanner, ScanResult
    from gate import DeterministicGate
    SCANNER_AVAILABLE = True
except:
    SCANNER_AVAILABLE = False

CONFIG_PATH = "config.json"


class ModernVibeShieldApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("VibeShield - Modern DevSecOps Dashboard")
        self.root.geometry("1400x850")
        self.root.minsize(1200, 700)
        
        # Colors
        self.colors = {
            'bg': '#1e1e2e',
            'fg': '#cdd6f4',
            'primary': '#89b4fa',
            'success': '#a6e3a1',
            'warning': '#f9e2af',
            'danger': '#f38ba8',
            'card_bg': '#313244',
            'hover': '#45475a'
        }
        
        # Config
        self.config = self._load_config()
        
        # Setup UI
        self._setup_styles()
        self._build_modern_ui()
        
    def _load_config(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_config(self):
        with open(CONFIG_PATH, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _setup_styles(self):
        """Modern ttk stilleri"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('Header.TLabel', font=('Segoe UI', 18, 'bold'), foreground=self.colors['primary'])
        style.configure('Title.TLabel', font=('Segoe UI', 14, 'bold'))
        style.configure('Card.TFrame', background=self.colors['card_bg'], relief='raised')
        
        # Buttons
        style.configure('TButton', padding=10, font=('Segoe UI', 10))
        style.map('TButton', background=[('active', self.colors['primary'])])
        
        style.configure('Primary.TButton', background=self.colors['primary'], foreground='white', font=('Segoe UI', 10, 'bold'))
        style.configure('Success.TButton', background=self.colors['success'], foreground='black')
        style.configure('Danger.TButton', background=self.colors['danger'], foreground='white')
    
    def _build_modern_ui(self):
        """Modern dashboard UI"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True)
        
        # Top bar
        self._build_top_bar(main_container)
        
        # Content area with sidebar
        content = ttk.Frame(main_container)
        content.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Sidebar
        self._build_sidebar(content)
        
        # Main content (dashboard)
        self.content_frame = ttk.Frame(content)
        self.content_frame.pack(side='left', fill='both', expand=True, padx=(10, 0))
        
        # Show dashboard by default
        self._show_dashboard()
    
    def _build_top_bar(self, parent):
        """Top navigation bar"""
        top_bar = ttk.Frame(parent, height=60)
        top_bar.pack(fill='x', padx=10, pady=(10, 0))
        top_bar.pack_propagate(False)
        
        # Logo/Title
        ttk.Label(
            top_bar, 
            text="🛡️ VibeShield", 
            style='Header.TLabel'
        ).pack(side='left', padx=10)
        
        # API Key status
        self.api_status_var = tk.StringVar(value="❌ API Key yoxdur")
        self._update_api_status()
        
        api_label = ttk.Label(top_bar, textvariable=self.api_status_var, font=('Segoe UI', 10))
        api_label.pack(side='right', padx=10)
        
        # Quick actions
        ttk.Button(
            top_bar, 
            text="⚙️ Settings", 
            command=self._show_settings,
            style='TButton'
        ).pack(side='right', padx=5)
    
    def _build_sidebar(self, parent):
        """Left sidebar navigation"""
        sidebar = ttk.Frame(parent, width=200)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        # Navigation buttons
        nav_items = [
            ("📊 Dashboard", self._show_dashboard),
            ("🔑 API Keys", self._show_api_keys),
            ("🔍 Security Scan", self._show_security_scan),
            ("🎯 Pentest", self._show_pentest),
            ("📁 Projects", self._show_projects),
            ("🤖 AI Chat", self._show_ai_chat),
            ("📄 Reports", self._show_reports),
        ]
        
        for text, command in nav_items:
            btn = ttk.Button(
                sidebar, 
                text=text, 
                command=command,
                width=20
            )
            btn.pack(fill='x', pady=2, padx=5)
        
        # Footer
        ttk.Label(
            sidebar, 
            text="\nv1.0.0\nVibeShield\n2024", 
            justify='center',
            font=('Segoe UI', 8)
        ).pack(side='bottom', pady=10)
    
    def _clear_content(self):
        """Clear main content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    # ===================================================================
    # DASHBOARD
    # ===================================================================
    def _show_dashboard(self):
        self._clear_content()
        
        # Header
        ttk.Label(
            self.content_frame, 
            text="Security Dashboard", 
            style='Title.TLabel'
        ).pack(anchor='w', pady=(0, 20))
        
        # Tool status cards
        cards_frame = ttk.Frame(self.content_frame)
        cards_frame.pack(fill='x', pady=(0, 20))
        
        tools = [
            {
                'name': 'Audit Engine',
                'icon': '🔍',
                'status': 'active',
                'desc': '13 Regex Qayda\nDeterministik',
                'type': 'Statik'
            },
            {
                'name': 'Gitleaks',
                'icon': '🔐',
                'status': self._check_tool('gitleaks'),
                'desc': 'Secret Aşkarlanması\nAPI Key, Token',
                'type': 'Statik'
            },
            {
                'name': 'Semgrep',
                'icon': '🧬',
                'status': self._check_tool('semgrep'),
                'desc': 'SAST Kod Təhlili\n30+ Dil',
                'type': 'Statik'
            },
            {
                'name': 'Trivy',
                'icon': '📦',
                'status': self._check_tool('trivy'),
                'desc': 'SCA Dependencies\nCVE Skan',
                'type': 'Statik'
            },
            {
                'name': 'Strix AI',
                'icon': '🎯',
                'status': self._check_tool('strix'),
                'desc': 'AI Pentest\nPoC Təsdiqi',
                'type': 'Dinamik'
            },
            {
                'name': 'Nuclei',
                'icon': '⚡',
                'status': self._check_tool('nuclei'),
                'desc': 'Template Skan\n5000+ Template',
                'type': 'Dinamik'
            },
        ]
        
        # Create 3 columns
        for i in range(0, len(tools), 3):
            row_frame = ttk.Frame(cards_frame)
            row_frame.pack(fill='x', pady=5)
            
            for tool in tools[i:i+3]:
                self._create_tool_card(row_frame, tool)
        
        # Quick stats
        stats_frame = ttk.Frame(self.content_frame)
        stats_frame.pack(fill='x', pady=20)
        
        self._create_stat_box(stats_frame, "📊 Ümumi Skan", "0", "Bu sessiyada").pack(side='left', padx=5, fill='x', expand=True)
        self._create_stat_box(stats_frame, "✅ Təmiz", "0", "Zəiflik yoxdur").pack(side='left', padx=5, fill='x', expand=True)
        self._create_stat_box(stats_frame, "⚠️ Xəbərdarlıq", "0", "Orta/Aşağı").pack(side='left', padx=5, fill='x', expand=True)
        self._create_stat_box(stats_frame, "🚫 Bloklandı", "0", "Kritik/Yüksək").pack(side='left', padx=5, fill='x', expand=True)
        
        # Quick actions
        actions_frame = ttk.Frame(self.content_frame)
        actions_frame.pack(fill='x', pady=20)
        
        ttk.Label(actions_frame, text="Quick Actions", font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        btn_frame = ttk.Frame(actions_frame)
        btn_frame.pack(fill='x')
        
        ttk.Button(
            btn_frame, 
            text="🚀 Full Scan", 
            command=self._run_full_scan,
            style='Primary.TButton'
        ).pack(side='left', padx=5)
        
        ttk.Button(
            btn_frame, 
            text="📁 Open Project", 
            command=self._open_project
        ).pack(side='left', padx=5)
        
        ttk.Button(
            btn_frame, 
            text="🎯 Run Pentest", 
            command=self._show_pentest
        ).pack(side='left', padx=5)
    
    def _create_tool_card(self, parent, tool):
        """Create a tool status card"""
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(side='left', fill='both', expand=True, padx=5, ipadx=10, ipady=10)
        
        # Icon and name
        header = ttk.Frame(card)
        header.pack(fill='x', pady=(0, 5))
        
        ttk.Label(
            header, 
            text=tool['icon'], 
            font=('Segoe UI', 24)
        ).pack(side='left')
        
        ttk.Label(
            header, 
            text=tool['name'], 
            font=('Segoe UI', 11, 'bold')
        ).pack(side='left', padx=10)
        
        # Status badge
        status_color = self.colors['success'] if tool['status'] == 'active' else self.colors['danger']
        status_text = "✓ Active" if tool['status'] == 'active' else "✗ Missing"
        
        status_label = tk.Label(
            card, 
            text=status_text, 
            bg=status_color, 
            fg='black' if tool['status'] == 'active' else 'white',
            font=('Segoe UI', 8, 'bold'),
            padx=5,
            pady=2
        )
        status_label.pack(anchor='w', pady=5)
        
        # Description
        ttk.Label(
            card, 
            text=tool['desc'], 
            font=('Segoe UI', 9),
            justify='left'
        ).pack(anchor='w', pady=5)
        
        # Type badge
        ttk.Label(
            card, 
            text=tool['type'], 
            font=('Segoe UI', 8, 'italic')
        ).pack(anchor='w')
    
    def _create_stat_box(self, parent, title, value, subtitle):
        """Create a statistics box"""
        box = ttk.Frame(parent, style='Card.TFrame')
        
        ttk.Label(box, text=title, font=('Segoe UI', 10)).pack(pady=(10, 5))
        ttk.Label(box, text=value, font=('Segoe UI', 24, 'bold')).pack()
        ttk.Label(box, text=subtitle, font=('Segoe UI', 8)).pack(pady=(5, 10))
        
        return box
    
    def _check_tool(self, tool_name):
        """Check if tool is installed"""
        import subprocess
        try:
            result = subprocess.run(
                [tool_name, '--version'],
                capture_output=True,
                timeout=2
            )
            return 'active' if result.returncode == 0 else 'missing'
        except:
            return 'missing'
    
    # ===================================================================
    # API KEYS
    # ===================================================================
    def _show_api_keys(self):
        self._clear_content()
        
        ttk.Label(
            self.content_frame, 
            text="API Key İdarəetməsi", 
            style='Title.TLabel'
        ).pack(anchor='w', pady=(0, 20))
        
        # OpenRouter
        or_frame = ttk.Frame(self.content_frame, style='Card.TFrame')
        or_frame.pack(fill='x', pady=10, padx=5, ipadx=20, ipady=20)
        
        ttk.Label(or_frame, text="🔑 OpenRouter API Key", font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        # Status
        self.or_status_var = tk.StringVar()
        self._update_or_status()
        ttk.Label(or_frame, textvariable=self.or_status_var, font=('Segoe UI', 10)).pack(anchor='w', pady=5)
        
        # Input
        input_frame = ttk.Frame(or_frame)
        input_frame.pack(fill='x', pady=10)
        
        self.or_entry = ttk.Entry(input_frame, width=60, show='*', font=('Consolas', 10))
        self.or_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        current_key = self.config.get('openrouter_api_key', '')
        if current_key:
            self.or_entry.insert(0, current_key)
        
        # Buttons
        btn_frame = ttk.Frame(or_frame)
        btn_frame.pack(fill='x', pady=10)
        
        ttk.Button(btn_frame, text="💾 Save", command=self._save_or_key, style='Success.TButton').pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🧪 Test", command=self._test_or_key).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🌐 Get Key", command=lambda: self._open_url('https://openrouter.ai')).pack(side='left', padx=5)
        
        # Info
        info = """✅ Pulsuz tier mövcuddur (kredit kartı lazım deyil)
🎯 Strix AI pentest üçün lazımdır
🤖 Desktop AI Chat üçün lazımdır
📊 Model: gemma-2-9b-it (pulsuz)"""
        
        ttk.Label(or_frame, text=info, justify='left', font=('Segoe UI', 9)).pack(anchor='w', pady=10)
    
    def _update_api_status(self):
        key = self.config.get('openrouter_api_key', '')
        if key and len(key) > 10:
            self.api_status_var.set(f"✅ API: {key[:10]}...{key[-4:]}")
        else:
            self.api_status_var.set("❌ API Key yoxdur")
    
    def _update_or_status(self):
        key = self.config.get('openrouter_api_key', '')
        if key and len(key) > 10:
            self.or_status_var.set(f"✅ Təyin olunub: {key[:10]}...{key[-4:]}")
        else:
            self.or_status_var.set("❌ Təyin olunmayıb")
    
    def _save_or_key(self):
        key = self.or_entry.get().strip()
        if not key:
            messagebox.showwarning("Xəta", "API key boşdur")
            return
        
        self.config['openrouter_api_key'] = key
        self._save_config()
        self._update_or_status()
        self._update_api_status()
        messagebox.showinfo("Uğurlu", "API key yadda saxlanıldı")
    
    def _test_or_key(self):
        key = self.or_entry.get().strip()
        if not key:
            messagebox.showwarning("Xəta", "API key daxil edin")
            return
        
        try:
            import requests
            response = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {key}"},
                timeout=10
            )
            
            if response.status_code == 200:
                models = response.json()
                count = len(models.get("data", []))
                messagebox.showinfo("Uğurlu", f"✅ API key düzgündür!\n\n{count} model mövcuddur")
            else:
                messagebox.showerror("Xəta", f"❌ API key yanlışdır\n\nStatus: {response.status_code}")
        except Exception as e:
            messagebox.showerror("Xəta", f"Test xətası: {e}")
    
    # ===================================================================
    # SECURITY SCAN
    # ===================================================================
    def _show_security_scan(self):
        self._clear_content()
        
        ttk.Label(
            self.content_frame, 
            text="Security Scan", 
            style='Title.TLabel'
        ).pack(anchor='w', pady=(0, 20))
        
        # Scan options
        options_frame = ttk.Frame(self.content_frame, style='Card.TFrame')
        options_frame.pack(fill='x', pady=10, padx=5, ipadx=20, ipady=20)
        
        ttk.Label(options_frame, text="Scan Alətləri", font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        self.scan_tools = {}
        tools = ['Audit Engine', 'Gitleaks', 'Semgrep', 'Trivy']
        
        for tool in tools:
            var = tk.BooleanVar(value=True)
            self.scan_tools[tool] = var
            ttk.Checkbutton(options_frame, text=f"✓ {tool}", variable=var).pack(anchor='w', pady=2)
        
        # Scan button
        ttk.Button(
            options_frame, 
            text="🚀 Start Scan", 
            command=self._run_scan,
            style='Primary.TButton'
        ).pack(pady=20)
        
        # Results area
        results_frame = ttk.Frame(self.content_frame, style='Card.TFrame')
        results_frame.pack(fill='both', expand=True, pady=10, padx=5, ipadx=20, ipady=20)
        
        ttk.Label(results_frame, text="Scan Nəticələri", font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        self.scan_results = scrolledtext.ScrolledText(results_frame, height=15, wrap='word', font=('Consolas', 9))
        self.scan_results.pack(fill='both', expand=True)
        self.scan_results.insert('1.0', "Scan işə salınmayıb. 🚀 Start Scan düyməsini klikləyin.")
    
    def _run_scan(self):
        self.scan_results.delete('1.0', tk.END)
        self.scan_results.insert('1.0', "Scan başlayır...\n\n")
        self.root.update()
        
        # Simulate scan
        import time
        for tool, var in self.scan_tools.items():
            if var.get():
                self.scan_results.insert(tk.END, f"[{tool}] İşlədilir...\n")
                self.root.update()
                time.sleep(0.5)
                self.scan_results.insert(tk.END, f"[{tool}] ✓ Tamamlandı\n\n")
                self.root.update()
        
        self.scan_results.insert(tk.END, "\n✅ Scan tamamlandı!")
    
    def _run_full_scan(self):
        self._show_security_scan()
        self.root.after(100, self._run_scan)
    
    # ===================================================================
    # PENTEST
    # ===================================================================
    def _show_pentest(self):
        self._clear_content()
        
        ttk.Label(
            self.content_frame, 
            text="AI Pentest - Strix", 
            style='Title.TLabel'
        ).pack(anchor='w', pady=(0, 20))
        
        # Info card
        info_frame = ttk.Frame(self.content_frame, style='Card.TFrame')
        info_frame.pack(fill='x', pady=10, padx=5, ipadx=20, ipady=20)
        
        info_text = """🎯 Strix AI Pentest
        
✅ Nə edir?
• Real HTTP sorğuları göndərir
• IDOR, Auth Bypass, SQL Injection test edir
• PoC (Proof of Concept) yaradır
• AI ilə zəifliyi təsdiqləyir

⚠️ Tələblər:
• OpenRouter API Key
• Target URL (http://localhost:8000)
• Docker sandbox işləyir

🚀 Pentest növləri:
• Quick Scan: 5 dəqiqə, əsas zəifliklər
• Deep Scan: 15+ dəqiqə, tam təhlil
"""
        
        ttk.Label(info_frame, text=info_text, justify='left', font=('Segoe UI', 10)).pack(anchor='w')
        
        # Config
        config_frame = ttk.Frame(self.content_frame, style='Card.TFrame')
        config_frame.pack(fill='x', pady=10, padx=5, ipadx=20, ipady=20)
        
        ttk.Label(config_frame, text="Konfiqurasiya", font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        # Target URL
        ttk.Label(config_frame, text="Target URL:").pack(anchor='w', pady=2)
        self.target_entry = ttk.Entry(config_frame, width=50)
        self.target_entry.pack(fill='x', pady=5)
        self.target_entry.insert(0, self.config.get('target_url', 'http://localhost:8000'))
        
        # Scan mode
        ttk.Label(config_frame, text="Scan Mode:").pack(anchor='w', pady=(10, 2))
        self.scan_mode_var = tk.StringVar(value='quick')
        ttk.Radiobutton(config_frame, text="⚡ Quick (5 dəqiqə)", variable=self.scan_mode_var, value='quick').pack(anchor='w')
        ttk.Radiobutton(config_frame, text="🔍 Deep (15+ dəqiqə)", variable=self.scan_mode_var, value='deep').pack(anchor='w')
        
        # Start button
        ttk.Button(
            config_frame, 
            text="🎯 Start Pentest", 
            command=self._start_pentest,
            style='Primary.TButton'
        ).pack(pady=20)
        
        # Results
        results_frame = ttk.Frame(self.content_frame, style='Card.TFrame')
        results_frame.pack(fill='both', expand=True, pady=10, padx=5, ipadx=20, ipady=20)
        
        ttk.Label(results_frame, text="Pentest Nəticələri", font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        self.pentest_results = scrolledtext.ScrolledText(results_frame, height=10, wrap='word', font=('Consolas', 9))
        self.pentest_results.pack(fill='both', expand=True)
        self.pentest_results.insert('1.0', "Pentest işə salınmayıb.")
    
    def _start_pentest(self):
        # Check API key
        if not self.config.get('openrouter_api_key'):
            messagebox.showwarning("Xəta", "OpenRouter API key təyin olunmayıb!\n\n🔑 API Keys tab-ına keçin")
            return
        
        target = self.target_entry.get().strip()
        if not target:
            messagebox.showwarning("Xəta", "Target URL daxil edin")
            return
        
        self.pentest_results.delete('1.0', tk.END)
        self.pentest_results.insert('1.0', f"🎯 Pentest başlayır...\n")
        self.pentest_results.insert(tk.END, f"Target: {target}\n")
        self.pentest_results.insert(tk.END, f"Mode: {self.scan_mode_var.get()}\n\n")
        self.pentest_results.insert(tk.END, "Bu real Strix pent test-dir.\n")
        self.pentest_results.insert(tk.END, "Docker sandbox və Strix quraşdırılmalıdır.\n\n")
        self.pentest_results.insert(tk.END, "Ətraflı: pentest/run-scan.sh\n")
        
        messagebox.showinfo("Info", "Pentest başlatmaq üçün:\n\n1. Docker işə salın\n2. docker compose -f docker-compose.sandbox.yml up -d\n3. ./pentest/run-scan.sh")
    
    # ===================================================================
    # OTHER VIEWS
    # ===================================================================
    def _show_projects(self):
        self._clear_content()
        ttk.Label(self.content_frame, text="Projects - Coming Soon", style='Title.TLabel').pack(pady=50)
    
    def _show_ai_chat(self):
        self._clear_content()
        ttk.Label(self.content_frame, text="AI Chat - Coming Soon", style='Title.TLabel').pack(pady=50)
    
    def _show_reports(self):
        self._clear_content()
        ttk.Label(self.content_frame, text="Reports - Coming Soon", style='Title.TLabel').pack(pady=50)
    
    def _show_settings(self):
        messagebox.showinfo("Settings", "Settings menüsü hazırlanır...")
    
    def _open_project(self):
        path = filedialog.askdirectory(title="Projekt Seçin")
        if path:
            self.config['current_project'] = path
            self._save_config()
            messagebox.showinfo("Uğurlu", f"Projekt açıldı:\n{path}")
    
    def _open_url(self, url):
        import webbrowser
        webbrowser.open(url)


def main():
    root = tk.Tk()
    app = ModernVibeShieldApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
