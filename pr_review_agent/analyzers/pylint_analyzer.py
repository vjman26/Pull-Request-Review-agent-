"""Pylint analyzer for code quality analysis."""

import subprocess
import tempfile
import os
from typing import List, Dict, Any
from pr_review_agent.core.models import CodeIssue, AnalysisConfig, IssueSeverity, IssueCategory


class PylintAnalyzer:
    """Pylint-based code analyzer."""

    def __init__(self, config: AnalysisConfig):
        """Initialize Pylint analyzer."""
        self.config = config

    def analyze(self, file_path: str, content: str) -> List[CodeIssue]:
        """Analyze file using Pylint."""
        if not self.should_analyze(file_path):
            return []

        issues = []
        
        try:
            # Create temporary file for analysis
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name

            # Run pylint
            result = subprocess.run([
                'pylint', 
                '--output-format=json',
                '--disable=all',
                '--enable=C,W,R,E,F',
                temp_file_path
            ], capture_output=True, text=True, timeout=30)

            # Parse JSON output
            if result.stdout:
                import json
                try:
                    pylint_output = json.loads(result.stdout)
                    for issue in pylint_output:
                        issues.append(self._convert_pylint_issue(issue, file_path))
                except json.JSONDecodeError:
                    # Fallback to text parsing if JSON fails
                    issues.extend(self._parse_text_output(result.stdout, file_path))

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            # Pylint not available or failed
            pass
        finally:
            # Clean up temporary file
            if 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass

        return issues

    def _convert_pylint_issue(self, issue: Dict[str, Any], file_path: str) -> CodeIssue:
        """Convert Pylint issue to CodeIssue."""
        severity_map = {
            'C': IssueSeverity.LOW,      # Convention
            'W': IssueSeverity.MEDIUM,   # Warning
            'R': IssueSeverity.MEDIUM,   # Refactor
            'E': IssueSeverity.HIGH,     # Error
            'F': IssueSeverity.CRITICAL  # Fatal
        }

        category_map = {
            'C': IssueCategory.STYLE,
            'W': IssueCategory.READABILITY,
            'R': IssueCategory.MAINTAINABILITY,
            'E': IssueCategory.BUG,
            'F': IssueCategory.BUG
        }

        return CodeIssue(
            file_path=file_path,
            line_number=issue.get('line', 1),
            column_number=issue.get('column'),
            severity=severity_map.get(issue.get('type', 'W'), IssueSeverity.MEDIUM),
            category=category_map.get(issue.get('type', 'W'), IssueCategory.READABILITY),
            message=issue.get('message', ''),
            rule_id=issue.get('message-id', ''),
            suggestion=self._get_suggestion(issue.get('message-id', ''))
        )

    def _parse_text_output(self, output: str, file_path: str) -> List[CodeIssue]:
        """Parse Pylint text output as fallback."""
        issues = []
        lines = output.split('\n')
        
        for line in lines:
            if ':' in line and ('error' in line.lower() or 'warning' in line.lower()):
                parts = line.split(':')
                if len(parts) >= 4:
                    line_num = int(parts[1]) if parts[1].isdigit() else 1
                    message = ':'.join(parts[3:]).strip()
                    
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=line_num,
                        severity=IssueSeverity.MEDIUM,
                        category=IssueCategory.READABILITY,
                        message=message
                    ))
        
        return issues

    def _get_suggestion(self, rule_id: str) -> str:
        """Get suggestion based on Pylint rule ID."""
        suggestions = {
            'C0103': "Consider using snake_case for variable names",
            'C0114': "Add a docstring to describe the module",
            'C0116': "Add a docstring to describe the function",
            'C0301': "Line too long - consider breaking into multiple lines",
            'C0304': "Missing final newline",
            'W0613': "Unused argument - consider removing or prefixing with underscore",
            'R0903': "Too few public methods - consider if this class is necessary",
            'E1101': "Instance of 'X' has no member 'Y' - check attribute name",
            'F0001': "Fatal error - check syntax and imports"
        }
        return suggestions.get(rule_id, "")

    def should_analyze(self, file_path: str) -> bool:
        """Check if file should be analyzed by Pylint."""
        return file_path.endswith('.py')

    def get_name(self) -> str:
        """Get analyzer name."""
        return "Pylint"

    def get_metrics(self, file_path: str, content: str) -> Dict[str, Any]:
        """Get Pylint metrics."""
        if not self.should_analyze(file_path):
            return {}

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name

            result = subprocess.run([
                'pylint', 
                '--output-format=json',
                '--score=y',
                temp_file_path
            ], capture_output=True, text=True, timeout=30)

            if result.stdout:
                import json
                try:
                    data = json.loads(result.stdout)
                    return {
                        'pylint_score': data.get('score', 0),
                        'pylint_issues_count': len(data)
                    }
                except json.JSONDecodeError:
                    pass
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        finally:
            if 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass

        return {}
