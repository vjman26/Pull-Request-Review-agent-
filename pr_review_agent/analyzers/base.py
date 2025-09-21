"""Base analyzer interface for code analysis."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pr_review_agent.core.models import CodeIssue, AnalysisConfig


class CodeAnalyzer(ABC):
    """Abstract base class for code analyzers."""

    def __init__(self, config: AnalysisConfig):
        """Initialize the analyzer with configuration."""
        self.config = config

    @abstractmethod
    def analyze(self, file_path: str, content: str) -> List[CodeIssue]:
        """Analyze a file and return list of issues."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of this analyzer."""
        pass

    def should_analyze(self, file_path: str) -> bool:
        """Check if this file should be analyzed by this analyzer."""
        # Default implementation - can be overridden
        return True

    def get_metrics(self, file_path: str, content: str) -> Dict[str, Any]:
        """Get additional metrics for the file."""
        return {}
