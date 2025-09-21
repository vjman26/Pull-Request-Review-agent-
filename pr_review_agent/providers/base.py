"""Base provider interface for git servers."""

from abc import ABC, abstractmethod
from typing import List, Optional
from ..core.models import PRInfo


class PRProvider(ABC):
    """Abstract base class for PR providers."""

    def __init__(self, token: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize the provider with authentication credentials."""
        self.token = token
        self.base_url = base_url

    @abstractmethod
    def get_pr_info(self, repo: str, pr_number: int) -> PRInfo:
        """Fetch pull request information."""
        pass

    @abstractmethod
    def get_pr_files(self, repo: str, pr_number: int) -> List[str]:
        """Get list of files changed in the PR."""
        pass

    @abstractmethod
    def get_file_content(self, repo: str, file_path: str, ref: str) -> str:
        """Get file content at a specific reference."""
        pass

    @abstractmethod
    def get_diff(self, repo: str, pr_number: int) -> str:
        """Get the diff for the pull request."""
        pass

    @abstractmethod
    def post_comment(self, repo: str, pr_number: int, comment: str, 
                    file_path: Optional[str] = None, 
                    line_number: Optional[int] = None) -> bool:
        """Post a comment on the pull request."""
        pass

    @abstractmethod
    def get_commits(self, repo: str, pr_number: int) -> List[dict]:
        """Get commits in the pull request."""
        pass

    def validate_repo(self, repo: str) -> bool:
        """Validate repository format."""
        return "/" in repo and len(repo.split("/")) == 2
