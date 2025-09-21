#!/usr/bin/env python3
"""
PR Review Agent - GUI Version
A simple desktop application for code review
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
from simple_pr_review import analyze_file, calculate_score, generate_feedback, SimplePRInfo, display_results

class PRReviewGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PR Review Agent - Code Quality Checker")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.current_file = None
        self.analysis_results = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        
        # Main title
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', padx=10, pady=10)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="🔍 PR Review Agent", 
            font=('Arial', 20, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(expand=True)
        
        subtitle_label = tk.Label(
            title_frame,
            text="Automated Code Quality Analysis",
            font=('Arial', 12),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        subtitle_label.pack()
        
        # File selection frame
        file_frame = tk.LabelFrame(self.root, text="📁 Select File to Analyze", font=('Arial', 12, 'bold'), bg='#f0f0f0')
        file_frame.pack(fill='x', padx=10, pady=5)
        
        file_select_frame = tk.Frame(file_frame, bg='#f0f0f0')
        file_select_frame.pack(fill='x', padx=10, pady=10)
        
        self.file_label = tk.Label(
            file_select_frame, 
            text="No file selected", 
            font=('Arial', 10),
            fg='#7f8c8d',
            bg='#f0f0f0'
        )
        self.file_label.pack(side='left', padx=(0, 10))
        
        browse_btn = tk.Button(
            file_select_frame,
            text="Browse Files",
            command=self.browse_file,
            bg='#3498db',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=5
        )
        browse_btn.pack(side='right')
        
        # Demo button
        demo_btn = tk.Button(
            file_select_frame,
            text="Run Demo",
            command=self.run_demo,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=5
        )
        demo_btn.pack(side='right', padx=(0, 10))
        
        # Analysis button
        analyze_btn = tk.Button(
            file_frame,
            text="🔍 Analyze Code",
            command=self.analyze_code,
            bg='#27ae60',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=30,
            pady=10,
            state='disabled'
        )
        analyze_btn.pack(pady=10)
        self.analyze_btn = analyze_btn
        
        # Results frame
        results_frame = tk.LabelFrame(self.root, text="📊 Analysis Results", font=('Arial', 12, 'bold'), bg='#f0f0f0')
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Summary tab
        self.summary_frame = tk.Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(self.summary_frame, text="📋 Summary")
        
        self.summary_text = scrolledtext.ScrolledText(
            self.summary_frame,
            height=15,
            font=('Consolas', 10),
            bg='white',
            fg='#2c3e50'
        )
        self.summary_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Issues tab
        self.issues_frame = tk.Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(self.issues_frame, text="🐛 Issues")
        
        self.issues_text = scrolledtext.ScrolledText(
            self.issues_frame,
            height=15,
            font=('Consolas', 10),
            bg='white',
            fg='#2c3e50'
        )
        self.issues_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Suggestions tab
        self.suggestions_frame = tk.Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(self.suggestions_frame, text="💡 Suggestions")
        
        self.suggestions_text = scrolledtext.ScrolledText(
            self.suggestions_frame,
            height=15,
            font=('Consolas', 10),
            bg='white',
            fg='#2c3e50'
        )
        self.suggestions_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to analyze code")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor='w',
            bg='#34495e',
            fg='white',
            font=('Arial', 9)
        )
        status_bar.pack(side='bottom', fill='x')
    
    def browse_file(self):
        """Browse for a Python file to analyze"""
        file_path = filedialog.askopenfilename(
            title="Select Python file to analyze",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        
        if file_path:
            self.current_file = file_path
            self.file_label.config(text=f"Selected: {os.path.basename(file_path)}", fg='#27ae60')
            self.analyze_btn.config(state='normal')
            self.status_var.set(f"File selected: {os.path.basename(file_path)}")
    
    def run_demo(self):
        """Run the demo analysis"""
        self.status_var.set("Running demo...")
        self.root.update()
        
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
    return session''',
            "models.py": '''class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email
        self.password = "default123"  # Hardcoded password'''
        }
        
        # Analyze files
        all_issues = []
        for file_path, content in file_contents.items():
            issues = analyze_file(file_path, content)
            all_issues.extend(issues)
        
        # Generate feedback
        feedback = generate_feedback(all_issues, pr_info)
        
        # Display results
        self.display_results(feedback, pr_info)
        self.status_var.set("Demo completed")
    
    def analyze_code(self):
        """Analyze the selected file"""
        if not self.current_file:
            messagebox.showerror("Error", "Please select a file first")
            return
        
        self.status_var.set("Analyzing code...")
        self.root.update()
        
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
            
            # Display results
            self.display_results(feedback, pr_info)
            self.status_var.set("Analysis completed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze file: {str(e)}")
            self.status_var.set("Analysis failed")
    
    def display_results(self, feedback, pr_info):
        """Display analysis results in the GUI"""
        
        # Clear previous results
        self.summary_text.delete(1.0, tk.END)
        self.issues_text.delete(1.0, tk.END)
        self.suggestions_text.delete(1.0, tk.END)
        
        # Summary tab
        summary_content = f"""📊 ANALYSIS RESULTS
{'='*50}

PR Information:
• Title: {pr_info.title}
• Author: {pr_info.author}
• Files: {len(pr_info.files_changed)}
• Changes: +{pr_info.additions} -{pr_info.deletions}

Overall Score: {feedback.overall_score:.1f}/10
{'🟢' if feedback.overall_score >= 8 else '🟡' if feedback.overall_score >= 6 else '🔴'}

Summary:
{feedback.summary}

File Statistics:
• Total lines: {pr_info.additions}
• Issues found: {len(feedback.issues)}
• Suggestions: {len(feedback.suggestions)}
• Strengths: {len(feedback.strengths)}
"""
        
        self.summary_text.insert(tk.END, summary_content)
        
        # Issues tab
        if feedback.issues:
            issues_content = f"🐛 ISSUES FOUND ({len(feedback.issues)})\n{'='*50}\n\n"
            
            for i, issue in enumerate(feedback.issues, 1):
                severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(issue.severity, "⚪")
                issues_content += f"{i}. {severity_emoji} {issue.severity.upper()} - {os.path.basename(issue.file_path)}:{issue.line_number}\n"
                issues_content += f"   {issue.message}\n"
                if issue.suggestion:
                    issues_content += f"   💡 Suggestion: {issue.suggestion}\n"
                issues_content += "\n"
        else:
            issues_content = "✅ No issues found! Your code looks great!"
        
        self.issues_text.insert(tk.END, issues_content)
        
        # Suggestions tab
        if feedback.suggestions:
            suggestions_content = f"💡 SUGGESTIONS ({len(feedback.suggestions)})\n{'='*50}\n\n"
            for i, suggestion in enumerate(feedback.suggestions, 1):
                suggestions_content += f"{i}. {suggestion}\n"
        else:
            suggestions_content = "✅ No suggestions - your code follows best practices!"
        
        if feedback.strengths:
            suggestions_content += f"\n✨ STRENGTHS\n{'='*30}\n"
            for strength in feedback.strengths:
                suggestions_content += f"• {strength}\n"
        
        self.suggestions_text.insert(tk.END, suggestions_content)
        
        # Switch to summary tab
        self.notebook.select(0)

def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = PRReviewGUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
