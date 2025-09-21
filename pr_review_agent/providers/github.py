"""GitHub provider implementation."""

import requests
from typing import List, Optional
from datetime import datetime
from pr_review_agent.core.models import PRInfo


class GitHubProvider:
    """GitHub API provider for pull requests."""

    def __init__(self, token: Optional[str] = None, base_url: str = "https://api.github.com"):
        """Initialize GitHub provider."""
        self.token = token
        self.base_url = base_url
        self.session = requests.Session()
        
        if self.token:
            self.session.headers.update({
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            })

    def get_pr_info(self, repo: str, pr_number: int) -> PRInfo:
        """Fetch pull request information from GitHub."""
        url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}"
        response = self.session.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        return PRInfo(
            number=data["number"],
            title=data["title"],
            description=data["body"] or "",
            author=data["user"]["login"],
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")),
            base_branch=data["base"]["ref"],
            head_branch=data["head"]["ref"],
            files_changed=self.get_pr_files(repo, pr_number),
            additions=data["additions"],
            deletions=data["deletions"],
            commits=data["commits"]
        )

    def get_pr_files(self, repo: str, pr_number: int) -> List[str]:
        """Get list of files changed in the PR."""
        url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}/files"
        response = self.session.get(url)
        response.raise_for_status()
        
        files = response.json()
        return [file["filename"] for file in files]

    def get_file_content(self, repo: str, file_path: str, ref: str) -> str:
        """Get file content at a specific reference."""
        url = f"{self.base_url}/repos/{repo}/contents/{file_path}"
        params = {"ref": ref}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        import base64
        return base64.b64decode(data["content"]).decode("utf-8")

    def get_diff(self, repo: str, pr_number: int) -> str:
        """Get the diff for the pull request."""
        url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}"
        headers = {"Accept": "application/vnd.github.v3.diff"}
        response = self.session.get(url, headers=headers)
        response.raise_for_status()
        
        return response.text

    def post_comment(self, repo: str, pr_number: int, comment: str, 
                    file_path: Optional[str] = None, 
                    line_number: Optional[int] = None) -> bool:
        """Post a comment on the pull request."""
        url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}/comments"
        
        payload = {"body": comment}
        
        if file_path and line_number:
            # Get the diff to find the commit SHA and position
            diff = self.get_diff(repo, pr_number)
            # This is simplified - in practice, you'd need to parse the diff
            # to find the correct position for inline comments
            payload.update({
                "path": file_path,
                "line": line_number,
                "side": "RIGHT"
            })
        
        response = self.session.post(url, json=payload)
        return response.status_code == 201

    def get_commits(self, repo: str, pr_number: int) -> List[dict]:
        """Get commits in the pull request."""
        url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}/commits"
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.json()
