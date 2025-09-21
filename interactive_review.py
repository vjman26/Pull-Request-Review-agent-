#!/usr/bin/env python3
"""
Interactive PR Review Agent
Run this to get a guided experience
"""

import os
import sys
from simple_pr_review import analyze_file, calculate_score, generate_feedback, SimplePRInfo, display_results

def get_user_input():
    """Get input from user"""
    print("🚀 Interactive PR Review Agent")
    print("=" * 50)
    print()
    
    # Get file to analyze
    while True:
        filename = input("📁 Enter Python file to analyze (or 'demo' for demo): ").strip()
        
        if filename.lower() == 'demo':
            return "demo", None
        
        if os.path.exists(filename):
            break
        else:
            print(f"❌ File '{filename}' not found. Please try again.")
    
    return "file", filename

def run_demo():
    """Run the demo"""
    print("\n🎯 Running Demo...")
    print("=" * 30)
    
    # Sample PR data
    pr_info = SimplePRInfo(
        number=123,
        title="Add user authentication feature",
        author="developer123",
        files_changed=["auth.py", "models.py"],
        additions=150,
        deletions=25
    )
    
    # Sample file contents
    file_contents = {
        "auth.py": '''
def authenticate_user(username, password):
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
''',
        "models.py": '''
class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email
        self.password = "default123"  # Hardcoded password
'''
    }
    
    # Analyze files
    all_issues = []
    for file_path, content in file_contents.items():
        issues = analyze_file(file_path, content)
        all_issues.extend(issues)
        print(f"📄 Analyzed {file_path}: {len(issues)} issues found")
    
    # Generate feedback
    feedback = generate_feedback(all_issues, pr_info)
    
    # Display results
    display_results(feedback)

def analyze_single_file(filename):
    """Analyze a single file"""
    print(f"\n🔍 Analyzing: {filename}")
    print("=" * 40)
    
    try:
        # Read file
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Analyze
        issues = analyze_file(filename, content)
        
        # Create PR info
        pr_info = SimplePRInfo(
            number=1,
            title=f"Analysis of {filename}",
            author="local_user",
            files_changed=[filename],
            additions=len(content.split('\n')),
            deletions=0
        )
        
        # Generate feedback
        feedback = generate_feedback(issues, pr_info)
        
        # Display results
        display_results(feedback)
        
        # Show statistics
        lines = content.split('\n')
        print(f"\n📊 File Statistics:")
        print(f"   • Total lines: {len(lines)}")
        print(f"   • Non-empty lines: {len([l for l in lines if l.strip()])}")
        print(f"   • Issues found: {len(issues)}")
        print(f"   • Quality score: {feedback.overall_score:.1f}/10")
        
    except Exception as e:
        print(f"❌ Error analyzing file: {e}")

def main():
    """Main interactive function"""
    try:
        mode, filename = get_user_input()
        
        if mode == "demo":
            run_demo()
        else:
            analyze_single_file(filename)
        
        print("\n🎉 Analysis complete!")
        print("\n💡 Tips:")
        print("   • Fix high/critical issues first")
        print("   • Use proper logging instead of print statements")
        print("   • Keep lines under 100 characters")
        print("   • Use environment variables for secrets")
        print("   • Add proper error handling")
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
