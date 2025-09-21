"""Bandit analyzer for security issues."""

import subprocess
import tempfile
import os
from typing import List, Dict, Any
from pr_review_agent.core.models import CodeIssue, AnalysisConfig, IssueSeverity, IssueCategory


class BanditAnalyzer:
    """Bandit-based security analyzer."""

    def __init__(self, config: AnalysisConfig):
        self.config = config

    def analyze(self, file_path: str, content: str) -> List[CodeIssue]:
        if not self.should_analyze(file_path):
            return []

        issues = []
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name

            result = subprocess.run([
                'bandit', '-f', 'json', temp_file_path
            ], capture_output=True, text=True, timeout=30)

            if result.stdout:
                import json
                data = json.loads(result.stdout)
                for result_item in data.get('results', []):
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=result_item.get('line_number', 1),
                        severity=self._get_severity(result_item.get('issue_severity', 'MEDIUM')),
                        category=IssueCategory.SECURITY,
                        message=result_item.get('issue_text', ''),
                        rule_id=result_item.get('test_id', ''),
                        suggestion=result_item.get('issue_text', '')
                    ))

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
            pass
        finally:
            if 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass

        return issues

    def _get_severity(self, severity: str) -> IssueSeverity:
        severity_map = {
            'LOW': IssueSeverity.LOW,
            'MEDIUM': IssueSeverity.MEDIUM,
            'HIGH': IssueSeverity.HIGH
        }
        return severity_map.get(severity.upper(), IssueSeverity.MEDIUM)

    def should_analyze(self, file_path: str) -> bool:
        return file_path.endswith('.py')

    def get_name(self) -> str:
        return "Bandit"

    def get_metrics(self, file_path: str, content: str) -> Dict[str, Any]:
        return {}
