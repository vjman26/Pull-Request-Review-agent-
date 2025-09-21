"""MyPy analyzer for type checking."""

import subprocess
import tempfile
import os
from typing import List, Dict, Any
from pr_review_agent.core.models import CodeIssue, AnalysisConfig, IssueSeverity, IssueCategory


class MyPyAnalyzer:
    """MyPy-based type checker."""

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
                'mypy', '--show-error-codes', '--no-error-summary', temp_file_path
            ], capture_output=True, text=True, timeout=30)

            if result.stdout:
                issues.extend(self._parse_output(result.stdout, file_path))

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        finally:
            if 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass

        return issues

    def _parse_output(self, output: str, file_path: str) -> List[CodeIssue]:
        issues = []
        for line in output.strip().split('\n'):
            if ':' in line and 'error:' in line:
                parts = line.split(':', 3)
                if len(parts) >= 4:
                    line_num = int(parts[1]) if parts[1].isdigit() else 1
                    message = parts[3].strip()
                    
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=line_num,
                        severity=IssueSeverity.HIGH,
                        category=IssueCategory.BUG,
                        message=message,
                        rule_id="mypy"
                    ))
        return issues

    def should_analyze(self, file_path: str) -> bool:
        return file_path.endswith('.py')

    def get_name(self) -> str:
        return "MyPy"

    def get_metrics(self, file_path: str, content: str) -> Dict[str, Any]:
        return {}
