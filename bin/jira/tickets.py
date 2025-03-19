import requests
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
