"""
Power Email Validation - Professional Edition
Advanced GUI application for comprehensive email validation
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import csv
import json
from datetime import datetime
from email_validator import EmailValidator
import queue


class AdvancedEmailValidatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Power Email Validation - Professional Edition")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)
        
        # Initialize validator
        self.validator = EmailValidator()
        
        # Statistics
        self.stats = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'deliverable': 0
        }
        
        # Results storage
        self.results = []
        
        # Queue for thread-safe updates
        self.update_queue = queue.Queue()
        
        # Validation state
        self.is_validating = False
        
        # Setup UI
        self.setup_ui()
        
        # Start queue processor
        self.process_queue()
        
    def setup_ui(self):
        """Setup the complete user interface"""
        # Configure root grid
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Header
        self.create_header()
        
        # Main content area
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=1, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=2)
        
        # Left panel
        self.create_left_panel(main_frame)
        
        # Right panel
        self.create_right_panel(main_frame)
        
        # Progress bar
        self.create_progress_bar()
        
        # Status bar
        self.create_status_bar()
        
    def create_header(self):
        """Create application header"""
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="Power Email Validation",
            font=("Segoe UI", 24, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(side="left", padx=20, pady=10)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Professional Edition - Comprehensive Email Validation",
            font=("Segoe UI", 12),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        subtitle_label.pack(side="left", padx=20, pady=10)
        
    def create_left_panel(self, parent):
        """Create left panel with inputs and controls"""
        left_frame = ttk.LabelFrame(parent, text="Validation Controls", padding="10")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_frame.grid_rowconfigure(4, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        
        # Single email input
        single_frame = ttk.LabelFrame(left_frame, text="Single Email Validation", padding="10")
        single_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        single_frame.grid_columnconfigure(0, weight=1)
        
        self.single_email_var = tk.StringVar()
        single_entry = ttk.Entry(single_frame, textvariable=self.single_email_var, font=("Segoe UI", 11))
        single_entry.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        validate_single_btn = ttk.Button(
            single_frame,
            text="Validate Email",
            command=self.validate_single_email
        )
        validate_single_btn.grid(row=1, column=0, sticky="ew")
        
        # Bulk email input
        bulk_frame = ttk.LabelFrame(left_frame, text="Bulk Email Validation", padding="10")
        bulk_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        bulk_frame.grid_columnconfigure(0, weight=1)
        
        self.bulk_text = scrolledtext.ScrolledText(
            bulk_frame,
            height=8,
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        self.bulk_text.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        bulk_btn_frame = ttk.Frame(bulk_frame)
        bulk_btn_frame.grid(row=1, column=0, sticky="ew")
        bulk_btn_frame.grid_columnconfigure(0, weight=1)
        bulk_btn_frame.grid_columnconfigure(1, weight=1)
        
        validate_bulk_btn = ttk.Button(
            bulk_btn_frame,
            text="Validate All",
            command=self.validate_bulk_emails
        )
        validate_bulk_btn.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        
        clear_bulk_btn = ttk.Button(
            bulk_btn_frame,
            text="Clear",
            command=self.clear_bulk
        )
        clear_bulk_btn.grid(row=0, column=1, sticky="ew", padx=(2, 0))
        
        # Import/Export buttons
        io_frame = ttk.LabelFrame(left_frame, text="Import / Export", padding="10")
        io_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        io_frame.grid_columnconfigure(0, weight=1)
        io_frame.grid_columnconfigure(1, weight=1)
        
        import_btn = ttk.Button(
            io_frame,
            text="Import Emails",
            command=self.import_emails
        )
        import_btn.grid(row=0, column=0, sticky="ew", padx=(0, 2), pady=(0, 5))
        
        export_csv_btn = ttk.Button(
            io_frame,
            text="Export CSV",
            command=lambda: self.export_results('csv')
        )
        export_csv_btn.grid(row=0, column=1, sticky="ew", padx=(2, 0), pady=(0, 5))
        
        export_json_btn = ttk.Button(
            io_frame,
            text="Export JSON",
            command=lambda: self.export_results('json')
        )
        export_json_btn.grid(row=1, column=0, sticky="ew", padx=(0, 2))
        
        export_report_btn = ttk.Button(
            io_frame,
            text="Export Report",
            command=lambda: self.export_results('report')
        )
        export_report_btn.grid(row=1, column=1, sticky="ew", padx=(2, 0))
        
        # Action buttons
        action_frame = ttk.Frame(left_frame)
        action_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        action_frame.grid_columnconfigure(0, weight=1)
        action_frame.grid_columnconfigure(1, weight=1)
        
        clear_results_btn = ttk.Button(
            action_frame,
            text="Clear Results",
            command=self.clear_results
        )
        clear_results_btn.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        
        clear_logs_btn = ttk.Button(
            action_frame,
            text="Clear Logs",
            command=self.clear_logs
        )
        clear_logs_btn.grid(row=0, column=1, sticky="ew", padx=(2, 0))
        
        # Statistics panel
        stats_frame = ttk.LabelFrame(left_frame, text="Statistics", padding="10")
        stats_frame.grid(row=4, column=0, sticky="nsew")
        stats_frame.grid_columnconfigure(1, weight=1)
        
        self.stats_labels = {}
        stats_config = [
            ('total', 'Total Validated:', '#3498db'),
            ('valid', 'Valid Format:', '#27ae60'),
            ('invalid', 'Invalid Format:', '#e74c3c'),
            ('deliverable', 'Deliverable:', '#2ecc71')
        ]
        
        for idx, (key, label, color) in enumerate(stats_config):
            label_widget = tk.Label(
                stats_frame,
                text=label,
                font=("Segoe UI", 10, "bold"),
                anchor="w"
            )
            label_widget.grid(row=idx, column=0, sticky="w", pady=2)
            
            value_widget = tk.Label(
                stats_frame,
                text="0",
                font=("Segoe UI", 14, "bold"),
                fg=color,
                anchor="e"
            )
            value_widget.grid(row=idx, column=1, sticky="e", pady=2)
            self.stats_labels[key] = value_widget
            
    def create_right_panel(self, parent):
        """Create right panel with results and logs"""
        right_frame = ttk.Frame(parent)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        
        # Tabbed interface
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        
        # Results tab
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="Detailed Results")
        
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Results treeview
        columns = ('email', 'status', 'valid', 'deliverable', 'details')
        self.results_tree = ttk.Treeview(
            results_frame,
            columns=columns,
            show='headings',
            selectmode='extended'
        )
        
        # Configure columns
        self.results_tree.heading('email', text='Email Address')
        self.results_tree.heading('status', text='Status')
        self.results_tree.heading('valid', text='Valid Format')
        self.results_tree.heading('deliverable', text='Deliverable')
        self.results_tree.heading('details', text='Details')
        
        self.results_tree.column('email', width=250)
        self.results_tree.column('status', width=120, anchor='center')
        self.results_tree.column('valid', width=100, anchor='center')
        self.results_tree.column('deliverable', width=100, anchor='center')
        self.results_tree.column('details', width=300)
        
        # Scrollbars for treeview
        tree_scroll_y = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        tree_scroll_x = ttk.Scrollbar(results_frame, orient="horizontal", command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll_y.grid(row=0, column=1, sticky="ns")
        tree_scroll_x.grid(row=1, column=0, sticky="ew")
        
        # Logs tab
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="Live Logs")
        
        logs_frame.grid_rowconfigure(0, weight=1)
        logs_frame.grid_columnconfigure(0, weight=1)
        
        self.logs_text = scrolledtext.ScrolledText(
            logs_frame,
            font=("Consolas", 10),
            wrap=tk.WORD,
            bg="#1e1e1e",
            fg="#d4d4d4"
        )
        self.logs_text.grid(row=0, column=0, sticky="nsew")
        
        # Configure log color tags
        self.logs_text.tag_config('success', foreground='#4ec9b0')
        self.logs_text.tag_config('error', foreground='#f48771')
        self.logs_text.tag_config('warning', foreground='#dcdcaa')
        self.logs_text.tag_config('info', foreground='#569cd6')
        
    def create_progress_bar(self):
        """Create progress bar"""
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.root,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 0))
        
    def create_status_bar(self):
        """Create status bar"""
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=3, column=0, sticky="ew")
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)
        
    def log_message(self, message, level='info'):
        """Add message to logs with color coding"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.update_queue.put(('log', formatted_message, level))
        
    def update_log_text(self, message, level):
        """Update log text widget (called from main thread)"""
        self.logs_text.insert(tk.END, message, level)
        self.logs_text.see(tk.END)
        
    def update_statistics(self):
        """Update statistics display"""
        for key, label in self.stats_labels.items():
            label.config(text=str(self.stats[key]))
            
    def update_status(self, message):
        """Update status bar"""
        self.status_var.set(message)
        
    def add_result_to_tree(self, result):
        """Add validation result to treeview"""
        email = result.get('email', 'N/A')
        is_valid = result.get('is_valid', False)
        is_deliverable = result.get('is_deliverable', False)
        smtp_status = result.get('smtp_status', 'unknown')
        
        # Determine status display
        if smtp_status == 'blocked':
            status = "⚠ Blocked"
            deliverable_display = "Likely Yes"
        elif smtp_status == 'confirmed':
            status = "✓ Confirmed"
            deliverable_display = "Yes" if is_deliverable else "No"
        elif is_valid:
            status = "✓ Valid"
            deliverable_display = "Yes" if is_deliverable else "No"
        else:
            status = "✗ Invalid"
            deliverable_display = "No"
            
        # Format details
        details_parts = []
        if result.get('syntax_valid'):
            details_parts.append("Syntax OK")
        if result.get('dns_valid'):
            details_parts.append("DNS OK")
        if smtp_status == 'blocked':
            details_parts.append("SMTP Blocked")
        elif smtp_status == 'confirmed':
            details_parts.append("SMTP Confirmed")
        elif result.get('smtp_valid'):
            details_parts.append("SMTP OK")
            
        if result.get('error'):
            details_parts.append(f"Error: {result['error']}")
            
        details = ", ".join(details_parts) if details_parts else "See logs"
        
        # Insert into tree
        self.results_tree.insert(
            '',
            tk.END,
            values=(
                email,
                status,
                "Yes" if is_valid else "No",
                deliverable_display,
                details
            )
        )
        
    def validate_single_email(self):
        """Validate single email address"""
        email = self.single_email_var.get().strip()
        
        if not email:
            messagebox.showwarning("Input Required", "Please enter an email address")
            return
            
        if self.is_validating:
            messagebox.showinfo("Validation In Progress", "Please wait for current validation to complete")
            return
            
        self.is_validating = True
        self.update_status(f"Validating {email}...")
        self.log_message(f"Starting validation for: {email}", 'info')
        
        # Run validation in thread
        thread = threading.Thread(target=self._validate_single_thread, args=(email,))
        thread.daemon = True
        thread.start()
        
    def _validate_single_thread(self, email):
        """Thread worker for single email validation"""
        try:
            result = self.validator.validate_email(email)
            self.update_queue.put(('result', result))
            
            # Log result
            if result.get('smtp_status') == 'blocked':
                self.log_message(
                    f"Email {email}: SMTP verification blocked - server does not accept verification",
                    'warning'
                )
            elif result.get('is_valid'):
                self.log_message(f"Email {email}: Valid ✓", 'success')
            else:
                self.log_message(f"Email {email}: Invalid ✗", 'error')
                
        except Exception as e:
            self.log_message(f"Error validating {email}: {str(e)}", 'error')
            
        finally:
            self.update_queue.put(('validation_complete', None))
            
    def validate_bulk_emails(self):
        """Validate multiple email addresses"""
        emails_text = self.bulk_text.get("1.0", tk.END).strip()
        
        if not emails_text:
            messagebox.showwarning("Input Required", "Please enter email addresses")
            return
            
        if self.is_validating:
            messagebox.showinfo("Validation In Progress", "Please wait for current validation to complete")
            return
            
        # Parse emails (one per line or comma-separated)
        emails = []
        for line in emails_text.split('\n'):
            line = line.strip()
            if ',' in line:
                emails.extend([e.strip() for e in line.split(',') if e.strip()])
            elif line:
                emails.append(line)
                
        if not emails:
            messagebox.showwarning("No Emails Found", "No valid email addresses found")
            return
            
        self.is_validating = True
        self.update_status(f"Validating {len(emails)} emails...")
        self.log_message(f"Starting bulk validation for {len(emails)} emails", 'info')
        
        # Run validation in thread
        thread = threading.Thread(target=self._validate_bulk_thread, args=(emails,))
        thread.daemon = True
        thread.start()
        
    def _validate_bulk_thread(self, emails):
        """Thread worker for bulk email validation"""
        total = len(emails)
        
        for idx, email in enumerate(emails, 1):
            try:
                result = self.validator.validate_email(email)
                self.update_queue.put(('result', result))
                
                # Log result
                if result.get('smtp_status') == 'blocked':
                    self.log_message(
                        f"[{idx}/{total}] {email}: SMTP verification blocked",
                        'warning'
                    )
                elif result.get('is_valid'):
                    self.log_message(f"[{idx}/{total}] {email}: Valid ✓", 'success')
                else:
                    self.log_message(f"[{idx}/{total}] {email}: Invalid ✗", 'error')
                    
            except Exception as e:
                self.log_message(f"[{idx}/{total}] Error validating {email}: {str(e)}", 'error')
                
            # Update progress
            progress = (idx / total) * 100
            self.update_queue.put(('progress', progress))
            
        self.update_queue.put(('validation_complete', None))
        
    def import_emails(self):
        """Import emails from file"""
        file_path = filedialog.askopenfilename(
            title="Import Emails",
            filetypes=[
                ("Text files", "*.txt"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
            
        try:
            emails = []
            
            if file_path.endswith('.csv'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        emails.extend([cell.strip() for cell in row if '@' in cell])
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        line = line.strip()
                        if ',' in line:
                            emails.extend([e.strip() for e in line.split(',') if '@' in e])
                        elif '@' in line:
                            emails.append(line)
                            
            if emails:
                current_text = self.bulk_text.get("1.0", tk.END).strip()
                if current_text:
                    self.bulk_text.insert(tk.END, "\n")
                self.bulk_text.insert(tk.END, "\n".join(emails))
                self.log_message(f"Imported {len(emails)} emails from {file_path}", 'success')
            else:
                messagebox.showwarning("No Emails Found", "No email addresses found in file")
                
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import emails: {str(e)}")
            self.log_message(f"Import error: {str(e)}", 'error')
            
    def export_results(self, format_type):
        """Export validation results"""
        if not self.results:
            messagebox.showinfo("No Results", "No validation results to export")
            return
            
        if format_type == 'csv':
            self._export_csv()
        elif format_type == 'json':
            self._export_json()
        elif format_type == 'report':
            self._export_report()
            
    def _export_csv(self):
        """Export results to CSV"""
        file_path = filedialog.asksaveasfilename(
            title="Export to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Email', 'Valid', 'Deliverable', 'SMTP Status', 'Syntax Valid', 'DNS Valid'])
                
                for result in self.results:
                    writer.writerow([
                        result.get('email', ''),
                        result.get('is_valid', False),
                        result.get('is_deliverable', False),
                        result.get('smtp_status', 'unknown'),
                        result.get('syntax_valid', False),
                        result.get('dns_valid', False)
                    ])
                    
            self.log_message(f"Exported {len(self.results)} results to CSV", 'success')
            messagebox.showinfo("Export Successful", f"Results exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
            self.log_message(f"Export error: {str(e)}", 'error')
            
    def _export_json(self):
        """Export results to JSON"""
        file_path = filedialog.asksaveasfilename(
            title="Export to JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'export_date': datetime.now().isoformat(),
                    'statistics': self.stats,
                    'results': self.results
                }, f, indent=2)
                
            self.log_message(f"Exported {len(self.results)} results to JSON", 'success')
            messagebox.showinfo("Export Successful", f"Results exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
            self.log_message(f"Export error: {str(e)}", 'error')
            
    def _export_report(self):
        """Export detailed text report"""
        file_path = filedialog.asksaveasfilename(
            title="Export Report",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("Power Email Validation - Detailed Validation Report\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("STATISTICS\n")
                f.write("-" * 80 + "\n")
                f.write(f"Total Validated:    {self.stats['total']}\n")
                f.write(f"Valid Format:       {self.stats['valid']}\n")
                f.write(f"Invalid Format:     {self.stats['invalid']}\n")
                f.write(f"Deliverable:        {self.stats['deliverable']}\n\n")
                
                f.write("DETAILED RESULTS\n")
                f.write("-" * 80 + "\n\n")
                
                for idx, result in enumerate(self.results, 1):
                    f.write(f"[{idx}] {result.get('email', 'N/A')}\n")
                    f.write(f"    Valid Format:    {result.get('is_valid', False)}\n")
                    f.write(f"    Deliverable:     {result.get('is_deliverable', False)}\n")
                    f.write(f"    SMTP Status:     {result.get('smtp_status', 'unknown')}\n")
                    f.write(f"    Syntax Valid:    {result.get('syntax_valid', False)}\n")
                    f.write(f"    DNS Valid:       {result.get('dns_valid', False)}\n")
                    
                    if result.get('smtp_status') == 'blocked':
                        f.write(f"    Note:            SMTP verification blocked by server\n")
                        
                    if result.get('error'):
                        f.write(f"    Error:           {result['error']}\n")
                        
                    f.write("\n")
                    
            self.log_message(f"Exported detailed report", 'success')
            messagebox.showinfo("Export Successful", f"Report exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
            self.log_message(f"Export error: {str(e)}", 'error')
            
    def clear_results(self):
        """Clear all results"""
        if self.results:
            response = messagebox.askyesno("Clear Results", "Are you sure you want to clear all results?")
            if not response:
                return
                
        # Clear treeview
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
            
        # Reset results and statistics
        self.results = []
        self.stats = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'deliverable': 0
        }
        self.update_statistics()
        self.progress_var.set(0)
        self.log_message("Results cleared", 'info')
        self.update_status("Ready")
        
    def clear_logs(self):
        """Clear log text"""
        self.logs_text.delete("1.0", tk.END)
        self.log_message("Logs cleared", 'info')
        
    def clear_bulk(self):
        """Clear bulk email textarea"""
        self.bulk_text.delete("1.0", tk.END)
        
    def process_queue(self):
        """Process updates from worker threads"""
        try:
            while True:
                item = self.update_queue.get_nowait()
                
                if item[0] == 'log':
                    self.update_log_text(item[1], item[2])
                    
                elif item[0] == 'result':
                    result = item[1]
                    self.results.append(result)
                    self.add_result_to_tree(result)
                    
                    # Update statistics
                    self.stats['total'] += 1
                    if result.get('is_valid'):
                        self.stats['valid'] += 1
                    else:
                        self.stats['invalid'] += 1
                    if result.get('is_deliverable') or result.get('smtp_status') == 'blocked':
                        self.stats['deliverable'] += 1
                        
                    self.update_statistics()
                    
                elif item[0] == 'progress':
                    self.progress_var.set(item[1])
                    
                elif item[0] == 'validation_complete':
                    self.is_validating = False
                    self.progress_var.set(0)
                    self.update_status("Validation complete")
                    
        except queue.Empty:
            pass
            
        # Schedule next check
        self.root.after(100, self.process_queue)


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = AdvancedEmailValidatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
