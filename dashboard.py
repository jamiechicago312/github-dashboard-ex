#!/usr/bin/env python3
"""
GitHub Repository Dashboard

A simple and lightweight tool to track metrics for multiple public GitHub repositories.
Collects data like stars, forks, contributors, PRs, commits, and more.
Data is refreshed every 7 days and saved to CSV.
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from data_manager import DataManager


def main():
    """Main entry point for the GitHub dashboard."""
    parser = argparse.ArgumentParser(
        description="GitHub Repository Dashboard - Track metrics for multiple repos"
    )
    parser.add_argument(
        "--update", 
        action="store_true", 
        help="Force update data (ignore 7-day refresh cycle)"
    )
    parser.add_argument(
        "--show", 
        action="store_true", 
        help="Display current data"
    )
    parser.add_argument(
        "--summary", 
        action="store_true", 
        help="Show summary statistics"
    )
    parser.add_argument(
        "--token", 
        type=str, 
        help="GitHub personal access token (optional, for higher rate limits)"
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Get GitHub token from args, environment, or use None
    github_token = args.token or os.getenv("GITHUB_TOKEN")
    
    # Initialize data manager
    data_manager = DataManager()
    
    # Handle different commands
    if args.show:
        data_manager.display_data()
    elif args.summary:
        summary = data_manager.get_summary()
        if "error" in summary:
            print(f"Error: {summary['error']}")
        else:
            print("GitHub Dashboard Summary:")
            print(f"Total Repositories: {summary['total_repositories']}")
            print(f"Total Stars: {summary['total_stars']:,}")
            print(f"Total Forks: {summary['total_forks']:,}")
            print(f"Total Contributors: {summary['total_contributors']:,}")
            print(f"Last Updated: {summary['last_update']}")
            print(f"Data File: {summary['csv_file']}")
    elif args.update:
        data_manager.collect_and_save_data(github_token, force_update=True)
    else:
        # Default behavior: check if update is needed and collect data
        print("GitHub Repository Dashboard")
        print("=" * 40)
        
        if data_manager.should_update():
            print("Data needs updating (7+ days old or missing).")
            data_manager.collect_and_save_data(github_token)
        else:
            print("Data is up to date.")
        
        # Show current data
        print("\nCurrent Data:")
        data_manager.display_data()


def setup_example_repos():
    """Set up example repositories for first-time users."""
    repos_file = "env/repos.txt"
    
    if os.path.exists(repos_file):
        with open(repos_file, 'r') as f:
            content = f.read().strip()
            # Check if file has actual repositories (not just comments)
            repos = [line.strip() for line in content.split('\n') 
                    if line.strip() and not line.strip().startswith('#')]
            if repos:
                return  # File already has repositories
    
    # Add some example repositories
    example_repos = [
        "# Example repositories - replace with your own",
        "microsoft/vscode",
        "facebook/react", 
        "python/cpython"
    ]
    
    print(f"Setting up example repositories in {repos_file}")
    with open(repos_file, 'w') as f:
        f.write('\n'.join(example_repos) + '\n')


if __name__ == "__main__":
    # Ensure we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Set up example repos if needed
    setup_example_repos()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)