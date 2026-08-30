import httpx
from typing import Dict, Any, List, Optional
import re
from app.core.config import settings

class GitHubAPIError(Exception):
    """Custom exception triggered when the GitHub API returns an error or rate limit."""
    pass

class GitHubClient:
    """
    Client wrapper for GitHub API v3.
    Requires GITHUB_TOKEN for higher rate limits (5000/hr) vs (60/hr).
    """
    
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Codebase-Investigator"
        }
        
        if settings.GITHUB_TOKEN:
            self.headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"

    def parse_url(self, url: str) -> tuple[str, str]:
        """
        Parses a typical github url (https://github.com/owner/repo) into a tuple (owner, repo).
        """
        match = re.search(r"github\.com/([^/]+)/([^/]+)", url)
        if not match:
            raise ValueError("Invalid GitHub URL provided.")
            
        owner = match.group(1)
        repo = match.group(2).replace(".git", "")
        return owner, repo

    async def get_repo_metadata(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetches repository metadata, including default branch and latest commit info."""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            
            if response.status_code != 200:
                raise GitHubAPIError(f"Failed to fetch metadata (Status: {response.status_code}): {response.text}")
                
            data = response.json()
            
            # Fetch latest commit SHA on default branch
            default_branch = data.get("default_branch", "main")
            commit_url = f"{self.base_url}/repos/{owner}/{repo}/commits/{default_branch}"
            
            commit_resp = await client.get(commit_url, headers=self.headers)
            commit_sha = ""
            if commit_resp.status_code == 200:
                commit_sha = commit_resp.json().get("sha", "")
                
            return {
                "name": data.get("name"),
                "owner": data.get("owner", {}).get("login"),
                "default_branch": default_branch,
                "commit_sha": commit_sha
            }

    async def get_repo_tree(self, owner: str, repo: str, commit_sha: str) -> List[Dict[str, Any]]:
        """
        Retrieves the flat recursive tree representation of the repository.
        Returns a list of dicts with 'path', 'type' (blob/tree), and 'url' (for downloading content).
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/{commit_sha}?recursive=1"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            
            if response.status_code != 200:
                raise GitHubAPIError(f"Failed to fetch repo tree (Status: {response.status_code}): {response.text}")
                
            data = response.json()
            return data.get("tree", [])

    async def get_file_content(self, download_url: str) -> str:
        """
        Given a raw download URL, fetches the textual content.
        Uses a standard HTTP GET without the strict GitHub API Authorization header 
        if downloading raw.githubusercontent domains (though having the token is fine).
        """
        async with httpx.AsyncClient() as client:
            # For raw file downloads via the API url style (blob API):
            # Normally tree returns git urls like "https://api.github.com/repos/x/y/git/blobs/sha"
            # We must use Accept: application/vnd.github.v3.raw or base64 decode it
            headers = self.headers.copy()
            headers["Accept"] = "application/vnd.github.v3.raw"
            
            response = await client.get(download_url, headers=headers)
            
            if response.status_code != 200:
                raise GitHubAPIError(f"Failed to fetch content from {download_url} (Status: {response.status_code})")
                
            try:
                # GitHub blobs might be returned as strings (already decoded due to the raw Accept header)
                # Ensure we capture it as text. If it fails decoding, it might be binary that we didn't filter out.
                return response.text
            except Exception as e:
                # In case decoding fails, gracefully return empty string or raise
                raise GitHubAPIError(f"Failed to parse content as text: {str(e)}")

# Singleton instance for easy dependency injection if needed
github_client = GitHubClient()
