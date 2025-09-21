"""Safety analyzer for dependency vulnerabilities."""

import subprocess
from typing import List, Dict, Any
from pr_review_agent.core.models import CodeIssue, AnalysisConfig, IssueSeverity, IssueCategory


class SafetyAnalyzer:
    """Safety-based dependency vulnerability analyzer."""

    def __init__(self, config: AnalysisConfig):
        self.config = config

    def analyze(self, file_path: str, content: str) -> List[CodeIssue]:
        if not self.should_analyze(file_path):
            return []

        issues = []
        try:
            result = subprocess.run([
                'safety', 'check', '--json'
            ], capture_output=True, text=True, timeout=30)

            if result.stdout:
                import json
                data = json.loads(result.stdout)
                for vuln in data:
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=1,
                        severity=IssueSeverity.HIGH,
                        category=IssueCategory.SECURITY,
                        message=f"Vulnerability in {vuln.get('package', 'unknown')}: {vuln.get('advisory', '')}",
                        rule_id="safety",
                        suggestion=f"Update {vuln.get('package', '')} to version {vuln.get('safe_version', 'latest')}"
                    ))

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
            pass

        return issues

    def should_analyze(self, file_path: str) -> bool:
        return file_path in ['requirements.txt', 'setup.py', 'pyproject.toml']

    def get_name(self) -> str:
        return "Safety"

    def get_metrics(self, file_path: str, content: str) -> Dict[str, Any]:
        return {}
