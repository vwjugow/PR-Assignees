#!./.venv/bin/python
import re
import requests

GITHUB_API = "https://api.github.com"


def _get_headers(token):
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }


def _is_pr_ready_for_review(pr):
    return not pr["draft"] and pr["state"] == "open"


def _is_pr_author_in_list(pr, authors):
    return (pr["user"]["login"] or "").lower() in authors


def get_next_page_url(link_header):
    # Regex to find the URL corresponding to the 'rel=next' in the Link header
    match = re.search(r'<(https://[^>]+)>; rel="next"', link_header)
    if match:
        return match.group(1)  # Extracted URL
    return None


def get_ready_prs_by_authors(org, repo, authors, token):
    headers = _get_headers(token)
    url = f"{GITHUB_API}/repos/{org}/{repo}/pulls?state=open&per_page=100"
    all_prs = []
    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        prs = response.json()
        all_prs.extend([pr for pr in prs if _is_pr_ready_for_review(pr) and _is_pr_author_in_list(pr, authors)])
        link_header = response.headers.get("Link")
        url = get_next_page_url(link_header)
    return all_prs


def get_commit_status(org, repo, sha, token):
    url = f"{GITHUB_API}/repos/{org}/{repo}/commits/{sha}/status"
    headers = _get_headers(token)
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    status = response.json()
    return status["state"], status["statuses"]


def get_merged_prs_last_30_days(org, repo, token):
    from datetime import datetime, timedelta, timezone

    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    headers = _get_headers(token)
    url = f"{GITHUB_API}/repos/{org}/{repo}/pulls?state=closed&sort=updated&direction=desc&per_page=100"
    all_merged_prs = []
    page = 1

    while url and page <= 6:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        prs = response.json()
        merged_prs = [
            pr for pr in prs
            if pr.get('merged_at') and datetime.fromisoformat(pr['merged_at'].replace('Z', '+00:00')) > thirty_days_ago
        ]
        all_merged_prs.extend(merged_prs)
        link_header = response.headers.get("Link")
        url = get_next_page_url(link_header)
        page += 1
    return all_merged_prs


def get_pr_approvers_and_past_reviewers(org, repo, pull_number, token):
    """
    Fetch the approvals and requested reviewers for a GitHub Pull Request,
    including the timestamps for when reviewers were requested.
    Args:
    -----
        org (str): The GitHub organization or username.
        repo (str): The GitHub repository name.
        pull_number (int): The number of the pull request.
        token (str): Your GitHub personal access token.
    Returns:
    --------
        tuple: A tuple containing:
            - list: A list of tuples containing the usernames of approved reviewers and the timestamp
                they were requested.
            - list: A list of tuples containing the usernames of past reviewers and the timestamp
                they were requested.
            - list: A list of tuples containing the usernames who requested changes and the timestamp
                they were requested.
            - list: A list of usernames of requested reviewers.
            - list: A list of tuples containing the usernames of requested reviewers and the timestamp
                they were requested.
    """
    from datetime import datetime, timezone

    headers = _get_headers(token)
    # Get reviews
    reviews_url = f"{GITHUB_API}/repos/{org}/{repo}/pulls/{pull_number}/reviews"
    response = requests.get(reviews_url, headers=headers)
    response.raise_for_status()
    reviews = response.json()
    approvals = [
        review for review in reviews if review['state'] == "APPROVED"
    ]
    changes_requested = [
        review for review in reviews if review['state'] == "CHANGES_REQUESTED"
    ]
    non_approvals = [
        review for review in reviews if review['state'] not in ["APPROVED", "CHANGES_REQUESTED"]
    ]
    today = datetime.now(timezone.utc)
    approvers = [(rv["user"]["login"].lower(), rv.get("submitted_at", today)) for rv in approvals]
    changes_requesters = [(rv["user"]["login"].lower(), rv.get("submitted_at", today)) for rv in changes_requested]
    non_approvers = [(rv["user"]["login"].lower(), rv.get("submitted_at", today)) for rv in non_approvals
                     if rv["user"]["login"] not in [rv["user"]["login"].lower() for rv in approvals]]

    # Get requested reviewers
    requested_reviewers_usernames = get_pr_reviewers(org, repo, pull_number, token)
    # Get PR timeline to find requested_at timestamps
    timeline_url = f"{GITHUB_API}/repos/{org}/{repo}/issues/{pull_number}/timeline"
    response = requests.get(timeline_url, headers=headers)
    response.raise_for_status()
    timeline_events = response.json()
    requested_reviewers = []
    for requested_reviewer in requested_reviewers_usernames:
        requested_reviewer_tuple = (requested_reviewer.lower(), None)
        for event in timeline_events:
            debug_print("events. event:", event)
            if event["event"] == "review_requested" and event.get("requested_reviewer", {}).get(
                    "login", "").lower() == requested_reviewer:
                if not requested_reviewer_tuple[1] or event["created_at"] > requested_reviewer_tuple[1]:
                    requested_reviewer_tuple = (requested_reviewer.lower(), event["created_at"])
        requested_reviewers.append(requested_reviewer_tuple)
    return approvers, non_approvers, changes_requesters, requested_reviewers


def get_pr_reviewers(org, repo, pull_number, token):
    """
    Fetch the assigned reviewers for a GitHub Pull Request.

    Args:
        github_api (str): The base URL for the GitHub API (e.g., 'https://api.github.com').
        org (str): The GitHub organization or username.
        repo (str): The GitHub repository name.
        pull_number (int): The number of the pull request.
        token (str): Your GitHub personal access token.

    Returns:
        list: A list of usernames who reviewed the pull request.
    """
    url = f"{GITHUB_API}/repos/{org}/{repo}/pulls/{pull_number}/requested_reviewers"
    headers = _get_headers(token)
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    reviewers = response.json()
    return [rv["login"].lower() for rv in reviewers["users"]]


def add_reviewer(org, repo, pull_number, reviewer, token):
    """
    Add a reviewer to a GitHub Pull Request.

    Args:
        github_api (str): The base URL for the GitHub API (e.g., 'https://api.github.com').
        org (str): The GitHub organization or username.
        repo (str): The GitHub repository name.
        pull_number (int): The number of the pull request.
        reviewer (str): The username of the reviewer to add.
        token (str): Your GitHub personal access token.

    Returns:
        dict: The response from the API.
    """
    url = f"{GITHUB_API}/repos/{org}/{repo}/pulls/{pull_number}/requested_reviewers"
    headers = _get_headers(token)
    data = {
        "reviewers": [reviewer]
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()
