import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from core.analytics import AnalyticsManager
from ui.styles import ThemeManager

class DashboardScreen(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Main.TFrame")
        self.analytics = AnalyticsManager()
        self._init_ui()
        # Defer loading to allow the window to show up first
        self.after(100, self.load_data)

    def _init_ui(self):
        # Header
        ttk.Label(self, text="Business Dashboard", style="Header.TLabel").pack(anchor="w", pady=(0, 20))

        # 1. Summary Cards
        self.cards_frame = ttk.Frame(self, style="Main.TFrame")
        self.cards_frame.pack(fill="x", pady=(0, 20))
        
        self.card_daily = self._create_card(self.cards_frame, "Today's Earnings", "₹0.00")
        self.card_monthly = self._create_card(self.cards_frame, "Monthly Earnings", "₹0.00")
        self.card_year = self._create_card(self.cards_frame, "Yearly Earnings", "₹0.00")
        
        # 2. Middle Section: Chart and Top Products
        split_frame = ttk.Frame(self, style="Main.TFrame")
        split_frame.pack(fill="both", expand=True)
        
        # Left: Revenue Chart
        self.chart_frame = ttk.Frame(split_frame, style="Card.TFrame", padding=10)
        self.chart_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        ttk.Label(self.chart_frame, text="Last 7 Days Revenue", style="SubHeader.TLabel").pack(anchor="w", pady=(0, 10))
        
        # Right: Top/Low Products via Tabs
        self.prod_frame = ttk.Frame(split_frame, style="Card.TFrame", padding=10)
        self.prod_frame.pack(side="right", fill="both", expand=True)
        
        self.notebook = ttk.Notebook(self.prod_frame)
        self.notebook.pack(fill="both", expand=True)

        # Tab 1: Top Selling
        self.tab_top = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_top, text="Top Selling")
        
        self.tree_top = ttk.Treeview(self.tab_top, columns=("Product", "Rev"), show="headings")
        self.tree_top.column("Product", width=120)
        self.tree_top.column("Rev", width=80, anchor="e")
        self.tree_top.heading("Product", text="Product")
        self.tree_top.heading("Rev", text="Revenue")
        self.tree_top.pack(fill="both", expand=True)

        # Tab 2: Low Selling
        self.tab_low = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_low, text="Low Selling")
        
        self.tree_low = ttk.Treeview(self.tab_low, columns=("Product", "Rev"), show="headings")
        self.tree_low.column("Product", width=120)
        self.tree_low.column("Rev", width=80, anchor="e")
        self.tree_low.heading("Product", text="Product")
        self.tree_low.heading("Rev", text="Revenue")
        self.tree_low.pack(fill="both", expand=True)

    def _create_card(self, parent, title, value):
        card = ttk.Frame(parent, style="Card.TFrame", padding=20)
        card.pack(side="left", fill="x", expand=True, padx=5)
        
        ttk.Label(card, text=title, font=("Segoe UI", 10), foreground="#6c757d", background="white").pack(anchor="w")
        lbl_value = ttk.Label(card, text=value, font=("Segoe UI", 18, "bold"), foreground=ThemeManager.PRIMARY_COLOR, background="white")
        lbl_value.pack(anchor="w", pady=(5, 0))
        return lbl_value

    def load_data(self):
        # 1. Summary
        daily = self.analytics.get_todays_earnings()
        monthly = self.analytics.get_monthly_earnings()
        yearly = self.analytics.get_yearly_earnings()
        
        self.card_daily.config(text=f"₹{daily:,.2f}")
        self.card_monthly.config(text=f"₹{monthly:,.2f}")
        self.card_year.config(text=f"₹{yearly:,.2f}")
        
        # 2. Chart
        days, amounts = self.analytics.get_last_7_days_revenue()
        self._draw_chart(days, amounts)
        
        # 3. Top Products
        top_prods = self.analytics.get_top_products()
        for item in self.tree_top.get_children():
            self.tree_top.delete(item)
            
        for name, qty, rev in top_prods:
            self.tree_top.insert("", "end", values=(name, f"₹{rev:,.2f}"))

        # 4. Low Selling Products
        low_prods = self.analytics.get_low_products()
        for item in self.tree_low.get_children():
            self.tree_low.delete(item)
            
        for name, qty, rev in low_prods:
            self.tree_low.insert("", "end", values=(name, f"₹{rev:,.2f}"))

    def _draw_chart(self, days, amounts):
        # Clear previous chart if any
        for widget in self.chart_frame.winfo_children():
            if isinstance(widget, tk.Canvas): # Or FigureCanvasTkAgg widget which sits on a canvas
                widget.destroy()
            if "matplotlib" in str(type(widget)): # loose check
                widget.destroy()

        # Simplify days for display (e.g. "05-12")
        days_fmt = [d[5:] for d in days] # Remove YYYY-

        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # Styling
        ax.bar(days_fmt, amounts, color=ThemeManager.SECONDARY_COLOR, alpha=0.7)
        ax.set_title("")
        ax.set_ylabel("Revenue (₹)")
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

