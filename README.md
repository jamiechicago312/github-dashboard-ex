# GitHub Repository Dashboard

A simple and lightweight tool to track metrics for multiple public GitHub repositories. This dashboard collects data like stars, forks, contributors, pull requests, commits, and other publicly available metrics without storing any personal information - just numbers.

## Features

- 📊 Track multiple repositories from a simple configuration file
- 🔄 Automatic data refresh every 7 days
- 📁 Data saved to CSV format for easy analysis
- 🚀 Lightweight with minimal dependencies
- 🔒 No personal data collection - only public metrics
- ⚡ Optional GitHub token support for higher rate limits

## Tracked Metrics

For each repository, the dashboard collects:

- **Basic Stats**: Stars, forks, watchers, size
- **Contributors**: Total contributor count
- **Issues**: Open, closed, and total issues
- **Pull Requests**: Open, closed, merged, and total PRs
- **Activity**: Recent commits (last 30 days)
- **Metadata**: Primary language, creation date, last update

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure repositories**:
   Edit `env/repos.txt` and add the repositories you want to track:
   ```
   microsoft/vscode
   facebook/react
   python/cpython
   ```

3. **Run the dashboard**:
   ```bash
   python dashboard.py
   ```

## Usage

### Basic Commands

```bash
# Run dashboard (auto-updates if data is 7+ days old)
python dashboard.py

# Force update data immediately
python dashboard.py --update

# Show current data
python dashboard.py --show

# Show summary statistics
python dashboard.py --summary
```

### With GitHub Token (Optional)

For higher rate limits, you can provide a GitHub personal access token:

```bash
# Via command line
python dashboard.py --token YOUR_GITHUB_TOKEN

# Via environment variable
export GITHUB_TOKEN=YOUR_GITHUB_TOKEN
python dashboard.py

# Via .env file
echo "GITHUB_TOKEN=YOUR_GITHUB_TOKEN" > .env
python dashboard.py
```

## Configuration

### Repository List

Add repositories to track in `env/repos.txt`:
```
# Format: owner/repository
microsoft/vscode
facebook/react
torvalds/linux
python/cpython
```

### Environment Variables

Create a `.env` file (optional):
```bash
# GitHub Personal Access Token (optional, for higher rate limits)
GITHUB_TOKEN=your_github_token_here
```

## Data Storage

- **CSV File**: `data/github_metrics.csv` - Contains all collected metrics
- **Update Tracking**: `data/last_update.txt` - Tracks when data was last refreshed
- **Auto-refresh**: Data is automatically refreshed every 7 days

## CSV Format

The generated CSV includes these columns:
- `repo`: Repository name (owner/name)
- `stars`: Star count
- `forks`: Fork count  
- `watchers`: Watcher count
- `contributors`: Total contributors
- `open_issues`, `total_issues`, `closed_issues`: Issue statistics
- `open_prs`, `total_prs`, `closed_prs`, `merged_prs`: Pull request statistics
- `recent_commits_30d`: Commits in last 30 days
- `size_kb`: Repository size in KB
- `language`: Primary programming language
- `created_at`, `updated_at`: Repository timestamps
- `last_fetched`: When this data was collected

## Rate Limits

- **Without token**: 60 requests per hour
- **With token**: 5,000 requests per hour

The dashboard is designed to work within these limits, but a token is recommended for tracking many repositories.

## Requirements

- Python 3.6+
- `requests` library
- `python-dotenv` library

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues and pull requests to improve the dashboard!