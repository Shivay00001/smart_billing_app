import tkinter as tk
from tkinter import ttk

class ThemeManager:
    # Color Palette - Professional Teal/Dark Blue Theme
    PRIMARY_COLOR = "#005f73"       # Dark Teal
    SECONDARY_COLOR = "#0a9396"     # Light Teal
    ACCENT_COLOR = "#ee9b00"        # Golden/Orange for highlights
    BG_COLOR = "#e9ecef"            # Light Gray Background
    SIDEBAR_BG = "#212529"          # Dark Sidebar
    TEXT_COLOR = "#212529"          # Dark Text
    WHITE = "#ffffff"

    @staticmethod
    def apply_theme(root):
        style = ttk.Style(root)
        style.theme_use('clam')  # Use 'clam' as base for better customization support on Windows

        # General App Background
        root.configure(bg=ThemeManager.BG_COLOR)

        # ---------------------------------------------------------------------
        # TFrame
        # ---------------------------------------------------------------------
        style.configure("Main.TFrame", background=ThemeManager.BG_COLOR)
        style.configure("Sidebar.TFrame", background=ThemeManager.SIDEBAR_BG)
        style.configure("Card.TFrame", background=ThemeManager.WHITE, relief="solid", borderwidth=1)

        # ---------------------------------------------------------------------
        # TLabel
        # ---------------------------------------------------------------------
        style.configure("TLabel", background=ThemeManager.BG_COLOR, foreground=ThemeManager.TEXT_COLOR, font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground=ThemeManager.PRIMARY_COLOR)
        style.configure("SubHeader.TLabel", font=("Segoe UI", 12, "bold"), foreground=ThemeManager.SECONDARY_COLOR)
        style.configure("Sidebar.TLabel", background=ThemeManager.SIDEBAR_BG, foreground="#adb5bd", font=("Segoe UI", 11))
        
        # ---------------------------------------------------------------------
        # TButton
        # ---------------------------------------------------------------------
        # Primary Button
        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            background=ThemeManager.PRIMARY_COLOR,
            foreground=ThemeManager.WHITE,
            borderwidth=0,
            focuscolor=ThemeManager.SECONDARY_COLOR
        )
        style.map(
            "Primary.TButton",
            background=[("active", ThemeManager.SECONDARY_COLOR)],
            foreground=[("active", ThemeManager.WHITE)]
        )

        # Secondary/Accent Button
        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 10, "bold"),
            background=ThemeManager.ACCENT_COLOR,
            foreground=ThemeManager.WHITE,
            borderwidth=0
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#ca6702")] # Darker orange
        )
        
        # Sidebar Button (Simulated with style)
        style.configure(
            "Sidebar.TButton",
            font=("Segoe UI", 11),
            background=ThemeManager.SIDEBAR_BG,
            foreground="#ced4da",
            borderwidth=0,
            anchor="w",
            padding=10
        )
        style.map(
            "Sidebar.TButton",
            background=[("active", "#343a40"), ("selected", ThemeManager.PRIMARY_COLOR)],
            foreground=[("active", ThemeManager.WHITE), ("selected", ThemeManager.WHITE)]
        )

        # ---------------------------------------------------------------------
        # TEntry
        # ---------------------------------------------------------------------
        style.configure("TEntry", fieldbackground=ThemeManager.WHITE, borderwidth=1, padding=5)

        # ---------------------------------------------------------------------
        # Treeview (Tables)
        # ---------------------------------------------------------------------
        style.configure(
            "Treeview",
            background=ThemeManager.WHITE,
            fieldbackground=ThemeManager.WHITE,
            foreground=ThemeManager.TEXT_COLOR,
            font=("Segoe UI", 10),
            rowheight=25
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background=ThemeManager.SECONDARY_COLOR,
            foreground=ThemeManager.WHITE,
            relief="flat"
        )
        style.map("Treeview", background=[("selected", ThemeManager.PRIMARY_COLOR)])
