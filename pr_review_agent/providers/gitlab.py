"""GitLab provider implementation."""

import requests
from typing import List, Optional
from datetime import datetime
from pr_review_agent.core.models import PRInfo


class GitLabProvider:
    """GitLab API provider for merge requests."""

    def __init__(self, token: Optional[str] = None, base_url: str = "https://gitlab.com"):
        """Initialize GitLab provider."""
        self.token = token
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/api/v4"
        self.session = requests.Session()
        
        if self.token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            })

    def get_pr_info(self, repo: str, pr_number: int) -> PRInfo:
        """Fetch merge request information from GitLab."""
        # Convert repo format from owner/repo to owner%2Frepo for GitLab API
        encoded_repo = repo.replace("/", "%2F")
        url = f"{self.api_url}/projects/{encoded_repo}/merge_requests/{pr_number}"
        response = self.session.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        return PRInfo(
            number=data["iid"],
            title=data["title"],
            description=data["description"] or "",
            author=data["author"]["username"],
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")),
            base_branch=data["target_branch"],
            head_branch=data["source_branch"],
            files_changed=self.get_pr_files(repo, pr_number),
            additions=data["changes_count"]["additions"],
            deletions=data["changes_count"]["deletions"],
            commits=data["commits_count"]
        )

    def get_pr_files(self, repo: str, pr_number: int) -> List[str]:
        """Get list of files changed in the merge request."""
        encoded_repo = repo.replace("/", "%2F")
        url = f"{self.api_url}/projects/{encoded_repo}/merge_requests/{pr_number}/changes"
        response = self.session.get(url)
        response.raise_for_status()
        
        data = response.json()
        return [change["new_path"] for change in data["changes"] if change["new_path"]]

    def get_file_content(self, repo: str, file_path: str, ref: str) -> str:
        """Get file content at a specific reference."""
        encoded_repo = repo.replace("/", "%2F")
        encoded_file = file_path.replace("/", "%2F")
        url = f"{self.api_url}/projects/{encoded_repo}/repository/files/{encoded_file}/raw"
        params = {"ref": ref}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        return response.text

    def get_diff(self, repo: str, pr_number: int) -> str:
        """Get the diff for the merge request."""
        encoded_repo = repo.replace("/", "%2F")
        url = f"{self.api_url}/projects/{encoded_repo}/merge_requests/{pr_number}/changes"
        response = self.session.get(url)
        response.raise_for_status()
        
        data = response.json()
        return data["diff"]

    def post_comment(self, repo: str, pr_number: int, comment: str, 
                    file_path: Optional[str] = None, 
                    line_number: Optional[int] = None) -> bool:
        """Post a comment on the merge request."""
        encoded_repo = repo.replace("/", "%2F")
        url = f"{self.api_url}/projects/{encoded_repo}/merge_requests/{pr_number}/notes"
        
        payload = {"body": comment}
        
        if file_path and line_number:
            payload.update({
                "position": {
                    "base_sha": None,  # Would need to get from MR details
                    "start_sha": None,  # Would need to get from MR details
                    "head_sha": None,  # Would need to get from MR details
                    "old_path": file_path,
                    "new_path": file_path,
                    "position_type": "text",
                    "new_line": line_number
                }
            })
        
        response = self.session.post(url, json=payload)
        return response.status_code == 201

    def get_commits(self, repo: str, pr_number: int) -> List[dict]:
        """Get commits in the merge request."""
        encoded_repo = repo.replace("/", "%2F")
        url = f"{self.api_url}/projects/{encoded_repo}/merge_requests/{pr_number}/commits"
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.json()
