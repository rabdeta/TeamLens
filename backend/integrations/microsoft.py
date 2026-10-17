import requests


MICROSOFT_GRAPH_URL = "https://graph.microsoft.com/v1.0"


class MicrosoftGraphError(Exception):
    """Raised when Microsoft Graph cannot return valid API data."""


def execute_query(
    access_token,
    endpoint,
    params=None,
):
    try:
        response = requests.get(
            f"{MICROSOFT_GRAPH_URL}{endpoint}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as error:
        raise MicrosoftGraphError(
            "Unable to retrieve data from Microsoft Graph"
        ) from error

    if not isinstance(payload, dict):
        raise MicrosoftGraphError(
            "Microsoft Graph returned an invalid response"
        )

    return payload

def get_current_user(access_token):
    payload = execute_query(
        access_token,
        "/me",
        params={
            "$select": "id,displayName",
        },
    )

    user_id = payload.get("id")
    display_name = payload.get("displayName")

    if (
        not isinstance(user_id, str)
        or not user_id
        or not isinstance(display_name, str)
        or not display_name
    ):
        raise MicrosoftGraphError(
            "Microsoft Graph returned invalid user data"
        )

    return {
        "id": user_id,
        "displayName": display_name,
    }