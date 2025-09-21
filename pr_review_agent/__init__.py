"""
PR Review Agent - A comprehensive pull request review system.

This package provides tools for analyzing pull requests from multiple git servers
and generating intelligent feedback on code quality, standards, and potential issues.
"""

__version__ = "1.0.0"
__author__ = "PR Review Agent Team"

from .core.agent import PRReviewAgent
from .core.models import PRReviewResult, ReviewFeedback, CodeIssue
from .providers.base import PRProvider
from .analyzers.base import CodeAnalyzer

__all__ = [
    "PRReviewAgent",
    "PRReviewResult", 
    "ReviewFeedback",
    "CodeIssue",
    "PRProvider",
    "CodeAnalyzer",
]
