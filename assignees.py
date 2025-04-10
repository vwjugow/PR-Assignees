#!./.venv/bin/python
import json
import random
import re

from bin.gh.prs import add_reviewer, get_ready_prs_by_authors, get_pr_approvers_and_past_reviewers, get_pr_reviewers
from bin.jira.tickets import get_ticket_status


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
JIRA_BASE_URL = CONFIG["jira"]["base_url"]
JIRA_EMAIL = CONFIG["jira"]["email"]
JIRA_TOKEN_FILE = CONFIG["jira"]["token_file"]
JIRA_TICKET_NUMBER_RE = CONFIG["jira"]["ticket_number_regex"]


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


GH_TOKEN = load_token(GH_TOKEN_FILE)
JIRA_TOKEN = load_token(JIRA_TOKEN_FILE)

def  _get_ticket_status(pr_title):
    if re.match(JIRA_TICKET_NUMBER_RE, pr_title):
        ticket_number = pr_title.split()[0]
        ticket_status = get_ticket_status(JIRA_BASE_URL, JIRA_EMAIL, ticket_number, JIRA_TOKEN)
        return ticket_status.lower()
    return None


def _handle_approved_pr(pr_number, pr_title, pr_author, ticket_status, approvals, gh_users):
    if approvals and any(user in gh_users for user in approvals):
        pass
        # print(f"PR: #{pr_number} | author: {pr_author} | JIRA: {pr_title} - {ticket_status} | Already approved")


def _handle_assigned_pr(reviewers, gh_users, slack_users_by_gh_users_dict):
    existing_reviewer = next(user for user in reviewers if user in gh_users)
    if existing_reviewer:
        print(f"  -> PR already assigned to @{slack_users_by_gh_users_dict[existing_reviewer]}")
    return existing_reviewer


def _print_pr_info(pr_number, pr_title, pr_author, ticket_status, pr_url):
    print()
    print(f"PR: #{pr_number} | author: {pr_author} | JIRA: {pr_title} - {ticket_status}")
    print(f"  -> LINK: {pr_url}")


def _assign_reviewer(pr_number, pr_author, assigned_prs_per_user, next_assignee_pr_count, slack_users_by_gh_users_dict):
    possible_assignees = []
    while not possible_assignees and next_assignee_pr_count < 10:
        for user, count in assigned_prs_per_user.items():
            if count <= next_assignee_pr_count and user != pr_author:
                possible_assignees.append(user)
        if not possible_assignees:
            next_assignee_pr_count += 1
    reviewer = None
    if possible_assignees:
        # Group assignees by their PR count
        assignees_by_count = {}
        for user in possible_assignees:
            count = assigned_prs_per_user[user]
            if count not in assignees_by_count:
                assignees_by_count[count] = []
            assignees_by_count[count].append(user)

        # Get assignees with the lowest PR count
        min_count = min(assignees_by_count.keys())
        min_count_assignees = assignees_by_count[min_count]

        # If there's only one assignee with the lowest count, choose them
        # Otherwise randomly select from those with the lowest count
        if len(min_count_assignees) == 1:
            reviewer = min_count_assignees[0]
        else:
            reviewer = random.choice(min_count_assignees)

    if reviewer:
        assigned_prs_per_user[reviewer] = assigned_prs_per_user.get(reviewer, 0) + 1
        print(f"  -> Assigning to @{slack_users_by_gh_users_dict[reviewer]} for review")
        add_reviewer(ORG, REPO, pr_number, reviewer, GH_TOKEN)
    return next_assignee_pr_count


def _is_ready_for_review(ticket_status):
    return ticket_status and (ticket_status == "code review" or ticket_status == "qa review" or ticket_status == "in review")

def _approved_by_us(approvals, gh_users):
    return approvals and any(user in gh_users for user in approvals)


def _assigned_to_us(reviewers, gh_users):
    return reviewers and any(user in gh_users for user in reviewers)


def _assign_prs(to_assign, assigned_prs_per_user, slack_users_by_gh_users_dict):
    next_assignee_pr_count = 0
    for pr_number, pr_data in to_assign.items():
        pr_author = pr_data[0]
        pr_url = pr_data[1]
        pr_title = pr_data[2]
        ticket_status = pr_data[3]
        _print_pr_info(pr_number, pr_title, pr_author, ticket_status, pr_url)
        next_assignee_pr_count = _assign_reviewer(pr_number, pr_author, assigned_prs_per_user, next_assignee_pr_count,
                                                  slack_users_by_gh_users_dict)


def _get_previously_assigned(pr_author, past_reviewers, gh_users):
    eligible_previous_reviewers = [user for user in past_reviewers if user in gh_users and user != pr_author]
    return eligible_previous_reviewers[0] if eligible_previous_reviewers else None


def assign_to_previously_assigned(pr_number, reviewer, assigned_prs_per_user, slack_users_by_gh_users_dict):
    assigned_prs_per_user[reviewer] = assigned_prs_per_user.get(reviewer, 0) + 1
    print(f"  -> Reassigning to previous reviewer @{slack_users_by_gh_users_dict[reviewer]}")
    add_reviewer(ORG, REPO, pr_number, reviewer, GH_TOKEN)


def assign_pending_prs(prs, slack_users_by_gh_users_dict, gh_users):
    assigned_prs_per_user = {u: 0 for u in gh_users}
    to_assign = {}
    for pr in prs:
        pr_number, pr_url, pr_title = pr["number"], pr["html_url"], pr["title"].split("|")[0].strip()
        pr_author = pr['user']['login'].lower()
        ticket_status = _get_ticket_status(pr_title)
        if _is_ready_for_review(ticket_status):
            approvals, past_reviewers = get_pr_approvers_and_past_reviewers(ORG, REPO, pr_number, GH_TOKEN)
            reviewers = get_pr_reviewers(ORG, REPO, pr_number, GH_TOKEN)
            if not _approved_by_us(approvals, gh_users):
                if _assigned_to_us(reviewers, gh_users):
                    _print_pr_info(pr_number, pr_title, pr_author, ticket_status, pr_url)
                    reviewer = _handle_assigned_pr(reviewers, gh_users, slack_users_by_gh_users_dict)
                    assigned_prs_per_user[reviewer] = assigned_prs_per_user.get(reviewer, 0) + 1
                else:
                    old_assignee = _get_previously_assigned(pr_author, past_reviewers, gh_users)
                    if old_assignee:
                        _print_pr_info(pr_number, pr_title, pr_author, ticket_status, pr_url)
                        assign_to_previously_assigned(pr_number, old_assignee, assigned_prs_per_user,
                                                                  slack_users_by_gh_users_dict)
                    else:
                        to_assign[pr_number] = (pr_author, pr_url, pr_title, ticket_status)
            else:
                _handle_approved_pr(pr_number, pr_title, pr_author, ticket_status, approvals, gh_users)
    _assign_prs(to_assign, assigned_prs_per_user, slack_users_by_gh_users_dict)


def main():
    slack_users_by_gh_users_dict = load_authors(AUTHORS_FILE)
    gh_users = slack_users_by_gh_users_dict.keys()
    prs = get_ready_prs_by_authors(ORG, REPO, gh_users, GH_TOKEN)

    if not prs:
        print("No pull requests found for this user.")
        return
    assign_pending_prs(prs, slack_users_by_gh_users_dict, gh_users)
    print()

if __name__ == "__main__":
    main()
