import os
import csv
import json
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from datetime import datetime

import pandas as pd

from email_validator import EmailValidator
from parallel_processor import ParallelBatchProcessor
from advanced_reporter import AdvancedReporter

# ─────────────────────────────────────────────────────────────────────────────
# COLOUR PALETTE
# ─────────────────────────────────────────────────────────────────────────────
C = {
    "bg":            "#f1f5f9",
    "surface":       "#ffffff",
    "surface2":      "#f8fafc",
    "nav":           "#0f172a",
    "nav_item":      "#1e293b",
    "nav_active":    "#1d4ed8",
    "nav_text":      "#94a3b8",
    "nav_text_act":  "#ffffff",
    "accent":        "#2563eb",
    "accent_dark":   "#1d4ed8",
    "accent_light":  "#eff6ff",
    "text":          "#0f172a",
    "text2":         "#475569",
    "text3":         "#94a3b8",
    "border":        "#e2e8f0",
    "border2":       "#cbd5e1",
    # status colours
    "green":         "#16a34a",
    "green_bg":      "#f0fdf4",
    "green_border":  "#86efac",
    "red":           "#dc2626",
    "red_bg":        "#fef2f2",
    "red_border":    "#fca5a5",
    "yellow":        "#b45309",
    "yellow_bg":     "#fffbeb",
    "yellow_border": "#fcd34d",
    "blue":          "#1d4ed8",
    "blue_bg":       "#eff6ff",
    "blue_border":   "#93c5fd",
    "purple":        "#6d28d9",
    "purple_bg":     "#f5f3ff",
    "teal":          "#0f766e",
    "teal_bg":       "#f0fdfa",
    # log window (GitHub dark) — always dark regardless of theme
    "log_bg":        "#0d1117",
    "log_panel":     "#161b22",
    "log_border":    "#30363d",
    "log_fg":        "#c9d1d9",
}

