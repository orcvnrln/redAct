"""
VibeShield - Sadə və Aydın Desktop UI
Hər şey bir səhifədə, anlaşılan dizayn
"""

import json
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import subprocess
from pathlib import Path

CONFIG_FILE = "config.json"


class VibeShieldApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🛡️ VibeShield - DevSecOps Security Scanner")
        self.root.geometry("1100x750")
        
        # Config yüklə
        self.config = self.load_config()
        
        # Rənglər
        self.bg_color = "#f0f0f0"
        self.card_color = "#ffffff"
        self.primary = "#4a90e2"
        self.success = "#5cb85c"
        self.warning = "#f0ad4e"
        self.danger = "#d9534f"
        
        self.root.configure(bg=self.bg_color)
        
        # UI qur
        self.build_ui()
        
        # Status yenilə
        self.refresh_status()
    
    def load_config(self):
        """Config yüklə"""
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
        """Config saxla"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def build_ui(self):
        """UI qur"""
        # ============================================================
        # BAŞLIQ
        # ============================================================
        header = tk.Frame(self.root, bg="#2c3e50", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🛡️ VibeShield Security Scanner",
            font=("Segoe UI", 20, "bold"),
            fg="white",
            bg="#2c3e50"
        ).pack(side="left", padx=20, pady=20)
        
        self.status_label = tk.Label(
            header,
            text="Hazır",
            font=("Segoe UI", 10),
            fg="#ecf0f1",
            bg="#2c3e50"
        )
        self.status_label.pack(side="right", padx=20)
        
        # ============================================================
        # ÜST PANEL - KONFİGURASİYA
        # ============================================================
        config_frame = tk.Frame(self.root, bg=self.card_color, relief="raised", bd=2)
        config_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        tk.Label(
            config_frame,
            text="⚙️ Konfiqurasiya",
            font=("Segoe UI", 14, "bold"),
            bg=self.card_color,
            fg="#2c3e50"
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        # Grid
        inner = tk.Frame(config_frame, bg=self.card_color)
        inner.pack(fill="x", padx=15, pady=(0, 15))
        
        # API Key
        tk.Label(inner, text="🔑 OpenRouter API Key:", bg=self.card_color, font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.api_entry = tk.Entry(inner, width=50, show="*", font=("Consolas", 10))
        self.api_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.api_entry.insert(0, self.config.get('openrouter_api_key', ''))
        
        btn_frame = tk.Frame(inner, bg=self.card_color)
        btn_frame.grid(row=0, column=2, padx=5)
        
        tk.Button(
            btn_frame,
            text="💾 Saxla",
            command=self.save_api_key,
            bg=self.success,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=10
        ).pack(side="left", padx=2)
        
        tk.Button(
            btn_frame,
            text="🧪 Test",
            command=self.test_api_key,
            bg=self.primary,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=10
        ).pack(side="left", padx=2)
        
        # Projekt
        tk.Label(inner, text="📁 Projekt:", bg=self.card_color, font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.project_entry = tk.Entry(inner, width=50, font=("Segoe UI", 9))
        self.project_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.project_entry.insert(0, self.config.get('project_path', ''))
        
        tk.Button(
            inner,
            text="📂 Seç",
            command=self.select_project,
            bg=self.primary,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=15
        ).grid(row=1, column=2, padx=5)
        
        # Target URL
        tk.Label(inner, text="🎯 Target URL:", bg=self.card_color, font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", pady=5)
        self.target_entry = tk.Entry(inner, width=50, font=("Segoe UI", 9))
        self.target_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.target_entry.insert(0, self.config.get('target_url', 'http://localhost:8000'))
        
        inner.columnconfigure(1, weight=1)
        
        # ============================================================
        # ORTA PANEL - SKAN ALƏTLƏRI
        # ============================================================
        tools_frame = tk.Frame(self.root, bg=self.card_color, relief="raised", bd=2)
        tools_frame.pack(fill="x", padx=15, pady=5)
        
        tk.Label(
            tools_frame,
            text="🔧 Təhlükəsizlik Alətləri",
            font=("Segoe UI", 14, "bold"),
            bg=self.card_color,
            fg="#2c3e50"
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        # Tool grid
        tools_grid = tk.Frame(tools_frame, bg=self.card_color)
        tools_grid.pack(fill="x", padx=15, pady=(0, 15))
        
        self.tool_vars = {}
        tools = [
            ("✓ Audit Engine", "audit", "13 Qayda, Deterministik", True),
            ("🔐 Gitleaks", "gitleaks", "Secret Aşkarlanması", True),
            ("🧬 Semgrep", "semgrep", "SAST Kod Təhlili", True),
            ("📦 Trivy", "trivy", "SCA Dependencies", True),
            ("🎯 Strix AI", "strix", "AI Pentest (LLM lazım)", False),
            ("⚡ Nuclei", "nuclei", "Template Skan", False),
        ]
        
        for i, (text, key, desc, default) in enumerate(tools):
            col = i % 3
            row = i // 3
            
            tool_card = tk.Frame(tools_grid, bg="#ecf0f1", relief="solid", bd=1)
            tool_card.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            var = tk.BooleanVar(value=default)
            self.tool_vars[key] = var
            
            cb = tk.Checkbutton(
                tool_card,
                text=text,
                variable=var,
                font=("Segoe UI", 10, "bold"),
                bg="#ecf0f1",
                activebackground="#ecf0f1"
            )
            cb.pack(anchor="w", padx=10, pady=(5, 0))
            
            tk.Label(
                tool_card,
                text=desc,
                font=("Segoe UI", 8),
                bg="#ecf0f1",
                fg="#7f8c8d"
            ).pack(anchor="w", padx=10, pady=(0, 5))
        
        for i in range(3):
            tools_grid.columnconfigure(i, weight=1)
        
        # ============================================================
        # SCAN DÜYMƏLƏRİ
        # ============================================================
        action_frame = tk.Frame(self.root, bg=self.bg_color)
        action_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Button(
            action_frame,
            text="🚀 FULL SCAN (Statik + Dinamik)",
            command=self.run_full_scan,
            bg="#e74c3c",
            fg="white",
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            padx=30,
            pady=15,
            cursor="hand2"
        ).pack(side="left", padx=5)
        
        tk.Button(
            action_frame,
            text="🔍 Yalnız Statik Skan",
            command=self.run_static_scan,
            bg=self.primary,
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2"
        ).pack(side="left", padx=5)
        
        tk.Button(
            action_frame,
            text="🎯 Yalnız Pentest",
            command=self.run_pentest,
            bg=self.warning,
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2"
        ).pack(side="left", padx=5)
        
        tk.Button(
            action_frame,
            text="🗑️ Təmizlə",
            command=self.clear_results,
            bg="#95a5a6",
            fg="white",
            font=("Segoe UI", 10),
            relief="flat",
            padx=15,
            pady=10
        ).pack(side="right", padx=5)
        
        # ============================================================
        # NƏTİCƏLƏR
        # ============================================================
        results_frame = tk.Frame(self.root, bg=self.card_color, relief="raised", bd=2)
        results_frame.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        
        tk.Label(
            results_frame,
            text="📊 Scan Nəticələri",
            font=("Segoe UI", 14, "bold"),
            bg=self.card_color,
            fg="#2c3e50"
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        # Results text
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            height=15,
            wrap="word",
            font=("Consolas", 9),
            bg="#2c3e50",
            fg="#ecf0f1",
            insertbackground="white"
        )
        self.results_text.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        
        self.log("✨ VibeShield hazırdır! Scan başlatmaq üçün düyməyə klikləyin.\n")
        self.log("━" * 80 + "\n")
    
    def log(self, text, tag=None):
        """Log əlavə et"""
        self.results_text.insert("end", text)
        self.results_text.see("end")
        self.root.update()
    
    def update_status(self, text, color="#ecf0f1"):
        """Status yenilə"""
        self.status_label.config(text=text, fg=color)
        self.root.update()
    
    def refresh_status(self):
        """Tool statuslarını yenilə"""
        api_key = self.config.get('openrouter_api_key', '')
        if api_key:
            self.update_status(f"✅ API: {api_key[:10]}...{api_key[-4:]}", "#2ecc71")
        else:
            self.update_status("❌ API Key yoxdur", "#e74c3c")
    
    def save_api_key(self):
        """API key saxla"""
        key = self.api_entry.get().strip()
        if not key:
            messagebox.showwarning("Xəta", "API key boşdur")
            return
        
        self.config['openrouter_api_key'] = key
        self.save_config()
        self.refresh_status()
        messagebox.showinfo("✅ Uğurlu", "API key yadda saxlanıldı")
        self.log(f"\n✅ API key saxlanıldı: {key[:10]}...{key[-4:]}\n")
    
    def test_api_key(self):
        """API key test et"""
        key = self.api_entry.get().strip()
        if not key:
            messagebox.showwarning("Xəta", "API key daxil edin")
            return
        
        self.log("\n🧪 API key test edilir...\n")
        self.update_status("🧪 API test...", "#f39c12")
        
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
                self.log(f"✅ API key düzgündür! {count} model mövcuddur.\n")
                self.update_status("✅ API düzgündür", "#2ecc71")
                messagebox.showinfo("✅ Uğurlu", f"API key düzgündür!\n\n{count} model mövcuddur")
            else:
                self.log(f"❌ API key yanlışdır! Status: {response.status_code}\n")
                self.update_status("❌ API yanlışdır", "#e74c3c")
                messagebox.showerror("❌ Xəta", f"API key yanlışdır!\n\nStatus: {response.status_code}")
        except Exception as e:
            self.log(f"❌ Test xətası: {e}\n")
            self.update_status("❌ Test xətası", "#e74c3c")
            messagebox.showerror("❌ Xəta", f"Test xətası:\n{e}")
    
    def select_project(self):
        """Projekt seç"""
        path = filedialog.askdirectory(title="Projekt Kataloqu Seçin")
        if path:
            self.project_entry.delete(0, "end")
            self.project_entry.insert(0, path)
            self.config['project_path'] = path
            self.save_config()
            self.log(f"\n📁 Projekt seçildi: {path}\n")
    
    def run_full_scan(self):
        """Full scan (Statik + Dinamik)"""
        self.clear_results()
        self.log("🚀 FULL SCAN BAŞLADI\n")
        self.log("━" * 80 + "\n\n")
        
        project = self.project_entry.get().strip()
        if not project or not os.path.exists(project):
            self.log("❌ Projekt seçilməyib və ya tapılmadı!\n")
            messagebox.showwarning("Xəta", "Əvvəlcə projekt seçin!")
            return
        
        # Statik
        self.run_static_scan()
        
        # Dinamik
        self.log("\n" + "━" * 80 + "\n")
        self.log("🎯 Dinamik Skan Başlayır...\n")
        self.log("━" * 80 + "\n\n")
        self.run_pentest()
        
        self.log("\n" + "━" * 80 + "\n")
        self.log("✅ FULL SCAN TAMAMLANDI!\n")
        self.log("━" * 80 + "\n")
        self.update_status("✅ Scan tamamlandı", "#2ecc71")
    
    def run_static_scan(self):
        """Statik skan"""
        self.log("🔍 STATİK SKAN\n")
        self.log("━" * 80 + "\n\n")
        self.update_status("🔍 Statik skan...", "#3498db")
        
        project = self.project_entry.get().strip()
        
        # Audit Engine
        if self.tool_vars.get('audit', tk.BooleanVar(value=True)).get():
            self.log("▶️ [1/4] Audit Engine (13 Qayda)\n")
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "audit.run_audit", "--project", project, "--out", "audit_out"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=Path(__file__).parent.parent
                )
                if "Kritik:" in result.stdout:
                    self.log(result.stdout + "\n")
                else:
                    self.log("  ✅ Tamamlandı\n\n")
            except Exception as e:
                self.log(f"  ⚠️ Xəta: {e}\n\n")
        
        # Gitleaks
        if self.tool_vars.get('gitleaks', tk.BooleanVar(value=True)).get():
            self.log("▶️ [2/4] Gitleaks (Secret Skan)\n")
            try:
                result = subprocess.run(
                    ["gitleaks", "detect", "--source", project, "--no-git", "--verbose"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    self.log("  ✅ Heç bir secret tapılmadı\n\n")
                else:
                    self.log("  ⚠️ Secret-lər tapıldı! (ətraflı: gitleaks.log)\n\n")
            except:
                self.log("  ⚠️ Gitleaks quraşdırılmayıb\n\n")
        
        # Semgrep
        if self.tool_vars.get('semgrep', tk.BooleanVar(value=True)).get():
            self.log("▶️ [3/4] Semgrep (SAST)\n")
            try:
                result = subprocess.run(
                    ["semgrep", "--config=auto", "--json", project],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                self.log("  ✅ Tamamlandı\n\n")
            except:
                self.log("  ⚠️ Semgrep quraşdırılmayıb (pip install semgrep)\n\n")
        
        # Trivy
        if self.tool_vars.get('trivy', tk.BooleanVar(value=True)).get():
            self.log("▶️ [4/4] Trivy (SCA)\n")
            try:
                result = subprocess.run(
                    ["trivy", "fs", project],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                self.log("  ✅ Tamamlandı\n\n")
            except:
                self.log("  ⚠️ Trivy quraşdırılmayıb\n\n")
        
        self.log("✅ Statik skan tamamlandı\n")
    
    def run_pentest(self):
        """Pentest (Strix)"""
        self.log("🎯 DİNAMİK PENTEST\n")
        self.log("━" * 80 + "\n\n")
        self.update_status("🎯 Pentest...", "#f39c12")
        
        api_key = self.config.get('openrouter_api_key', '')
        if not api_key:
            self.log("❌ OpenRouter API key yoxdur!\n")
            self.log("   → 🔑 API Keys bölməsində əlavə edin\n\n")
            return
        
        target = self.target_entry.get().strip()
        
        if self.tool_vars.get('strix', tk.BooleanVar(value=False)).get():
            self.log("▶️ Strix AI Pentest\n")
            self.log(f"   Target: {target}\n")
            self.log(f"   LLM: OpenRouter/Gemma-2-9B\n\n")
            
            self.log("   Test edilir:\n")
            self.log("   • IDOR (Insecure Direct Object Reference)\n")
            self.log("   • Auth Bypass\n")
            self.log("   • SQL Injection\n")
            self.log("   • Secret Exposure\n")
            self.log("   • Debug Endpoints\n\n")
            
            self.log("   ℹ️ Real pentest üçün:\n")
            self.log("   1. Docker-i başladın\n")
            self.log("   2. docker compose -f docker-compose.sandbox.yml up -d\n")
            self.log("   3. ./pentest/run-scan.sh\n\n")
        
        if self.tool_vars.get('nuclei', tk.BooleanVar(value=False)).get():
            self.log("▶️ Nuclei Template Skan\n")
            self.log("   ⚠️ Nuclei quraşdırılmalıdır\n\n")
    
    def clear_results(self):
        """Nəticələri təmizlə"""
        self.results_text.delete("1.0", "end")
        self.log("🗑️ Nəticələr təmizləndi\n\n")


def main():
    root = tk.Tk()
    app = VibeShieldApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
