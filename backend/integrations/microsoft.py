import requests
from datetime import datetime

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

def get_calendar_events(
    access_token,
    start_datetime,
    end_datetime,
):
    payload = execute_query(
        access_token,
        "/me/calendar/calendarView",
        params={
            "startDateTime": start_datetime,
            "endDateTime": end_datetime,
            "$select": (
                "start,end,isCancelled,responseStatus"
            ),
            "$top": "1000",
        },
    )

    events = payload.get("value")

    if not isinstance(events, list):
        raise MicrosoftGraphError(
            "Microsoft Graph returned invalid calendar data"
        )

    safe_events = []

    for event in events:
        if not isinstance(event, dict):
            raise MicrosoftGraphError(
                "Microsoft Graph returned invalid calendar data"
            )

        start = event.get("start")
        end = event.get("end")
        response_status = event.get("responseStatus", {})

        if (
            not isinstance(start, dict)
            or not isinstance(end, dict)
            or not isinstance(response_status, dict)
            or not isinstance(start.get("dateTime"), str)
            or not isinstance(end.get("dateTime"), str)
        ):
            raise MicrosoftGraphError(
                "Microsoft Graph returned invalid calendar data"
            )

        response = response_status.get("response", "none")

        if not isinstance(response, str):
            raise MicrosoftGraphError(
                "Microsoft Graph returned invalid calendar data"
            )

        safe_events.append(
            {
                "start": start["dateTime"],
                "end": end["dateTime"],
                "isCancelled": bool(
                    event.get("isCancelled", False)
                ),
                "response": response,
            }
        )

    return safe_events

def summarize_calendar_events(events):
    scheduled_count = 0
    accepted_count = 0
    scheduled_minutes = 0

    for event in events:
        if event["isCancelled"]:
            continue

        try:
            start = datetime.fromisoformat(event["start"])
            end = datetime.fromisoformat(event["end"])
        except (TypeError, ValueError) as error:
            raise MicrosoftGraphError(
                "Microsoft Graph returned invalid calendar data"
            ) from error

        duration_minutes = int(
            (end - start).total_seconds() / 60
        )

        if duration_minutes < 0:
            raise MicrosoftGraphError(
                "Microsoft Graph returned invalid calendar data"
            )

        scheduled_count += 1
        scheduled_minutes += duration_minutes

        if event["response"].lower() == "accepted":
            accepted_count += 1

    accepted_percent = (
        round((accepted_count / scheduled_count) * 100)
        if scheduled_count
        else 0
    )

    return {
        "scheduledMeetingCount": scheduled_count,
        "acceptedMeetingCount": accepted_count,
        "acceptedMeetingPercent": accepted_percent,
        "scheduledMeetingMinutes": scheduled_minutes,
        "measurementPeriodDays": 30,
    }

def refresh_oauth_tokens(
    refresh_token,
    client_id,
    client_secret,
    authority_tenant,
):
    try:
        response = requests.post(
            "https://login.microsoftonline.com/"
            f"{authority_tenant}/oauth2/v2.0/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
                "scope": (
                    "openid profile offline_access "
                    "User.Read Calendars.Read"
                ),
            },
            timeout=10,
        )
        response.raise_for_status()
        token_data = response.json()
    except (requests.RequestException, ValueError) as error:
        raise MicrosoftGraphError(
            "Unable to refresh Microsoft OAuth tokens"
        ) from error

    access_token = token_data.get("access_token")
    new_refresh_token = token_data.get(
        "refresh_token",
        refresh_token,
    )
    expires_in = token_data.get("expires_in")

    if (
        not isinstance(access_token, str)
        or not access_token
        or not isinstance(new_refresh_token, str)
        or not new_refresh_token
        or not isinstance(expires_in, int)
    ):
        raise MicrosoftGraphError(
            "Microsoft returned an invalid token response"
        )

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "expires_in": expires_in,
    }