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