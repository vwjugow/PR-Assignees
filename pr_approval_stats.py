#!./.venv/bin/python
import json

from bin.gh.prs import get_merged_prs_last_x_days, get_pr_approvers_and_past_reviewers


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


def generate_pr_approval_stats(last_days, slack_users_by_gh_users_dict, gh_token):
    merged_prs = get_merged_prs_last_x_days(ORG, REPO, gh_token, last_days)
    approval_counts = {}
    our_merged_prs_count = 0
    for pr in merged_prs:
        # Check if PR author is in the authors list
        pr_author = pr['user']['login'].lower()
        if pr_author not in slack_users_by_gh_users_dict:
            continue
        our_merged_prs_count += 1
        pr_number = pr['number']
        approvals, _, _, _ = get_pr_approvers_and_past_reviewers(ORG, REPO, pr_number, gh_token)
        approvals = [t[0] for t in approvals]
        for approver in approvals:
            if approver in slack_users_by_gh_users_dict:
                approval_counts[approver] = approval_counts.get(approver, 0) + 1

    print(f"\nPR Approval Statistics (Last {last_days} Days):")
    print(f"\nMerged PRs: {our_merged_prs_count}")
    for approver, count in sorted(approval_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"@{slack_users_by_gh_users_dict[approver]} has approved {count} merged PR{'s' if count != 1 else ''}")


def main():
    import argparse
    global AUTHORS_FILE, GH_TOKEN_FILE
    parser = argparse.ArgumentParser(description="Generate PR approval statistics.")
    parser.add_argument("--last_days", type=int, default=30, help="Number of days to look back for merged PRs.")
    parser.add_argument("--authors_file", type=str, default=AUTHORS_FILE, help="Path to the authors file.")
    parser.add_argument("--gh_token_file", type=str, default=GH_TOKEN_FILE, help="Path to the GitHub token file.")
    args = parser.parse_args()
    AUTHORS_FILE = args.authors_file
    GH_TOKEN_FILE = args.gh_token_file
    last_days = args.last_days
    print(f"Looking back {last_days} days for merged PRs.")
    gh_token = load_token(GH_TOKEN_FILE)
    slack_users_by_gh_users_dict = load_authors(AUTHORS_FILE)
    generate_pr_approval_stats(last_days, slack_users_by_gh_users_dict, gh_token)


if __name__ == "__main__":
    main()
