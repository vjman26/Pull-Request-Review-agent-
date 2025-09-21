"""Bitbucket provider implementation."""

import requests
from typing import List, Optional
from datetime import datetime
from pr_review_agent.core.models import PRInfo


class BitbucketProvider:
    """Bitbucket API provider for pull requests."""

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None, 
                 base_url: str = "https://api.bitbucket.org"):
        """Initialize Bitbucket provider."""
        self.username = username
        self.password = password
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/2.0"
        self.session = requests.Session()
        
        if self.username and self.password:
            self.session.auth = (self.username, self.password)

    def get_pr_info(self, repo: str, pr_number: int) -> PRInfo:
        """Fetch pull request information from Bitbucket."""
        url = f"{self.api_url}/repositories/{repo}/pullrequests/{pr_number}"
        response = self.session.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        return PRInfo(
            number=data["id"],
            title=data["title"],
            description=data["description"] or "",
            author=data["author"]["display_name"],
            created_at=datetime.fromisoformat(data["created_on"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data["updated_on"].replace("Z", "+00:00")),
            base_branch=data["destination"]["branch"]["name"],
            head_branch=data["source"]["branch"]["name"],
            files_changed=self.get_pr_files(repo, pr_number),
            additions=data["summary"]["additions"],
            deletions=data["summary"]["deletions"],
            commits=len(self.get_commits(repo, pr_number))
        )

    def get_pr_files(self, repo: str, pr_number: int) -> List[str]:
        """Get list of files changed in the PR."""
        url = f"{self.api_url}/repositories/{repo}/pullrequests/{pr_number}/diffstat"
        response = self.session.get(url)
        response.raise_for_status()
        
        data = response.json()
        return [file["new"]["path"] for file in data["values"] if "new" in file]

    def get_file_content(self, repo: str, file_path: str, ref: str) -> str:
        """Get file content at a specific reference."""
        url = f"{self.api_url}/repositories/{repo}/src/{ref}/{file_path}"
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.text

    def get_diff(self, repo: str, pr_number: int) -> str:
        """Get the diff for the pull request."""
        url = f"{self.api_url}/repositories/{repo}/pullrequests/{pr_number}/diff"
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.text

    def post_comment(self, repo: str, pr_number: int, comment: str, 
                    file_path: Optional[str] = None, 
                    line_number: Optional[int] = None) -> bool:
        """Post a comment on the pull request."""
        url = f"{self.api_url}/repositories/{repo}/pullrequests/{pr_number}/comments"
        
        payload = {"content": {"raw": comment}}
        
        if file_path and line_number:
            # Bitbucket inline comments require more complex structure
            payload.update({
                "inline": {
                    "path": file_path,
                    "to": line_number
                }
            })
        
        response = self.session.post(url, json=payload)
        return response.status_code == 201

    def get_commits(self, repo: str, pr_number: int) -> List[dict]:
        """Get commits in the pull request."""
        url = f"{self.api_url}/repositories/{repo}/pullrequests/{pr_number}/commits"
        response = self.session.get(url)
        response.raise_for_status()
        
        data = response.json()
        return data["values"]
