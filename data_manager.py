import csv
import os
from datetime import datetime, timedelta
from typing import List, Dict
from github_client import GitHubClient


class DataManager:
    """Manages data collection and CSV storage for GitHub repository metrics."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.csv_file = os.path.join(data_dir, "github_metrics.csv")
        self.last_update_file = os.path.join(data_dir, "last_update.txt")
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # CSV headers
        self.headers = [
            "repo", "stars", "forks", "watchers", "contributors",
            "open_issues", "total_issues", "closed_issues",
            "open_prs", "total_prs", "closed_prs", "merged_prs",
            "recent_commits_30d", "size_kb", "language",
            "created_at", "updated_at", "last_fetched"
        ]
    
    def should_update(self) -> bool:
        """Check if data should be updated (every 7 days)."""
        if not os.path.exists(self.last_update_file):
            return True
        
        try:
            with open(self.last_update_file, 'r') as f:
                last_update_str = f.read().strip()
                last_update = datetime.fromisoformat(last_update_str)
                
                # Check if 7 days have passed
                return datetime.now() - last_update >= timedelta(days=7)
        except (ValueError, FileNotFoundError):
            return True
    
    def load_repositories(self, repos_file: str = "env/repos.txt") -> List[str]:
        """Load repository list from configuration file."""
        repos = []
        
        if not os.path.exists(repos_file):
            print(f"Repository configuration file not found: {repos_file}")
            return repos
        
        try:
            with open(repos_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        repos.append(line)
        except Exception as e:
            print(f"Error reading repositories file: {e}")
        
        return repos
    
    def collect_and_save_data(self, github_token: str = None, force_update: bool = False):
        """Collect data from GitHub API and save to CSV."""
        if not force_update and not self.should_update():
            print("Data is up to date. Use force_update=True to refresh anyway.")
            return
        
        # Load repositories to track
        repos = self.load_repositories()
        if not repos:
            print("No repositories configured. Please add repositories to env/repos.txt")
            return
        
        print(f"Collecting data for {len(repos)} repositories...")
        
        # Initialize GitHub client
        client = GitHubClient(github_token)
        
        # Collect data for all repositories
        all_data = []
        for i, repo in enumerate(repos, 1):
            print(f"Fetching data for {repo} ({i}/{len(repos)})...")
            repo_data = client.get_repo_data(repo)
            all_data.append(repo_data)
        
        # Save to CSV
        self._save_to_csv(all_data)
        
        # Update last update timestamp
        self._update_timestamp()
        
        print(f"Data collection complete. Results saved to {self.csv_file}")
    
    def _save_to_csv(self, data: List[Dict]):
        """Save repository data to CSV file."""
        try:
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.headers)
                writer.writeheader()
                
                for repo_data in data:
                    # Filter out any extra fields not in headers
                    filtered_data = {k: v for k, v in repo_data.items() if k in self.headers}
                    writer.writerow(filtered_data)
                    
        except Exception as e:
            print(f"Error saving data to CSV: {e}")
    
    def _update_timestamp(self):
        """Update the last update timestamp."""
        try:
            with open(self.last_update_file, 'w') as f:
                f.write(datetime.now().isoformat())
        except Exception as e:
            print(f"Error updating timestamp: {e}")
    
    def get_summary(self) -> Dict:
        """Get a summary of the current data."""
        if not os.path.exists(self.csv_file):
            return {"error": "No data file found. Run data collection first."}
        
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
            
            if not data:
                return {"error": "No data in CSV file."}
            
            # Calculate summary statistics
            total_repos = len(data)
            total_stars = sum(int(row.get('stars', 0)) for row in data)
            total_forks = sum(int(row.get('forks', 0)) for row in data)
            total_contributors = sum(int(row.get('contributors', 0)) for row in data)
            
            # Get last update time
            last_update = "Unknown"
            if os.path.exists(self.last_update_file):
                try:
                    with open(self.last_update_file, 'r') as f:
                        last_update = f.read().strip()
                except Exception:
                    pass
            
            return {
                "total_repositories": total_repos,
                "total_stars": total_stars,
                "total_forks": total_forks,
                "total_contributors": total_contributors,
                "last_update": last_update,
                "csv_file": self.csv_file
            }
            
        except Exception as e:
            return {"error": f"Error reading data: {e}"}
    
    def display_data(self):
        """Display current data in a readable format."""
        if not os.path.exists(self.csv_file):
            print("No data file found. Run data collection first.")
            return
        
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
            
            if not data:
                print("No data in CSV file.")
                return
            
            print(f"\n{'Repository':<30} {'Stars':<8} {'Forks':<8} {'Contributors':<12} {'Open PRs':<10} {'Language':<15}")
            print("-" * 90)
            
            for row in data:
                repo = row.get('repo', 'Unknown')[:29]
                stars = row.get('stars', '0')
                forks = row.get('forks', '0')
                contributors = row.get('contributors', '0')
                open_prs = row.get('open_prs', '0')
                language = row.get('language', 'Unknown')[:14]
                
                print(f"{repo:<30} {stars:<8} {forks:<8} {contributors:<12} {open_prs:<10} {language:<15}")
            
            # Display summary
            summary = self.get_summary()
            print(f"\nSummary:")
            print(f"Total Repositories: {summary.get('total_repositories', 0)}")
            print(f"Total Stars: {summary.get('total_stars', 0):,}")
            print(f"Total Forks: {summary.get('total_forks', 0):,}")
            print(f"Total Contributors: {summary.get('total_contributors', 0):,}")
            print(f"Last Updated: {summary.get('last_update', 'Unknown')}")
            
        except Exception as e:
            print(f"Error displaying data: {e}")