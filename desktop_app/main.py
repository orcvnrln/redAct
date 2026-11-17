"""
DevSecOps Desktop Tool — Main GUI (Tkinter)
7-addımli deterministik DevSecOps pipeline-i local olaraq idarə edir.
"""

import json
import os
import sys
import tkinter as tk
import tkinter.simpledialog
from tkinter import ttk, messagebox, filedialog, scrolledtext
from typing import Dict, Any, List

from scanner import DesktopScanner, ScanResult
from gate import DeterministicGate

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


class DevSecOpsDesktopApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("DevSecOps Desktop Tool — 7 Addım Deterministik Pipeline")
        self.root.geometry("1100x750")
        self.root.minsize(900, 650)

        self.config = self._load_config()
        self.scanner = DesktopScanner(self.config)
        self.gate = DeterministicGate(
            severity_threshold=self.config.get("severity_threshold", ["critical", "high"])
        )

        self._build_ui()
        self._refresh_status()

    # ------------------------------------------------------------------ #
    # Konfiqurasiya
    # ------------------------------------------------------------------ #
    def _load_config(self) -> Dict[str, Any]:
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def _save_config(self):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------ #
    # UI qurulumu
    # ------------------------------------------------------------------ #
    def _build_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self.tab_config = ttk.Frame(notebook)
        self.tab_api_keys = ttk.Frame(notebook)
        self.tab_projects = ttk.Frame(notebook)
        self.tab_scanner = ttk.Frame(notebook)
        self.tab_gate = ttk.Frame(notebook)
        self.tab_ai_chat = ttk.Frame(notebook)
        self.tab_report = ttk.Frame(notebook)
        self.tab_logs = ttk.Frame(notebook)

        notebook.add(self.tab_config, text="⚙️ Konfiqurasiya")
        notebook.add(self.tab_api_keys, text="🔑 API Keys")
        notebook.add(self.tab_projects, text="📁 Projektlər")
        notebook.add(self.tab_scanner, text="🔍 Skanlar")
        notebook.add(self.tab_gate, text="🚪 Deterministik Qapı")
        notebook.add(self.tab_ai_chat, text="🤖 AI Chat")
        notebook.add(self.tab_report, text="📄 Hesabat")
        notebook.add(self.tab_logs, text="📋 Loglar")

        self._build_config_tab()
        self._build_api_keys_tab()
        self._build_projects_tab()
        self._build_scanner_tab()
        self._build_gate_tab()
        self._build_ai_chat_tab()
        self._build_report_tab()
        self._build_logs_tab()

        # Status bar
        self.status_var = tk.StringVar(value="Hazır")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x")

    # ------------------------------------------------------------------ #
    # Sekme: Konfiqurasiya
    # ------------------------------------------------------------------ #
    def _build_config_tab(self):
        frame = ttk.Frame(self.tab_config, padding=12)
        frame.pack(fill="both", expand=True)

        # OpenRouter
        ttk.Label(frame, text="OpenRouter API Açarı:").grid(row=0, column=0, sticky="w", pady=4)
        self.ent_api_key = ttk.Entry(frame, width=60, show="*")
        self.ent_api_key.grid(row=0, column=1, columnspan=2, sticky="ew", pady=4)
        self.ent_api_key.insert(0, self.config.get("openrouter_api_key", ""))

        ttk.Label(frame, text="Model:").grid(row=1, column=0, sticky="w", pady=4)
        self.ent_model = ttk.Entry(frame, width=60)
        self.ent_model.grid(row=1, column=1, columnspan=2, sticky="ew", pady=4)
        self.ent_model.insert(0, self.config.get("openrouter_model", "openrouter/google/gemma-2-9b-it"))

        ttk.Label(frame, text="API Base URL:").grid(row=2, column=0, sticky="w", pady=4)
        self.ent_base = ttk.Entry(frame, width=60)
        self.ent_base.grid(row=2, column=1, columnspan=2, sticky="ew", pady=4)
        self.ent_base.insert(0, self.config.get("openrouter_base", "https://openrouter.ai/api/v1"))

        # Target
        ttk.Label(frame, text="Hedef URL:").grid(row=3, column=0, sticky="w", pady=4)
        self.ent_target = ttk.Entry(frame, width=60)
        self.ent_target.grid(row=3, column=1, columnspan=2, sticky="ew", pady=4)
        self.ent_target.insert(0, self.config.get("target_url", "http://localhost:8000"))

        # Tools
        ttk.Label(frame, text="Aktiv Alətlər:").grid(row=4, column=0, sticky="w", pady=(12, 4))
        tools_frame = ttk.Frame(frame)
        tools_frame.grid(row=4, column=1, columnspan=2, sticky="w", pady=(12, 4))

        self.tool_vars = {}
        tools = [
            ("strix", "Strix AI Pentest"),
            ("nuclei", "Nuclei (LLM-siz)"),
            ("semgrep", "Semgrep SAST"),
            ("trivy", "Trivy SCA"),
            ("gitleaks", "Gitleaks Secrets"),
            ("sonarqube", "SonarQube"),
        ]
        for i, (key, label) in enumerate(tools):
            var = tk.BooleanVar(value=self.config.get("tools", {}).get(key, True if key != "sonarqube" else False))
            self.tool_vars[key] = var
            ttk.Checkbutton(tools_frame, text=label, variable=var).grid(row=0, column=i, sticky="w", padx=6)

        # Threshold
        ttk.Label(frame, text="Qapı Səviyyəsi:").grid(row=5, column=0, sticky="w", pady=(12, 4))
        self.ent_threshold = ttk.Entry(frame, width=30)
        self.ent_threshold.grid(row=5, column=1, sticky="w", pady=(12, 4))
        self.ent_threshold.insert(0, ",".join(self.config.get("severity_threshold", ["critical", "high"])))

        ttk.Button(frame, text="� konfiqurasiyaı yadda saxla", command=self._save_config_from_ui).grid(
            row=6, column=0, columnspan=3, pady=(16, 0)
        )

        frame.columnconfigure(1, weight=1)

    def _save_config_from_ui(self):
        self.config["openrouter_api_key"] = self.ent_api_key.get().strip()
        self.config["openrouter_model"] = self.ent_model.get().strip()
        self.config["openrouter_base"] = self.ent_base.get().strip()
        self.config["target_url"] = self.ent_target.get().strip()
        self.config["tools"] = {k: v.get() for k, v in self.tool_vars.items()}
        thr = [t.strip() for t in self.ent_threshold.get().split(",") if t.strip()]
        self.config["severity_threshold"] = thr
        self._save_config()
        self.scanner = DesktopScanner(self.config)
        self.gate = DeterministicGate(severity_threshold=thr)
        self.status_var.set("Konfiqurasiya yadda saxlanıldı")
        messagebox.showinfo("Uğurlu", "Konfiqurasiya yadda saxlanıldı.")

    # ------------------------------------------------------------------ #
    # Sekme: API Keys Management
    # ------------------------------------------------------------------ #
    def _build_api_keys_tab(self):
        frame = ttk.Frame(self.tab_api_keys, padding=12)
        frame.pack(fill="both", expand=True)

        # Header
        ttk.Label(
            frame, 
            text="API Key İdarəetməsi", 
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(0, 16))

        # Info
        info_frame = ttk.LabelFrame(frame, text="ℹ️ Məlumat", padding=12)
        info_frame.pack(fill="x", pady=(0, 16))

        info_text = """Sistemin tam işləməsi üçün aşağıdakı API key-lər lazımdır:

• OPENROUTER_API_KEY (Mütləq) - Strix AI pentest və Desktop AI Chat üçün
• GITHUB_TOKEN (Avtomatik) - GitHub Actions tərəfindən verilir
• SONAR_TOKEN (İstəyə görə) - SonarCloud kod keyfiyyəti üçün

Pulsuz key-lər:
- OpenRouter: https://openrouter.ai (kredit kartı lazım deyil)
- SonarCloud: https://sonarcloud.io (GitHub ilə login)
"""
        ttk.Label(info_frame, text=info_text, justify="left").pack(anchor="w")

        # ================================================================
        # 1. OpenRouter API Key
        # ================================================================
        openrouter_frame = ttk.LabelFrame(frame, text="🔑 OpenRouter API Key (Mütləq)", padding=12)
        openrouter_frame.pack(fill="x", pady=(0, 12))

        # Status
        self.openrouter_status_var = tk.StringVar()
        self._update_openrouter_status()
        
        status_label = ttk.Label(
            openrouter_frame, 
            textvariable=self.openrouter_status_var,
            font=("Segoe UI", 10, "bold")
        )
        status_label.pack(anchor="w", pady=(0, 8))

        # Input
        input_frame = ttk.Frame(openrouter_frame)
        input_frame.pack(fill="x", pady=(0, 8))

        ttk.Label(input_frame, text="API Key:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.openrouter_entry = ttk.Entry(input_frame, width=60, show="*")
        self.openrouter_entry.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        
        # Show/Hide button
        self.show_openrouter_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            input_frame, 
            text="Göstər", 
            variable=self.show_openrouter_var,
            command=self._toggle_openrouter_visibility
        ).grid(row=0, column=2)

        input_frame.columnconfigure(1, weight=1)

        # Current value
        current_key = self.config.get("openrouter_api_key", "")
        if current_key:
            self.openrouter_entry.insert(0, current_key)

        # Buttons
        btn_frame = ttk.Frame(openrouter_frame)
        btn_frame.pack(fill="x", pady=(8, 0))

        ttk.Button(
            btn_frame, 
            text="💾 Yadda Saxla", 
            command=self._save_openrouter_key
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            btn_frame, 
            text="🧪 Test Et", 
            command=self._test_openrouter_key
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            btn_frame, 
            text="🌐 OpenRouter-a Get", 
            command=lambda: self._open_url("https://openrouter.ai")
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            btn_frame, 
            text="🗑️ Təmizlə", 
            command=self._clear_openrouter_key
        ).pack(side="left")

        # ================================================================
        # 2. GitHub Token
        # ================================================================
        github_frame = ttk.LabelFrame(frame, text="🔑 GitHub Token (GitHub Actions üçün)", padding=12)
        github_frame.pack(fill="x", pady=(0, 12))

        github_info = """GitHub Actions-da GITHUB_TOKEN avtomatik təmin edilir.
Lokal işlər üçün Personal Access Token yarada bilərsiniz:

1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select scopes: repo, workflow
4. Copy token"""

        ttk.Label(github_frame, text=github_info, justify="left").pack(anchor="w", pady=(0, 8))

        ttk.Button(
            github_frame, 
            text="🌐 GitHub Token Yarat", 
            command=lambda: self._open_url("https://github.com/settings/tokens")
        ).pack(anchor="w")

        # ================================================================
        # 3. SonarCloud Token
        # ================================================================
        sonar_frame = ttk.LabelFrame(frame, text="🔑 SonarCloud Token (İstəyə görə)", padding=12)
        sonar_frame.pack(fill="x", pady=(0, 12))

        # Status
        self.sonar_status_var = tk.StringVar()
        self._update_sonar_status()
        
        ttk.Label(
            sonar_frame, 
            textvariable=self.sonar_status_var,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", pady=(0, 8))

        # Input
        sonar_input_frame = ttk.Frame(sonar_frame)
        sonar_input_frame.pack(fill="x", pady=(0, 8))

        ttk.Label(sonar_input_frame, text="Token:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.sonar_entry = ttk.Entry(sonar_input_frame, width=60, show="*")
        self.sonar_entry.grid(row=0, column=1, sticky="ew")

        sonar_input_frame.columnconfigure(1, weight=1)

        current_sonar = self.config.get("sonar_token", "")
        if current_sonar:
            self.sonar_entry.insert(0, current_sonar)

        # Buttons
        sonar_btn_frame = ttk.Frame(sonar_frame)
        sonar_btn_frame.pack(fill="x", pady=(8, 0))

        ttk.Button(
            sonar_btn_frame, 
            text="💾 Yadda Saxla", 
            command=self._save_sonar_token
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            sonar_btn_frame, 
            text="🌐 SonarCloud-a Get", 
            command=lambda: self._open_url("https://sonarcloud.io")
        ).pack(side="left")

        # ================================================================
        # GitHub Secrets Helper
        # ================================================================
        secrets_frame = ttk.LabelFrame(frame, text="📋 GitHub Secrets Konfiqurasiyası", padding=12)
        secrets_frame.pack(fill="x", pady=(0, 12))

        secrets_info = """GitHub Actions-da istifadə üçün API key-ləri GitHub Secrets-ə əlavə edin:

1. Repository → Settings → Secrets and variables → Actions
2. New repository secret
3. Name: OPENROUTER_API_KEY
4. Value: (yuxarıda saxladığınız key)
5. Add secret

Eyni şəkildə SONAR_TOKEN əlavə edin (istəyə görə)."""

        ttk.Label(secrets_frame, text=secrets_info, justify="left").pack(anchor="w", pady=(0, 8))

        ttk.Button(
            secrets_frame, 
            text="🌐 Repository Secrets-ə Get", 
            command=self._open_github_secrets
        ).pack(anchor="w")

    def _update_openrouter_status(self):
        key = self.config.get("openrouter_api_key", "")
        if key and len(key) > 10:
            masked = key[:10] + "..." + key[-4:]
            self.openrouter_status_var.set(f"✅ Təyin olunub: {masked}")
        else:
            self.openrouter_status_var.set("❌ Təyin olunmayıb")

    def _update_sonar_status(self):
        token = self.config.get("sonar_token", "")
        if token and len(token) > 10:
            masked = token[:10] + "..." + token[-4:]
            self.sonar_status_var.set(f"✅ Təyin olunub: {masked}")
        else:
            self.sonar_status_var.set("⚠️ Təyin olunmayıb (istəyə görə)")

    def _toggle_openrouter_visibility(self):
        if self.show_openrouter_var.get():
            self.openrouter_entry.config(show="")
        else:
            self.openrouter_entry.config(show="*")

    def _save_openrouter_key(self):
        key = self.openrouter_entry.get().strip()
        if not key:
            messagebox.showwarning("Xəta", "API key boşdur")
            return

        if not key.startswith("sk-or-"):
            confirm = messagebox.askyesno(
                "Təsdiq", 
                "API key 'sk-or-' ilə başlamır. Davam edilsin?"
            )
            if not confirm:
                return

        self.config["openrouter_api_key"] = key
        self._save_config()
        self._update_openrouter_status()
        self._write_log(f"OpenRouter API key yadda saxlanıldı: {key[:10]}...")
        messagebox.showinfo("Uğurlu", "API key yadda saxlanıldı")

    def _test_openrouter_key(self):
        key = self.openrouter_entry.get().strip()
        if not key:
            messagebox.showwarning("Xəta", "API key daxil edin")
            return

        try:
            import requests
            
            self.status_var.set("OpenRouter test edilir...")
            self.root.update()

            response = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {key}"},
                timeout=10
            )

            if response.status_code == 200:
                models = response.json()
                model_count = len(models.get("data", []))
                messagebox.showinfo(
                    "Uğurlu", 
                    f"✅ API key düzgündür!\n\n{model_count} model mövcuddur."
                )
                self._write_log("OpenRouter API key test - uğurlu")
                self.status_var.set("API key test uğurlu")
            else:
                messagebox.showerror(
                    "Xəta", 
                    f"❌ API key yanlışdır\n\nStatus: {response.status_code}\n{response.text[:200]}"
                )
                self.status_var.set("API key test uğursuz")
        except Exception as e:
            messagebox.showerror("Xəta", f"Test xətası: {e}")
            self.status_var.set("API key test xətası")

    def _clear_openrouter_key(self):
        confirm = messagebox.askyesno("Təsdiq", "API key-i silmək istədiyinizə əminsiniz?")
        if confirm:
            self.openrouter_entry.delete(0, tk.END)
            self.config["openrouter_api_key"] = ""
            self._save_config()
            self._update_openrouter_status()
            self._write_log("OpenRouter API key silindi")
            messagebox.showinfo("Uğurlu", "API key silindi")

    def _save_sonar_token(self):
        token = self.sonar_entry.get().strip()
        self.config["sonar_token"] = token
        self._save_config()
        self._update_sonar_status()
        self._write_log(f"SonarCloud token yadda saxlanıldı")
        messagebox.showinfo("Uğurlu", "Token yadda saxlanıldı")

    def _open_url(self, url):
        import webbrowser
        webbrowser.open(url)
        self._write_log(f"Brauzer açıldı: {url}")

    def _open_github_secrets(self):
        # Try to get repo from git remote
        try:
            import subprocess
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                remote_url = result.stdout.strip()
                # Parse GitHub URL
                if "github.com" in remote_url:
                    # https://github.com/user/repo.git → user/repo
                    repo_path = remote_url.split("github.com")[-1].strip("/:").replace(".git", "")
                    url = f"https://github.com/{repo_path}/settings/secrets/actions"
                    self._open_url(url)
                    return
        except:
            pass
        
        # Fallback: generic GitHub settings
        messagebox.showinfo(
            "GitHub Secrets", 
            "Repository → Settings → Secrets and variables → Actions\n\n" +
            "Bu yolu manual gedib OPENROUTER_API_KEY əlavə edin"
        )

    # ------------------------------------------------------------------ #
    # Sekme: Projektlər (Fayl/Folder Brauzer)
    # ------------------------------------------------------------------ #
    def _build_projects_tab(self):
        frame = ttk.Frame(self.tab_projects, padding=12)
        frame.pack(fill="both", expand=True)

        # Toolbar
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill="x", pady=(0, 10))

        ttk.Button(toolbar, text="📁 Projekt Aç", command=self._open_project).pack(side="left", padx=4)
        ttk.Button(toolbar, text="➕ Fayl Əlavə Et", command=self._add_file).pack(side="left", padx=4)
        ttk.Button(toolbar, text="➕ Folder Əlavə Et", command=self._add_folder).pack(side="left", padx=4)
        ttk.Button(toolbar, text="🗑️ Sil", command=self._delete_item).pack(side="left", padx=4)
        ttk.Button(toolbar, text="🔄 Yenilə", command=self._refresh_project_tree).pack(side="left", padx=4)

        # Current project path
        self.project_path_var = tk.StringVar(value="Heç bir projekt açılmayıb")
        ttk.Label(frame, textvariable=self.project_path_var, font=("Segoe UI", 10), foreground="blue").pack(anchor="w", pady=(0, 8))

        # Paned window: Tree + Preview
        paned = ttk.PanedWindow(frame, orient="horizontal")
        paned.pack(fill="both", expand=True)

        # Left: File tree
        tree_frame = ttk.Frame(paned)
        paned.add(tree_frame, weight=1)

        self.project_tree = ttk.Treeview(tree_frame, show="tree", selectmode="browse")
        self.project_tree.pack(side="left", fill="both", expand=True)

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.project_tree.yview)
        self.project_tree.configure(yscroll=tree_scroll.set)
        tree_scroll.pack(side="right", fill="y")

        self.project_tree.bind("<<TreeviewSelect>>", self._on_project_item_select)
        self.project_tree.bind("<Double-Button-1>", self._on_project_item_double_click)

        # Right: Preview
        preview_frame = ttk.Frame(paned)
        paned.add(preview_frame, weight=2)

        ttk.Label(preview_frame, text="Fayl Önizləmə:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 4))
        self.file_preview = scrolledtext.ScrolledText(preview_frame, height=20, wrap="word", font=("Consolas", 9))
        self.file_preview.pack(fill="both", expand=True)

        # Store current project root
        self.current_project_root = None
        self.tree_node_map = {}  # iid -> full_path

    def _open_project(self):
        path = filedialog.askdirectory(title="Projekt Kataloqu Seçin")
        if not path:
            return

        self.current_project_root = path
        self.project_path_var.set(f"Projekt: {path}")
        self.config["current_project"] = path
        self._save_config()
        self._refresh_project_tree()
        self._write_log(f"Projekt açıldı: {path}")

    def _refresh_project_tree(self):
        if not self.current_project_root:
            return

        # Clear tree
        for item in self.project_tree.get_children():
            self.project_tree.delete(item)
        self.tree_node_map.clear()

        # Populate tree
        root_iid = self.project_tree.insert("", "end", text=os.path.basename(self.current_project_root), open=True)
        self.tree_node_map[root_iid] = self.current_project_root
        self._populate_tree(root_iid, self.current_project_root)

    def _populate_tree(self, parent_iid, path):
        try:
            items = sorted(os.listdir(path))
        except PermissionError:
            return

        for item in items:
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                icon = "📁"
                iid = self.project_tree.insert(parent_iid, "end", text=f"{icon} {item}", open=False)
                self.tree_node_map[iid] = full_path
                # Lazy load
                self.project_tree.insert(iid, "end", text="...")  # Placeholder
            else:
                icon = "📄"
                iid = self.project_tree.insert(parent_iid, "end", text=f"{icon} {item}")
                self.tree_node_map[iid] = full_path

    def _on_project_item_select(self, event):
        sel = self.project_tree.selection()
        if not sel:
            return

        iid = sel[0]
        path = self.tree_node_map.get(iid)
        if not path or not os.path.isfile(path):
            return

        # Load file preview
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(10000)  # İlk 10KB
            self.file_preview.delete("1.0", tk.END)
            self.file_preview.insert(tk.END, content)
        except Exception as e:
            self.file_preview.delete("1.0", tk.END)
            self.file_preview.insert(tk.END, f"Fayl oxunmaya xəta: {e}")

    def _on_project_item_double_click(self, event):
        sel = self.project_tree.selection()
        if not sel:
            return

        iid = sel[0]
        path = self.tree_node_map.get(iid)

        if os.path.isdir(path):
            # Expand folder lazily
            children = self.project_tree.get_children(iid)
            if len(children) == 1 and self.project_tree.item(children[0])["text"] == "...":
                # Remove placeholder
                self.project_tree.delete(children[0])
                # Populate
                self._populate_tree(iid, path)

    def _add_file(self):
        if not self.current_project_root:
            messagebox.showwarning("Xəta", "Əvvəl projekt açın")
            return

        file_path = filedialog.asksaveasfilename(
            title="Yeni Fayl Yarat",
            initialdir=self.current_project_root,
            defaultextension=".txt"
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("# Yeni fayl\n")
            messagebox.showinfo("Uğurlu", f"Fayl yaradıldı: {file_path}")
            self._refresh_project_tree()
            self._write_log(f"Fayl yaradıldı: {file_path}")
        except Exception as e:
            messagebox.showerror("Xəta", f"Fayl yaradılmaya xəta: {e}")

    def _add_folder(self):
        if not self.current_project_root:
            messagebox.showwarning("Xəta", "Əvvəl projekt açın")
            return

        folder_name = tkinter.simpledialog.askstring("Yeni Folder", "Folder adı:")
        if not folder_name:
            return

        folder_path = os.path.join(self.current_project_root, folder_name)
        try:
            os.makedirs(folder_path, exist_ok=True)
            messagebox.showinfo("Uğurlu", f"Folder yaradıldı: {folder_path}")
            self._refresh_project_tree()
            self._write_log(f"Folder yaradıldı: {folder_path}")
        except Exception as e:
            messagebox.showerror("Xəta", f"Folder yaradılmaya xəta: {e}")

    def _delete_item(self):
        sel = self.project_tree.selection()
        if not sel:
            messagebox.showwarning("Xəta", "Silinəcək fayl/folder seçin")
            return

        iid = sel[0]
        path = self.tree_node_map.get(iid)

        if not path:
            return

        confirm = messagebox.askyesno("Təsdiq", f"Silmək istədiyinizdən əminsiniz?\n{path}")
        if not confirm:
            return

        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                import shutil
                shutil.rmtree(path)

            messagebox.showinfo("Uğurlu", f"Silindi: {path}")
            self._refresh_project_tree()
            self._write_log(f"Silindi: {path}")
        except Exception as e:
            messagebox.showerror("Xəta", f"Silinmə xətası: {e}")

    # ------------------------------------------------------------------ #
    # Sekme: AI Chat
    # ------------------------------------------------------------------ #
    def _build_ai_chat_tab(self):
        frame = ttk.Frame(self.tab_ai_chat, padding=12)
        frame.pack(fill="both", expand=True)

        # Chat history
        ttk.Label(frame, text="AI Chat — Təhlükəsizlik Məsləhətçisi", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 8))

        self.chat_history = scrolledtext.ScrolledText(frame, height=20, wrap="word", font=("Segoe UI", 10))
        self.chat_history.pack(fill="both", expand=True, pady=(0, 8))
        self.chat_history.tag_configure("user", foreground="blue", font=("Segoe UI", 10, "bold"))
        self.chat_history.tag_configure("ai", foreground="green", font=("Segoe UI", 10))
        self.chat_history.tag_configure("error", foreground="red")

        # Input frame
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill="x", pady=(8, 0))

        ttk.Label(input_frame, text="Sual:").pack(side="left", padx=(0, 4))
        self.chat_input = ttk.Entry(input_frame, width=80, font=("Segoe UI", 10))
        self.chat_input.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.chat_input.bind("<Return>", lambda e: self._send_ai_message())

        ttk.Button(input_frame, text="📤 Göndər", command=self._send_ai_message).pack(side="left", padx=4)
        ttk.Button(input_frame, text="🗑️ Təmizlə", command=self._clear_chat).pack(side="left")

        # Predefined prompts
        prompts_frame = ttk.LabelFrame(frame, text="Hazır Suallar", padding=8)
        prompts_frame.pack(fill="x", pady=(8, 0))

        prompts = [
            "unified_findings.json-dakı ən kritik zəifliyi izah et",
            "IDOR zəifliyini necə düzəldə bilərəm?",
            "Hardcoded secret-ləri necə təmizləyim?",
            "Bu proyektdə hansı OWASP Top 10 zəiflikləri var?",
        ]

        for i, prompt in enumerate(prompts):
            btn = ttk.Button(
                prompts_frame,
                text=f"{i+1}. {prompt[:50]}...",
                command=lambda p=prompt: self._use_prompt(p)
            )
            btn.pack(fill="x", pady=2)

    def _use_prompt(self, prompt):
        self.chat_input.delete(0, tk.END)
        self.chat_input.insert(0, prompt)
        self._send_ai_message()

    def _send_ai_message(self):
        user_msg = self.chat_input.get().strip()
        if not user_msg:
            return

        self.chat_history.insert(tk.END, f"👤 Siz: {user_msg}\n", "user")
        self.chat_history.see(tk.END)
        self.chat_input.delete(0, tk.END)

        # Get AI response
        ai_response = self._get_ai_response(user_msg)

        self.chat_history.insert(tk.END, f"🤖 AI: {ai_response}\n\n", "ai")
        self.chat_history.see(tk.END)
        self._write_log(f"AI Chat | User: {user_msg} | AI: {ai_response[:100]}...")

    def _get_ai_response(self, user_msg: str) -> str:
        """
        AI cavabı (OpenRouter API ilə və ya lokal məlumat əsaslı)
        """
        api_key = self.config.get("openrouter_api_key", "").strip()

        # Əvvəlcə lokal context-dən cavab verməyə çalış
        context = self._get_local_context()

        # API key yoxdursa, lokal məlumat əsaslı cavab ver
        if not api_key:
            return self._get_local_ai_response(user_msg, context)

        # OpenRouter ilə cavab al
        try:
            import requests

            model = self.config.get("openrouter_model", "openrouter/google/gemma-2-9b-it")
            base_url = self.config.get("openrouter_base", "https://openrouter.ai/api/v1")

            system_prompt = f"""Sən təhlükəsizlik məsləhətçisisən. İstifadəçinin proyektində aşağıdakı məlumatlar var:

{context}

İstifadəçinin sualına qısa və konkret cavab ver. Azərbaycan dilində cavab ver."""

            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ],
                "temperature": 0.3,
                "max_tokens": 500
            }

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            response = requests.post(
                f"{base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"API xətası: {response.status_code} - {response.text[:200]}"

        except Exception as e:
            return f"Xəta: {str(e)}\n\nLokal cavab istifadə olunur:\n{self._get_local_ai_response(user_msg, context)}"

    def _get_local_context(self) -> str:
        """Lokal unified_findings.json və konfiqurasiyanı oxuyur"""
        context = []

        # Unified findings
        unified_path = self.config.get("paths", {}).get("unified_findings_json", "unified_findings.json")
        if os.path.exists(unified_path):
            try:
                with open(unified_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    summary = data.get("summary", {})
                    findings = data.get("findings", [])[:5]  # İlk 5 tapıntı

                    context.append(f"Tapıntı sayı: {summary.get('total', 0)}")
                    context.append(f"Kritik: {summary.get('critical', 0)}, Yüksək: {summary.get('high', 0)}")

                    if findings:
                        context.append("\nƏn vacib tapıntılar:")
                        for f in findings:
                            context.append(f"- {f.get('tool', '?')}: {f.get('title', '?')} ({f.get('severity', '?')})")
            except:
                pass

        # Current project
        if self.current_project_root:
            context.append(f"\nCari projekt: {self.current_project_root}")

        return "\n".join(context) if context else "Heç bir məlumat yoxdur"

    def _get_local_ai_response(self, user_msg: str, context: str) -> str:
        """API olmadan sadə cavab"""
        msg_lower = user_msg.lower()

        if "kritik" in msg_lower or "critical" in msg_lower:
            return f"Kritik zəifliklər:\n{context}\n\nTövsiyə: Hardcoded secret-ləri environment variable-lara köçürün, auth middleware əlavə edin."

        if "idor" in msg_lower:
            return """IDOR (Insecure Direct Object Reference) düzəltmə:

1. Ownership yoxlaması əlavə edin:
   ```
   if (requestedUserId !== tokenUserId) {
       return res.status(403).json({ error: 'Access denied' });
   }
   ```

2. Authorization middleware istifadə edin
3. API-da user context-ini yoxlayın"""

        if "hardcoded" in msg_lower or "secret" in msg_lower:
            return """Hardcoded secret-ləri təmizləmək:

1. Environment variable istifadə edin:
   const API_KEY = process.env.API_KEY;

2. .env faylını .gitignore-a əlavə edin

3. Secret management (AWS Secrets Manager, HashiCorp Vault)

4. Gitleaks pre-commit hook quraşdırın"""

        if "owasp" in msg_lower:
            return f"""Proyektdəki OWASP Top 10 zəiflikləri:

{context}

Ən çox: A01 (Broken Access Control), A02 (Cryptographic Failures), A03 (Injection)"""

        return f"Məlumat:\n{context}\n\nDaha ətraflı cavab üçün OpenRouter API key konfiqurasiyada təyin edin."

    def _clear_chat(self):
        self.chat_history.delete("1.0", tk.END)
        self._write_log("AI Chat təmizləndi")
    def _build_scanner_tab(self):
        frame = ttk.Frame(self.tab_scanner, padding=12)
        frame.pack(fill="both", expand=True)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(btn_frame, text="🚀 Bütün aktif skanları işlət", command=self._run_all_scans).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="🔄 Yenilə", command=self._refresh_status).pack(side="left", padx=4)

        self.scan_tree = ttk.Treeview(
            frame,
            columns=("tool", "status", "output", "file", "error"),
            show="headings",
            height=12,
        )
        self.scan_tree.heading("tool", text="Alət")
        self.scan_tree.heading("status", text="Status")
        self.scan_tree.heading("output", text="Çıxış")
        self.scan_tree.heading("file", text="Fayl")
        self.scan_tree.heading("error", text="Xəta")
        self.scan_tree.column("tool", width=100)
        self.scan_tree.column("status", width=80)
        self.scan_tree.column("output", width=400)
        self.scan_tree.column("file", width=150)
        self.scan_tree.column("error", width=200)
        self.scan_tree.pack(fill="both", expand=True)

        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.scan_tree.yview)
        self.scan_tree.configure(yscroll=scroll.set)
        scroll.pack(side="right", fill="y")

        self.scan_detail = scrolledtext.ScrolledText(frame, height=10, wrap="word")
        self.scan_detail.pack(fill="both", expand=True, pady=(8, 0))
        self.scan_tree.bind("<<TreeviewSelect>>", self._on_scan_select)

    def _run_all_scans(self):
        api_key = self.config.get("openrouter_api_key", "")
        target = self.config.get("target_url", "http://localhost:8000")

        if not api_key and self.config.get("tools", {}).get("strix", True):
            messagebox.showwarning(
                "Açar tələb olunur",
                "Strix üçün OpenRouter API açarı konfiqurasiya sekmesində tələb olunur.",
            )
            return

        # Clear tree
        for item in self.scan_tree.get_children():
            self.scan_tree.delete(item)

        self.status_var.set("Skanlar işlədilir...")
        self.root.update()

        results = self.scanner.run_all_local(api_key=api_key, target=target)

        for r in results:
            status = "✅ Uğurlu" if r.success else "❌ Xəta"
            self.scan_tree.insert(
                "", "end",
                values=(r.tool, status, r.output[:120] + ("..." if len(r.output) > 120 else ""), r.file or "-", r.error or "-")
            )

        self.status_var.set(f"{len(results)} skan tamamlandı")
        self._refresh_status()

    def _on_scan_select(self, event):
        sel = self.scan_tree.selection()
        if not sel:
            return
        item = self.scan_tree.item(sel[0])
        tool_name = item["values"][0]
        for r in self.scanner.get_results():
            if r["tool"] == tool_name:
                self.scan_detail.delete("1.0", tk.END)
                self.scan_detail.insert(tk.END, json.dumps(r, indent=2, ensure_ascii=False))
                break

    # ------------------------------------------------------------------ #
    # Sekme: Deterministik Qapı
    # ------------------------------------------------------------------ #
    def _build_gate_tab(self):
        frame = ttk.Frame(self.tab_gate, padding=12)
        frame.pack(fill="both", expand=True)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(btn_frame, text="🔗 Nəticələri Birləşdir", command=self._unify_findings).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="🚪 Qapıni Dəyərləndir", command=self._evaluate_gate).pack(side="left", padx=4)

        self.gate_result_var = tk.StringVar(value="Qapı hələ dəyərlənməyib")
        ttk.Label(frame, textvariable=self.gate_result_var, font=("Segoe UI", 12, "bold")).pack(pady=8)

        self.gate_detail = scrolledtext.ScrolledText(frame, height=14, wrap="word")
        self.gate_detail.pack(fill="both", expand=True)

    def _unify_findings(self):
        paths = []
        p = self.config.get("paths", {})
        for key in ["semgrep_json", "trivy_json", "findings_json", "nuclei_json"]:
            path = p.get(key, "")
            if path and os.path.exists(path):
                paths.append(path)

        if not paths:
            messagebox.showwarning("Fayl tapılmadı", "Heç bir nəticə faylı tapılmadı. Əvvəl skan işlətin.")
            return

        output_path = p.get("unified_findings_json", "unified_findings.json")
        try:
            unified = self.gate.unify_findings(paths, output_path=output_path)
            self.gate_detail.delete("1.0", tk.END)
            self.gate_detail.insert(tk.END, json.dumps(unified, indent=2, ensure_ascii=False))
            self.status_var.set(f"Birləşdirmə tamamlandı: {len(unified.get('findings', []))} tapıntı → {output_path}")
            messagebox.showinfo("Uğurlu", f"{output_path} yaradıldı. Tapıntı sayı: {len(unified.get('findings', []))}")
        except Exception as e:
            messagebox.showerror("Xəta", str(e))

    def _evaluate_gate(self):
        output_path = self.config.get("paths", {}).get("unified_findings_json", "unified_findings.json")
        if not os.path.exists(output_path):
            messagebox.showwarning("Fayl tapılmadı", "unified_findings.json tapılmadı. Əvvəl 'Nəticələri Birləşdir' klikləyin.")
            return

        report = self.gate.gate_report(unified_path=output_path)

        self.gate_detail.delete("1.0", tk.END)
        self.gate_detail.insert(tk.END, json.dumps(report, indent=2, ensure_ascii=False))

        if report["passed"]:
            self.gate_result_var.set(f"✅ {report['decision']}")
            self.gate_detail.tag_configure("ok", foreground="green")
            self.gate_detail.insert(tk.END, f"\n\n{report['reason']}\nDeterministik: {report['deterministic']}\nLLM müdaxiləsi: {report['llm_involved']}", "ok")
            self.status_var.set("Qapı KEÇDİ — publish/deploy icazə verilir")
        else:
            self.gate_result_var.set(f"❌ {report['decision']}")
            self.gate_detail.tag_configure("bad", foreground="red")
            self.gate_detail.insert(tk.END, f"\n\n{report['reason']}\nDeterministik: {report['deterministic']}\nLLM müdaxiləsi: {report['llm_involved']}", "bad")
            self.status_var.set("Qapı BLOKEOLDU — publish/deploy yoxdur")

    # ------------------------------------------------------------------ #
    # Sekme: Hesabat
    # ------------------------------------------------------------------ #
    def _build_report_tab(self):
        frame = ttk.Frame(self.tab_report, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Button(frame, text="📄 report.pdf aç / yoxla", command=self._open_report).pack(anchor="w", pady=(0, 8))

        self.report_text = scrolledtext.ScrolledText(frame, height=25, wrap="word")
        self.report_text.pack(fill="both", expand=True)

    def _open_report(self):
        p = self.config.get("paths", {})
        pdf = p.get("report_pdf", "report.pdf")
        unified = p.get("unified_findings_json", "unified_findings.json")

        content = ""
        if os.path.exists(pdf):
            content += f"PDF hesabatı tapıldı: {pdf}\n\n"
        else:
            content += f"PDF hesabatı tapılmadı: {pdf}\n\n"

        if os.path.exists(unified):
            try:
                with open(unified, "r", encoding="utf-8") as f:
                    data = json.load(f)
                content += f"unified_findings.json:\n{json.dumps(data, indent=2, ensure_ascii=False)}"
            except Exception as e:
                content += f"unified_findings.json oxunmaya xəta: {e}"
        else:
            content += f"unified_findings.json tapılmadı: {unified}"

        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, content)

    # ------------------------------------------------------------------ #
    # Sekme: Loglar
    # ------------------------------------------------------------------ #
    def _build_logs_tab(self):
        frame = ttk.Frame(self.tab_logs, padding=12)
        frame.pack(fill="both", expand=True)

        self.log_text = scrolledtext.ScrolledText(frame, height=25, wrap="word")
        self.log_text.pack(fill="both", expand=True)
        self._write_log("Uygulama başlatıldı.\n")

    def _write_log(self, text: str):
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)

    # ------------------------------------------------------------------ #
    # Helper
    # ------------------------------------------------------------------ #
    def _refresh_status(self):
        p = self.config.get("paths", {})
        files = []
        for key in ["semgrep_json", "trivy_json", "findings_json", "nuclei_json", "unified_findings_json"]:
            path = p.get(key, "")
            if path and os.path.exists(path):
                files.append(path)

        if files:
            self.status_var.set(f"Mövcut fayllar: {', '.join(files)}")
        else:
            self.status_var.set("Hazır — skan işləməmisiniz")


def main():
    root = tk.Tk()
    app = DevSecOpsDesktopApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()