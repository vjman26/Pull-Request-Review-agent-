#!/usr/bin/env python3
"""
Simple demo of PR Review Agent functionality
This shows how the system works without requiring external API tokens
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# Add the current directory to Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Simple mock classes to demonstrate the functionality
class MockCodeIssue:
    def __init__(self, file_path: str, line_number: int, severity: str, category: str, message: str, suggestion: str = ""):
        self.file_path = file_path
        self.line_number = line_number
        self.severity = severity
        self.category = category
        self.message = message
        self.suggestion = suggestion

class MockPRInfo:
    def __init__(self, number: int, title: str, author: str, files_changed: List[str], additions: int, deletions: int):
        self.number = number
        self.title = title
        self.author = author
        self.files_changed = files_changed
        self.additions = additions
        self.deletions = deletions

class MockReviewFeedback:
    def __init__(self, overall_score: float, summary: str, issues: List[MockCodeIssue], suggestions: List[str], strengths: List[str]):
        self.overall_score = overall_score
        self.summary = summary
        self.issues = issues
        self.suggestions = suggestions
        self.strengths = strengths

class SimpleCodeAnalyzer:
    """Simple code analyzer that checks for common issues"""
    
    def analyze(self, file_path: str, content: str) -> List[MockCodeIssue]:
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for common issues
            if 'print(' in line and 'debug' not in line.lower():
                issues.append(MockCodeIssue(
                    file_path, i, "low", "readability",
                    "Debug print statement found",
                    "Remove or replace with proper logging"
                ))
            
            if 'password' in line.lower() and '=' in line:
                issues.append(MockCodeIssue(
                    file_path, i, "high", "security",
                    "Potential hardcoded password",
                    "Use environment variables for sensitive data"
                ))
            
            if len(line) > 100:
                issues.append(MockCodeIssue(
                    file_path, i, "medium", "style",
                    "Line too long",
                    "Break long lines for better readability"
                ))
            
            if 'TODO' in line or 'FIXME' in line:
                issues.append(MockCodeIssue(
                    file_path, i, "low", "maintainability",
                    "TODO/FIXME comment found",
                    "Address pending tasks before merging"
                ))
        
        return issues

def calculate_score(issues: List[MockCodeIssue]) -> float:
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

def generate_feedback(issues: List[MockCodeIssue], pr_info: MockPRInfo) -> MockReviewFeedback:
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
    
    return MockReviewFeedback(score, summary, issues, suggestions, strengths)

def demo_pr_review():
    """Demonstrate PR review process"""
    
    print("🔍 PR Review Agent Demo")
    print("=" * 50)
    
    # Mock PR information
    pr_info = MockPRInfo(
        number=123,
        title="Add user authentication feature",
        author="developer123",
        files_changed=["auth.py", "models.py", "test_auth.py", "README.md"],
        additions=150,
        deletions=25
    )
    
    print(f"\n📋 PR #{pr_info.number}: {pr_info.title}")
    print(f"Author: {pr_info.author}")
    print(f"Files: {len(pr_info.files_changed)} | +{pr_info.additions} -{pr_info.deletions}")
    
    # Sample code to analyze
    sample_code = '''
def authenticate_user(username, password):
    # TODO: Add rate limiting
    print(f"Authenticating user: {username}")  # Debug print
    user_password = "admin123"  # Hardcoded password - security issue
    if password == user_password:
        return True
    return False

def create_user_session(user_id, session_data):
    # This is a very long line that exceeds the recommended line length and should be broken into multiple lines for better readability
    session = Session(user_id=user_id, data=session_data, created_at=datetime.now(), expires_at=datetime.now() + timedelta(hours=24))
    return session
'''
    
    print(f"\n🔍 Analyzing code...")
    
    # Analyze the code
    analyzer = SimpleCodeAnalyzer()
    issues = analyzer.analyze("auth.py", sample_code)
    
    # Generate feedback
    feedback = generate_feedback(issues, pr_info)
    
    # Display results
    print(f"\n📊 Review Results")
    print("=" * 30)
    
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
            print(f"   {i}. {severity_emoji} {issue.severity.upper()} - Line {issue.line_number}: {issue.message}")
            if issue.suggestion:
                print(f"      💡 Suggestion: {issue.suggestion}")
    
    # Suggestions
    if feedback.suggestions:
        print(f"\n💡 Suggestions:")
        for i, suggestion in enumerate(feedback.suggestions, 1):
            print(f"   {i}. {suggestion}")
    
    # Strengths
    if feedback.strengths:
        print(f"\n✨ Strengths:")
        for strength in feedback.strengths:
            print(f"   • {strength}")
    
    print(f"\n🎯 This demonstrates how the PR Review Agent:")
    print(f"   • Analyzes code for quality, security, and style issues")
    print(f"   • Provides actionable suggestions for improvement")
    print(f"   • Calculates an overall quality score")
    print(f"   • Identifies both issues and strengths")
    print(f"   • Works with multiple file types and git servers")

if __name__ == "__main__":
    demo_pr_review()
