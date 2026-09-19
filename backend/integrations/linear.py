import requests


LINEAR_GRAPHQL_URL = "https://api.linear.app/graphql"


class LinearAPIError(Exception):
    """Raised when Linear cannot return valid API data."""


def execute_query(access_token, query, variables=None):
    try:
        response = requests.post(
            LINEAR_GRAPHQL_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json={
                "query": query,
                "variables": variables or {},
            },
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as error:
        raise LinearAPIError(
            "Unable to retrieve data from Linear"
        ) from error

    if payload.get("errors"):
        raise LinearAPIError("Linear returned a GraphQL error")

    data = payload.get("data")

    if not isinstance(data, dict):
        raise LinearAPIError("Linear returned an invalid response")

    return data

WORKSPACE_MEMBERS_QUERY = """
query WorkspaceMembers {
  users(first: 100) {
    nodes {
      id
      name
      active
    }
  }
}
"""


def get_workspace_members(access_token):
    data = execute_query(
        access_token,
        WORKSPACE_MEMBERS_QUERY,
    )

    users = data.get("users", {})
    members = users.get("nodes")

    if not isinstance(members, list):
        raise LinearAPIError(
            "Linear returned invalid workspace member data"
        )

    return members