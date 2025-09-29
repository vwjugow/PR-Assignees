# PR Assignment & Approval Stats

Scripts for automating GitHub PR reviewer assignment and tracking approval statistics for the BriteCore team.

## Scripts

### assignees.py
Automatically assigns reviewers to pending pull requests and manages ticket transitions.

**Usage:**
```bash
./assignees.py
```

**Options:**
- `--debug` or `-d`: Enable debug output

**Features:**
- Assigns reviewers to PRs based on workload balancing
- Moves JIRA tickets between statuses (Code Review → QA Review)
- Reassigns PRs to previous reviewers when applicable
- Handles change requests and moves tickets to In Progress
- Notifies when PRs are ready to merge

### pr_approval_stats.py
Generates statistics on PR approvals for team members.

**Usage:**
```bash
./pr_approval_stats.py --last_days 21
```

**Options:**
- `--last_days`: Number of days to look back (default: 30)
- `--authors_file`: Path to authors file (default: authors.txt)
- `--gh_token_file`: Path to GitHub token file (default: gh_token)

## Setup

### Prerequisites
1. Python 3.x with virtual environment
2. GitHub personal access token
3. JIRA API token

### Installation

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create configuration files from examples:

```bash
# Copy example files and customize with your values
cp config.json.example config.json
cp authors.txt.example authors.txt
cp gh_token.example gh_token
cp jira_token.example jira_token
```

**config.json** - Main configuration file (see `config.json.example`):
- Set your GitHub organization and repository
- Configure JIRA base URL and email
- Customize ticket regex pattern if needed

**authors.txt** - Map GitHub usernames to Slack handles (see `authors.txt.example`):
```
githubuser1:slack.user1
githubuser2:slack.user2
```

**gh_token** - GitHub personal access token ([Create one here](https://github.com/settings/tokens)):
- Requires `repo` scope for private repositories
- Requires `public_repo` scope for public repositories

**jira_token** - JIRA API token ([Create one here](https://id.atlassian.com/manage-profile/security/api-tokens))

### Configuration

All settings are now centralized in `config.json`. Edit this file to customize:
- GitHub organization and repository
- JIRA instance URL and email
- Token file locations
- JIRA ticket number regex pattern
- Authors file location

## How It Works

### assignees.py
1. Fetches all open PRs from specified authors
2. Checks JIRA ticket status for each PR
3. For PRs in "Code Review", "QA Review", or "In Review" status:
   - If approved by team member → moves ticket to QA or prompts to merge
   - If assigned to team member → reminds reviewer if overdue
   - If changes requested → moves ticket back to In Progress
   - Otherwise → assigns to available reviewer with lowest workload

### pr_approval_stats.py
1. Fetches merged PRs from the last X days
2. Collects approval data for each PR
3. Generates statistics showing approval counts per team member

## Requirements

- `requests`: HTTP library for GitHub/JIRA API calls
