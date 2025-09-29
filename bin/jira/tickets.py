import math
import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth


def get_ticket_status(base_url, email, ticket_id, api_token):
    """
    Fetch the status of a JIRA ticket using the JIRA API.

    Args:
        base_url (str): The base URL of the JIRA instance (e.g., 'https://your-company.atlassian.net').
        ticket_id (str): The JIRA ticket ID to check (e.g., 'PROJ-123').
        email (str): Your JIRA account email.
        api_token (str): Your JIRA API token.

    Returns:
        str: The status of the JIRA ticket.
    """
    url = f"{base_url}/rest/api/3/issue/{ticket_id}"
    auth = HTTPBasicAuth(email, api_token)
    headers = {
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers, auth=auth)

    if response.status_code == 200:
        ticket_data = response.json()
        status = ticket_data['fields']['status']['name']  # Extract the ticket status
        return status
    else:
        raise Exception(f"Failed to fetch ticket data. Status Code: {response.status_code}, Response: {response.text}")


def transition_ticket_to_qa_review(base_url, email, ticket_id, api_token):
    """
    Transition a JIRA ticket to the 'QA REVIEW' status using the JIRA API.

    Args:
        base_url (str): The base URL of the JIRA instance (e.g., 'https://your-company.atlassian.net').
        ticket_id (str): The JIRA ticket ID to transition (e.g., 'PROJ-123').
        email (str): Your JIRA account email.
        api_token (str): Your JIRA API token.

    Raises:
        Exception: If the transition fails or 'QA REVIEW' is not a valid transition.
    """
    auth = HTTPBasicAuth(email, api_token)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    # Get available transitions
    transitions_url = f"{base_url}/rest/api/3/issue/{ticket_id}/transitions"
    response = requests.get(transitions_url, headers=headers, auth=auth)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch transitions. Status Code: {response.status_code}, Response: {response.text}")
    transitions = response.json().get("transitions", [])
    qa_review_transition = next((t for t in transitions if t["name"].upper() == "READY FOR QA REVIEW"), None)
    if not qa_review_transition:
        raise Exception(f"No 'Ready for QA Review' transition available for ticket {ticket_id}.")
    transition_id = qa_review_transition["id"]
    # Perform the transition
    payload = {"transition": {"id": transition_id}}
    transition_response = requests.post(transitions_url, headers=headers, auth=auth, json=payload)
    if transition_response.status_code != 204:
        raise Exception(f"Failed to transition ticket. Status Code: {transition_response.status_code}, Response: "
                        f"{transition_response.text}")
    return True


def transition_ticket_to_in_progress(base_url, email, ticket_id, api_token):
    """
    Transition a JIRA ticket to the 'In Progress' status using the JIRA API.

    Args:
        base_url (str): The base URL of the JIRA instance (e.g., 'https://your-company.atlassian.net').
        ticket_id (str): The JIRA ticket ID to transition (e.g., 'PROJ-123').
        email (str): Your JIRA account email.
        api_token (str): Your JIRA API token.

    Raises:
        Exception: If the transition fails or 'In Progress' is not a valid transition.
    """
    auth = HTTPBasicAuth(email, api_token)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    transitions_url = f"{base_url}/rest/api/3/issue/{ticket_id}/transitions"
    response = requests.get(transitions_url, headers=headers, auth=auth)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch transitions. Status Code: {response.status_code}, Response: {response.text}")
    transitions = response.json().get("transitions", [])
    in_progress_transition = next((t for t in transitions if t["to"]["name"].upper() == "IN PROGRESS"), None)
    if not in_progress_transition:
        raise Exception(f"No transition to 'In Progress' available for ticket {ticket_id}.")
    transition_id = in_progress_transition["id"]
    payload = {"transition": {"id": transition_id}}
    transition_response = requests.post(transitions_url, headers=headers, auth=auth, json=payload)
    if transition_response.status_code != 204:
        raise Exception(f"Failed to transition ticket. Status Code: {transition_response.status_code}, Response: "
                        f"{transition_response.text}")
    return True


def get_ticket_age_in_current_status(base_url, email, ticket_id, api_token):
    """
    Get the history of status transitions for a JIRA ticket.

    Args:
        base_url (str): The base URL of the JIRA instance (e.g., 'https://your-company.atlassian.net').
        ticket_id (str): The JIRA ticket ID to check (e.g., 'PROJ-123').
        email (str): Your JIRA account email.
        api_token (str): Your JIRA API token.

    Returns:
        list: A list of dictionaries containing status transition details.
              Each dictionary includes 'from', 'to', 'date', and 'days_in_status'.
    """
    auth = HTTPBasicAuth(email, api_token)
    headers = {
        "Accept": "application/json"
    }
    url = f"{base_url}/rest/api/3/issue/{ticket_id}?expand=changelog"
    response = requests.get(url, headers=headers, auth=auth)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch ticket data. Status Code: {response.status_code}, Response: {response.text}")

    ticket_data = response.json()
    changelog = ticket_data.get('changelog', {}).get('histories', [])

    status_transitions = []
    last_status_change_date = datetime.strptime(ticket_data['fields']['created'], '%Y-%m-%dT%H:%M:%S.%f%z')
    # Collect all status transitions
    for change in changelog:
        for item in change['items']:
            if item['field'] == 'status':
                from_status = item['fromString']
                to_status = item['toString']
                transition_date = datetime.strptime(change['created'], '%Y-%m-%dT%H:%M:%S.%f%z')

                status_transitions.append({
                    'from': from_status,
                    'to': to_status,
                    'date': transition_date
                })
    # Sort transitions by date
    status_transitions.sort(key=lambda x: x['date'])
    # Calculate days in current status from last transition to today
    current_status_start_date = status_transitions[-1]['date'] if status_transitions else last_status_change_date
    time_in_current_status = datetime.now(current_status_start_date.tzinfo) - current_status_start_date
    days_in_current_status = math.ceil(float(time_in_current_status.total_seconds() / 3600) / 24.0) - 1
    return days_in_current_status
