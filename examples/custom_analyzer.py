"""Example of creating a custom analyzer."""

from pr_review_agent.analyzers.base import CodeAnalyzer
from pr_review_agent.core.models import CodeIssue, AnalysisConfig, IssueSeverity, IssueCategory
from typing import List, Dict, Any
import re


class CustomAnalyzer(CodeAnalyzer):
    """Custom analyzer for specific business rules."""
    
    def __init__(self, config: AnalysisConfig):
        super().__init__(config)
        # Define custom patterns to check
        self.patterns = {
            'hardcoded_password': r'password\s*=\s*["\'][^"\']+["\']',
            'debug_print': r'print\s*\(',
            'todo_comment': r'#\s*TODO',
            'long_function': r'def\s+\w+\([^)]*\):\s*$'
        }
    
    def analyze(self, file_path: str, content: str) -> List[CodeIssue]:
        """Analyze file for custom patterns."""
        if not self.should_analyze(file_path):
            return []
        
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Check for hardcoded passwords
            if re.search(self.patterns['hardcoded_password'], line, re.IGNORECASE):
                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=line_num,
                    severity=IssueSeverity.HIGH,
                    category=IssueCategory.SECURITY,
                    message="Hardcoded password detected",
                    rule_id="custom-hardcoded-password",
                    suggestion="Use environment variables or secure configuration"
                ))
            
            # Check for debug prints
            if re.search(self.patterns['debug_print'], line):
                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=line_num,
                    severity=IssueSeverity.LOW,
                    category=IssueCategory.READABILITY,
                    message="Debug print statement found",
                    rule_id="custom-debug-print",
                    suggestion="Remove or replace with proper logging"
                ))
            
            # Check for TODO comments
            if re.search(self.patterns['todo_comment'], line):
                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=line_num,
                    severity=IssueSeverity.LOW,
                    category=IssueCategory.MAINTAINABILITY,
                    message="TODO comment found",
                    rule_id="custom-todo",
                    suggestion="Consider addressing TODO items before merging"
                ))
        
        return issues
    
    def should_analyze(self, file_path: str) -> bool:
        """Only analyze Python files."""
        return file_path.endswith('.py')
    
    def get_name(self) -> str:
        """Get analyzer name."""
        return "Custom Analyzer"
    
    def get_metrics(self, file_path: str, content: str) -> Dict[str, Any]:
        """Get custom metrics."""
        lines = content.split('\n')
        return {
            'total_lines': len(lines),
            'todo_count': len([l for l in lines if re.search(self.patterns['todo_comment'], l)]),
            'debug_prints': len([l for l in lines if re.search(self.patterns['debug_print'], l)])
        }


def main():
    """Example of using custom analyzer."""
    from pr_review_agent import PRReviewAgent
    
    # Create configuration
    config = AnalysisConfig(
        enable_pylint=False,  # Disable default analyzers for this example
        enable_flake8=False,
        enable_black=False,
        enable_mypy=False,
        enable_bandit=False,
        enable_safety=False
    )
    
    # Create agent
    agent = PRReviewAgent(config)
    
    # Add custom analyzer
    custom_analyzer = CustomAnalyzer(config)
    agent.analyzers.append(custom_analyzer)
    
    # Test with sample code
    sample_code = '''
def login(username, password="admin123"):  # Hardcoded password
    print(f"Logging in user: {username}")  # Debug print
    # TODO: Implement proper authentication
    return True
'''
    
    issues = custom_analyzer.analyze("test.py", sample_code)
    
    print("Custom Analysis Results:")
    for issue in issues:
        print(f"  {issue.severity.value.upper()}: {issue.message} (line {issue.line_number})")
        if issue.suggestion:
            print(f"    Suggestion: {issue.suggestion}")

if __name__ == "__main__":
    main()
