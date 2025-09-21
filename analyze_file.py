#!/usr/bin/env python3
"""
Analyze a single Python file with the PR Review Agent
Usage: python analyze_file.py <filename>
"""

import sys
import os
from simple_pr_review import analyze_file, calculate_score, generate_feedback, SimplePRInfo, display_results

def main():
    if len(sys.argv) != 2:
        print("Usage: python analyze_file.py <filename>")
        print("Example: python analyze_file.py my_script.py")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    
    if not filename.endswith('.py'):
        print("Warning: This analyzer works best with Python files")
    
    print(f"🔍 Analyzing file: {filename}")
    print("=" * 50)
    
    try:
        # Read the file
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Analyze the file
        issues = analyze_file(filename, content)
        
        # Create mock PR info
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
        
        # Show file statistics
        lines = content.split('\n')
        print(f"📊 File Statistics:")
        print(f"   • Total lines: {len(lines)}")
        print(f"   • Non-empty lines: {len([l for l in lines if l.strip()])}")
        print(f"   • Issues found: {len(issues)}")
        print(f"   • Quality score: {feedback.overall_score:.1f}/10")
        
    except Exception as e:
        print(f"Error analyzing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