# ─────────────────────────────────────────────────────────────────────────────
# THEME PALETTES
# Each entry overrides the keys in C. Log colours never change (terminal look).
# ─────────────────────────────────────────────────────────────────────────────
THEMES = {
    "Light": {
        # Already the default — clean white/light-grey
        "bg":            "#f1f5f9",
        "surface":       "#ffffff",
        "surface2":      "#f8fafc",
        "nav":           "#0f172a",
        "nav_item":      "#1e293b",
        "nav_active":    "#1d4ed8",
        "nav_text":      "#94a3b8",
        "nav_text_act":  "#ffffff",
        "accent":        "#2563eb",
        "accent_dark":   "#1d4ed8",
        "accent_light":  "#eff6ff",
        "text":          "#0f172a",
        "text2":         "#475569",
        "text3":         "#94a3b8",
        "border":        "#e2e8f0",
        "border2":       "#cbd5e1",
        "green":         "#16a34a",
        "green_bg":      "#f0fdf4",
        "green_border":  "#86efac",
        "red":           "#dc2626",
        "red_bg":        "#fef2f2",
        "red_border":    "#fca5a5",
        "yellow":        "#b45309",
        "yellow_bg":     "#fffbeb",
        "yellow_border": "#fcd34d",
        "blue":          "#1d4ed8",
        "blue_bg":       "#eff6ff",
        "blue_border":   "#93c5fd",
        "purple":        "#6d28d9",
        "purple_bg":     "#f5f3ff",
        "teal":          "#0f766e",
        "teal_bg":       "#f0fdfa",
    },
    "Dark": {
        # Slate-dark full dark mode
        "bg":            "#0f1117",
        "surface":       "#1a1f2e",
        "surface2":      "#141824",
        "nav":           "#07090f",
        "nav_item":      "#0f1117",
        "nav_active":    "#3b82f6",
        "nav_text":      "#64748b",
        "nav_text_act":  "#ffffff",
        "accent":        "#3b82f6",
        "accent_dark":   "#2563eb",
        "accent_light":  "#1e3a5f",
        "text":          "#e2e8f0",
        "text2":         "#94a3b8",
        "text3":         "#64748b",
        "border":        "#1e293b",
        "border2":       "#334155",
        "green":         "#22c55e",
        "green_bg":      "#052e16",
        "green_border":  "#15803d",
        "red":           "#f87171",
        "red_bg":        "#2d0a0a",
        "red_border":    "#991b1b",
        "yellow":        "#fbbf24",
        "yellow_bg":     "#292210",
        "yellow_border": "#854d0e",
        "blue":          "#60a5fa",
        "blue_bg":       "#1e3a5f",
        "blue_border":   "#1d4ed8",
        "purple":        "#a78bfa",
        "purple_bg":     "#1e1040",
        "teal":          "#2dd4bf",
        "teal_bg":       "#0a2520",
    },
    "Ocean": {
        # Teal / slate ocean theme — calming mid-tone
        "bg":            "#0d1b2a",
        "surface":       "#112240",
        "surface2":      "#0a192f",
        "nav":           "#060f1a",
        "nav_item":      "#0d1b2a",
        "nav_active":    "#00b4d8",
        "nav_text":      "#4a7c9e",
        "nav_text_act":  "#caf0f8",
        "accent":        "#00b4d8",
        "accent_dark":   "#0077b6",
        "accent_light":  "#0a3550",
        "text":          "#caf0f8",
        "text2":         "#90e0ef",
        "text3":         "#4a7c9e",
        "border":        "#1a3a5c",
        "border2":       "#23527c",
        "green":         "#52b788",
        "green_bg":      "#081c15",
        "green_border":  "#1b4332",
        "red":           "#e63946",
        "red_bg":        "#2d0a0a",
        "red_border":    "#9b2226",
        "yellow":        "#ffb703",
        "yellow_bg":     "#241a00",
        "yellow_border": "#7b5800",
        "blue":          "#48cae4",
        "blue_bg":       "#0a2a40",
        "blue_border":   "#0077b6",
        "purple":        "#7b2d8b",
        "purple_bg":     "#1a0d26",
        "teal":          "#26c6da",
        "teal_bg":       "#062030",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _pill(parent, text, fg, bg, font=("Segoe UI", 9, "bold")):
    """Small coloured pill / badge label."""
    return tk.Label(parent, text=f"  {text}  ", fg=fg, bg=bg,
                    font=font, relief="flat", padx=2, pady=1)


def _divider(parent, bg=None, height=1, pady=0):
    bg = bg or C["border"]
    f = tk.Frame(parent, bg=bg, height=height)
    f.pack(fill="x", pady=pady)
    return f


def _card(parent, **kw):
    """White card with border."""
    bg = kw.pop("bg", C["surface"])
    f = tk.Frame(parent, bg=bg,
                 highlightbackground=C["border"],
                 highlightthickness=1, **kw)
    return f


class EmailValidatorGUI:
    """Power Email Validation – Enterprise Console."""

    # ─────────────────────────────────────────────────────────────────────────
    def __init__(self, root):
        self.root = root
        self.root.title("Power Email Validation – Enterprise Console")
        self.root.geometry("1480x920")
        self.root.minsize(1200, 760)
        self.root.configure(bg=C["bg"])

        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self._configure_styles()

        self.validator       = EmailValidator(timeout=10)
        self.batch_processor = ParallelBatchProcessor(max_workers=6, validator_timeout=10)
        self.reporter        = AdvancedReporter()

        self.validation_results    = []
        self.recent_results        = []
        self.source_rows           = []
        self.source_columns        = []
        self.source_file_path      = None
        self.source_file_ext       = None
        self.selected_email_column = None
        self.selected_sheet_name   = None

        # Live log
        self.live_counts = {k: 0 for k in
                            ("total", "valid", "invalid", "deliverable", "catchall", "disposable")}
        self.log_autoscroll     = True
        self.live_log_text      = None
        self._autoscroll_btn    = None
        self._live_count_labels = {}
        self._log_status_var    = None
        self._nav_buttons       = {}

        # Theme state
        self.current_theme = "Light"

        self._build_layout()
        self._set_status("Ready – Power Email Validation v2.0")
        self._tick_clock()

    # ─────────────────────────────────────────────────────────────────────────
    # STYLES
    # ─────────────────────────────────────────────────────────────────────────
    def _configure_styles(self):
        s = self.style

        s.configure("Root.TFrame",    background=C["bg"])
        s.configure("Surface.TFrame", background=C["surface"])

        # Notebook
        s.configure("TNotebook",
                    background=C["surface"], tabmargins=[0, 0, 0, 0], borderwidth=0)
        s.configure("TNotebook.Tab",
                    background=C["bg"], foreground=C["text2"],
                    padding=(20, 10), font=("Segoe UI", 10, "bold"))
        s.map("TNotebook.Tab",
              background=[("selected", C["accent"])],
              foreground=[("selected", "#ffffff")])

        # Treeview
        s.configure("Treeview",
                    background=C["surface"], foreground=C["text"],
                    fieldbackground=C["surface"], rowheight=34,
                    font=("Segoe UI", 10))
        s.configure("Treeview.Heading",
                    background=C["bg"], foreground=C["text2"],
                    font=("Segoe UI", 10, "bold"), relief="flat")
        s.map("Treeview",
              background=[("selected", C["accent"])],
              foreground=[("selected", "#ffffff")])

        # Progressbar
        s.configure("green.Horizontal.TProgressbar",
                    troughcolor=C["border"], background=C["accent"],
                    thickness=6)

        # Scrollbar
        s.configure("Vertical.TScrollbar",
                    troughcolor=C["bg"], background=C["border2"])
        s.configure("Horizontal.TScrollbar",
                    troughcolor=C["bg"], background=C["border2"])

    # ─────────────────────────────────────────────────────────────────────────
    # THEME SWITCHER
    # ─────────────────────────────────────────────────────────────────────────
    def _switch_theme(self, name: str):
        """Rebuild the entire UI with the chosen colour palette."""
        if name not in THEMES:
            return
        self.current_theme = name
        # Apply new palette to the global C dict in-place
        C.update(THEMES[name])

        # Preserve data state across rebuild
        saved_results  = list(self.validation_results)
        saved_recent   = list(self.recent_results)
        saved_log_text = ""
        if self.live_log_text:
            self.live_log_text.configure(state="normal")
            saved_log_text = self.live_log_text.get("1.0", tk.END)
            self.live_log_text.configure(state="disabled")
        saved_counts  = dict(self.live_counts)

        # Clear notebook ref BEFORE destroying, so _nav_click skips .select()
        self.notebook = None
        # Tear down
        self._root_frame.destroy()

        # Reset widget references
        self.live_log_text      = None
        self._autoscroll_btn    = None
        self._live_count_labels = {}
        self._log_status_var    = None
        self._nav_buttons       = {}

        # Rebuild styles and UI
        self._configure_styles()
        self.root.configure(bg=C["bg"])
        self._build_layout()

        # Restore data
        self.validation_results = saved_results
        self.recent_results     = saved_recent
        self.live_counts        = saved_counts
        self._update_live_counters()
        self._refresh_dashboard()
        self._update_kpis()

        # Restore log text
        if saved_log_text.strip() and self.live_log_text:
            self.live_log_text.configure(state="normal")
            self.live_log_text.delete("1.0", tk.END)
            self.live_log_text.insert(tk.END, saved_log_text)
            self.live_log_text.configure(state="disabled")

        self._set_status(f"Theme changed to  {name}")

    # ─────────────────────────────────────────────────────────────────────────
    # LAYOUT
    # ─────────────────────────────────────────────────────────────────────────
    def _build_layout(self):
        self._root_frame = tk.Frame(self.root, bg=C["bg"])
        self._root_frame.pack(fill="both", expand=True)
        self._root_frame.columnconfigure(1, weight=1)
        self._root_frame.rowconfigure(0, weight=1)
        root_frame = self._root_frame

        self._build_nav(root_frame)

        content = tk.Frame(root_frame, bg=C["bg"])
        content.grid(row=0, column=1, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)

        self._build_topbar(content)
        self._build_workspace(content)
        self._build_statusbar(content)

    # ─────────────────────────────────────────────────────────────────────────
    # SIDEBAR
    # ─────────────────────────────────────────────────────────────────────────
    def _build_nav(self, parent):
        nav = tk.Frame(parent, bg=C["nav"], width=226)
        nav.grid(row=0, column=0, sticky="ns")
        nav.grid_propagate(False)
        nav.rowconfigure(12, weight=1)

        # Brand
        brand = tk.Frame(nav, bg="#1e3a8a", pady=18, padx=16)
        brand.grid(row=0, column=0, sticky="ew")
        tk.Label(brand, text="⚡  Power Email", bg="#1e3a8a", fg="#ffffff",
                 font=("Segoe UI", 14, "bold"), anchor="w").pack(fill="x")
        tk.Label(brand, text="Validation Suite", bg="#1e3a8a", fg="#93c5fd",
                 font=("Segoe UI", 9), anchor="w").pack(fill="x")

        tk.Frame(nav, bg="#1e293b", height=1).grid(row=1, column=0, sticky="ew")

        # Section label
        tk.Label(nav, text="NAVIGATION", bg=C["nav"], fg="#334155",
                 font=("Segoe UI", 8, "bold"), anchor="w",
                 padx=16, pady=0).grid(row=2, column=0, sticky="ew", pady=(14, 4))

        nav_items = [
            ("  Dashboard",       "dashboard", 0),
            ("  Validate Single", "single",    1),
            ("  Batch Validate",  "batch",     2),
            ("  Reports",         "reports",   3),
            ("  Live Logs",       "logs",      4),
        ]
        for row_idx, (label, key, tab) in enumerate(nav_items):
            btn = tk.Button(nav, text=label, bg=C["nav"], fg=C["nav_text"],
                            activebackground=C["nav_item"], activeforeground="#ffffff",
                            relief="flat", bd=0, anchor="w", padx=16, pady=11,
                            font=("Segoe UI", 10), cursor="hand2",
                            command=lambda t=tab, k=label: self._nav_click(t, k))
            btn.grid(row=3 + row_idx, column=0, sticky="ew")
            self._nav_buttons[label] = btn

        # Spacer
        tk.Frame(nav, bg=C["nav"]).grid(row=12, column=0, sticky="nsew")

        # Version
        tk.Label(nav, text="v2.0  Power Email Validation",
                 bg=C["nav"], fg="#334155",
                 font=("Segoe UI", 8)).grid(row=13, column=0, pady=10)

        # Default highlight
        self._nav_click(0, "  Dashboard")

    def _nav_click(self, tab_index, label):
        for lbl, btn in self._nav_buttons.items():
            btn.configure(bg=C["nav"], fg=C["nav_text"], font=("Segoe UI", 10))
        if label in self._nav_buttons:
            self._nav_buttons[label].configure(
                bg=C["nav_active"], fg="#ffffff", font=("Segoe UI", 10, "bold"))
        # Guard: notebook may be None (during initial build or theme rebuild)
        # or may point to a destroyed widget — catch both safely.
        try:
            if getattr(self, "notebook", None) is not None:
                self.notebook.select(tab_index)
        except Exception:
            pass

    # ─────────────────────────────────────────────────────────────────────────
    # TOPBAR
    # ─────────────────────────────────────────────────────────────────────────
    def _build_topbar(self, parent):
        top = tk.Frame(parent, bg=C["surface"])
        top.grid(row=0, column=0, sticky="ew")

        # Accent stripe
        tk.Frame(top, bg=C["accent"], height=3).pack(fill="x")

        inner = tk.Frame(top, bg=C["surface"], padx=20, pady=14)
        inner.pack(fill="x")
        inner.columnconfigure(0, weight=1)

        # Left
        left = tk.Frame(inner, bg=C["surface"])
        left.grid(row=0, column=0, sticky="w")
        tk.Label(left, text="Email Validation Platform",
                 bg=C["surface"], fg=C["text"],
                 font=("Segoe UI", 19, "bold")).pack(anchor="w")
        tk.Label(left,
                 text="Enterprise-grade  ·  Real-time monitoring  ·  Bulk processing  ·  Audit-ready",
                 bg=C["surface"], fg=C["text3"],
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 0))

        # Right — keep it clean: just theme switcher + refresh
        right = tk.Frame(inner, bg=C["surface"])
        right.grid(row=0, column=1, sticky="e")

        # Theme switcher
        tk.Label(right, text="Theme:", bg=C["surface"], fg=C["text2"],
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 6))
        self._theme_var = tk.StringVar(value=self.current_theme)
        theme_cb = ttk.Combobox(right, textvariable=self._theme_var,
                                values=list(THEMES.keys()),
                                state="readonly", width=9,
                                font=("Segoe UI", 10))
        theme_cb.pack(side="left", padx=(0, 14))
        theme_cb.bind("<<ComboboxSelected>>",
                      lambda e: self._switch_theme(self._theme_var.get()))

        # Refresh button
        self._btn(right, "  Refresh Dashboard", C["border2"], C["text"],
                  self._refresh_dashboard).pack(side="left")

    # ─────────────────────────────────────────────────────────────────────────
    # KPI BAR
    # ─────────────────────────────────────────────────────────────────────────
    def _build_workspace(self, parent):
        body = tk.Frame(parent, bg=C["bg"])
        body.grid(row=1, column=0, sticky="nsew", padx=16, pady=(12, 0))
        body.columnconfigure(0, weight=1)
        body.rowconfigure(1, weight=1)

        self._build_kpis(body)

        # Main notebook area
        nb_frame = tk.Frame(body, bg=C["surface"],
                             highlightbackground=C["border"], highlightthickness=1)
        nb_frame.grid(row=1, column=0, sticky="nsew", padx=0)
        nb_frame.columnconfigure(0, weight=1)
        nb_frame.rowconfigure(0, weight=1)

        self.notebook = ttk.Notebook(nb_frame)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        self.dashboard_tab = tk.Frame(self.notebook, bg=C["surface"])
        self.single_tab    = tk.Frame(self.notebook, bg=C["surface"])
        self.bulk_tab      = tk.Frame(self.notebook, bg=C["surface"])
        self.reports_tab   = tk.Frame(self.notebook, bg=C["surface"])
        self.log_tab       = tk.Frame(self.notebook, bg=C["log_bg"])

        self.notebook.add(self.dashboard_tab, text="   Dashboard   ")
        self.notebook.add(self.single_tab,    text="   Single   ")
        self.notebook.add(self.bulk_tab,      text="   Batch   ")
        self.notebook.add(self.reports_tab,   text="   Reports   ")
        self.notebook.add(self.log_tab,       text="   Live Logs   ")

        self._build_dashboard_tab()
        self._build_single_tab()
        self._build_bulk_tab()
        self._build_reports_tab()
        self._build_log_tab()

    def _build_kpis(self, parent):
        bar = tk.Frame(parent, bg=C["bg"])
        bar.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        kpi_defs = [
            ("Total Validated",  "total",       C["accent"],  C["blue_bg"],   C["blue_border"],   "TOTAL"),
            ("Valid Emails",      "valid",       C["green"],   C["green_bg"],  C["green_border"],  "VALID"),
            ("Deliverable",       "deliverable", C["teal"],    C["teal_bg"],   C["teal"],          "DELIVERABLE"),
            ("Avg Confidence",    "confidence",  C["purple"],  C["purple_bg"], "#a78bfa",          "CONFIDENCE"),
        ]
        self.kpi_labels = {}
        for col, (title, key, color, bg, border, badge) in enumerate(kpi_defs):
            card = tk.Frame(bar, bg=C["surface"],
                            highlightbackground=border, highlightthickness=2)
            card.grid(row=0, column=col, sticky="ew",
                      padx=(0 if col == 0 else 10, 0))
            bar.columnconfigure(col, weight=1)

            # Coloured top accent bar
            tk.Frame(card, bg=color, height=5).pack(fill="x")

            body = tk.Frame(card, bg=C["surface"], padx=18, pady=14)
            body.pack(fill="both")
            body.columnconfigure(0, weight=1)

            # Badge
            bdg = tk.Label(body, text=badge, bg=bg, fg=color,
                           font=("Segoe UI", 8, "bold"), padx=8, pady=4,
                           relief="flat")
            bdg.grid(row=0, column=1, rowspan=2, sticky="ne")

            tk.Label(body, text=title, bg=C["surface"], fg=C["text2"],
                     font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w")

            val = tk.Label(body,
                           text="0" if key != "confidence" else "0%",
                           bg=C["surface"], fg=color,
                           font=("Segoe UI", 28, "bold"))
            val.grid(row=1, column=0, sticky="w", pady=(4, 0))
            self.kpi_labels[key] = val

    # ─────────────────────────────────────────────────────────────────────────
    # DASHBOARD TAB
    # ─────────────────────────────────────────────────────────────────────────
    def _build_dashboard_tab(self):
        frame = tk.Frame(self.dashboard_tab, bg=C["surface"])
        frame.pack(fill="both", expand=True, padx=20, pady=16)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        # Header row with quick stats
        hdr = tk.Frame(frame, bg=C["surface"])
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        hdr.columnconfigure(0, weight=1)

        self._section_label(hdr, "Recent Validation Activity").grid(
            row=0, column=0, sticky="w")

        # Quick tip banner
        tip = tk.Frame(frame, bg=C["accent_light"],
                       highlightbackground=C["blue_border"], highlightthickness=1)
        tip.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        tip_inner = tk.Frame(tip, bg=C["accent_light"], padx=14, pady=8)
        tip_inner.pack(fill="x")
        tk.Label(tip_inner, text="  Quick Start:",
                 bg=C["accent_light"], fg=C["accent"],
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        tk.Label(tip_inner,
                 text="Go to  'Single'  to validate one email  |  "
                      "'Batch'  to validate thousands  |  "
                      "Click  'Live Logs'  to monitor in real-time",
                 bg=C["accent_light"], fg=C["text2"],
                 font=("Segoe UI", 9)).pack(side="left", padx=(4, 0))

        # Table
        tbl_wrap = tk.Frame(frame, bg=C["surface"])
        tbl_wrap.grid(row=2, column=0, sticky="nsew")
        tbl_wrap.columnconfigure(0, weight=1)
        tbl_wrap.rowconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        cols = ("email", "status", "confidence", "smtp", "mx", "flags", "time")
        self.recent_table = ttk.Treeview(tbl_wrap, columns=cols, show="headings")
        specs = [
            ("email",      "Email Address",  320, "w"),
            ("status",     "Status",         100, "center"),
            ("confidence", "Confidence",     100, "center"),
            ("smtp",       "SMTP Status",    120, "center"),
            ("mx",         "MX Records",      90, "center"),
            ("flags",      "Flags",          200, "w"),
            ("time",       "Time (s)",        80, "center"),
        ]
        for c, t, w, a in specs:
            self.recent_table.heading(c, text=t)
            self.recent_table.column(c, width=w, anchor=a, minwidth=60)

        self.recent_table.tag_configure("valid",
            background=C["green_bg"], foreground=C["green"])
        self.recent_table.tag_configure("invalid",
            background=C["red_bg"],   foreground=C["red"])
        self.recent_table.tag_configure("warn",
            background=C["yellow_bg"],foreground=C["yellow"])

        vsb = ttk.Scrollbar(tbl_wrap, orient="vertical",
                            command=self.recent_table.yview)
        self.recent_table.configure(yscrollcommand=vsb.set)
        self.recent_table.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

    # ─────────────────────────────────────────────────────────────────────────
    # SINGLE EMAIL TAB
    # ─────────────────────────────────────────────────────────────────────────
    def _build_single_tab(self):
        outer = tk.Frame(self.single_tab, bg=C["bg"])
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=1)

        # ── Input panel ─────────────────────────────────────────────────────
        input_card = tk.Frame(outer, bg=C["surface"],
                              highlightbackground=C["border"], highlightthickness=1)
        input_card.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 0))
        input_card.columnconfigure(0, weight=1)

        # Coloured top bar
        tk.Frame(input_card, bg=C["accent"], height=4).pack(fill="x")

        inp = tk.Frame(input_card, bg=C["surface"], padx=20, pady=16)
        inp.pack(fill="x")
        inp.columnconfigure(1, weight=1)

        tk.Label(inp, text="Email Address to Validate",
                 bg=C["surface"], fg=C["text"],
                 font=("Segoe UI", 11, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))

        self.single_email_entry = tk.Entry(
            inp, font=("Segoe UI", 13),
            bg="#ffffff", fg=C["text"],
            relief="solid", bd=1,
            insertbackground=C["accent"],
            highlightcolor=C["accent"],
            highlightthickness=2)
        self.single_email_entry.grid(row=1, column=0, sticky="ew",
                                      ipady=8, padx=(0, 10))
        inp.columnconfigure(0, weight=1)
        self.single_email_entry.bind("<Return>",
                                      lambda e: self.validate_single_email())

        self.single_validate_btn = tk.Button(
            inp, text="  Run Validation  ",
            bg=C["accent"], fg="#ffffff",
            activebackground=C["accent_dark"], activeforeground="#ffffff",
            relief="flat", bd=0, padx=18, pady=9,
            font=("Segoe UI", 11, "bold"), cursor="hand2",
            command=self.validate_single_email)
        self.single_validate_btn.grid(row=1, column=1, sticky="w")

        # SMTP checkbox
        smtp_row = tk.Frame(inp, bg=C["surface"])
        smtp_row.grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))
        self.single_smtp_var = tk.BooleanVar(value=False)
        tk.Checkbutton(smtp_row, text="Enable SMTP verification",
                       variable=self.single_smtp_var,
                       bg=C["surface"], fg=C["text2"],
                       activebackground=C["surface"],
                       font=("Segoe UI", 10)).pack(side="left")
        tk.Label(smtp_row, text="(slower · more accurate · connects to mail server)",
                 bg=C["surface"], fg=C["text3"],
                 font=("Segoe UI", 9)).pack(side="left", padx=(6, 0))

        # ── Result area ──────────────────────────────────────────────────────
        result_outer = tk.Frame(outer, bg=C["bg"])
        result_outer.grid(row=1, column=0, sticky="nsew", padx=20, pady=12)
        result_outer.columnconfigure(0, weight=1)
        result_outer.columnconfigure(1, weight=1)
        result_outer.rowconfigure(0, weight=1)

        # Left: status cards
        self._single_left = tk.Frame(result_outer, bg=C["bg"])
        self._single_left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self._build_single_status_panel(self._single_left)

        # Right: detail log
        self._single_right = tk.Frame(result_outer, bg=C["bg"])
        self._single_right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        self._build_single_detail_panel(self._single_right)

    def _build_single_status_panel(self, parent):
        """Left panel: Status cards shown after validation."""
        # Header
        hdr = tk.Frame(parent, bg=C["bg"])
        hdr.pack(fill="x", pady=(0, 8))
        self._section_label(hdr, "Validation Result").pack(side="left")

        # Placeholder
        self._status_placeholder = tk.Frame(parent, bg=C["surface"],
                                             highlightbackground=C["border"],
                                             highlightthickness=1)
        self._status_placeholder.pack(fill="both", expand=True)
        tk.Label(self._status_placeholder,
                 text="\n\n\n  Validate an email to see\n  detailed status cards here\n\n\n",
                 bg=C["surface"], fg=C["text3"],
                 font=("Segoe UI", 11), justify="center").pack(expand=True)

        # Real status frame (hidden until result)
        self._status_frame = tk.Frame(parent, bg=C["bg"])
        # Will be populated dynamically

    def _build_single_detail_panel(self, parent):
        """Right panel: Detail log."""
        hdr = tk.Frame(parent, bg=C["bg"])
        hdr.pack(fill="x", pady=(0, 8))
        self._section_label(hdr, "Validation Messages & Details").pack(side="left")

        log_card = tk.Frame(parent, bg=C["surface2"],
                            highlightbackground=C["border"],
                            highlightthickness=1)
        log_card.pack(fill="both", expand=True)

        self.single_result_box = tk.Text(
            log_card, font=("Consolas", 10),
            bg=C["surface2"], fg=C["text"],
            wrap=tk.WORD, relief="flat",
            padx=14, pady=12,
            insertbackground=C["text"],
            selectbackground=C["accent_light"],
            state="normal")
        vsb = ttk.Scrollbar(log_card, orient="vertical",
                             command=self.single_result_box.yview)
        self.single_result_box.configure(yscrollcommand=vsb.set)
        self.single_result_box.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Tags — use theme palette so they look correct on any theme
        self.single_result_box.tag_config("ph",      foreground=C["text3"])
        self.single_result_box.tag_config("ts",      foreground=C["text3"])
        self.single_result_box.tag_config("key",     foreground=C["accent"],
                                           font=("Consolas", 10, "bold"))
        self.single_result_box.tag_config("ok",      foreground=C["green"])
        self.single_result_box.tag_config("bad",     foreground=C["red"])
        self.single_result_box.tag_config("warn",    foreground=C["yellow"])
        self.single_result_box.tag_config("neutral", foreground=C["text2"])
        self.single_result_box.tag_config("header",  foreground=C["text"],
                                           font=("Consolas", 11, "bold"))
        self.single_result_box.tag_config("sep",     foreground=C["border2"])

        # Placeholder text
        self.single_result_box.insert(tk.END, "\n")
        self.single_result_box.insert(tk.END,
            "  Enter an email address above and click 'Run Validation'.\n\n", "ph")
        self.single_result_box.insert(tk.END,
            "  Detailed messages, DNS info, SMTP responses\n"
            "  and confidence scoring will appear here.\n", "ph")
        self.single_result_box.configure(state="disabled")

    # ─────────────────────────────────────────────────────────────────────────
    # BATCH TAB
    # ─────────────────────────────────────────────────────────────────────────
    def _build_bulk_tab(self):
        outer = tk.Frame(self.bulk_tab, bg=C["bg"])
        outer.pack(fill="both", expand=True, padx=20, pady=16)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(2, weight=1)

        # ── Control bar ──────────────────────────────────────────────────────
        ctrl_card = tk.Frame(outer, bg=C["surface"],
                             highlightbackground=C["border"], highlightthickness=1)
        ctrl_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        tk.Frame(ctrl_card, bg=C["accent"], height=4).pack(fill="x")

        ctrl = tk.Frame(ctrl_card, bg=C["surface"], padx=16, pady=12)
        ctrl.pack(fill="x")
        ctrl.columnconfigure(5, weight=1)

        self._btn(ctrl, "  Import File",    "#e2e8f0", C["text"],
                  self.import_emails).grid(row=0, column=0, padx=(0, 8))
        self.bulk_validate_btn = tk.Button(
            ctrl, text="  Validate Batch",
            bg=C["accent"], fg="#ffffff",
            activebackground=C["accent_dark"], activeforeground="#ffffff",
            relief="flat", bd=0, padx=16, pady=8,
            font=("Segoe UI", 10, "bold"), cursor="hand2",
            command=self.validate_bulk_emails)
        self.bulk_validate_btn.grid(row=0, column=1, padx=(0, 8))
        self._btn(ctrl, "  Export Results", "#16a34a", "#ffffff",
                  self.export_results).grid(row=0, column=2, padx=(0, 20))

        sep = tk.Frame(ctrl, bg=C["border"], width=1)
        sep.grid(row=0, column=3, sticky="ns", padx=(0, 16))

        self.bulk_smtp_var = tk.BooleanVar(value=False)
        smtp_f = tk.Frame(ctrl, bg=C["surface"])
        smtp_f.grid(row=0, column=4)
        tk.Checkbutton(smtp_f, text="Enable SMTP",
                       variable=self.bulk_smtp_var,
                       bg=C["surface"], fg=C["text2"],
                       activebackground=C["surface"],
                       font=("Segoe UI", 10)).pack(side="left")
        tk.Label(smtp_f, text="(deeper check)", bg=C["surface"], fg=C["text3"],
                 font=("Segoe UI", 9)).pack(side="left", padx=(4, 0))

        # ── Email input area ─────────────────────────────────────────────────
        input_card = tk.Frame(outer, bg=C["surface"],
                              highlightbackground=C["border"], highlightthickness=1)
        input_card.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        inp_hdr = tk.Frame(input_card, bg=C["bg"], padx=14, pady=8)
        inp_hdr.pack(fill="x")
        inp_hdr.columnconfigure(0, weight=1)
        tk.Label(inp_hdr, text="Email List",
                 bg=C["bg"], fg=C["text"], font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, sticky="w")
        tk.Label(inp_hdr, text="One email per line  |  or paste comma-separated",
                 bg=C["bg"], fg=C["text3"], font=("Segoe UI", 9)).grid(
            row=0, column=1, sticky="e")

        self.bulk_text = tk.Text(
            input_card, height=6, font=("Segoe UI", 11),
            bg="#ffffff", fg=C["text"],
            relief="flat", padx=12, pady=8,
            insertbackground=C["accent"],
            wrap=tk.WORD)
        self.bulk_text.pack(fill="x", padx=1, pady=(0, 1))
        self.bulk_text.insert("1.0",
            "user@example.com\ncontact@company.org\ntest@domain.net")

        # ── Progress bar ─────────────────────────────────────────────────────
        prog_card = tk.Frame(outer, bg=C["surface"],
                             highlightbackground=C["border"], highlightthickness=1)
        prog_card.grid(row=2, column=0, sticky="nsew")
        prog_card.columnconfigure(0, weight=1)
        prog_card.rowconfigure(1, weight=1)

        prog_top = tk.Frame(prog_card, bg=C["surface"], padx=14, pady=8)
        prog_top.pack(fill="x")
        prog_top.columnconfigure(0, weight=1)

        self.bulk_status_label = tk.Label(
            prog_top, text="Ready to validate",
            bg=C["surface"], fg=C["text2"],
            font=("Segoe UI", 10))
        self.bulk_status_label.grid(row=0, column=0, sticky="w")

        self.bulk_progress = ttk.Progressbar(
            prog_card, orient="horizontal",
            mode="determinate",
            style="green.Horizontal.TProgressbar")
        self.bulk_progress.pack(fill="x", padx=14, pady=(0, 8))

        # Results table
        tbl_frame = tk.Frame(prog_card, bg=C["surface"])
        tbl_frame.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        tbl_frame.columnconfigure(0, weight=1)
        tbl_frame.rowconfigure(0, weight=1)

        cols = ("email", "status", "confidence", "smtp", "mx", "flags", "time")
        self.bulk_table = ttk.Treeview(tbl_frame, columns=cols, show="headings")
        specs = [
            ("email",      "Email Address", 300, "w"),
            ("status",     "Status",        100, "center"),
            ("confidence", "Confidence",    100, "center"),
            ("smtp",       "SMTP Status",   120, "center"),
            ("mx",         "MX Records",     90, "center"),
            ("flags",      "Flags",         180, "w"),
            ("time",       "Time (s)",       80, "center"),
        ]
        for c, t, w, a in specs:
            self.bulk_table.heading(c, text=t)
            self.bulk_table.column(c, width=w, anchor=a, minwidth=50)

        self.bulk_table.tag_configure("valid",
            background=C["green_bg"], foreground=C["green"])
        self.bulk_table.tag_configure("invalid",
            background=C["red_bg"],   foreground=C["red"])
        self.bulk_table.tag_configure("warn",
            background=C["yellow_bg"],foreground=C["yellow"])

        vsb = ttk.Scrollbar(tbl_frame, orient="vertical",
                            command=self.bulk_table.yview)
        self.bulk_table.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        self.bulk_table.configure(yscrollcommand=vsb.set)

    # ─────────────────────────────────────────────────────────────────────────
    # REPORTS TAB
    # ─────────────────────────────────────────────────────────────────────────
    def _build_reports_tab(self):
        outer = tk.Frame(self.reports_tab, bg=C["bg"])
        outer.pack(fill="both", expand=True, padx=20, pady=16)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=1)

        # Toolbar
        toolbar = tk.Frame(outer, bg=C["surface"],
                           highlightbackground=C["border"], highlightthickness=1)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        tk.Frame(toolbar, bg="#7c3aed", height=4).pack(fill="x")

        tb_inner = tk.Frame(toolbar, bg=C["surface"], padx=16, pady=10)
        tb_inner.pack(fill="x")
        tb_inner.columnconfigure(4, weight=1)

        self.report_generate_btn = tk.Button(
            tb_inner, text="  Generate Report",
            bg=C["purple"], fg="#ffffff",
            activebackground="#5b21b6", activeforeground="#ffffff",
            relief="flat", bd=0, padx=16, pady=8,
            font=("Segoe UI", 10, "bold"), cursor="hand2",
            command=self.generate_report)
        self.report_generate_btn.grid(row=0, column=0, padx=(0, 8))
        self._btn(tb_inner, "  Export .txt",  "#e2e8f0", C["text"],
                  self.export_report).grid(row=0, column=1, padx=(0, 8))
        self._btn(tb_inner, "  Export .json", "#e2e8f0", C["text"],
                  lambda: self.export_report(fmt="json")).grid(row=0, column=2)

        self.report_metadata = tk.Label(
            tb_inner, text="No report generated yet",
            bg=C["surface"], fg=C["text3"], font=("Segoe UI", 9))
        self.report_metadata.grid(row=0, column=4, sticky="e")

        # Report split view
        split = tk.Frame(outer, bg=C["bg"])
        split.grid(row=1, column=0, sticky="nsew")
        split.columnconfigure(0, weight=1)
        split.columnconfigure(1, weight=2)
        split.rowconfigure(0, weight=1)

        # Left: summary cards (populated after generate)
        self._report_summary_frame = tk.Frame(split, bg=C["bg"])
        self._report_summary_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._section_label(self._report_summary_frame, "Summary").pack(anchor="w", pady=(0, 8))
        self._report_cards_host = tk.Frame(self._report_summary_frame, bg=C["bg"])
        self._report_cards_host.pack(fill="both", expand=True)
        tk.Label(self._report_cards_host,
                 text="Generate a report to see\nsummary stats here.",
                 bg=C["bg"], fg=C["text3"],
                 font=("Segoe UI", 10), justify="center").pack(expand=True)

        # Right: full text
        right = tk.Frame(split, bg=C["bg"])
        right.grid(row=0, column=1, sticky="nsew")
        self._section_label(right, "Full Report").pack(anchor="w", pady=(0, 8))

        log_card = tk.Frame(right, bg=C["surface2"],
                            highlightbackground=C["border"],
                            highlightthickness=1)
        log_card.pack(fill="both", expand=True)
        self.report_summary = tk.Text(
            log_card, font=("Consolas", 10),
            bg=C["surface2"], fg=C["text"],
            wrap=tk.WORD, relief="flat", padx=14, pady=12,
            selectbackground=C["accent_light"],
            state="disabled")
        vsb = ttk.Scrollbar(log_card, orient="vertical",
                            command=self.report_summary.yview)
        self.report_summary.configure(yscrollcommand=vsb.set)
        self.report_summary.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

    # ─────────────────────────────────────────────────────────────────────────
    # ACTIVITY PANEL (right column)
    # ─────────────────────────────────────────────────────────────────────────
    def _build_activity_panel(self, parent):
        panel = tk.Frame(parent, bg=C["surface"],
                         highlightbackground=C["border"], highlightthickness=1)
        panel.grid(row=1, column=1, sticky="nsew")
        panel.rowconfigure(1, weight=1)
        panel.columnconfigure(0, weight=1)

        # Header
        hdr = tk.Frame(panel, bg=C["nav_active"], padx=12, pady=10)
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew")
        tk.Label(hdr, text="  Activity Log",
                 bg=C["nav_active"], fg="#ffffff",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")

        self.audit_feed = tk.Text(
            panel, font=("Consolas", 9),
            bg=C["surface"], fg=C["text2"],
            wrap=tk.WORD, relief="flat", padx=10, pady=8)
        vsb = ttk.Scrollbar(panel, orient="vertical",
                            command=self.audit_feed.yview)
        self.audit_feed.configure(yscrollcommand=vsb.set)
        self.audit_feed.grid(row=1, column=0, sticky="nsew")
        vsb.grid(row=1, column=1, sticky="ns")

        self.audit_feed.configure(state="normal")
        ts = datetime.now().strftime("%H:%M:%S")
        self.audit_feed.insert(tk.END, f"[{ts}]  System initialized\n")
        self.audit_feed.configure(state="disabled")

    # ─────────────────────────────────────────────────────────────────────────
    # STATUS BAR
    # ─────────────────────────────────────────────────────────────────────────
    def _build_statusbar(self, parent):
        bar = tk.Frame(parent, bg=C["nav"], pady=5)
        bar.grid(row=2, column=0, sticky="ew")
        bar.columnconfigure(0, weight=1)

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(bar, textvariable=self.status_var,
                 bg=C["nav"], fg="#94a3b8",
                 font=("Segoe UI", 9), padx=14).grid(row=0, column=0, sticky="w")

        self.clock_var = tk.StringVar()
        tk.Label(bar, textvariable=self.clock_var,
                 bg=C["nav"], fg="#475569",
                 font=("Segoe UI", 9), padx=14).grid(row=0, column=1, sticky="e")

    # ─────────────────────────────────────────────────────────────────────────
    # LIVE LOGS TAB  (embedded in notebook — no popup)
    # ─────────────────────────────────────────────────────────────────────────
    def _build_log_tab(self):
        """Build the Live Logs panel directly inside the notebook tab."""
        tab = self.log_tab

        # ── Header / control bar ─────────────────────────────────────────────
        tbar = tk.Frame(tab, bg="#1f2937", pady=10, padx=16)
        tbar.pack(fill="x")
        tbar.columnconfigure(0, weight=1)

        tk.Label(tbar, text="  ⚡  Live Validation Log",
                 bg="#1f2937", fg="#f9fafb",
                 font=("Segoe UI", 13, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(tbar,
                 text="Real-time results stream — updates automatically during validation",
                 bg="#1f2937", fg="#6b7280",
                 font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w")

        btn_row = tk.Frame(tbar, bg="#1f2937")
        btn_row.grid(row=0, column=1, rowspan=2, sticky="e")

        self._autoscroll_btn = tk.Button(
            btn_row, text="  Auto-scroll  ON",
            bg="#2563eb", fg="#ffffff",
            activebackground="#1d4ed8", activeforeground="#ffffff",
            relief="flat", bd=0, padx=12, pady=6,
            font=("Segoe UI", 9, "bold"), cursor="hand2",
            command=self._toggle_autoscroll)
        self._autoscroll_btn.pack(side="left", padx=(0, 6))

        tk.Button(btn_row, text="  Clear",
                  bg="#374151", fg="#e5e7eb",
                  activebackground="#4b5563", activeforeground="#ffffff",
                  relief="flat", bd=0, padx=12, pady=6,
                  font=("Segoe UI", 9), cursor="hand2",
                  command=self._clear_live_logs).pack(side="left", padx=(0, 6))

        tk.Button(btn_row, text="  Export Log",
                  bg="#374151", fg="#e5e7eb",
                  activebackground="#4b5563", activeforeground="#ffffff",
                  relief="flat", bd=0, padx=12, pady=6,
                  font=("Segoe UI", 9), cursor="hand2",
                  command=self._export_live_logs).pack(side="left")

        # ── Live counter tiles ───────────────────────────────────────────────
        cbar = tk.Frame(tab, bg=C["log_panel"], pady=8, padx=12)
        cbar.pack(fill="x")

        tile_defs = [
            ("Total",      "total",       "#8b949e", "#21262d"),
            ("Valid",      "valid",       "#3fb950", "#0e2a1a"),
            ("Invalid",    "invalid",     "#f85149", "#2a0e0e"),
            ("Delivered",  "deliverable", "#58a6ff", "#0e1e2a"),
            ("Catch-all",  "catchall",    "#d29922", "#2a240e"),
            ("Disposable", "disposable",  "#bc8cff", "#1e0e2a"),
        ]
        self._live_count_labels = {}
        for col, (label, key, color, bg) in enumerate(tile_defs):
            cell = tk.Frame(cbar, bg=bg, padx=14, pady=6,
                            highlightbackground=C["log_border"],
                            highlightthickness=1)
            cell.grid(row=0, column=col, padx=3, sticky="ew")
            cbar.columnconfigure(col, weight=1)
            tk.Label(cell, text=label, bg=bg, fg="#6b7280",
                     font=("Segoe UI", 8, "bold")).pack(anchor="w")
            lbl = tk.Label(cell, text="0", bg=bg, fg=color,
                           font=("Segoe UI", 20, "bold"))
            lbl.pack(anchor="w")
            self._live_count_labels[key] = lbl

        # ── Log text area ────────────────────────────────────────────────────
        log_frame = tk.Frame(tab, bg=C["log_bg"])
        log_frame.pack(fill="both", expand=True)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.live_log_text = tk.Text(
            log_frame, font=("Consolas", 10),
            bg=C["log_bg"], fg=C["log_fg"],
            wrap=tk.NONE, relief="flat",
            padx=14, pady=10,
            insertbackground=C["log_fg"],
            selectbackground="#264f78",
            state="disabled")

        vsb = ttk.Scrollbar(log_frame, orient="vertical",
                            command=self.live_log_text.yview)
        hsb = ttk.Scrollbar(log_frame, orient="horizontal",
                            command=self.live_log_text.xview)
        self.live_log_text.configure(yscrollcommand=vsb.set,
                                      xscrollcommand=hsb.set)
        self.live_log_text.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Syntax colour tags (GitHub Dark terminal palette)
        self.live_log_text.tag_config("ts",         foreground="#484f58")
        self.live_log_text.tag_config("info",       foreground="#58a6ff")
        self.live_log_text.tag_config("success",    foreground="#3fb950")
        self.live_log_text.tag_config("error",      foreground="#f85149")
        self.live_log_text.tag_config("warning",    foreground="#d29922")
        self.live_log_text.tag_config("warn",       foreground="#d29922")
        self.live_log_text.tag_config("header",     foreground="#f0f6fc",
                                      font=("Consolas", 10, "bold"))
        self.live_log_text.tag_config("detail",     foreground="#6e7681")
        self.live_log_text.tag_config("catchall",   foreground="#d29922")
        self.live_log_text.tag_config("disposable", foreground="#bc8cff")
        self.live_log_text.tag_config("sep",        foreground="#21262d")

        # ── Status bar ───────────────────────────────────────────────────────
        sbar = tk.Frame(tab, bg="#21262d", pady=5, padx=14)
        sbar.pack(fill="x")
        self._log_status_var = tk.StringVar(value="Waiting for validation to start…")
        tk.Label(sbar, textvariable=self._log_status_var,
                 bg="#21262d", fg="#6e7681", font=("Consolas", 9)).pack(side="left")

        # Initial message — written synchronously so theme rebuild cannot
        # produce a duplicate via the async root.after path in _log().
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.live_log_text.configure(state="normal")
        self.live_log_text.insert(tk.END, f"[{ts}]  ", "ts")
        self.live_log_text.insert(tk.END,
                                  "System ready — start validating to see live results.\n",
                                  "info")
        self.live_log_text.configure(state="disabled")

    # ─────────────────────────────────────────────────────────────────────────
    # LOG HELPERS
    # ─────────────────────────────────────────────────────────────────────────
    def _log(self, message, level="info"):
        def _do():
            if not self.live_log_text:
                return
            self.live_log_text.configure(state="normal")
            ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            self.live_log_text.insert(tk.END, f"[{ts}]  ", "ts")
            self.live_log_text.insert(tk.END, f"{message}\n", level)
            if self.log_autoscroll:
                self.live_log_text.see(tk.END)
            self.live_log_text.configure(state="disabled")
            if self._log_status_var:
                self._log_status_var.set(message[:100])
        self.root.after(0, _do)

    def _log_separator(self):
        def _do():
            if not self.live_log_text:
                return
            self.live_log_text.configure(state="normal")
            self.live_log_text.insert(tk.END, "─" * 110 + "\n", "sep")
            if self.log_autoscroll:
                self.live_log_text.see(tk.END)
            self.live_log_text.configure(state="disabled")
        self.root.after(0, _do)

    def _log_result_block(self, result):
        email       = result.get("email", "?")
        is_valid    = result.get("is_valid", False)
        deliverable = result.get("deliverable", False)
        confidence  = result.get("confidence", 0)
        smtp_status = result.get("smtp_status", "not_checked")
        is_catch    = result.get("is_catchall")   # may be None
        is_disp     = result.get("is_disposable", False)
        is_role     = result.get("is_role_based", False)
        has_mx      = bool(result.get("mx_records"))
        has_spf     = result.get("has_spf", False)
        has_dkim    = result.get("has_dkim", False)
        vtime       = result.get("validation_time", 0)
        messages    = result.get("messages", [])

        smtp_skipped = smtp_status == "skipped"

        # Icon and colour based on real outcome
        if not is_valid:
            icon, level = "[INVALID]", "error"
            status_label = "INVALID — Bad syntax or domain"
        elif smtp_skipped:
            icon, level = "[?]     ", "warn"
            status_label = "DOMAIN OK — Mailbox UNVERIFIED (enable SMTP for real check)"
        elif deliverable and smtp_status == "confirmed":
            icon, level = "[PASS]  ", "success"
            status_label = "CONFIRMED DELIVERABLE"
        elif smtp_status == "quota_exceeded":
            icon, level = "[~]     ", "warn"
            status_label = "MAILBOX EXISTS — Currently full / over storage quota"
        elif smtp_status == "blocked":
            icon, level = "[~]     ", "warn"
            status_label = "LIKELY DELIVERABLE — Server blocked SMTP probe"
        elif smtp_status == "unreachable":
            icon, level = "[~]     ", "warn"
            status_label = "LIKELY DELIVERABLE — Mail servers unreachable (firewall/geo-block)"
        elif is_catch is True and not deliverable:
            # Catch-all: server accepted our probe but we can't verify this address
            icon, level = "[~]     ", "warn"
            status_label = "CATCH-ALL DOMAIN — Individual mailbox existence cannot be verified"
        elif smtp_status == "not_found":
            icon, level = "[FAIL]  ", "error"
            status_label = "NOT DELIVERABLE — Mailbox does not exist (SMTP 550)"
        else:
            icon, level = "[FAIL]  ", "error"
            status_label = "NOT DELIVERABLE — Mailbox does not exist"

        def _do():
            if not self.live_log_text:
                return
            self.live_log_text.configure(state="normal")
            ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            self.live_log_text.insert(tk.END, f"[{ts}]  ", "ts")
            self.live_log_text.insert(tk.END, f"{icon}  {email}\n", level)
            self.live_log_text.insert(tk.END,
                f"          Status     : {status_label}\n", level)
            self.live_log_text.insert(tk.END,
                f"          Confidence : {confidence:.1f}%   "
                f"SMTP: {smtp_status}   Time: {vtime:.2f}s\n", "detail")
            mx_cnt = len(result.get("mx_records", []))
            self.live_log_text.insert(tk.END,
                f"          MX={mx_cnt}  "
                f"SPF={'Yes' if has_spf else 'No'}  "
                f"DKIM={'Yes' if has_dkim else 'No'}", "detail")
            if is_catch is True:
                self.live_log_text.insert(tk.END, "  [CATCH-ALL]", "catchall")
            elif is_catch is None and not smtp_skipped:
                self.live_log_text.insert(tk.END, "  [CATCH-ALL: unknown]", "warn")
            if is_disp:
                self.live_log_text.insert(tk.END, "  [DISPOSABLE]", "disposable")
            if is_role:
                self.live_log_text.insert(tk.END, "  [ROLE-BASED]", "warn")
            self.live_log_text.insert(tk.END, "\n")
            for msg in messages:
                self.live_log_text.insert(tk.END, f"          > {msg}\n", "detail")
            if self.log_autoscroll:
                self.live_log_text.see(tk.END)
            self.live_log_text.configure(state="disabled")
        self.root.after(0, _do)

    def _update_live_counters(self):
        def _do():
            for key, lbl in self._live_count_labels.items():
                lbl.configure(text=str(self.live_counts[key]))
        self.root.after(0, _do)

    def _clear_live_logs(self):
        if self.live_log_text:
            self.live_log_text.configure(state="normal")
            self.live_log_text.delete("1.0", tk.END)
            self.live_log_text.configure(state="disabled")
        self.live_counts = {k: 0 for k in self.live_counts}
        self._update_live_counters()
        self._log("Logs cleared.", "info")

    def _toggle_autoscroll(self):
        self.log_autoscroll = not self.log_autoscroll
        if self._autoscroll_btn:
            if self.log_autoscroll:
                self._autoscroll_btn.configure(text="  Auto-scroll  ON",
                                               bg=C["accent"])
            else:
                self._autoscroll_btn.configure(text="  Auto-scroll  OFF",
                                               bg="#374151")

    def _export_live_logs(self):
        if not self.live_log_text:
            return
        fn = filedialog.asksaveasfilename(title="Export Live Logs",
                                           defaultextension=".txt",
                                           filetypes=[("Text", "*.txt"),
                                                      ("All", "*.*")])
        if not fn:
            return
        try:
            with open(fn, "w", encoding="utf-8") as f:
                f.write(self.live_log_text.get("1.0", tk.END))
            self._append_audit(f"Logs exported: {os.path.basename(fn)}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    # ─────────────────────────────────────────────────────────────────────────
    # CLOCK / STATUS
    # ─────────────────────────────────────────────────────────────────────────
    def _tick_clock(self):
        self.clock_var.set(datetime.now().strftime("  %Y-%m-%d   %H:%M:%S  "))
        self.root.after(1000, self._tick_clock)

    def _set_status(self, msg):
        self.status_var.set(f"  {msg}")

    def _append_audit(self, msg):
        # Activity panel has been removed — guard to avoid AttributeError
        if not hasattr(self, "audit_feed"):
            return
        ts = datetime.now().strftime("%H:%M:%S")
        self.audit_feed.configure(state="normal")
        self.audit_feed.insert("1.0", f"[{ts}]  {msg}\n")
        self.audit_feed.configure(state="disabled")

    # ─────────────────────────────────────────────────────────────────────────
    # KPI UPDATE
    # ─────────────────────────────────────────────────────────────────────────
    def _update_kpis(self):
        n     = len(self.validation_results)
        valid = sum(1 for r in self.validation_results if r.get("is_valid"))
        deliv = sum(1 for r in self.validation_results if r.get("deliverable"))
        avg   = (sum(r.get("confidence", 0) for r in self.validation_results) / n) if n else 0
        self.kpi_labels["total"].configure(text=str(n))
        self.kpi_labels["valid"].configure(text=str(valid))
        self.kpi_labels["deliverable"].configure(text=str(deliv))
        self.kpi_labels["confidence"].configure(text=f"{avg:.1f}%")

    def _refresh_dashboard(self):
        self.recent_table.delete(*self.recent_table.get_children())
        for r in self.recent_results:
            is_valid  = r.get("is_valid")
            is_catch  = r.get("is_catchall")
            smtp_s    = r.get("smtp_status", "-")
            deliv     = r.get("deliverable", False)
            if not is_valid:
                status = "Invalid"
            elif smtp_s == "skipped":
                status = "Unverified"
            elif smtp_s == "confirmed" and deliv:
                status = "Confirmed"
            elif smtp_s == "quota_exceeded":
                status = "Mailbox Full"
            elif smtp_s in ("blocked", "unreachable"):
                status = "Likely Deliverable"
            elif is_catch and not deliv:
                status = "Catch-all"
            elif smtp_s == "not_found":
                status = "Not Found"
            elif deliv:
                status = "Deliverable"
            else:
                status = "Not Deliverable"
            conf   = f"{r.get('confidence', 0):.1f}%"
            mx_cnt = len(r.get("mx_records", []))
            t      = f"{r.get('validation_time', 0):.2f}"
            flags  = []
            if r.get("is_disposable"):  flags.append("Disposable")
            if r.get("is_role_based"):  flags.append("Role-based")
            if is_catch:                flags.append("Catch-all")
            if smtp_s == "skipped":     flags.append("SMTP Off")
            if smtp_s == "unreachable": flags.append("Unreachable")
            if smtp_s == "quota_exceeded": flags.append("Full Inbox")
            if not is_valid:
                tag = "invalid"
            elif smtp_s in ("skipped", "blocked", "unreachable", "quota_exceeded") or is_catch:
                tag = "warn"
            elif deliv and smtp_s == "confirmed":
                tag = "valid"
            else:
                tag = "invalid"
            self.recent_table.insert("", "end", tags=(tag,),
                values=(r.get("email", ""), status, conf, smtp_s, mx_cnt,
                        " | ".join(flags), t))
        self._update_kpis()

    # ─────────────────────────────────────────────────────────────────────────
    # SINGLE VALIDATION
    # ─────────────────────────────────────────────────────────────────────────
    def validate_single_email(self):
        email = self.single_email_entry.get().strip()
        if not email:
            messagebox.showwarning("Input Required", "Please enter an email address.")
            return

        self.single_validate_btn.configure(state="disabled",
                                            text="  Validating…  ")
        self._set_status(f"Validating  {email}…")
        # Switch to Live Logs tab so user sees progress immediately
        self.notebook.select(4)

        def task():
            self._log(f"Validating: {email}", "info")
            self._log_separator()
            result = self.validator.validate_email(email,
                                                   check_smtp=self.single_smtp_var.get())
            # counters
            self.live_counts["total"] += 1
            if result.get("is_valid"):      self.live_counts["valid"]       += 1
            else:                           self.live_counts["invalid"]     += 1
            if result.get("deliverable"):   self.live_counts["deliverable"] += 1
            if result.get("is_catchall"):   self.live_counts["catchall"]    += 1
            if result.get("is_disposable"): self.live_counts["disposable"]  += 1
            self._update_live_counters()
            self._log_result_block(result)
            self._log_separator()
            self._log(f"Done in {result.get('validation_time', 0):.2f}s", "success")

            self.validation_results.insert(0, result)
            self.recent_results.insert(0, result)
            self.recent_results = self.recent_results[:20]

            self.root.after(0, lambda: self._display_single_result(result))
            self.root.after(0, self._refresh_dashboard)
            self.root.after(0, lambda: self._append_audit(f"Validated: {email}"))
            self.root.after(0, lambda: self._set_status("Validation complete"))
            self.root.after(0, lambda: self.single_validate_btn.configure(
                state="normal", text="  Run Validation  "))

        threading.Thread(target=task, daemon=True).start()

    def _display_single_result(self, result):
        is_valid    = result.get("is_valid", False)
        deliverable = result.get("deliverable", False)
        confidence  = result.get("confidence", 0)
        smtp_status = result.get("smtp_status", "not_checked")
        is_catch    = result.get("is_catchall", False)
        is_disp     = result.get("is_disposable", False)
        has_mx      = bool(result.get("mx_records"))
        has_spf     = result.get("has_spf", False)
        has_dkim    = result.get("has_dkim", False)
        vtime       = result.get("validation_time", 0)
        mx_list     = result.get("mx_records", [])

        # ── Left panel: status cards ─────────────────────────────────────────
        self._status_placeholder.pack_forget()
        for w in self._status_frame.winfo_children():
            w.destroy()

        self._status_frame.pack(fill="both", expand=True)

        # Overall verdict card
        smtp_skipped = smtp_status == "skipped"
        if not is_valid:
            verdict_color, verdict_bg = C["red"],    C["red_bg"]
            verdict_text = "INVALID EMAIL"
        elif deliverable and smtp_status == "confirmed":
            verdict_color, verdict_bg = C["green"],  C["green_bg"]
            verdict_text = "VALID & DELIVERABLE"
        elif smtp_skipped:
            verdict_color, verdict_bg = C["yellow"], C["yellow_bg"]
            verdict_text = "DOMAIN VALID  —  MAILBOX UNVERIFIED"
        elif smtp_status == "quota_exceeded":
            verdict_color, verdict_bg = C["yellow"], C["yellow_bg"]
            verdict_text = "MAILBOX EXISTS  —  FULL / OVER QUOTA"
        elif smtp_status == "blocked":
            verdict_color, verdict_bg = C["yellow"], C["yellow_bg"]
            verdict_text = "LIKELY VALID  —  SERVER BLOCKED SMTP"
        elif smtp_status == "unreachable":
            verdict_color, verdict_bg = C["yellow"], C["yellow_bg"]
            verdict_text = "LIKELY VALID  —  MAIL SERVERS UNREACHABLE"
        elif is_catch:
            verdict_color, verdict_bg = C["yellow"], C["yellow_bg"]
            verdict_text = "CATCH-ALL DOMAIN  —  MAILBOX UNVERIFIABLE"
        else:
            verdict_color, verdict_bg = C["red"],    C["red_bg"]
            verdict_text = "NOT DELIVERABLE"
        verdict_card  = tk.Frame(self._status_frame, bg=verdict_bg,
                                 highlightbackground=verdict_color,
                                 highlightthickness=2)
        verdict_card.pack(fill="x", pady=(0, 8))
        tk.Frame(verdict_card, bg=verdict_color, height=5).pack(fill="x")
        vc_inner = tk.Frame(verdict_card, bg=verdict_bg, padx=16, pady=12)
        vc_inner.pack(fill="x")
        tk.Label(vc_inner, text=verdict_text, bg=verdict_bg, fg=verdict_color,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(vc_inner, text=result.get("email", ""),
                 bg=verdict_bg, fg=verdict_color,
                 font=("Segoe UI", 10)).pack(anchor="w")

        # Grid of check cards
        # Each entry: (label, state, display_value)
        # state: "ok" | "bad" | "warn"
        if smtp_skipped:
            deliv_state, deliv_val = "warn", "Not Checked"
            smtp_state,  smtp_val  = "warn", "Skipped"
        elif deliverable and smtp_status == "confirmed":
            deliv_state, deliv_val = "ok",   "Yes"
            smtp_state,  smtp_val  = "ok",   "Confirmed"
        elif smtp_status == "quota_exceeded":
            deliv_state, deliv_val = "warn", "Likely Yes"
            smtp_state,  smtp_val  = "warn", "Full Inbox"
        elif smtp_status == "blocked":
            deliv_state, deliv_val = "warn", "Likely"
            smtp_state,  smtp_val  = "warn", "Blocked"
        elif smtp_status == "unreachable":
            deliv_state, deliv_val = "warn", "Likely"
            smtp_state,  smtp_val  = "warn", "Unreachable"
        elif is_catch and not deliverable:
            deliv_state, deliv_val = "warn", "Unverifiable"
            smtp_state,  smtp_val  = "warn", "Catch-all"
        else:
            deliv_state, deliv_val = "bad",  "No"
            smtp_state,  smtp_val  = "bad",  smtp_status.replace("_", " ").title()

        checks = [
            ("Deliverable",  deliv_state, deliv_val),
            ("Confidence",   "ok" if confidence >= 70 else "warn" if confidence >= 40 else "bad",
                             f"{confidence:.1f}%"),
            ("SMTP Status",  smtp_state,  smtp_val),
            ("MX Records",   "ok"  if has_mx   else "bad",
                             f"{len(mx_list)} found" if has_mx else "None"),
            ("SPF Record",   "ok"  if has_spf  else "warn", "Present" if has_spf  else "Missing"),
            ("DKIM Record",  "ok"  if has_dkim else "warn", "Present" if has_dkim else "Missing"),
            ("Disposable",   "bad" if is_disp  else "ok",   "YES — DISPOSABLE" if is_disp else "Clean"),
            ("Catch-all",    "warn"if is_catch else "ok",   "YES" if is_catch else "No"),
        ]
        grid = tk.Frame(self._status_frame, bg=C["bg"])
        grid.pack(fill="both", expand=True)
        for col in range(2):
            grid.columnconfigure(col, weight=1)

        _state_colors = {
            "ok":   (C["green_bg"],  C["green"],  C["green_border"]),
            "bad":  (C["red_bg"],    C["red"],    C["red_border"]),
            "warn": (C["yellow_bg"], C["yellow"], C["yellow_border"]),
        }
        for idx, (label, state, val) in enumerate(checks):
            col = idx % 2
            row = idx // 2
            c_bg, c_fg, c_bd = _state_colors.get(state, _state_colors["warn"])
            c = tk.Frame(grid, bg=c_bg,
                         highlightbackground=c_bd, highlightthickness=1)
            c.grid(row=row, column=col, sticky="ew",
                   padx=(0 if col == 0 else 4, 4 if col == 0 else 0),
                   pady=3)
            inner = tk.Frame(c, bg=c_bg, padx=12, pady=8)
            inner.pack(fill="x")
            tk.Label(inner, text=label, bg=c_bg, fg=C["text2"],
                     font=("Segoe UI", 9)).pack(anchor="w")
            tk.Label(inner, text=val, bg=c_bg, fg=c_fg,
                     font=("Segoe UI", 12, "bold")).pack(anchor="w")

        # Time
        t_row = tk.Frame(self._status_frame, bg=C["bg"], padx=0, pady=6)
        t_row.pack(fill="x")
        tk.Label(t_row, text=f"Validation time: {vtime:.3f}s",
                 bg=C["bg"], fg=C["text3"],
                 font=("Segoe UI", 9)).pack(side="left")

        # ── Right panel: detail log ───────────────────────────────────────────
        self.single_result_box.configure(state="normal")
        self.single_result_box.delete("1.0", tk.END)

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.single_result_box.insert(tk.END,
            f"  ── Validation Report ─────────────────────────────────\n", "sep")
        self.single_result_box.insert(tk.END,
            f"  Email:    {result.get('email')}\n"
            f"  Time:     {ts}\n"
            f"  Duration: {vtime:.3f}s\n\n", "detail")

        _uncertain = smtp_status in ("blocked", "unreachable", "quota_exceeded")
        _catch_unverifiable = is_catch and not deliverable
        if smtp_skipped:
            deliv_display = "Skipped (enable SMTP)"
            deliv_ok      = False
            deliv_tag     = "warn"
        elif deliverable and smtp_status == "confirmed":
            deliv_display = "Yes — Confirmed"
            deliv_ok      = True
            deliv_tag     = None
        elif _uncertain or _catch_unverifiable:
            deliv_display = "Likely (unconfirmed)"
            deliv_ok      = True
            deliv_tag     = "warn"
        else:
            deliv_display = "No"
            deliv_ok      = False
            deliv_tag     = None

        _smtp_label_map = {
            "confirmed":      "confirmed ✓",
            "blocked":        "blocked (likely real)",
            "unreachable":    "unreachable (likely real)",
            "quota_exceeded": "quota exceeded (exists, full)",
            "not_found":      "not_found (550)",
            "skipped":        "skipped — enable SMTP",
            "error":          "error",
        }
        smtp_display = _smtp_label_map.get(smtp_status, smtp_status)
        smtp_ok      = smtp_status in ("confirmed", "quota_exceeded", "blocked", "unreachable")
        smtp_tag     = "warn" if (smtp_skipped or _uncertain or _catch_unverifiable) else None

        rows = [
            ("Syntax Valid",  str(result.get("syntax_valid", False)), result.get("syntax_valid", False), None),
            ("Domain Exists", str(has_mx),   has_mx,      None),
            ("Deliverable",   deliv_display, deliv_ok,    deliv_tag),
            ("Confidence",    f"{confidence:.1f}%", confidence >= 50, None),
            ("SMTP Status",   smtp_display,  smtp_ok,     smtp_tag),
            ("MX Records",    f"{len(mx_list)}", has_mx,  None),
            ("SPF Record",    str(has_spf),  has_spf,     None),
            ("DKIM Record",   str(has_dkim), has_dkim,    None),
            ("Disposable",    str(is_disp),  not is_disp, None),
            ("Catch-all",     str(is_catch), not is_catch,None),
        ]
        for k, v, ok, forced_tag in rows:
            self.single_result_box.insert(tk.END, f"  {k:<20}", "key")
            tag = forced_tag if forced_tag else ("ok" if ok else "bad")
            self.single_result_box.insert(tk.END, f"{v}\n", tag)

        if mx_list:
            self.single_result_box.insert(tk.END,
                f"\n  MX Hosts:\n", "key")
            for mx in mx_list[:5]:
                self.single_result_box.insert(tk.END,
                    f"    > {mx}\n", "neutral")

        self.single_result_box.insert(tk.END,
            f"\n  ── Validator Messages ──────────────────────────────\n", "sep")
        for msg in result.get("messages", []):
            self.single_result_box.insert(tk.END, f"  > {msg}\n", "neutral")

        self.single_result_box.configure(state="disabled")

    # ─────────────────────────────────────────────────────────────────────────
    # BATCH VALIDATION
    # ─────────────────────────────────────────────────────────────────────────
    def validate_bulk_emails(self):
        content = self.bulk_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Input Required", "Please enter or import email addresses.")
            return
        emails = [l.strip() for l in content.splitlines() if l.strip()]
        if not emails:
            messagebox.showwarning("No Emails", "No valid emails found.")
            return

        self.bulk_validate_btn.configure(state="disabled", text="  Processing…")
        self.bulk_table.delete(*self.bulk_table.get_children())
        self.bulk_progress["value"] = 0
        self.bulk_status_label.configure(text=f"Validating {len(emails)} emails…")
        self._set_status(f"Batch running: {len(emails)} emails…")

        # Switch to Live Logs tab to show real-time progress
        self.notebook.select(4)
        smtp_on = self.bulk_smtp_var.get()
        self._log_separator()
        self._log(
            f"Batch started — {len(emails)} emails   "
            f"SMTP={'ON' if smtp_on else 'OFF'}   Workers=6", "header")
        if not smtp_on:
            self._log(
                "  NOTE: SMTP is OFF — only syntax + domain will be checked.",
                "warning")
            self._log(
                "  Results show domain validity only, NOT mailbox existence.",
                "warning")
        self._log_separator()
        self.live_counts = {k: 0 for k in self.live_counts}
        self._update_live_counters()

        total_emails = len(emails)

        def on_progress(email, result, progress):
            self.live_counts["total"] += 1
            if result.get("is_valid"):      self.live_counts["valid"]       += 1
            else:                           self.live_counts["invalid"]     += 1
            if result.get("deliverable"):   self.live_counts["deliverable"] += 1
            if result.get("is_catchall"):   self.live_counts["catchall"]    += 1
            if result.get("is_disposable"): self.live_counts["disposable"]  += 1
            self._update_live_counters()

            done = self.live_counts["total"]
            self._log(f"[{done}/{total_emails}]  {int(progress)}%", "info")
            self._log_result_block(result)
            self.root.after(0, lambda: self._update_bulk_row(result, progress))

        def on_complete(results, stats):
            self.validation_results = results
            self.recent_results     = results[:20]
            self._log_separator()
            # Precise per-status counts
            n_domain_valid    = sum(1 for r in results if r.get("is_valid"))
            n_confirmed       = sum(1 for r in results if r.get("smtp_status") == "confirmed" and r.get("deliverable"))
            n_blocked         = sum(1 for r in results if r.get("smtp_status") == "blocked")
            n_unreachable     = sum(1 for r in results if r.get("smtp_status") == "unreachable")
            n_quota           = sum(1 for r in results if r.get("smtp_status") == "quota_exceeded")
            n_catchall        = sum(1 for r in results if r.get("is_catchall") and not r.get("deliverable"))
            n_not_found       = sum(1 for r in results if r.get("smtp_status") == "not_found")
            if smtp_on:
                self._log(
                    f"Batch complete   "
                    f"Total:{stats.get('total_emails',0)}   "
                    f"Confirmed:{n_confirmed}   "
                    f"Blocked:{n_blocked}   "
                    f"Unreachable:{n_unreachable}   "
                    f"Catch-all:{n_catchall}   "
                    f"Not Found:{n_not_found}"
                    + (f"   Quota Full:{n_quota}" if n_quota else "") +
                    f"   Avg:{stats.get('average_confidence',0):.1f}%   "
                    f"Speed:{stats.get('emails_per_second',0):.1f} e/s",
                    "success")
            else:
                self._log(
                    f"Batch complete   "
                    f"Total:{stats.get('total_emails',0)}   "
                    f"Domain Valid:{n_domain_valid}   "
                    f"Unverified:{n_domain_valid}   "
                    f"Avg:{stats.get('average_confidence',0):.1f}%",
                    "warning")
                self._log(
                    "  WARNING: SMTP was OFF — results show domain existence only.",
                    "warning")
                self._log(
                    "  Enable 'Enable SMTP' checkbox for mailbox-level verification.",
                    "warning")
            self._log_separator()
            self.root.after(0, self._refresh_dashboard)
            self.root.after(0, lambda: self.bulk_validate_btn.configure(
                state="normal", text="  Validate Batch"))
            self.root.after(0, lambda: self.bulk_status_label.configure(
                text=f"Done: {stats.get('total_emails',0)} emails validated"))
            self.root.after(0, lambda: self._append_audit(
                f"Batch done ({stats.get('total_emails',0)} emails)"))
            self.root.after(0, lambda: self._set_status("Batch validation complete"))

        threading.Thread(
            target=lambda: self.batch_processor.validate_batch(
                emails=emails,
                check_smtp=self.bulk_smtp_var.get(),
                on_progress=on_progress,
                on_complete=on_complete,
            ),
            daemon=True,
        ).start()

    def _update_bulk_row(self, result, progress):
        is_valid    = result.get("is_valid", False)
        is_catch    = result.get("is_catchall", False)
        smtp_st     = result.get("smtp_status", "-")
        deliverable = result.get("deliverable", False)
        # Status label — precise per smtp_status
        if not is_valid:
            status = "Invalid"
        elif smtp_st == "skipped":
            status = "Unverified"
        elif smtp_st == "confirmed" and deliverable:
            status = "Confirmed"
        elif smtp_st == "quota_exceeded":
            status = "Mailbox Full"
        elif smtp_st in ("blocked", "unreachable"):
            status = "Likely Deliverable"
        elif is_catch and not deliverable:
            status = "Catch-all"
        elif smtp_st == "not_found":
            status = "Not Found"
        elif deliverable:
            status = "Deliverable"
        else:
            status = "Not Deliverable"
        conf        = f"{result.get('confidence', 0):.1f}%"
        mx_cnt      = len(result.get("mx_records", []))
        t           = f"{result.get('validation_time', 0):.2f}"
        flags       = []
        if result.get("is_disposable"): flags.append("Disposable")
        if result.get("is_role_based"): flags.append("Role-based")
        if is_catch:                    flags.append("Catch-all")
        if smtp_st == "skipped":        flags.append("SMTP Off")
        if smtp_st == "unreachable":    flags.append("Unreachable")
        if smtp_st == "quota_exceeded": flags.append("Full Inbox")
        # Row colour — green only for confirmed; yellow for uncertain; red for failures
        if not is_valid:
            tag = "invalid"
        elif smtp_st in ("skipped", "blocked", "unreachable", "quota_exceeded") or is_catch:
            tag = "warn"
        elif deliverable and smtp_st == "confirmed":
            tag = "valid"
        else:
            tag = "invalid"
        self.bulk_table.insert("", "end", tags=(tag,),
            values=(result.get("email", ""), status, conf, smtp_st,
                    mx_cnt, " | ".join(flags), t))
        self.bulk_progress["value"] = progress
        self.bulk_status_label.configure(
            text=f"{int(progress)}%   Last: {result.get('email', '')}")

    # ─────────────────────────────────────────────────────────────────────────
    # REPORTS
    # ─────────────────────────────────────────────────────────────────────────
    def generate_report(self):
        if not self.validation_results:
            messagebox.showwarning("No Data", "Validate some emails first.")
            return
        self.report_generate_btn.configure(state="disabled", text="  Generating…")
        self._set_status("Generating report…")

        def task():
            try:
                report = self.reporter.generate_full_report(
                    self.validation_results, title="Power Email Validation Report")
                self.root.after(0, lambda: self._render_report(report))
                self.root.after(0, lambda: self._append_audit("Report generated"))
                self.root.after(0, lambda: self._set_status("Report ready"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            finally:
                self.root.after(0, lambda: self.report_generate_btn.configure(
                    state="normal", text="  Generate Report"))

        threading.Thread(target=task, daemon=True).start()

    def _render_report(self, report):
        summary = report.get("summary", {})
        recs    = report.get("recommendations", [])
        gen_at  = report.get("metadata", {}).get("generated_at", "")

        # ── Left: summary stat cards ─────────────────────────────────────────
        for w in self._report_cards_host.winfo_children():
            w.destroy()

        stat_defs = [
            ("Total Emails",   summary.get("total_emails", 0),  C["accent"]),
            ("Valid",          summary.get("valid_emails", 0),   C["green"]),
            ("Deliverable",    summary.get("deliverable", 0),    C["teal"]),
            ("Quality Score",  f"{summary.get('quality_score', 0):.1f}%", C["purple"]),
            ("Avg Confidence", f"{summary.get('avg_confidence', 0):.1f}%", C["yellow"]),
            ("Disposable",     summary.get("disposable", 0),     C["red"]),
        ]
        for i, (label, val, color) in enumerate(stat_defs):
            c = tk.Frame(self._report_cards_host, bg=C["surface"],
                         highlightbackground=C["border"], highlightthickness=1)
            c.pack(fill="x", pady=3)
            tk.Frame(c, bg=color, height=3).pack(fill="x")
            inner = tk.Frame(c, bg=C["surface"], padx=14, pady=8)
            inner.pack(fill="x")
            inner.columnconfigure(0, weight=1)
            tk.Label(inner, text=label, bg=C["surface"], fg=C["text2"],
                     font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w")
            tk.Label(inner, text=str(val), bg=C["surface"], fg=color,
                     font=("Segoe UI", 16, "bold")).grid(row=1, column=0, sticky="w")

        # ── Right: full text ─────────────────────────────────────────────────
        self.report_summary.configure(state="normal")
        self.report_summary.delete("1.0", tk.END)
        self.report_summary.insert(tk.END,
            f"  Power Email Validation Report\n"
            f"  Generated: {gen_at}\n"
            f"  {'─'*60}\n\n")
        self.report_summary.insert(tk.END, "  SUMMARY\n")
        for k, v in summary.items():
            self.report_summary.insert(tk.END, f"    {k:<28} {v}\n")
        self.report_summary.insert(tk.END, f"\n  {'─'*60}\n")
        self.report_summary.insert(tk.END, "  RECOMMENDATIONS\n")
        for rec in recs:
            self.report_summary.insert(tk.END, f"    • {rec}\n")
        self.report_summary.configure(state="disabled")

        self.report_metadata.configure(
            text=f"Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def export_report(self, fmt="txt"):
        self.report_summary.configure(state="normal")
        text = self.report_summary.get("1.0", tk.END).strip()
        self.report_summary.configure(state="disabled")
        if not text:
            messagebox.showwarning("No Report", "Generate a report first.")
            return
        ext = ".json" if fmt == "json" else ".txt"
        fn = filedialog.asksaveasfilename(title="Export Report",
                                          defaultextension=ext,
                                          filetypes=[(f"{ext.upper()[1:]} Files", f"*{ext}")])
        if not fn:
            return
        try:
            with open(fn, "w", encoding="utf-8") as f:
                if fmt == "json":
                    json.dump({"report": text,
                               "results": self.validation_results}, f, indent=2)
                else:
                    f.write(text)
            self._append_audit(f"Report exported: {os.path.basename(fn)}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    # ─────────────────────────────────────────────────────────────────────────
    # IMPORT / EXPORT
    # ─────────────────────────────────────────────────────────────────────────
    def import_emails(self):
        fn = filedialog.askopenfilename(
            title="Import Email Data",
            filetypes=[("Supported", "*.txt *.csv *.xls *.xlsx"), ("All", "*.*")])
        if not fn:
            return
        ext = os.path.splitext(fn)[1].lower()
        self.source_file_path = fn
        self.source_file_ext  = ext
        self.source_rows      = []
        self.source_columns   = []
        try:
            if ext == ".txt":
                with open(fn, "r", encoding="utf-8") as f:
                    lines = [l.strip() for l in f if l.strip()]
                self.source_columns = ["email"]
                self.source_rows    = [{"email": l} for l in lines]
            elif ext == ".csv":
                df = pd.read_csv(fn, dtype=str).fillna("")
                self.source_columns = list(df.columns)
                self.source_rows    = df.to_dict(orient="records")
            elif ext in (".xls", ".xlsx"):
                xls = pd.ExcelFile(fn)
                sheet = xls.sheet_names[0]
                self.selected_sheet_name = sheet
                df = pd.read_excel(fn, sheet_name=sheet, dtype=str).fillna("")
                self.source_columns = list(df.columns)
                self.source_rows    = df.to_dict(orient="records")
            else:
                raise ValueError("Unsupported file type")

            if not self.source_rows:
                messagebox.showwarning("No Data", "File loaded but empty.")
                return

            selected = self._open_column_mapper_dialog(self.source_columns)
            if not selected:
                return
            self.selected_email_column = selected
            emails = [str(r.get(selected, "")).strip() for r in self.source_rows]
            emails = [e for e in emails if e]

            self.bulk_text.delete("1.0", tk.END)
            self.bulk_text.insert(tk.END, "\n".join(emails))
            self._append_audit(
                f"Imported {len(emails)} rows from {os.path.basename(fn)}")
            self._set_status(f"Imported {len(emails)} records")
        except Exception as e:
            messagebox.showerror("Import Error", str(e))

    def export_results(self):
        if not self.validation_results:
            messagebox.showwarning("No Results", "No validation results to export.")
            return
        by_email = {}
        for r in self.validation_results:
            k = str(r.get("email", "")).strip().lower()
            if k and k not in by_email:
                by_email[k] = r

        if self.source_file_path and self.source_rows:
            base, ext = os.path.splitext(self.source_file_path)
            out = f"{base}_validated{ext}"
            try:
                enriched = []
                for row in self.source_rows:
                    rc  = dict(row)
                    ev  = str(rc.get(self.selected_email_column or "email", "")).strip().lower()
                    res = by_email.get(ev, {})
                    rc["pev_valid"]      = res.get("is_valid", False)
                    rc["pev_deliverable"]= res.get("deliverable", False)
                    rc["pev_confidence"] = res.get("confidence", 0)
                    rc["pev_smtp"]       = res.get("smtp_status", "")
                    rc["pev_messages"]   = " | ".join(res.get("messages", []))
                    enriched.append(rc)
                if ext == ".txt":
                    with open(out, "w", encoding="utf-8") as f:
                        for r in enriched:
                            e = str(r.get(self.selected_email_column or "email","")).strip()
                            f.write(f"{e} | valid={r['pev_valid']} | "
                                    f"deliverable={r['pev_deliverable']} | "
                                    f"confidence={r['pev_confidence']}\n")
                elif ext == ".csv":
                    pd.DataFrame(enriched).to_csv(out, index=False)
                else:
                    pd.DataFrame(enriched).to_excel(out, index=False)
                self._append_audit(f"Exported: {os.path.basename(out)}")
                self._set_status("Results exported")
                messagebox.showinfo("Export OK", f"Saved:\n{out}")
                return
            except Exception as e:
                messagebox.showerror("Export Error", str(e))

        # fallback
        fn = filedialog.asksaveasfilename(title="Export Results",
                                          defaultextension=".csv",
                                          filetypes=[("CSV","*.csv"),
                                                     ("JSON","*.json"),
                                                     ("Text","*.txt")])
        if not fn:
            return
        try:
            if fn.endswith(".json"):
                with open(fn, "w", encoding="utf-8") as f:
                    json.dump({"results": self.validation_results}, f, indent=2)
            elif fn.endswith(".csv"):
                csv_text = self.reporter.export_to_csv(self.validation_results)
                with open(fn, "w", encoding="utf-8", newline="") as f:
                    f.write(csv_text)
            else:
                with open(fn, "w", encoding="utf-8") as f:
                    for r in self.validation_results:
                        f.write(f"{r.get('email','')} | "
                                f"valid={r.get('is_valid')} | "
                                f"deliverable={r.get('deliverable')} | "
                                f"confidence={r.get('confidence',0):.1f}%\n")
            self._append_audit(f"Exported: {os.path.basename(fn)}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    # ─────────────────────────────────────────────────────────────────────────
    # COLUMN MAPPER DIALOG
    # ─────────────────────────────────────────────────────────────────────────
    def _open_column_mapper_dialog(self, columns):
        lc  = [str(c).strip().lower() for c in columns]
        pref = columns[0]
        for cand in ("email", "email_address", "mail", "e-mail", "contact_email"):
            if cand in lc:
                pref = columns[lc.index(cand)]
                break

        dlg = tk.Toplevel(self.root)
        dlg.title("Select Email Column")
        dlg.geometry("480x180")
        dlg.configure(bg=C["surface"])
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(dlg, text="Select the column that contains email addresses:",
                 bg=C["surface"], fg=C["text"],
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=18, pady=(18, 6))

        sel_var = tk.StringVar(value=str(pref))
        ttk.Combobox(dlg, textvariable=sel_var,
                     values=[str(c) for c in columns],
                     state="readonly", width=52).pack(anchor="w", padx=18)

        result = {"value": None}

        def confirm():
            result["value"] = sel_var.get().strip()
            dlg.destroy()

        btn_row = tk.Frame(dlg, bg=C["surface"])
        btn_row.pack(fill="x", padx=18, pady=(16, 12))
        self._btn(btn_row, "Cancel",  "#e2e8f0", C["text"], dlg.destroy).pack(side="right")
        self._btn(btn_row, "Confirm", C["accent"], "#ffffff", confirm).pack(
            side="right", padx=(0, 8))

        self.root.wait_window(dlg)
        return result["value"]

    # ─────────────────────────────────────────────────────────────────────────
    # UI UTILITIES
    # ─────────────────────────────────────────────────────────────────────────
    def _btn(self, parent, text, bg, fg, command, bold=False):
        return tk.Button(parent, text=text, bg=bg, fg=fg,
                         activebackground=bg, activeforeground=fg,
                         relief="flat", bd=0, padx=14, pady=7,
                         font=("Segoe UI", 10, "bold") if bold else ("Segoe UI", 10),
                         cursor="hand2", command=command)

    def _section_label(self, parent, text):
        f = tk.Frame(parent, bg=parent.cget("bg"))
        tk.Frame(f, bg=C["accent"], width=4, height=20).pack(side="left", padx=(0, 8))
        tk.Label(f, text=text, bg=parent.cget("bg"), fg=C["text"],
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        return f


# ─────────────────────────────────────────────────────────────────────────────
def main():
    root = tk.Tk()
    EmailValidatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
