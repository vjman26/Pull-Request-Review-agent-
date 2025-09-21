#!/usr/bin/env python3
"""
Simplified PR Review Agent - Works without external dependencies
This is a working version that demonstrates the core functionality
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

class SimpleCodeIssue:
    def __init__(self, file_path: str, line_number: int, severity: str, category: str, message: str, suggestion: str = ""):
        self.file_path = file_path
        self.line_number = line_number
        self.severity = severity
        self.category = category
        self.message = message
        self.suggestion = suggestion

class SimplePRInfo:
    def __init__(self, number: int, title: str, author: str, files_changed: List[str], additions: int, deletions: int):
        self.number = number
        self.title = title
        self.author = author
        self.files_changed = files_changed
        self.additions = additions
        self.deletions = deletions

class SimpleReviewFeedback:
    def __init__(self, overall_score: float, summary: str, issues: List[SimpleCodeIssue], suggestions: List[str], strengths: List[str]):
        self.overall_score = overall_score
        self.summary = summary
        self.issues = issues
        self.suggestions = suggestions
        self.strengths = strengths

class SimpleCodeAnalyzer:
    """Simple code analyzer that checks for common issues"""
    
    def analyze(self, file_path: str, content: str) -> List[SimpleCodeIssue]:
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_lower = line.lower().strip()
            
            # Skip empty lines and comments
            if not line_lower or line_lower.startswith('#'):
                continue
                
            # Check for common issues
            if 'print(' in line and 'debug' not in line_lower:
                issues.append(SimpleCodeIssue(
                    file_path, i, "low", "readability",
                    "Debug print statement found",
                    "Remove or replace with proper logging"
                ))
            
            if 'password' in line_lower and '=' in line and '"' in line:
                issues.append(SimpleCodeIssue(
                    file_path, i, "high", "security",
                    "Potential hardcoded password",
                    "Use environment variables for sensitive data"
                ))
            
            if len(line) > 100:
                issues.append(SimpleCodeIssue(
                    file_path, i, "medium", "style",
                    "Line too long",
                    "Break long lines for better readability"
                ))
            
            if 'todo' in line_lower or 'fixme' in line_lower:
                issues.append(SimpleCodeIssue(
                    file_path, i, "low", "maintainability",
                    "TODO/FIXME comment found",
                    "Address pending tasks before merging"
                ))
            
            if 'except:' in line_lower and 'except Exception:' not in line_lower:
                issues.append(SimpleCodeIssue(
                    file_path, i, "medium", "bug",
                    "Bare except clause",
                    "Specify exception types for better error handling"
                ))
            
            if 'eval(' in line_lower or 'exec(' in line_lower:
                issues.append(SimpleCodeIssue(
                    file_path, i, "high", "security",
                    "Use of eval/exec detected",
                    "Avoid eval/exec for security reasons"
                ))

        return issues

def calculate_score(issues: List[SimpleCodeIssue]) -> float:
    """Calculate quality score based on issues"""
    if not issues:
        return 10.0
    
    base_score = 10.0
    penalty = 0
    
    for issue in issues:
        if issue.severity == "critical":
            penalty += 2.0
        elif issue.severity == "high":
            penalty += 1.0
        elif issue.severity == "medium":
            penalty += 0.5
        elif issue.severity == "low":
            penalty += 0.1
    
    return max(0.0, base_score - penalty)

def generate_feedback(issues: List[SimpleCodeIssue], pr_info: SimplePRInfo) -> SimpleReviewFeedback:
    """Generate comprehensive feedback"""
    
    # Calculate score
    score = calculate_score(issues)
    
    # Generate summary
    if not issues:
        summary = f"✅ Excellent work! No issues found in this {pr_info.additions + pr_info.deletions} line change across {len(pr_info.files_changed)} files."
    else:
        severity_counts = {}
        for issue in issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
        
        summary_parts = [f"Found {len(issues)} issues in {len(pr_info.files_changed)} files:"]
        for severity in ["critical", "high", "medium", "low"]:
            count = severity_counts.get(severity, 0)
            if count > 0:
                summary_parts.append(f"  • {count} {severity} severity")
        
        summary = " ".join(summary_parts)
    
    # Extract suggestions
    suggestions = list(set([issue.suggestion for issue in issues if issue.suggestion]))
    
    # Identify strengths
    strengths = []
    if pr_info.additions > 0 and pr_info.deletions > 0:
        strengths.append("Good balance of additions and deletions")
    if len(pr_info.files_changed) <= 10:
        strengths.append("Focused changes across reasonable number of files")
    if any('test' in f.lower() for f in pr_info.files_changed):
        strengths.append("Includes test updates")
    if any(f.endswith('.md') for f in pr_info.files_changed):
        strengths.append("Includes documentation updates")

    return SimpleReviewFeedback(score, summary, issues, suggestions, strengths)

def analyze_file(file_path: str, content: str) -> List[SimpleCodeIssue]:
    """Analyze a single file"""
    analyzer = SimpleCodeAnalyzer()
    return analyzer.analyze(file_path, content)

def review_pr(pr_info: SimplePRInfo, file_contents: Dict[str, str]) -> SimpleReviewFeedback:
    """Review a pull request"""
    
    print(f"🔍 Analyzing PR #{pr_info.number}: {pr_info.title}")
    print(f"Author: {pr_info.author}")
    print(f"Files: {len(pr_info.files_changed)} | +{pr_info.additions} -{pr_info.deletions}")
    print()
    
    all_issues = []
    
    # Analyze each file
    for file_path in pr_info.files_changed:
        if file_path in file_contents:
            print(f"📄 Analyzing {file_path}...")
            issues = analyze_file(file_path, file_contents[file_path])
            all_issues.extend(issues)
            print(f"   Found {len(issues)} issues")
        else:
            print(f"⚠️  Skipping {file_path} (content not provided)")
    
    print()
    
    # Generate feedback
    feedback = generate_feedback(all_issues, pr_info)
    
    return feedback

def display_results(feedback: SimpleReviewFeedback):
    """Display review results in a nice format"""
    
    print("📊 Review Results")
    print("=" * 50)
    
    # Overall score
    score_color = "🟢" if feedback.overall_score >= 8 else "🟡" if feedback.overall_score >= 6 else "🔴"
    print(f"\n{score_color} Overall Score: {feedback.overall_score:.1f}/10")
    
    # Summary
    print(f"\n📝 Summary:")
    print(f"   {feedback.summary}")
    
    # Issues found
    if feedback.issues:
        print(f"\n🐛 Issues Found ({len(feedback.issues)}):")
        for i, issue in enumerate(feedback.issues, 1):
            severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(issue.severity, "⚪")
            print(f"   {i}. {severity_emoji} {issue.severity.upper()} - {issue.file_path}:{issue.line_number}")
            print(f"      {issue.message}")
            if issue.suggestion:
                print(f"      💡 Suggestion: {issue.suggestion}")
            print()
    
    # Suggestions
    if feedback.suggestions:
        print(f"💡 Suggestions:")
        for i, suggestion in enumerate(feedback.suggestions, 1):
            print(f"   {i}. {suggestion}")
        print()
    
    # Strengths
    if feedback.strengths:
        print(f"✨ Strengths:")
        for strength in feedback.strengths:
            print(f"   • {strength}")
        print()

def main():
    """Main function to run the PR review"""
    
    print("🚀 Simple PR Review Agent")
    print("=" * 50)
    print()
    
    # Sample PR data
    pr_info = SimplePRInfo(
        number=456,
        title="Add user authentication and session management",
        author="developer123",
        files_changed=["auth.py", "models.py", "test_auth.py", "README.md"],
        additions=200,
        deletions=30
    )
    
    # Sample file contents
    file_contents = {
        "auth.py": '''
def authenticate_user(username, password):
    # TODO: Add rate limiting
    print(f"Authenticating user: {username}")  # Debug print
    user_password = "admin123"  # Hardcoded password
    if password == user_password:
        return True
    return False

def create_user_session(user_id, session_data):
    # This is a very long line that exceeds the recommended line length and should be broken into multiple lines for better readability
    session = Session(user_id=user_id, data=session_data, created_at=datetime.now(), expires_at=datetime.now() + timedelta(hours=24))
    return session

def process_payment(amount):
    try:
        # Process payment
        result = payment_gateway.charge(amount)
        return result
    except:  # Bare except clause
        return None

def execute_user_code(code):
    # Dangerous use of eval
    return eval(code)
''',
        "models.py": '''
class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email
        self.password = "default123"  # Another hardcoded password
    
    def validate_password(self, password):
        # FIXME: Implement proper password validation
        return password == self.password
''',
        "test_auth.py": '''
import unittest
from auth import authenticate_user

class TestAuth(unittest.TestCase):
    def test_authenticate_user(self):
        # Test valid authentication
        result = authenticate_user("test", "admin123")
        self.assertTrue(result)
    
    def test_invalid_credentials(self):
        # Test invalid credentials
        result = authenticate_user("test", "wrong")
        self.assertFalse(result)
''',
        "README.md": '''
# Authentication Module

This module provides user authentication functionality.

## Features
- User login
- Session management
- Password validation

## Usage
```python
from auth import authenticate_user
result = authenticate_user("username", "password")
```
'''
    }
    
    # Run the review
    feedback = review_pr(pr_info, file_contents)
    
    # Display results
    display_results(feedback)
    
    print("🎯 This demonstrates the PR Review Agent's capabilities:")
    print("   • Automatic code analysis")
    print("   • Issue detection and categorization")
    print("   • Quality scoring")
    print("   • Actionable suggestions")
    print("   • Strength identification")

if __name__ == "__main__":
    main()
