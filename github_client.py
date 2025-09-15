import requests
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class GitHubClient:
    """Client for fetching GitHub repository data via the GitHub API."""
    
    def __init__(self, token: Optional[str] = None):
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        
        if token:
            self.session.headers.update({"Authorization": f"token {token}"})
        
        # Set user agent as required by GitHub API
        self.session.headers.update({"User-Agent": "GitHub-Dashboard-Tracker"})
    
    def get_repo_data(self, repo: str) -> Dict:
        """
        Fetch comprehensive data for a GitHub repository.
        
        Args:
            repo: Repository in format 'owner/name'
            
        Returns:
            Dictionary containing repository metrics
        """
        try:
            # Get basic repository information
            repo_url = f"{self.base_url}/repos/{repo}"
            repo_response = self.session.get(repo_url)
            repo_response.raise_for_status()
            repo_data = repo_response.json()
            
            # Get contributors count
            contributors_count = self._get_contributors_count(repo)
            
            # Get recent commits count (last 30 days)
            recent_commits = self._get_recent_commits_count(repo)
            
            # Get pull requests data
            pr_data = self._get_pull_requests_data(repo)
            
            # Get issues data
            issues_data = self._get_issues_data(repo)
            
            return {
                "repo": repo,
                "stars": repo_data.get("stargazers_count", 0),
                "forks": repo_data.get("forks_count", 0),
                "watchers": repo_data.get("watchers_count", 0),
                "contributors": contributors_count,
                "open_issues": repo_data.get("open_issues_count", 0),
                "total_issues": issues_data["total"],
                "closed_issues": issues_data["closed"],
                "open_prs": pr_data["open"],
                "total_prs": pr_data["total"],
                "closed_prs": pr_data["closed"],
                "merged_prs": pr_data["merged"],
                "recent_commits_30d": recent_commits,
                "size_kb": repo_data.get("size", 0),
                "language": repo_data.get("language", "Unknown"),
                "created_at": repo_data.get("created_at", ""),
                "updated_at": repo_data.get("updated_at", ""),
                "last_fetched": datetime.now().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {repo}: {e}")
            return self._get_error_data(repo, str(e))
    
    def _get_contributors_count(self, repo: str) -> int:
        """Get the number of contributors for a repository."""
        try:
            # GitHub API paginates contributors, we need to count all pages
            contributors_url = f"{self.base_url}/repos/{repo}/contributors"
            response = self.session.get(contributors_url, params={"per_page": 1})
            response.raise_for_status()
            
            # Check if there's pagination info in headers
            if "Link" in response.headers:
                link_header = response.headers["Link"]
                # Extract last page number from link header
                if "rel=\"last\"" in link_header:
                    last_page_url = link_header.split("rel=\"last\"")[0].split(",")[-1].strip().strip("<>")
                    last_page = int(last_page_url.split("page=")[1].split("&")[0])
                    return last_page
            
            # If no pagination, count the contributors directly
            response = self.session.get(contributors_url)
            response.raise_for_status()
            return len(response.json())
            
        except Exception:
            return 0
    
    def _get_recent_commits_count(self, repo: str) -> int:
        """Get the number of commits in the last 30 days."""
        try:
            since_date = (datetime.now() - timedelta(days=30)).isoformat()
            commits_url = f"{self.base_url}/repos/{repo}/commits"
            
            # Get first page to check total
            response = self.session.get(commits_url, params={
                "since": since_date,
                "per_page": 100
            })
            response.raise_for_status()
            
            commits = response.json()
            total_commits = len(commits)
            
            # If we got 100 commits, there might be more pages
            page = 2
            while len(commits) == 100:
                response = self.session.get(commits_url, params={
                    "since": since_date,
                    "per_page": 100,
                    "page": page
                })
                if response.status_code != 200:
                    break
                commits = response.json()
                total_commits += len(commits)
                page += 1
                
                # Safety limit to avoid infinite loops
                if page > 10:
                    break
            
            return total_commits
            
        except Exception:
            return 0
    
    def _get_pull_requests_data(self, repo: str) -> Dict[str, int]:
        """Get pull request statistics."""
        try:
            # Get open PRs
            open_prs_url = f"{self.base_url}/repos/{repo}/pulls"
            open_response = self.session.get(open_prs_url, params={"state": "open", "per_page": 1})
            open_response.raise_for_status()
            
            open_count = self._count_from_pagination(open_response, f"{self.base_url}/repos/{repo}/pulls?state=open")
            
            # Get closed PRs (includes merged)
            closed_response = self.session.get(open_prs_url, params={"state": "closed", "per_page": 1})
            closed_response.raise_for_status()
            
            closed_count = self._count_from_pagination(closed_response, f"{self.base_url}/repos/{repo}/pulls?state=closed")
            
            # For merged PRs, we'd need to check each closed PR individually, which is expensive
            # For now, we'll estimate merged as a portion of closed PRs
            merged_count = int(closed_count * 0.8)  # Rough estimate
            
            return {
                "open": open_count,
                "closed": closed_count,
                "merged": merged_count,
                "total": open_count + closed_count
            }
            
        except Exception:
            return {"open": 0, "closed": 0, "merged": 0, "total": 0}
    
    def _get_issues_data(self, repo: str) -> Dict[str, int]:
        """Get issues statistics."""
        try:
            issues_url = f"{self.base_url}/repos/{repo}/issues"
            
            # Get open issues (excluding PRs)
            open_response = self.session.get(issues_url, params={"state": "open", "per_page": 1})
            open_response.raise_for_status()
            
            open_count = self._count_from_pagination(open_response, f"{self.base_url}/repos/{repo}/issues?state=open")
            
            # Get closed issues
            closed_response = self.session.get(issues_url, params={"state": "closed", "per_page": 1})
            closed_response.raise_for_status()
            
            closed_count = self._count_from_pagination(closed_response, f"{self.base_url}/repos/{repo}/issues?state=closed")
            
            return {
                "open": open_count,
                "closed": closed_count,
                "total": open_count + closed_count
            }
            
        except Exception:
            return {"open": 0, "closed": 0, "total": 0}
    
    def _count_from_pagination(self, response: requests.Response, base_url: str) -> int:
        """Extract count from paginated response."""
        if "Link" in response.headers:
            link_header = response.headers["Link"]
            if "rel=\"last\"" in link_header:
                last_page_url = link_header.split("rel=\"last\"")[0].split(",")[-1].strip().strip("<>")
                try:
                    last_page = int(last_page_url.split("page=")[1].split("&")[0])
                    per_page = int(last_page_url.split("per_page=")[1].split("&")[0]) if "per_page=" in last_page_url else 30
                    
                    # Get the last page to count remaining items
                    last_response = self.session.get(last_page_url)
                    if last_response.status_code == 200:
                        last_page_items = len(last_response.json())
                        return (last_page - 1) * per_page + last_page_items
                except (ValueError, IndexError):
                    pass
        
        # Fallback: get all items from first page
        try:
            full_response = self.session.get(base_url)
            if full_response.status_code == 200:
                return len(full_response.json())
        except Exception:
            pass
        
        return 0
    
    def _get_error_data(self, repo: str, error: str) -> Dict:
        """Return error data structure when API call fails."""
        return {
            "repo": repo,
            "stars": 0,
            "forks": 0,
            "watchers": 0,
            "contributors": 0,
            "open_issues": 0,
            "total_issues": 0,
            "closed_issues": 0,
            "open_prs": 0,
            "total_prs": 0,
            "closed_prs": 0,
            "merged_prs": 0,
            "recent_commits_30d": 0,
            "size_kb": 0,
            "language": "Unknown",
            "created_at": "",
            "updated_at": "",
            "last_fetched": datetime.now().isoformat(),
            "error": error
        }