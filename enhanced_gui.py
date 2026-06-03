"""
Power Email Validation - Enterprise GUI
Enterprise layout with dashboard, queue manager, audit logs, and reports.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
from advanced_email_validator import AdvancedEmailValidator
import csv
import json
from datetime import datetime
from PIL import Image, ImageTk
import os


class ToolTip:
    """Simple tooltip for Tkinter widgets."""

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show)
        self.widget.bind("<Leave>", self.hide)

    def show(self, _event=None):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self.text,
            justify='left',
            background='#1f2a44',
            foreground='white',
            relief='solid',
            borderwidth=1,
            font=('Segoe UI', 8),
            padx=6,
            pady=4
        )
        label.pack()

    def hide(self, _event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class EnhancedEmailValidatorGUI:
    """Enterprise GUI with dashboard, queue manager, and audit logging."""

    TRUSTED_DOMAINS = {"umaxbooks.com"}

    def __init__(self, root):
        self.root = root
        self.root.title("Power Email Validation - Enterprise")
        self.root.geometry("1100x650")

        self.colors = {
            'bg': '#f4f6f8',
            'panel': '#ffffff',
            'border': '#e5e7eb',
            'primary': '#1f2a44',
            'secondary': '#2f3b52',
            'accent': '#3b82f6',
            'text': '#1f2937',
            'muted': '#6b7280',
            'success': '#16a34a',
            'warning': '#f59e0b',
            'danger': '#dc2626'
        }

        self.root.configure(bg=self.colors['bg'])

        self.validator = AdvancedEmailValidator(timeout=10)
        self.validation_results = []
        self.is_validating = False
        self.queue = []
        self.queue_running = False
        self.trusted_domains = set(self.TRUSTED_DOMAINS)

        self.create_widgets()

    def create_widgets(self):
        self.build_topbar()
        self.build_layout()
        self.build_dashboard()
        self.build_validation_view()
        self.build_results_view()
        self.build_reports_view()
        self.build_audit_view()
        self.build_settings_view()
        self.show_view('Dashboard')
        self.log_message("Application started", "info")

    def build_topbar(self):
        topbar = tk.Frame(self.root, bg=self.colors['primary'], height=60)
        topbar.pack(fill='x')

        # Load and display logo
        logo_path = os.path.join(os.path.dirname(__file__), 'UmaxBooks-Logo.png')
        if os.path.exists(logo_path):
            try:
                logo_img = Image.open(logo_path)
                # Resize logo to fit topbar (height: 45px, maintain aspect ratio)
                ratio = 45 / logo_img.height
                new_width = int(logo_img.width * ratio)
                logo_img = logo_img.resize((new_width, 45), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                logo_container = tk.Frame(
                    topbar,
                    bg=self.colors['panel'],
                    highlightbackground=self.colors['border'],
                    highlightcolor=self.colors['border'],
                    highlightthickness=1,
                    padx=4,
                    pady=2
                )
                logo_container.pack(side='left', padx=12, pady=8)
                logo_label = tk.Label(
                    logo_container,
                    image=self.logo_photo,
                    bg=self.colors['panel']
                )
                logo_label.pack()
            except Exception as e:
                print(f"Error loading logo: {e}")

        title = tk.Label(
            topbar,
            text="Power Email Validation",
            font=('Segoe UI', 16, 'bold'),
            bg=self.colors['primary'],
            fg='white'
        )
        title.pack(side='left', padx=20)

        role_label = tk.Label(
            topbar,
            text="Role:",
            font=('Segoe UI', 9),
            bg=self.colors['primary'],
            fg='white'
        )
        role_label.pack(side='right', padx=(0, 6))

        self.role_var = tk.StringVar(value="Admin")
        self.role_combo = ttk.Combobox(
            topbar,
            textvariable=self.role_var,
            values=["Admin", "Operator"],
            width=12,
            state='readonly'
        )
        self.role_combo.pack(side='right', padx=(10, 10))
        self.role_combo.bind("<<ComboboxSelected>>", self.apply_role_permissions)

        # Process control buttons
        controls_frame = tk.Frame(topbar, bg=self.colors['primary'])
        controls_frame.pack(side='right', padx=(0, 20))

        self.process_start_btn = tk.Button(
            controls_frame,
            text="▶ Start",
            command=self.start_queue,
            bg='#16a34a',
            fg='white',
            relief='flat',
            font=('Segoe UI', 8),
            padx=6,
            pady=4
        )
        self.process_start_btn.pack(side='left', padx=4)

        self.process_pause_btn = tk.Button(
            controls_frame,
            text="⏸ Pause",
            command=self.pause_queue,
            bg='#f59e0b',
            fg='white',
            relief='flat',
            font=('Segoe UI', 8),
            padx=6,
            pady=4
        )
        self.process_pause_btn.pack(side='left', padx=4)

        self.process_stop_btn = tk.Button(
            controls_frame,
            text="⏹ Stop",
            command=self.stop_queue,
            bg='#dc2626',
            fg='white',
            relief='flat',
            font=('Segoe UI', 8),
            padx=6,
            pady=4
        )
        self.process_stop_btn.pack(side='left', padx=4)

    def build_layout(self):
        body = tk.Frame(self.root, bg=self.colors['bg'])
        body.pack(fill='both', expand=True)

        self.sidebar = tk.Frame(body, bg=self.colors['secondary'], width=180)
        self.sidebar.pack(side='left', fill='y')

        self.content = tk.Frame(body, bg=self.colors['bg'])
        self.content.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        self.views = {}

        buttons = [
            ("Dashboard", self.show_view),
            ("Validation", self.show_view),
            ("Results", self.show_view),
            ("Reports", self.show_view),
            ("Audit Log", self.show_view),
            ("Settings", self.show_view)
        ]

        for label, handler in buttons:
            btn = tk.Button(
                self.sidebar,
                text=label,
                command=lambda l=label: handler(l),
                bg=self.colors['secondary'],
                fg='white',
                relief='flat',
                anchor='w',
                padx=12,
                pady=8,
                font=('Segoe UI', 9)
            )
            btn.pack(fill='x')

    def build_dashboard(self):
        frame = tk.Frame(self.content, bg=self.colors['bg'])
        self.views['Dashboard'] = frame

        kpi_bar = tk.Frame(frame, bg=self.colors['bg'])
        kpi_bar.pack(fill='x')

        self.kpi_total = self.create_kpi(kpi_bar, "Total", "0")
        self.kpi_valid = self.create_kpi(kpi_bar, "Valid", "0")
        self.kpi_invalid = self.create_kpi(kpi_bar, "Invalid", "0")
        self.kpi_conf = self.create_kpi(kpi_bar, "Avg Confidence", "0%")

        mid = tk.Frame(frame, bg=self.colors['bg'])
        mid.pack(fill='both', expand=True, pady=8)

        queue_panel = tk.LabelFrame(
            mid,
            text="Queue Manager",
            bg=self.colors['panel'],
            fg=self.colors['text'],
            font=('Segoe UI', 9, 'bold'),
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['border'],
            highlightthickness=1,
            bd=0,
            padx=8,
            pady=8
        )
        queue_panel.pack(side='left', fill='both', expand=True, padx=(0, 8))

        self.queue_list = tk.Listbox(queue_panel, height=6)
        self.queue_list.pack(fill='both', expand=True)

        queue_controls = tk.Frame(queue_panel, bg=self.colors['panel'])
        queue_controls.pack(fill='x', pady=(6, 0))

        self.queue_start_btn = tk.Button(
            queue_controls,
            text="Start",
            command=self.start_queue,
            bg=self.colors['accent'],
            fg='white',
            relief='flat',
            font=('Segoe UI', 8),
            padx=4,
            pady=2
        )
        self.queue_start_btn.pack(side='left', padx=(0, 4))

        self.queue_pause_btn = tk.Button(
            queue_controls,
            text="Pause",
            command=self.pause_queue,
            bg=self.colors['secondary'],
            fg='white',
            relief='flat',
            font=('Segoe UI', 8),
            padx=4,
            pady=2
        )
        self.queue_pause_btn.pack(side='left', padx=(0, 4))

        self.queue_clear_btn = tk.Button(
            queue_controls,
            text="Clear",
            command=self.clear_queue,
            bg=self.colors['danger'],
            fg='white',
            relief='flat',
            font=('Segoe UI', 8),
            padx=4,
            pady=2
        )
        self.queue_clear_btn.pack(side='left')

        activity_panel = tk.LabelFrame(
            mid,
            text="Activity Feed",
            bg=self.colors['panel'],
            fg=self.colors['text'],
            font=('Segoe UI', 9, 'bold'),
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['border'],
            highlightthickness=1,
            bd=0,
            padx=8,
            pady=8
        )
        activity_panel.pack(side='left', fill='both', expand=True)

        self.activity_text = scrolledtext.ScrolledText(
            activity_panel,
            height=6,
            font=('Consolas', 8),
            bg='#0f172a',
            fg='#e2e8f0',
            relief='flat'
        )
        self.activity_text.pack(fill='both', expand=True)

    def build_validation_view(self):
        frame = tk.Frame(self.content, bg=self.colors['bg'])
        self.views['Validation'] = frame

        left = tk.Frame(frame, bg=self.colors['bg'])
        left.pack(side='left', fill='both', expand=True, padx=(0, 8))

        right = tk.Frame(frame, bg=self.colors['bg'])
        right.pack(side='left', fill='y')

        single_box = tk.LabelFrame(
            left,
            text="Single Validation",
            bg=self.colors['panel'],
            fg=self.colors['text'],
            font=('Segoe UI', 9, 'bold'),
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['border'],
            highlightthickness=1,
            bd=0,
            padx=8,
            pady=8
        )
        single_box.pack(fill='x', pady=(0, 8))

        tk.Label(single_box, text="Email", bg=self.colors['panel'], fg=self.colors['muted'], font=('Segoe UI', 8)).pack(anchor='w')
        self.email_entry = tk.Entry(single_box, font=('Segoe UI', 9))
        self.email_entry.pack(fill='x', pady=(3, 6))

        options_row = tk.Frame(single_box, bg=self.colors['panel'])
        options_row.pack(fill='x')

        self.smtp_check_var = tk.BooleanVar(value=False)
        self.smtp_check = tk.Checkbutton(
            options_row,
            text="Deep SMTP Check",
            variable=self.smtp_check_var,
            bg=self.colors['panel'],
            fg=self.colors['muted'],
            font=('Segoe UI', 8)
        )
        self.smtp_check.pack(side='left')
        ToolTip(
            self.smtp_check,
            "Connects to mail server to verify mailbox existence.\n"
            "Some providers block this check."
        )

        self.catchall_check_var = tk.BooleanVar(value=False)
        self.catchall_check = tk.Checkbutton(
            options_row,
            text="Detect Catch-all",
            variable=self.catchall_check_var,
            bg=self.colors['panel'],
            fg=self.colors['muted'],
            font=('Segoe UI', 8)
        )
        self.catchall_check.pack(side='left', padx=(8, 0))
        ToolTip(
            self.catchall_check,
            "Detects domains that accept all emails."
        )

        action_row = tk.Frame(single_box, bg=self.colors['panel'])
        action_row.pack(fill='x', pady=(6, 0))

        self.validate_btn = tk.Button(
            action_row,
            text="Validate",
            command=self.validate_single_email,
            bg=self.colors['accent'],
            fg='white',
            relief='flat',
            font=('Segoe UI', 8),
            padx=6,
            pady=2
        )
        self.validate_btn.pack(side='left', padx=(0, 4))

        self.queue_add_btn = tk.Button(
            action_row,
            text="Add to Queue",
            command=self.add_single_to_queue,
            bg=self.colors['secondary'],
            fg='white',
            relief='flat',
            font=('Segoe UI', 8),
            padx=6,
            pady=2
        )
        self.queue_add_btn.pack(side='left')

        bulk_box = tk.LabelFrame(
            left,
            text="Bulk Validation",
            bg=self.colors['panel'],
            fg=self.colors['text'],
            font=('Segoe UI', 9, 'bold'),
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['border'],
            highlightthickness=1,
            bd=0,
            padx=8,
            pady=8
        )
        bulk_box.pack(fill='both', expand=True)

        self.bulk_text = scrolledtext.ScrolledText(bulk_box, height=4, font=('Consolas', 8))
        self.bulk_text.pack(fill='both', expand=True)

        bulk_actions = tk.Frame(bulk_box, bg=self.colors['panel'])
        bulk_actions.pack(fill='x', pady=(6, 0))

        self.import_btn = tk.Button(
            bulk_actions,
            text="Import",
            command=self.import_emails,
            bg=self.colors['secondary'],
            fg='white',
            relief='flat',
            font=('Segoe UI', 8),
            padx=4,
            pady=2
        )
        self.import_btn.pack(side='left', padx=(0, 4))

        self.validate_bulk_btn = tk.Button(
            bulk_actions,
            text="Validate Bulk",
            command=self.validate_bulk_emails,
            bg=self.colors['accent'],
            fg='white',
            relief='flat',
            font=('Segoe UI', 8),
            padx=4,
            pady=2
        )
        self.validate_bulk_btn.pack(side='left', padx=(0, 4))

        self.bulk_queue_btn = tk.Button(
            bulk_actions,
            text="Queue Bulk",
            command=self.add_bulk_to_queue,
            bg=self.colors['secondary'],
            fg='white',
            relief='flat',
            font=('Segoe UI', 8),
            padx=4,
            pady=2
        )
        self.bulk_queue_btn.pack(side='left')

        template_box = tk.LabelFrame(
            right,
            text="Templates",
            bg=self.colors['panel'],
            fg=self.colors['text'],
            font=('Segoe UI', 9, 'bold'),
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['border'],
            highlightthickness=1,
            bd=0,
            padx=8,
            pady=8
        )
        template_box.pack(fill='x')

        self.template_var = tk.StringVar(value="Standard")
        self.template_combo = ttk.Combobox(
            template_box,
            textvariable=self.template_var,
            values=["Standard", "Deep SMTP", "MX Only"],
            state='readonly',
            font=('Segoe UI', 8)
        )
        self.template_combo.pack(fill='x')
        self.template_combo.bind("<<ComboboxSelected>>", self.apply_template)

        progress_box = tk.LabelFrame(
            right,
            text="Progress",
            bg=self.colors['panel'],
            fg=self.colors['text'],
            font=('Segoe UI', 9, 'bold'),
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['border'],
            highlightthickness=1,
            bd=0,
            padx=8,
            pady=8
        )
        progress_box.pack(fill='x', pady=(8, 0))

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_box, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill='x')
        self.progress_label = tk.Label(progress_box, text="Ready", bg=self.colors['panel'], fg=self.colors['muted'])
        self.progress_label.pack(anchor='w', pady=(6, 0))

    def build_results_view(self):
        frame = tk.Frame(self.content, bg=self.colors['bg'])
        self.views['Results'] = frame

        table_box = tk.LabelFrame(
            frame,
            text="Validation Results",
            bg=self.colors['panel'],
            fg=self.colors['text'],
            font=('Segoe UI', 10, 'bold'),
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['border'],
            highlightthickness=1,
            bd=0,
            padx=10,
            pady=10
        )
        table_box.pack(fill='both', expand=True)

        columns = ('Email', 'Status', 'Confidence', 'Deliverable', 'SMTP', 'Notes')
        self.results_tree = ttk.Treeview(table_box, columns=columns, show='headings', height=18)

        for col in columns:
            self.results_tree.heading(col, text=col)

        self.results_tree.column('Email', width=260)
        self.results_tree.column('Status', width=120)
        self.results_tree.column('Confidence', width=110)
        self.results_tree.column('Deliverable', width=110)
        self.results_tree.column('SMTP', width=120)
        self.results_tree.column('Notes', width=460)

        scrollbar = ttk.Scrollbar(table_box, orient='vertical', command=self.results_tree.yview)
        self.results_tree.configure(yscroll=scrollbar.set)
        self.results_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def build_reports_view(self):
        frame = tk.Frame(self.content, bg=self.colors['bg'])
        self.views['Reports'] = frame

        panel = tk.LabelFrame(
            frame,
            text="Export Center",
            bg=self.colors['panel'],
            fg=self.colors['text'],
            font=('Segoe UI', 10, 'bold'),
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['border'],
            highlightthickness=1,
            bd=0,
            padx=10,
            pady=10
        )
        panel.pack(fill='x')

        self.export_btn = tk.Button(
            panel,
            text="Export Results",
            command=self.export_results,
            bg=self.colors['accent'],
            fg='white',
            relief='flat'
        )
        self.export_btn.pack(side='left')

        summary = tk.LabelFrame(
            frame,
            text="Summary",
            bg=self.colors['panel'],
            fg=self.colors['text'],
            font=('Segoe UI', 10, 'bold'),
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['border'],
            highlightthickness=1,
            bd=0,
            padx=10,
            pady=10
        )
        summary.pack(fill='both', expand=True, pady=(12, 0))

        self.summary_text = scrolledtext.ScrolledText(summary, height=10, font=('Consolas', 9))
        self.summary_text.pack(fill='both', expand=True)

    def build_audit_view(self):
        frame = tk.Frame(self.content, bg=self.colors['bg'])
        self.views['Audit Log'] = frame

        panel = tk.LabelFrame(
            frame,
            text="Audit Log",
            bg=self.colors['panel'],
            fg=self.colors['text'],
            font=('Segoe UI', 10, 'bold'),
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['border'],
            highlightthickness=1,
            bd=0,
            padx=10,
            pady=10
        )
        panel.pack(fill='both', expand=True)

        self.logs_text = scrolledtext.ScrolledText(
            panel,
            font=('Consolas', 9),
            bg='#0f172a',
            fg='#e2e8f0',
            relief='flat'
        )
        self.logs_text.pack(fill='both', expand=True)

        self.logs_text.tag_config('info', foreground='#38bdf8')
        self.logs_text.tag_config('success', foreground='#4ade80')
        self.logs_text.tag_config('warning', foreground='#facc15')
        self.logs_text.tag_config('error', foreground='#f87171')
        self.logs_text.tag_config('timestamp', foreground='#94a3b8')

    def build_settings_view(self):
        frame = tk.Frame(self.content, bg=self.colors['bg'])
        self.views['Settings'] = frame

        panel = tk.LabelFrame(
            frame,
            text="Trusted Domains",
            bg=self.colors['panel'],
            fg=self.colors['text'],
            font=('Segoe UI', 10, 'bold'),
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['border'],
            highlightthickness=1,
            bd=0,
            padx=10,
            pady=10
        )
        panel.pack(fill='x')

        row = tk.Frame(panel, bg=self.colors['panel'])
        row.pack(fill='x', pady=(0, 8))

        self.trusted_entry = tk.Entry(row)
        self.trusted_entry.pack(side='left', fill='x', expand=True, padx=(0, 6))

        add_btn = tk.Button(
            row,
            text="Add",
            command=self.add_trusted_domain,
            bg=self.colors['accent'],
            fg='white',
            relief='flat'
        )
        add_btn.pack(side='left')

        self.trusted_list = tk.Listbox(panel, height=6)
        self.trusted_list.pack(fill='x')
        self.refresh_trusted_list()

    def show_view(self, name):
        for view in self.views.values():
            view.pack_forget()
        self.views[name].pack(fill='both', expand=True)

    def create_kpi(self, parent, label, value):
        card = tk.Frame(parent, bg=self.colors['panel'], padx=10, pady=8)
        card.pack(side='left', padx=(0, 8), fill='x', expand=True)

        tk.Label(card, text=label, bg=self.colors['panel'], fg=self.colors['muted'], font=('Segoe UI', 7)).pack(anchor='w')
        value_label = tk.Label(card, text=value, bg=self.colors['panel'], fg=self.colors['text'], font=('Segoe UI', 13, 'bold'))
        value_label.pack(anchor='w')
        return value_label

    def apply_role_permissions(self, _event=None):
        role = self.role_var.get()
        if role == 'Operator':
            self.export_btn.config(state='disabled')
            self.sidebar.winfo_children()[-1].config(state='disabled')
        else:
            self.export_btn.config(state='normal')
            self.sidebar.winfo_children()[-1].config(state='normal')

    def apply_template(self, _event=None):
        template = self.template_var.get()
        if template == 'Standard':
            self.smtp_check_var.set(False)
            self.catchall_check_var.set(False)
        elif template == 'Deep SMTP':
            self.smtp_check_var.set(True)
            self.catchall_check_var.set(False)
        elif template == 'MX Only':
            self.smtp_check_var.set(False)
            self.catchall_check_var.set(False)

    def log_message(self, msg, level='info'):
        ts = datetime.now().strftime("%H:%M:%S")
        prefix = {'success': 'OK', 'error': 'ERR', 'warning': 'WARN', 'info': 'INFO'}.get(level, 'INFO')
        line = f"[{ts}] {prefix} {msg}\n"

        self.logs_text.insert('end', line, level)
        self.logs_text.see('end')
        self.activity_text.insert('end', line)
        self.activity_text.see('end')

    def get_status_text(self, result):
        status_type = result.get('smtp_status', 'unknown')
        if status_type == 'confirmed':
            return "Confirmed"
        if status_type == 'trusted':
            return "Trusted"
        if status_type in ('blocked', 'error'):
            return "Unverified"
        if status_type == 'not_found':
            return "Invalid"
        return "Valid" if result.get('deliverable') else "Invalid"

    def get_deliverable_text(self, result):
        status_type = result.get('smtp_status', 'unknown')
        if status_type in ('blocked', 'error'):
            return "Likely"
        if status_type == 'trusted':
            return "Yes"
        return "Yes" if result.get('deliverable') else "No"

    def validate_single_email(self):
        email = self.email_entry.get().strip()
        if not email:
            messagebox.showwarning("Input Required", "Enter an email")
            return

        self.log_message(f"Validating: {email}", "info")
        self.validate_btn.config(state='disabled')

        def validate():
            try:
                result = self.validator.validate_email(
                    email,
                    check_smtp=self.smtp_check_var.get(),
                    check_catchall=self.catchall_check_var.get(),
                    trusted_domains=self.trusted_domains
                )
                self.validation_results = [result]
                self.display_results()

                status_type = result.get('smtp_status', 'unknown')
                if status_type == 'trusted':
                    self.log_message(f"Trusted deliverable: {email}", "success")
                elif status_type in ('blocked', 'error'):
                    self.log_message(f"Unverified (server blocked): {email}", "warning")
                elif result.get('deliverable'):
                    self.log_message(f"Valid: {email}", "success")
                else:
                    self.log_message(f"Invalid: {email}", "error")
            except Exception as e:
                self.log_message(f"Error: {str(e)}", "error")
            finally:
                self.validate_btn.config(state='normal')

        threading.Thread(target=validate, daemon=True).start()

    def validate_bulk_emails(self):
        emails_text = self.bulk_text.get('1.0', 'end').strip()
        if not emails_text:
            messagebox.showwarning("Input Required", "Enter emails")
            return

        emails = [e.strip() for e in emails_text.split('\n') if e.strip()]
        if not emails:
            messagebox.showwarning("Input Required", "No valid emails")
            return

        self.clear_results_table()
        self.validation_results = []
        self.log_message(f"Starting validation for {len(emails)} emails", "info")
        self.validate_bulk_btn.config(state='disabled')
        self.is_validating = True

        def validate():
            try:
                for i, email in enumerate(emails, 1):
                    if not self.is_validating:
                        break

                    self.log_message(f"[{i}/{len(emails)}] {email}", "info")

                    result = self.validator.validate_email(
                        email,
                        check_smtp=self.smtp_check_var.get(),
                        check_catchall=self.catchall_check_var.get(),
                        trusted_domains=self.trusted_domains
                    )
                    self.validation_results.append(result)
                    self.insert_result_row(result)

                    progress = (i / len(emails)) * 100
                    self.progress_var.set(progress)
                    self.progress_label.config(text=f"{i}/{len(emails)} ({progress:.0f}%)")
                    self.update_stats()
                    self.root.update_idletasks()

                self.log_message("Validation completed", "success")
            except Exception as e:
                self.log_message(f"Error: {str(e)}", "error")
            finally:
                self.validate_bulk_btn.config(state='normal')
                self.is_validating = False

        threading.Thread(target=validate, daemon=True).start()

    def display_results(self):
        self.clear_results_table()
        if not self.validation_results:
            return
        self.insert_result_row(self.validation_results[0])
        self.update_stats()

    def clear_results_table(self):
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

    def insert_result_row(self, result):
        status = self.get_status_text(result)
        deliverable = self.get_deliverable_text(result)
        confidence = f"{result['confidence']}%"
        smtp_status = result.get('smtp_status', 'unknown')
        notes = ' | '.join(result['messages'][:3])

        self.results_tree.insert('', 'end', values=(
            result['email'],
            status,
            confidence,
            deliverable,
            smtp_status,
            notes
        ))

    def update_stats(self):
        if not self.validation_results:
            return

        total = len(self.validation_results)
        valid = sum(1 for r in self.validation_results if r['deliverable'])
        invalid = total - valid
        avg_conf = sum(r['confidence'] for r in self.validation_results) // total

        self.kpi_total.config(text=str(total))
        self.kpi_valid.config(text=str(valid))
        self.kpi_invalid.config(text=str(invalid))
        self.kpi_conf.config(text=f"{avg_conf}%")

        summary = (
            f"Total: {total}\n"
            f"Valid: {valid}\n"
            f"Invalid: {invalid}\n"
            f"Average Confidence: {avg_conf}%\n"
            f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        self.summary_text.delete('1.0', 'end')
        self.summary_text.insert('1.0', summary)

    def import_emails(self):
        filename = filedialog.askopenfilename(
            title="Select File",
            filetypes=[("Text", "*.txt"), ("CSV", "*.csv"), ("All", "*.*")]
        )
        if not filename:
            return

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                if filename.endswith('.csv'):
                    reader = csv.reader(f)
                    emails = [row[0] for row in reader if row]
                else:
                    emails = [line.strip() for line in f if line.strip()]

            self.bulk_text.delete('1.0', 'end')
            self.bulk_text.insert('1.0', '\n'.join(emails))
            self.log_message(f"Imported {len(emails)} emails", "success")
        except Exception as e:
            self.log_message(f"Import failed: {str(e)}", "error")

    def export_results(self):
        if not self.validation_results:
            messagebox.showwarning("No Results", "No results to export")
            return

        filename = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("JSON", "*.json")]
        )
        if not filename:
            return

        try:
            if filename.endswith('.json'):
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.validation_results, f, indent=2)
            else:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'Email', 'Valid', 'Deliverable', 'Confidence',
                        'Catch-all', 'Disposable', 'Has SPF', 'SMTP Status', 'Messages'
                    ])
                    for r in self.validation_results:
                        writer.writerow([
                            r['email'],
                            r['is_valid'],
                            r['deliverable'],
                            r['confidence'],
                            r['is_catchall'],
                            r['is_disposable'],
                            r['has_spf'],
                            r['smtp_status'],
                            ' | '.join(r['messages'])
                        ])

            self.log_message(f"Exported {len(self.validation_results)} results", "success")
            messagebox.showinfo("Success", f"Results saved to:\n{filename}")
        except Exception as e:
            self.log_message(f"Export failed: {str(e)}", "error")

    def add_single_to_queue(self):
        email = self.email_entry.get().strip()
        if not email:
            messagebox.showwarning("Input Required", "Enter an email")
            return
        self.queue.append(email)
        self.queue_list.insert('end', email)
        self.log_message(f"Queued: {email}", "info")

    def add_bulk_to_queue(self):
        emails_text = self.bulk_text.get('1.0', 'end').strip()
        emails = [e.strip() for e in emails_text.split('\n') if e.strip()]
        if not emails:
            messagebox.showwarning("Input Required", "No valid emails")
            return
        for email in emails:
            self.queue.append(email)
            self.queue_list.insert('end', email)
        self.log_message(f"Queued {len(emails)} emails", "info")

    def start_queue(self):
        if self.queue_running or not self.queue:
            return
        self.queue_running = True
        self.log_message("Queue started", "info")

        def run_queue():
            while self.queue_running and self.queue:
                email = self.queue.pop(0)
                self.queue_list.delete(0)
                result = self.validator.validate_email(
                    email,
                    check_smtp=self.smtp_check_var.get(),
                    check_catchall=self.catchall_check_var.get(),
                    trusted_domains=self.trusted_domains
                )
                self.validation_results.append(result)
                self.insert_result_row(result)
                self.update_stats()
            self.queue_running = False
            self.log_message("Queue finished", "success")

        threading.Thread(target=run_queue, daemon=True).start()

    def pause_queue(self):
        self.queue_running = False
        self.log_message("Queue paused", "warning")

    def stop_queue(self):
        self.queue_running = False
        self.queue = []
        self.queue_list.delete(0, 'end')
        self.log_message("Queue stopped and cleared", "warning")

    def clear_queue(self):
        self.queue = []
        self.queue_list.delete(0, 'end')
        self.log_message("Queue cleared", "warning")

    def add_trusted_domain(self):
        domain = self.trusted_entry.get().strip().lower()
        if not domain:
            return
        self.trusted_domains.add(domain)
        self.trusted_entry.delete(0, 'end')
        self.refresh_trusted_list()
        self.log_message(f"Trusted domain added: {domain}", "success")

    def refresh_trusted_list(self):
        self.trusted_list.delete(0, 'end')
        for domain in sorted(self.trusted_domains):
            self.trusted_list.insert('end', domain)


def main():
    root = tk.Tk()
    app = EnhancedEmailValidatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
