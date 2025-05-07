#!./.venv/bin/python
import json

from bin.gh.prs import get_merged_prs_last_30_days, get_pr_approvers_and_past_reviewers


def load_config(config_file="config.json"):
    try:
        with open(config_file, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: Config file '{config_file}' not found.")
        exit(1)
    except Exception as e:
        print(f"Error: Unable to read the config file. Details: {e}")
        exit(1)


CONFIG = load_config()
AUTHORS_FILE = CONFIG["authors_file"]
ORG = CONFIG["github"]["org"]
REPO = CONFIG["github"]["repo"]
GH_TOKEN_FILE = CONFIG["github"]["token_file"]


def load_authors(file_path):
    try:
        with open(file_path, "r") as file:
            slack_users_by_gh_users_dict = {}
            for line in file.readlines():
                gh_user, slack_user = line.strip().split(":")
                gh_user = gh_user.lower()
                slack_users_by_gh_users_dict[gh_user] = slack_user
            return slack_users_by_gh_users_dict
    except FileNotFoundError:
        print(f"Error: Authors file '{file_path}' not found. Please create the file with your desired authors.")
        exit(1)
    except Exception as e:
        print(f"Error: Unable to read the authors file. Details: {e}")
        exit(1)


def load_token(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Error: Token file '{file_path}' not found. Please create the file with your GitHub token.")
        exit(1)
    except Exception as e:
        print(f"Error: Unable to read the token file. Details: {e}")
        exit(1)


def generate_pr_approval_stats(slack_users_by_gh_users_dict, gh_token):
    merged_prs = get_merged_prs_last_30_days(ORG, REPO, gh_token)
    approval_counts = {}

    for pr in merged_prs:
        # Check if PR author is in the authors list
        pr_author = pr['user']['login'].lower()
        if pr_author not in slack_users_by_gh_users_dict:
            continue

        pr_number = pr['number']
        approvals, _ = get_pr_approvers_and_past_reviewers(ORG, REPO, pr_number, gh_token)
        print(f"Processing PR {pr_number} ({pr['title'][:50]}...), author: {pr_author}, approvals: {approvals}")
        for approver in approvals:
            if approver in slack_users_by_gh_users_dict:
                approval_counts[approver] = approval_counts.get(approver, 0) + 1

    print("\nPR Approval Statistics (Last 30 Days):")
    for approver, count in sorted(approval_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"@{slack_users_by_gh_users_dict[approver]}: {count} PR{'s' if count != 1 else ''} approved")


def main():
    gh_token = load_token(GH_TOKEN_FILE)
    slack_users_by_gh_users_dict = load_authors(AUTHORS_FILE)
    generate_pr_approval_stats(slack_users_by_gh_users_dict, gh_token)


if __name__ == "__main__":
    main()
