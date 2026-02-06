import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
from ui.styles import ThemeManager
from database import DatabaseManager

class SettingsScreen(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Main.TFrame")
        self.db = DatabaseManager()
        self._init_ui()
        self._load_settings()

    def _init_ui(self):
        ttk.Label(self, text="Settings & Support", style="Header.TLabel").pack(anchor="w", pady=(0, 20))

        # 1. Business Configuration
        config_frame = ttk.LabelFrame(self, text="Business Configuration", style="Card.TFrame", padding=15)
        config_frame.pack(fill="x", pady=(0, 20))
        
        # GST Config
        ttk.Label(config_frame, text="GST Percentage (%)").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_gst = ttk.Entry(config_frame)
        self.entry_gst.grid(row=0, column=1, padx=10, pady=5)
        
        # Business Name
        ttk.Label(config_frame, text="Business Name").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_biz_name = ttk.Entry(config_frame, width=40)
        self.entry_biz_name.grid(row=1, column=1, padx=10, pady=5)
        
        # Printer Format
        ttk.Label(config_frame, text="Printer Format").grid(row=2, column=0, sticky="w", pady=5)
        self.combo_printer = ttk.Combobox(config_frame, values=["Thermal 80mm", "Thermal 58mm", "A4 (Standard)"], state="readonly", width=20)
        self.combo_printer.current(0)
        self.combo_printer.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        ttk.Button(config_frame, text="Save Settings", command=self._save_settings).grid(row=3, column=1, sticky="e", pady=10)

        # 2. Business Logo
        logo_frame = ttk.LabelFrame(self, text="Business Logo", style="Card.TFrame", padding=15)
        logo_frame.pack(fill="x", pady=(0, 20))
        
        self.lbl_logo_path = ttk.Label(logo_frame, text="No logo selected", foreground="gray")
        self.lbl_logo_path.pack(side="left", padx=(0, 10))
        
        ttk.Button(logo_frame, text="Browse...", command=self._browse_logo).pack(side="left", padx=5)
        ttk.Button(logo_frame, text="Clear", command=self._clear_logo).pack(side="left", padx=5)
        
        # 3. Support Form
        support_frame = ttk.LabelFrame(self, text="Support", style="Card.TFrame", padding=15)
        support_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(support_frame, text="Name").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_sup_name = ttk.Entry(support_frame, width=30)
        self.entry_sup_name.grid(row=0, column=1, padx=10, sticky="w")
        
        ttk.Label(support_frame, text="Email").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_sup_email = ttk.Entry(support_frame, width=30)
        self.entry_sup_email.grid(row=1, column=1, padx=10, sticky="w")
        
        ttk.Label(support_frame, text="Message").grid(row=2, column=0, sticky="nw", pady=5)
        self.txt_sup_msg = tk.Text(support_frame, height=4, width=40, font=("Segoe UI", 10))
        self.txt_sup_msg.grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Button(support_frame, text="Send Message", command=self._send_support).grid(row=3, column=1, sticky="e", pady=10)

    def _load_settings(self):
        # Load from DB
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM settings")
        rows = cursor.fetchall()
        data = dict(rows)
        conn.close()
        
        if "gst_percent" in data:
            self.entry_gst.insert(0, data["gst_percent"])
        else:
            self.entry_gst.insert(0, "18.0")
            
        if "biz_name" in data:
            self.entry_biz_name.insert(0, data["biz_name"])
            
        if "print_format" in data:
            self.combo_printer.set(data["print_format"])
            
        if "company_logo" in data and data["company_logo"]:
            self.logo_path = data["company_logo"]
            self.lbl_logo_path.config(text=self.logo_path)
        else:
            self.logo_path = None

    def _browse_logo(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if path:
            self.logo_path = path
            self.lbl_logo_path.config(text=path)

    def _clear_logo(self):
        self.logo_path = None
        self.lbl_logo_path.config(text="No logo selected")

    def _save_settings(self):
        gst = self.entry_gst.get().strip()
        name = self.entry_biz_name.get().strip()
        p_format = self.combo_printer.get()
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("REPLACE INTO settings (key, value) VALUES ('gst_percent', ?)", (gst,))
        cursor.execute("REPLACE INTO settings (key, value) VALUES ('biz_name', ?)", (name,))
        cursor.execute("REPLACE INTO settings (key, value) VALUES ('print_format', ?)", (p_format,))
        
        if hasattr(self, 'logo_path') and self.logo_path:
            cursor.execute("REPLACE INTO settings (key, value) VALUES ('company_logo', ?)", (self.logo_path,))
        else:
            # If cleared, remove it (or set empty)
            cursor.execute("REPLACE INTO settings (key, value) VALUES ('company_logo', ?)", ("",))
            
        conn.commit()
        conn.close()
        messagebox.showinfo("Saved", "Settings updated successfully.")

    def _send_support(self):
        name = self.entry_sup_name.get()
        email = self.entry_sup_email.get()
        msg = self.txt_sup_msg.get("1.0", tk.END).strip()
        
        if not name or not email or not msg:
            messagebox.showwarning("Missing Info", "Please fill all support fields.")
            return

        # Threading to prevent GUI freeze
        threading.Thread(target=self._post_to_formspree, args=(name, email, msg), daemon=True).start()

    def _post_to_formspree(self, name, email, msg):
        url = "https://formspree.io/f/mdkyoyna"
        data = {
            "name": name,
            "email": email,
            "message": msg
        }
        try:
            resp = requests.post(url, data=data)
            if resp.ok:
                self.after(0, lambda: messagebox.showinfo("Success", "Support request sent!"))
                self.after(0, self._clear_support)
            else:
                self.after(0, lambda: messagebox.showerror("Error", "Failed to send message."))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Connection error: {e}"))

    def _clear_support(self):
        self.entry_sup_name.delete(0, tk.END)
        self.entry_sup_email.delete(0, tk.END)
        self.txt_sup_msg.delete("1.0", tk.END)
