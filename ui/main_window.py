import tkinter as tk
from tkinter import ttk
from ui.styles import ThemeManager
from ui.billing_screen import BillingScreen
from ui.dashboard_screen import DashboardScreen
from ui.settings_screen import SettingsScreen
from ui.reports_screen import ReportsScreen
from ui.products_screen import ProductsScreen

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Smart Billing Pro")
        self.geometry("1200x800")
        self.minsize(1024, 768)
        
        # Icon
        try:
            icon = tk.PhotoImage(file="app_icon.png")
            self.iconphoto(False, icon)
        except Exception:
            pass
        
        # Apply Theme
        ThemeManager.apply_theme(self)

        # Layout Setup
        self._setup_layout()
        self._setup_sidebar()
        self._setup_main_area()

        # Show initial screen
        self.show_dashboard()

    def _setup_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _setup_sidebar(self):
        self.sidebar = ttk.Frame(self, style="Sidebar.TFrame", width=250)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        # App Logo / Title area
        lbl_title = ttk.Label(self.sidebar, text="BILLING PRO", style="Sidebar.TLabel", font=("Segoe UI", 16, "bold"))
        lbl_title.pack(pady=30, padx=20, anchor="w")

        # Navigation Buttons
        self._create_nav_button("Dashboard", self.show_dashboard)
        self._create_nav_button("New Bill", self.show_billing)
        self._create_nav_button("Products", self.show_products)
        self._create_nav_button("Reports", self.show_reports)
        self._create_nav_button("Settings", self.show_settings)

        # Support Section at bottom
        lbl_support = ttk.Label(self.sidebar, text="Need Help?", style="Sidebar.TLabel", font=("Segoe UI", 9))
        lbl_support.pack(side="bottom", pady=10,padx=20, anchor="w")

    def _create_nav_button(self, text, command):
        btn = ttk.Button(self.sidebar, text=text, style="Sidebar.TButton", command=command, cursor="hand2")
        btn.pack(fill="x", pady=2, padx=10)

    def _setup_main_area(self):
        self.main_container = ttk.Frame(self, style="Main.TFrame")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.current_frame = None

    def _switch_content(self, frame_class):
        if self.current_frame:
            self.current_frame.destroy()
        
        # Placeholder for specific screens
        self.current_frame = frame_class(self.main_container)
        self.current_frame.pack(fill="both", expand=True)

    # --- Navigation Methods ---
    def show_dashboard(self):
        self._switch_content(DashboardScreen)

    def show_billing(self):
        self._switch_content(BillingScreen)

    def show_products(self):
        self._switch_content(ProductsScreen)
        
    def show_reports(self):
        self._switch_content(ReportsScreen)

    def show_settings(self):
        self._switch_content(SettingsScreen)

# Temporary Placeholders until real screens are implemented
class DashboardPlaceholder(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Main.TFrame")
        ttk.Label(self, text="Dashboard", style="Header.TLabel").pack(anchor="w")

class BillingPlaceholder(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Main.TFrame")
        ttk.Label(self, text="Billing Screen", style="Header.TLabel").pack(anchor="w")

class LabelPlaceholder(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Main.TFrame")
        ttk.Label(self, text="Work in Progress", style="Header.TLabel").pack(anchor="w")
