#!/usr/bin/env python3
"""
PR Review Agent - Enhanced GUI Version
A professional desktop application for code review with advanced features
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, font
import os
import sys
import threading
import webbrowser
from datetime import datetime
from simple_pr_review import analyze_file, calculate_score, generate_feedback, SimplePRInfo, display_results

class EnhancedPRReviewGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PR Review Agent Pro - Advanced Code Quality Analysis")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f8f9fa')
        
        # Variables
        self.current_file = None
        self.analysis_results = None
        self.analysis_history = []
        
        # Configure styles
        self.setup_styles()
        self.setup_ui()
        
        # Center window
        self.center_window()
    
    def setup_styles(self):
        """Configure custom styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', font=('Segoe UI', 24, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Segoe UI', 12), foreground='#7f8c8d')
        style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), foreground='#34495e')
        style.configure('Success.TLabel', font=('Segoe UI', 10), foreground='#27ae60')
        style.configure('Warning.TLabel', font=('Segoe UI', 10), foreground='#f39c12')
        style.configure('Error.TLabel', font=('Segoe UI', 10), foreground='#e74c3c')
        
        # Button styles
        style.configure('Primary.TButton', font=('Segoe UI', 10, 'bold'), padding=(20, 10))
        style.configure('Secondary.TButton', font=('Segoe UI', 9), padding=(15, 8))
        style.configure('Success.TButton', font=('Segoe UI', 10, 'bold'), padding=(20, 10))
        style.configure('Warning.TButton', font=('Segoe UI', 10, 'bold'), padding=(20, 10))
        style.configure('Info.TButton', font=('Segoe UI', 10, 'bold'), padding=(20, 10))
    
    def setup_ui(self):
        """Set up the enhanced user interface"""
        
        # Create main container with padding
        main_container = tk.Frame(self.root, bg='#f8f9fa')
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header section
        self.create_header(main_container)
        
        # Main content area
        content_frame = tk.Frame(main_container, bg='#f8f9fa')
        content_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        # Left panel - Controls
        self.create_control_panel(content_frame)
        
        # Right panel - Results
        self.create_results_panel(content_frame)
        
        # Status bar
        self.create_status_bar(main_container)
    
    def create_header(self, parent):
        """Create the header section"""
        header_frame = tk.Frame(parent, bg='#2c3e50', height=100)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Title and subtitle
        title_frame = tk.Frame(header_frame, bg='#2c3e50')
        title_frame.pack(expand=True)
        
        title_label = tk.Label(
            title_frame,
            text="🔍 PR Review Agent Pro",
            font=('Segoe UI', 28, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Advanced Code Quality Analysis & Automated Review System",
            font=('Segoe UI', 14),
            fg='#bdc3c7',
            bg='#2c3e50'
        )
        subtitle_label.pack()
        
        # Quick stats
        stats_frame = tk.Frame(header_frame, bg='#2c3e50')
        stats_frame.pack(side='right', padx=20)
        
        self.stats_label = tk.Label(
            stats_frame,
            text="Ready to analyze",
            font=('Segoe UI', 10),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        self.stats_label.pack()
    
    def create_control_panel(self, parent):
        """Create the left control panel"""
        control_frame = tk.LabelFrame(
            parent,
            text="🎛️ Analysis Controls",
            font=('Segoe UI', 12, 'bold'),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        control_frame.pack(side='left', fill='y', padx=(0, 10))
        control_frame.configure(width=350)
        control_frame.pack_propagate(False)
        
        # File selection section
        file_section = tk.Frame(control_frame, bg='#f8f9fa')
        file_section.pack(fill='x', padx=15, pady=15)
        
        tk.Label(
            file_section,
            text="📁 Select File to Analyze",
            font=('Segoe UI', 11, 'bold'),
            bg='#f8f9fa',
            fg='#34495e'
        ).pack(anchor='w')
        
        self.file_label = tk.Label(
            file_section,
            text="No file selected",
            font=('Segoe UI', 9),
            fg='#7f8c8d',
            bg='#f8f9fa',
            wraplength=300
        )
        self.file_label.pack(anchor='w', pady=(5, 10))
        
        # File selection buttons
        btn_frame = tk.Frame(file_section, bg='#f8f9fa')
        btn_frame.pack(fill='x')
        
        browse_btn = ttk.Button(
            btn_frame,
            text="📂 Browse Files",
            command=self.browse_file,
            style='Primary.TButton'
        )
        browse_btn.pack(side='left', padx=(0, 5))
        
        demo_btn = ttk.Button(
            btn_frame,
            text="🎯 Run Demo",
            command=self.run_demo,
            style='Info.TButton'
        )
        demo_btn.pack(side='left')
        
        # Analysis options
        options_section = tk.Frame(control_frame, bg='#f8f9fa')
        options_section.pack(fill='x', padx=15, pady=15)
        
        tk.Label(
            options_section,
            text="⚙️ Analysis Options",
            font=('Segoe UI', 11, 'bold'),
            bg='#f8f9fa',
            fg='#34495e'
        ).pack(anchor='w')
        
        # Severity threshold
        severity_frame = tk.Frame(options_section, bg='#f8f9fa')
        severity_frame.pack(fill='x', pady=(10, 5))
        
        tk.Label(
            severity_frame,
            text="Severity Threshold:",
            font=('Segoe UI', 9),
            bg='#f8f9fa',
            fg='#34495e'
        ).pack(side='left')
        
        self.severity_var = tk.StringVar(value="medium")
        severity_combo = ttk.Combobox(
            severity_frame,
            textvariable=self.severity_var,
            values=["low", "medium", "high", "critical"],
            state="readonly",
            width=10
        )
        severity_combo.pack(side='right')
        
        # Analysis button
        analyze_btn = ttk.Button(
            control_frame,
            text="🔍 Analyze Code",
            command=self.analyze_code,
            style='Success.TButton',
            state='disabled'
        )
        analyze_btn.pack(pady=20)
        self.analyze_btn = analyze_btn
        
        # Quick actions
        actions_section = tk.Frame(control_frame, bg='#f8f9fa')
        actions_section.pack(fill='x', padx=15, pady=15)
        
        tk.Label(
            actions_section,
            text="🚀 Quick Actions",
            font=('Segoe UI', 11, 'bold'),
            bg='#f8f9fa',
            fg='#34495e'
        ).pack(anchor='w')
        
        # Action buttons
        action_btn_frame = tk.Frame(actions_section, bg='#f8f9fa')
        action_btn_frame.pack(fill='x', pady=(10, 0))
        
        export_btn = ttk.Button(
            action_btn_frame,
            text="💾 Export Report",
            command=self.export_report,
            style='Secondary.TButton',
            state='disabled'
        )
        export_btn.pack(fill='x', pady=2)
        self.export_btn = export_btn
        
        clear_btn = ttk.Button(
            action_btn_frame,
            text="🗑️ Clear Results",
            command=self.clear_results,
            style='Secondary.TButton'
        )
        clear_btn.pack(fill='x', pady=2)
        
        help_btn = ttk.Button(
            action_btn_frame,
            text="❓ Help & Tips",
            command=self.show_help,
            style='Secondary.TButton'
        )
        help_btn.pack(fill='x', pady=2)
    
    def create_results_panel(self, parent):
        """Create the right results panel"""
        results_frame = tk.LabelFrame(
            parent,
            text="📊 Analysis Results",
            font=('Segoe UI', 12, 'bold'),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        results_frame.pack(side='right', fill='both', expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Summary tab
        self.create_summary_tab()
        
        # Issues tab
        self.create_issues_tab()
        
        # Suggestions tab
        self.create_suggestions_tab()
        
        # History tab
        self.create_history_tab()
    
    def create_summary_tab(self):
        """Create the summary tab"""
        self.summary_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(self.summary_frame, text="📋 Summary")
        
        # Summary content
        self.summary_text = scrolledtext.ScrolledText(
            self.summary_frame,
            font=('Consolas', 10),
            bg='white',
            fg='#2c3e50',
            wrap=tk.WORD,
            padx=15,
            pady=15
        )
        self.summary_text.pack(fill='both', expand=True)
        
        # Add initial content
        self.summary_text.insert(tk.END, "Welcome to PR Review Agent Pro!\n\n")
        self.summary_text.insert(tk.END, "Select a Python file or run the demo to get started.\n\n")
        self.summary_text.insert(tk.END, "Features:\n")
        self.summary_text.insert(tk.END, "• 🔍 Advanced code analysis\n")
        self.summary_text.insert(tk.END, "• 🐛 Bug and security detection\n")
        self.summary_text.insert(tk.END, "• 💡 Intelligent suggestions\n")
        self.summary_text.insert(tk.END, "• 📊 Quality scoring\n")
        self.summary_text.insert(tk.END, "• 📈 Analysis history\n")
        self.summary_text.config(state='disabled')
    
    def create_issues_tab(self):
        """Create the issues tab"""
        self.issues_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(self.issues_frame, text="🐛 Issues")
        
        # Issues content
        self.issues_text = scrolledtext.ScrolledText(
            self.issues_frame,
            font=('Consolas', 10),
            bg='white',
            fg='#2c3e50',
            wrap=tk.WORD,
            padx=15,
            pady=15
        )
        self.issues_text.pack(fill='both', expand=True)
        
        # Add initial content
        self.issues_text.insert(tk.END, "No issues found yet.\n\n")
        self.issues_text.insert(tk.END, "Issues will be displayed here after analysis.\n")
        self.issues_text.insert(tk.END, "Each issue includes:\n")
        self.issues_text.insert(tk.END, "• Severity level (Critical, High, Medium, Low)\n")
        self.issues_text.insert(tk.END, "• File location and line number\n")
        self.issues_text.insert(tk.END, "• Description of the problem\n")
        self.issues_text.insert(tk.END, "• Suggested fix\n")
        self.issues_text.config(state='disabled')
    
    def create_suggestions_tab(self):
        """Create the suggestions tab"""
        self.suggestions_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(self.suggestions_frame, text="💡 Suggestions")
        
        # Suggestions content
        self.suggestions_text = scrolledtext.ScrolledText(
            self.suggestions_frame,
            font=('Consolas', 10),
            bg='white',
            fg='#2c3e50',
            wrap=tk.WORD,
            padx=15,
            pady=15
        )
        self.suggestions_text.pack(fill='both', expand=True)
        
        # Add initial content
        self.suggestions_text.insert(tk.END, "No suggestions yet.\n\n")
        self.suggestions_text.insert(tk.END, "Suggestions will appear here after analysis.\n")
        self.suggestions_text.insert(tk.END, "These help you:\n")
        self.suggestions_text.insert(tk.END, "• Fix code issues\n")
        self.suggestions_text.insert(tk.END, "• Improve code quality\n")
        self.suggestions_text.insert(tk.END, "• Follow best practices\n")
        self.suggestions_text.insert(tk.END, "• Enhance security\n")
        self.suggestions_text.config(state='disabled')
    
    def create_history_tab(self):
        """Create the history tab"""
        self.history_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(self.history_frame, text="📈 History")
        
        # History content
        self.history_text = scrolledtext.ScrolledText(
            self.history_frame,
            font=('Consolas', 10),
            bg='white',
            fg='#2c3e50',
            wrap=tk.WORD,
            padx=15,
            pady=15
        )
        self.history_text.pack(fill='both', expand=True)
        
        # Add initial content
        self.history_text.insert(tk.END, "Analysis History\n")
        self.history_text.insert(tk.END, "=" * 50 + "\n\n")
        self.history_text.insert(tk.END, "No analyses performed yet.\n\n")
        self.history_text.insert(tk.END, "History will show:\n")
        self.history_text.insert(tk.END, "• Timestamp of each analysis\n")
        self.history_text.insert(tk.END, "• File analyzed\n")
        self.history_text.insert(tk.END, "• Quality score\n")
        self.history_text.insert(tk.END, "• Number of issues found\n")
        self.history_text.config(state='disabled')
    
    def create_status_bar(self, parent):
        """Create the status bar"""
        status_frame = tk.Frame(parent, bg='#34495e', height=30)
        status_frame.pack(fill='x', pady=(20, 0))
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to analyze code")
        
        status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=('Segoe UI', 9),
            fg='white',
            bg='#34495e',
            anchor='w'
        )
        status_label.pack(side='left', padx=10, fill='x', expand=True)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            status_frame,
            mode='indeterminate',
            length=200
        )
        self.progress.pack(side='right', padx=10)
        self.progress.pack_forget()  # Hide initially
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def browse_file(self):
        """Browse for a Python file to analyze"""
        file_path = filedialog.askopenfilename(
            title="Select Python file to analyze",
            filetypes=[
                ("Python files", "*.py"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.current_file = file_path
            filename = os.path.basename(file_path)
            self.file_label.config(
                text=f"Selected: {filename}",
                fg='#27ae60'
            )
            self.analyze_btn.config(state='normal')
            self.status_var.set(f"File selected: {filename}")
            
            # Update stats
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                self.stats_label.config(text=f"File: {filename} ({lines} lines)")
            except:
                self.stats_label.config(text=f"File: {filename}")
    
    def run_demo(self):
        """Run the demo analysis in a separate thread"""
        self.status_var.set("Running demo...")
        self.progress.pack(side='right', padx=10)
        self.progress.start()
        
        def demo_thread():
            try:
                # Demo PR data
                pr_info = SimplePRInfo(
                    number=123,
                    title="Add user authentication feature",
                    author="developer123",
                    files_changed=["auth.py", "models.py"],
                    additions=150,
                    deletions=25
                )
                
                # Demo file contents
                file_contents = {
                    "auth.py": '''def authenticate_user(username, password):
    # TODO: Add rate limiting
    print(f"Authenticating user: {username}")
    user_password = "admin123"  # Hardcoded password
    if password == user_password:
        return True
    return False

def create_session(user_id):
    # This is a very long line that exceeds the recommended line length
    session = Session(user_id=user_id, created_at=datetime.now())
    return session

def process_payment(amount):
    try:
        # Process payment
        result = payment_gateway.charge(amount)
        return result
    except:  # Bare except clause
        return None''',
                    "models.py": '''class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email
        self.password = "default123"  # Hardcoded password
    
    def validate_password(self, password):
        # FIXME: Implement proper password validation
        return password == self.password'''
                }
                
                # Analyze files
                all_issues = []
                for file_path, content in file_contents.items():
                    issues = analyze_file(file_path, content)
                    all_issues.extend(issues)
                
                # Generate feedback
                feedback = generate_feedback(all_issues, pr_info)
                
                # Update UI in main thread
                self.root.after(0, lambda: self.display_results(feedback, pr_info, "Demo"))
                
            except Exception as e:
                self.root.after(0, lambda: self.show_error(f"Demo failed: {str(e)}"))
            finally:
                self.root.after(0, self.analysis_complete)
        
        threading.Thread(target=demo_thread, daemon=True).start()
    
    def analyze_code(self):
        """Analyze the selected file in a separate thread"""
        if not self.current_file:
            messagebox.showerror("Error", "Please select a file first")
            return
        
        self.status_var.set("Analyzing code...")
        self.progress.pack(side='right', padx=10)
        self.progress.start()
        self.analyze_btn.config(state='disabled')
        
        def analysis_thread():
            try:
                # Read file
                with open(self.current_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Analyze
                issues = analyze_file(self.current_file, content)
                
                # Create PR info
                pr_info = SimplePRInfo(
                    number=1,
                    title=f"Analysis of {os.path.basename(self.current_file)}",
                    author="local_user",
                    files_changed=[self.current_file],
                    additions=len(content.split('\n')),
                    deletions=0
                )
                
                # Generate feedback
                feedback = generate_feedback(issues, pr_info)
                
                # Update UI in main thread
                self.root.after(0, lambda: self.display_results(feedback, pr_info, "File Analysis"))
                
            except Exception as e:
                self.root.after(0, lambda: self.show_error(f"Analysis failed: {str(e)}"))
            finally:
                self.root.after(0, self.analysis_complete)
        
        threading.Thread(target=analysis_thread, daemon=True).start()
    
    def display_results(self, feedback, pr_info, analysis_type):
        """Display analysis results in the GUI"""
        
        # Store results
        self.analysis_results = (feedback, pr_info)
        
        # Clear previous results
        self.summary_text.config(state='normal')
        self.issues_text.config(state='normal')
        self.suggestions_text.config(state='normal')
        
        self.summary_text.delete(1.0, tk.END)
        self.issues_text.delete(1.0, tk.END)
        self.suggestions_text.delete(1.0, tk.END)
        
        # Summary tab
        score_emoji = "🟢" if feedback.overall_score >= 8 else "🟡" if feedback.overall_score >= 6 else "🔴"
        score_color = "#27ae60" if feedback.overall_score >= 8 else "#f39c12" if feedback.overall_score >= 6 else "#e74c3c"
        
        summary_content = f"""📊 ANALYSIS RESULTS - {analysis_type.upper()}
{'='*60}

📋 PR Information:
• Title: {pr_info.title}
• Author: {pr_info.author}
• Files: {len(pr_info.files_changed)}
• Changes: +{pr_info.additions} -{pr_info.deletions}

🎯 Overall Score: {feedback.overall_score:.1f}/10 {score_emoji}

📝 Summary:
{feedback.summary}

📊 File Statistics:
• Total lines: {pr_info.additions}
• Issues found: {len(feedback.issues)}
• Suggestions: {len(feedback.suggestions)}
• Strengths: {len(feedback.strengths)}

⏰ Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        self.summary_text.insert(tk.END, summary_content)
        
        # Issues tab
        if feedback.issues:
            issues_content = f"🐛 ISSUES FOUND ({len(feedback.issues)})\n{'='*60}\n\n"
            
            # Group issues by severity
            severity_groups = {"critical": [], "high": [], "medium": [], "low": []}
            for issue in feedback.issues:
                severity_groups[issue.severity].append(issue)
            
            for severity in ["critical", "high", "medium", "low"]:
                issues = severity_groups[severity]
                if issues:
                    severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}[severity]
                    issues_content += f"{severity_emoji} {severity.upper()} SEVERITY ({len(issues)} issues)\n"
                    issues_content += "-" * 40 + "\n\n"
                    
                    for i, issue in enumerate(issues, 1):
                        issues_content += f"{i}. {os.path.basename(issue.file_path)}:{issue.line_number}\n"
                        issues_content += f"   {issue.message}\n"
                        if issue.suggestion:
                            issues_content += f"   💡 Suggestion: {issue.suggestion}\n"
                        issues_content += "\n"
        else:
            issues_content = "✅ No issues found! Your code looks great!\n\n"
            issues_content += "This means your code follows best practices and is well-written."
        
        self.issues_text.insert(tk.END, issues_content)
        
        # Suggestions tab
        if feedback.suggestions:
            suggestions_content = f"💡 SUGGESTIONS ({len(feedback.suggestions)})\n{'='*60}\n\n"
            for i, suggestion in enumerate(feedback.suggestions, 1):
                suggestions_content += f"{i}. {suggestion}\n"
        else:
            suggestions_content = "✅ No suggestions - your code follows best practices!\n\n"
        
        if feedback.strengths:
            suggestions_content += f"\n✨ STRENGTHS\n{'='*30}\n"
            for strength in feedback.strengths:
                suggestions_content += f"• {strength}\n"
        
        self.suggestions_text.insert(tk.END, suggestions_content)
        
        # Update history
        self.update_history(feedback, pr_info, analysis_type)
        
        # Enable export button
        self.export_btn.config(state='normal')
        
        # Switch to summary tab
        self.notebook.select(0)
        
        # Disable text widgets
        self.summary_text.config(state='disabled')
        self.issues_text.config(state='disabled')
        self.suggestions_text.config(state='disabled')
    
    def update_history(self, feedback, pr_info, analysis_type):
        """Update the analysis history"""
        self.analysis_history.append({
            'timestamp': datetime.now(),
            'type': analysis_type,
            'file': pr_info.title,
            'score': feedback.overall_score,
            'issues': len(feedback.issues)
        })
        
        # Update history tab
        self.history_text.config(state='normal')
        self.history_text.delete(1.0, tk.END)
        
        history_content = "📈 ANALYSIS HISTORY\n"
        history_content += "=" * 50 + "\n\n"
        
        if self.analysis_history:
            for i, entry in enumerate(reversed(self.analysis_history[-10:]), 1):  # Show last 10
                history_content += f"{i}. {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                history_content += f"   Type: {entry['type']}\n"
                history_content += f"   File: {entry['file']}\n"
                history_content += f"   Score: {entry['score']:.1f}/10\n"
                history_content += f"   Issues: {entry['issues']}\n\n"
        else:
            history_content += "No analyses performed yet.\n"
        
        self.history_text.insert(tk.END, history_content)
        self.history_text.config(state='disabled')
    
    def analysis_complete(self):
        """Called when analysis is complete"""
        self.progress.stop()
        self.progress.pack_forget()
        self.analyze_btn.config(state='normal')
        self.status_var.set("Analysis completed")
    
    def show_error(self, message):
        """Show error message"""
        self.progress.stop()
        self.progress.pack_forget()
        self.analyze_btn.config(state='normal')
        self.status_var.set("Analysis failed")
        messagebox.showerror("Error", message)
    
    def export_report(self):
        """Export analysis report to file"""
        if not self.analysis_results:
            messagebox.showwarning("Warning", "No analysis results to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Analysis Report",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                feedback, pr_info = self.analysis_results
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("PR Review Agent Pro - Analysis Report\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"File: {pr_info.title}\n")
                    f.write(f"Score: {feedback.overall_score:.1f}/10\n\n")
                    f.write("SUMMARY:\n")
                    f.write(feedback.summary + "\n\n")
                    f.write("ISSUES:\n")
                    for i, issue in enumerate(feedback.issues, 1):
                        f.write(f"{i}. {issue.severity.upper()} - {issue.file_path}:{issue.line_number}\n")
                        f.write(f"   {issue.message}\n")
                        if issue.suggestion:
                            f.write(f"   Suggestion: {issue.suggestion}\n")
                        f.write("\n")
                    f.write("SUGGESTIONS:\n")
                    for i, suggestion in enumerate(feedback.suggestions, 1):
                        f.write(f"{i}. {suggestion}\n")
                
                messagebox.showinfo("Success", f"Report exported to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report: {str(e)}")
    
    def clear_results(self):
        """Clear all results"""
        if messagebox.askyesno("Confirm", "Clear all results and history?"):
            # Clear text widgets
            self.summary_text.config(state='normal')
            self.issues_text.config(state='normal')
            self.suggestions_text.config(state='normal')
            
            self.summary_text.delete(1.0, tk.END)
            self.issues_text.delete(1.0, tk.END)
            self.suggestions_text.delete(1.0, tk.END)
            
            # Reset to initial content
            self.summary_text.insert(tk.END, "Welcome to PR Review Agent Pro!\n\n")
            self.summary_text.insert(tk.END, "Select a Python file or run the demo to get started.\n")
            self.summary_text.config(state='disabled')
            
            self.issues_text.insert(tk.END, "No issues found yet.\n")
            self.issues_text.config(state='disabled')
            
            self.suggestions_text.insert(tk.END, "No suggestions yet.\n")
            self.suggestions_text.config(state='disabled')
            
            # Clear history
            self.analysis_history.clear()
            self.history_text.config(state='normal')
            self.history_text.delete(1.0, tk.END)
            self.history_text.insert(tk.END, "Analysis History\n" + "=" * 50 + "\n\nNo analyses performed yet.\n")
            self.history_text.config(state='disabled')
            
            # Reset variables
            self.analysis_results = None
            self.export_btn.config(state='disabled')
            self.status_var.set("Results cleared")
    
    def show_help(self):
        """Show help dialog"""
        help_text = """PR Review Agent Pro - Help & Tips

🎯 How to Use:
1. Click 'Browse Files' to select a Python file
2. Click 'Run Demo' to see a sample analysis
3. Click 'Analyze Code' to analyze your file
4. Check the tabs for detailed results

📊 Understanding Results:
• Score 8-10: Excellent code quality
• Score 6-7: Good code with minor issues
• Score 4-5: Fair code with several issues
• Score 0-3: Poor code with many issues

🐛 Issue Severity:
• 🔴 Critical: Security vulnerabilities, major bugs
• 🟠 High: Important issues that should be fixed
• 🟡 Medium: Style and quality improvements
• 🟢 Low: Minor suggestions and best practices

💡 Tips for Better Code:
• Use environment variables for secrets
• Add proper error handling
• Keep lines under 100 characters
• Add docstrings to functions
• Use meaningful variable names
• Remove debug print statements

🚀 Features:
• Real-time analysis
• Export reports
• Analysis history
• Multiple file support
• Professional interface

For more help, visit: https://github.com/your-repo/pr-review-agent
"""
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Help & Tips")
        help_window.geometry("600x500")
        help_window.configure(bg='#f8f9fa')
        
        help_text_widget = scrolledtext.ScrolledText(
            help_window,
            font=('Segoe UI', 10),
            bg='white',
            fg='#2c3e50',
            wrap=tk.WORD,
            padx=20,
            pady=20
        )
        help_text_widget.pack(fill='both', expand=True, padx=20, pady=20)
        help_text_widget.insert(tk.END, help_text)
        help_text_widget.config(state='disabled')

def main():
    """Main function to run the enhanced GUI"""
    root = tk.Tk()
    app = EnhancedPRReviewGUI(root)
    
    # Set window icon (if available)
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    root.mainloop()

if __name__ == "__main__":
    main()
