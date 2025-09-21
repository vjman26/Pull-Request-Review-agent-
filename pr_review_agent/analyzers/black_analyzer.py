"""Black formatter analyzer for code style consistency."""

import subprocess
import tempfile
import os
from typing import List, Dict, Any
from pr_review_agent.core.models import CodeIssue, AnalysisConfig, IssueSeverity, IssueCategory


class BlackAnalyzer:
    """Black formatter-based code analyzer."""

    def __init__(self, config: AnalysisConfig):
        """Initialize Black analyzer."""
        self.config = config

    def analyze(self, file_path: str, content: str) -> List[CodeIssue]:
        """Analyze file using Black formatter."""
        if not self.should_analyze(file_path):
            return []

        issues = []
        
        try:
            # Create temporary file for analysis
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name

            # Run black in check mode
            result = subprocess.run([
                'black', 
                '--check', 
                '--diff',
                temp_file_path
            ], capture_output=True, text=True, timeout=30)

            # If exit code is 1, the file needs formatting
            if result.returncode == 1 and result.stdout:
                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=1,
                    severity=IssueSeverity.LOW,
                    category=IssueCategory.STYLE,
                    message="Code formatting issues detected by Black",
                    rule_id="black-formatting",
                    suggestion="Run 'black' to format the code",
                    code_snippet=result.stdout[:500]  # First 500 chars of diff
                ))

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            # Black not available or failed
            pass
        finally:
            # Clean up temporary file
            if 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass

        return issues

    def should_analyze(self, file_path: str) -> bool:
        """Check if file should be analyzed by Black."""
        return file_path.endswith('.py')

    def get_name(self) -> str:
        """Get analyzer name."""
        return "Black"

    def get_metrics(self, file_path: str, content: str) -> Dict[str, Any]:
        """Get Black metrics."""
        if not self.should_analyze(file_path):
            return {}

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name

            result = subprocess.run([
                'black', 
                '--check',
                temp_file_path
            ], capture_output=True, text=True, timeout=30)

            return {
                'black_needs_formatting': result.returncode == 1,
                'black_compatible': result.returncode == 0
            }
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return {'black_available': False}
        finally:
            if 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass
