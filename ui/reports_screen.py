import tkinter as tk
from tkinter import ttk, messagebox
import os
from core.exporter import Exporter

class ReportsScreen(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Main.TFrame")
        self.exporter = Exporter()
        self._init_ui()

    def _init_ui(self):
        ttk.Label(self, text="Reports & Exports", style="Header.TLabel").pack(anchor="w", pady=(0, 20))
        
        card = ttk.Frame(self, style="Card.TFrame", padding=20)
        card.pack(fill="x", anchor="n")
        
        ttk.Label(card, text="Export Data to Excel", style="SubHeader.TLabel").pack(anchor="w", pady=(0, 15))
        
        btn_weekly = ttk.Button(card, text="Export Last 7 Days", style="Primary.TButton", command=self._export_weekly)
        btn_weekly.pack(side="left", padx=10)
        
        btn_monthly = ttk.Button(card, text="Export Current Month", style="Primary.TButton", command=self._export_monthly)
        btn_monthly.pack(side="left", padx=10)
        
        self.lbl_status = ttk.Label(card, text="", foreground="green")
        self.lbl_status.pack(side="left", padx=20)

    def _export_weekly(self):
        self.lbl_status.config(text="Exporting...", foreground="blue")
        self.update_idletasks()
        success, msg = self.exporter.export_weekly_data()
        self._show_result(success, msg)

    def _export_monthly(self):
        self.lbl_status.config(text="Exporting...", foreground="blue")
        self.update_idletasks()
        success, msg = self.exporter.export_monthly_data()
        self._show_result(success, msg)

    def _show_result(self, success, msg):
        if success:
            self.lbl_status.config(text=f"Saved: {os.path.basename(msg)}", foreground="green")
            # Open folder (Windows only)
            os.startfile(os.path.dirname(msg))
        else:
            self.lbl_status.config(text=f"Error: {msg}", foreground="red")
            messagebox.showerror("Export Failed", msg)
