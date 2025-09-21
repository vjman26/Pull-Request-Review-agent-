"""Flake8 analyzer for code style and quality."""

import subprocess
import tempfile
import os
from typing import List, Dict, Any
from pr_review_agent.core.models import CodeIssue, AnalysisConfig, IssueSeverity, IssueCategory


class Flake8Analyzer:
    """Flake8-based code analyzer."""

    def __init__(self, config: AnalysisConfig):
        """Initialize Flake8 analyzer."""
        self.config = config

    def analyze(self, file_path: str, content: str) -> List[CodeIssue]:
        """Analyze file using Flake8."""
        if not self.should_analyze(file_path):
            return []

        issues = []
        
        try:
            # Create temporary file for analysis
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name

            # Run flake8
            result = subprocess.run([
                'flake8',
                '--format=%(path)s:%(row)d:%(col)d: %(code)s %(text)s',
                temp_file_path
            ], capture_output=True, text=True, timeout=30)

            # Parse output
            if result.stdout:
                issues.extend(self._parse_output(result.stdout, file_path))

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            # Flake8 not available or failed
            pass
        finally:
            # Clean up temporary file
            if 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass

        return issues

    def _parse_output(self, output: str, file_path: str) -> List[CodeIssue]:
        """Parse Flake8 output."""
        issues = []
        lines = output.strip().split('\n')
        
        for line in lines:
            if ':' in line:
                parts = line.split(':', 3)
                if len(parts) >= 4:
                    line_num = int(parts[1]) if parts[1].isdigit() else 1
                    col_num = int(parts[2]) if parts[2].isdigit() else None
                    code_and_message = parts[3].strip()
                    
                    # Extract code and message
                    if ' ' in code_and_message:
                        code, message = code_and_message.split(' ', 1)
                    else:
                        code = code_and_message
                        message = code_and_message
                    
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=line_num,
                        column_number=col_num,
                        severity=self._get_severity(code),
                        category=self._get_category(code),
                        message=message,
                        rule_id=code,
                        suggestion=self._get_suggestion(code)
                    ))
        
        return issues

    def _get_severity(self, code: str) -> IssueSeverity:
        """Get severity based on Flake8 error code."""
        if code.startswith('E'):
            return IssueSeverity.HIGH
        elif code.startswith('W'):
            return IssueSeverity.MEDIUM
        elif code.startswith('F'):
            return IssueSeverity.CRITICAL
        else:
            return IssueSeverity.LOW

    def _get_category(self, code: str) -> IssueCategory:
        """Get category based on Flake8 error code."""
        if code.startswith('E'):
            return IssueCategory.BUG
        elif code.startswith('W'):
            return IssueCategory.READABILITY
        elif code.startswith('F'):
            return IssueCategory.BUG
        elif code.startswith('C'):
            return IssueCategory.STYLE
        else:
            return IssueCategory.READABILITY

    def _get_suggestion(self, code: str) -> str:
        """Get suggestion based on Flake8 error code."""
        suggestions = {
            'E501': "Line too long - consider breaking into multiple lines",
            'E302': "Expected 2 blank lines before function definition",
            'E305': "Expected 2 blank lines after class definition",
            'E111': "Indentation is not a multiple of 4",
            'E112': "Expected an indented block",
            'E113': "Unexpected indentation",
            'E114': "Indentation is not a multiple of 4 (comment)",
            'E115': "Expected an indented block (comment)",
            'E116': "Unexpected indentation (comment)",
            'E117': "Over-indented",
            'E201': "Whitespace after '['",
            'E202': "Whitespace before ']'",
            'E203': "Whitespace before ':'",
            'E211': "Whitespace before '('",
            'E221': "Multiple spaces before operator",
            'E222': "Multiple spaces after operator",
            'E223': "Tab before operator",
            'E224': "Tab after operator",
            'E225': "Missing whitespace around operator",
            'E226': "Missing whitespace around arithmetic operator",
            'E227': "Missing whitespace around bitwise or shift operator",
            'E228': "Missing whitespace around modulo operator",
            'E231': "Missing whitespace after ','",
            'E241': "Multiple spaces after ','",
            'E242': "Tab after ','",
            'E251': "Unexpected spaces around keyword / parameter equals",
            'E261': "At least two spaces before inline comment",
            'E262': "Inline comment should start with '# '",
            'E265': "Block comment should start with '# '",
            'E266': "Too many leading '#' for block comment",
            'E271': "Multiple spaces after keyword",
            'E272': "Multiple spaces before keyword",
            'E273': "Tab after keyword",
            'E274': "Tab before keyword",
            'E275': "Missing whitespace after keyword",
            'E301': "Expected 1 blank line",
            'E303': "Too many blank lines",
            'E304': "Blank lines found after function decorator",
            'E306': "Expected 1 blank line before a nested definition",
            'E401': "Multiple imports on one line",
            'E402': "Module level import not at top of file",
            'E501': "Line too long",
            'E502': "The backslash is redundant between brackets",
            'E701': "Multiple statements on one line (colon)",
            'E702': "Multiple statements on one line (semicolon)",
            'E703': "Statement ends with a semicolon",
            'E704': "Multiple statements on one line (def)",
            'E711': "Comparison to None should be 'cond is None'",
            'E712': "Comparison to True should be 'cond is True' or 'if cond:'",
            'E713': "Test for membership should be 'not in'",
            'E714': "Test for object identity should be 'is not'",
            'E721': "Do not compare types, use 'isinstance()'",
            'E722': "Do not use bare 'except'",
            'E731': "Do not assign a lambda expression, use a def",
            'E741': "Do not use variables named 'l', 'O', or 'I'",
            'E742': "Do not define classes named 'l', 'O', or 'I'",
            'E743': "Do not define functions named 'l', 'O', or 'I'",
            'W191': "Indentation contains tabs",
            'W291': "Trailing whitespace",
            'W292': "No newline at end of file",
            'W293': "Blank line contains whitespace",
            'W391': "Blank line at end of file",
            'W503': "Line break occurred before binary operator",
            'W504': "Line break occurred after binary operator",
            'W601': ".has_key() is deprecated, use 'in'",
            'W602': "Using deprecated exception syntax",
            'W603': "'<>' is deprecated, use '!='",
            'W604': "Backticks are deprecated, use 'repr()'",
            'W605': "Invalid escape sequence",
            'W606': "'async' and 'await' are reserved keywords starting with Python 3.7",
            'F401': "Imported but unused",
            'F402': "Import module level import not at top of file",
            'F403': "Star import used",
            'F404': "Future import(s) after other statements",
            'F405': "Name may be undefined, or defined from star imports",
            'F406': "Cannot import from module level",
            'F407': "An import does not have a corresponding 'from' import",
            'F501': "Percent-encoded string is not valid",
            'F502': "Cannot use 'f' strings in 'except' clause",
            'F503': "Cannot use 'f' strings in 'except' clause",
            'F504': "Percent-encoded string is not valid",
            'F505': "Cannot use 'f' strings in 'except' clause",
            'F506': "Cannot use 'f' strings in 'except' clause",
            'F507': "Cannot use 'f' strings in 'except' clause",
            'F508': "Cannot use 'f' strings in 'except' clause",
            'F509': "Cannot use 'f' strings in 'except' clause",
            'F601': "Dictionary key name repeated",
            'F602': "Dictionary key name repeated",
            'F621': "Cannot use 'f' strings in 'except' clause",
            'F622': "Cannot use 'f' strings in 'except' clause",
            'F631': "Cannot use 'f' strings in 'except' clause",
            'F701': "A break statement outside of a for or while loop",
            'F702': "A continue statement outside of a for or while loop",
            'F703': "A break statement outside of a for or while loop",
            'F704': "A continue statement outside of a for or while loop",
            'F705': "A break statement outside of a for or while loop",
            'F706': "A continue statement outside of a for or while loop",
            'F707': "A break statement outside of a for or while loop",
            'F708': "A continue statement outside of a for or while loop",
            'F721': "Syntax error in forward annotation",
            'F722': "Syntax error in forward annotation",
            'F731': "Empty class definition",
            'F732': "Empty class definition",
            'F811': "Redefinition of unused name",
            'F812': "List comprehension redefines 'list' from line",
            'F821': "Undefined name",
            'F822': "Undefined name in __all__",
            'F831': "Redefinition of unused name",
            'F841': "Local variable is assigned to but never used",
            'F901': "Raise NotImplementedError",
            'F902': "Invalid forward reference",
            'F903': "Invalid forward reference",
            'F904': "Invalid forward reference",
            'F905': "Invalid forward reference",
            'F906': "Invalid forward reference",
            'F907': "Invalid forward reference",
            'F908': "Invalid forward reference",
            'F909': "Invalid forward reference",
            'F910': "Invalid forward reference",
            'F911': "Invalid forward reference",
            'F912': "Invalid forward reference",
            'F913': "Invalid forward reference",
            'F914': "Invalid forward reference",
            'F915': "Invalid forward reference",
            'F916': "Invalid forward reference",
            'F917': "Invalid forward reference",
            'F918': "Invalid forward reference",
            'F919': "Invalid forward reference",
            'F920': "Invalid forward reference",
            'F921': "Invalid forward reference",
            'F922': "Invalid forward reference",
            'F923': "Invalid forward reference",
            'F924': "Invalid forward reference",
            'F925': "Invalid forward reference",
            'F926': "Invalid forward reference",
            'F927': "Invalid forward reference",
            'F928': "Invalid forward reference",
            'F929': "Invalid forward reference",
            'F930': "Invalid forward reference",
            'F931': "Invalid forward reference",
            'F932': "Invalid forward reference",
            'F933': "Invalid forward reference",
            'F934': "Invalid forward reference",
            'F935': "Invalid forward reference",
            'F936': "Invalid forward reference",
            'F937': "Invalid forward reference",
            'F938': "Invalid forward reference",
            'F939': "Invalid forward reference",
            'F940': "Invalid forward reference",
            'F941': "Invalid forward reference",
            'F942': "Invalid forward reference",
            'F943': "Invalid forward reference",
            'F944': "Invalid forward reference",
            'F945': "Invalid forward reference",
            'F946': "Invalid forward reference",
            'F947': "Invalid forward reference",
            'F948': "Invalid forward reference",
            'F949': "Invalid forward reference",
            'F950': "Invalid forward reference",
            'F951': "Invalid forward reference",
            'F952': "Invalid forward reference",
            'F953': "Invalid forward reference",
            'F954': "Invalid forward reference",
            'F955': "Invalid forward reference",
            'F956': "Invalid forward reference",
            'F957': "Invalid forward reference",
            'F958': "Invalid forward reference",
            'F959': "Invalid forward reference",
            'F960': "Invalid forward reference",
            'F961': "Invalid forward reference",
            'F962': "Invalid forward reference",
            'F963': "Invalid forward reference",
            'F964': "Invalid forward reference",
            'F965': "Invalid forward reference",
            'F966': "Invalid forward reference",
            'F967': "Invalid forward reference",
            'F968': "Invalid forward reference",
            'F969': "Invalid forward reference",
            'F970': "Invalid forward reference",
            'F971': "Invalid forward reference",
            'F972': "Invalid forward reference",
            'F973': "Invalid forward reference",
            'F974': "Invalid forward reference",
            'F975': "Invalid forward reference",
            'F976': "Invalid forward reference",
            'F977': "Invalid forward reference",
            'F978': "Invalid forward reference",
            'F979': "Invalid forward reference",
            'F980': "Invalid forward reference",
            'F981': "Invalid forward reference",
            'F982': "Invalid forward reference",
            'F983': "Invalid forward reference",
            'F984': "Invalid forward reference",
            'F985': "Invalid forward reference",
            'F986': "Invalid forward reference",
            'F987': "Invalid forward reference",
            'F988': "Invalid forward reference",
            'F989': "Invalid forward reference",
            'F990': "Invalid forward reference",
            'F991': "Invalid forward reference",
            'F992': "Invalid forward reference",
            'F993': "Invalid forward reference",
            'F994': "Invalid forward reference",
            'F995': "Invalid forward reference",
            'F996': "Invalid forward reference",
            'F997': "Invalid forward reference",
            'F998': "Invalid forward reference",
            'F999': "Invalid forward reference"
        }
        return suggestions.get(code, "")

    def should_analyze(self, file_path: str) -> bool:
        """Check if file should be analyzed by Flake8."""
        return file_path.endswith('.py')

    def get_name(self) -> str:
        """Get analyzer name."""
        return "Flake8"

    def get_metrics(self, file_path: str, content: str) -> Dict[str, Any]:
        """Get Flake8 metrics."""
        if not self.should_analyze(file_path):
            return {}

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name

            result = subprocess.run([
                'flake8',
                '--count',
                '--statistics',
                temp_file_path
            ], capture_output=True, text=True, timeout=30)

            if result.stdout:
                lines = result.stdout.strip().split('\n')
                if lines and lines[-1]:
                    # Parse statistics line
                    stats = lines[-1].split()
                    if len(stats) >= 2:
                        return {
                            'flake8_issues_count': int(stats[0]) if stats[0].isdigit() else 0,
                            'flake8_files_analyzed': int(stats[1]) if stats[1].isdigit() else 0
                        }
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        finally:
            if 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass

        return {}
