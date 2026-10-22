from unittest.mock import Mock, patch
import pytest
from backend.integrations.microsoft import (
    MicrosoftGraphError,
    execute_query,
    get_current_user,
)
from backend.integrations.microsoft import (
    MicrosoftGraphError,
    execute_query,
    get_calendar_events,
    get_current_user,
)
from backend.integrations.microsoft import (
    MicrosoftGraphError,
    execute_query,
    get_calendar_events,
    get_current_user,
    summarize_calendar_events,
)
from backend.integrations.microsoft import (
    MicrosoftGraphError,
    execute_query,
    get_calendar_events,
    get_current_user,
    refresh_oauth_tokens,
    summarize_calendar_events,
)

def test_refresh_oauth_tokens_returns_rotated_tokens():
    token_response = Mock()
    token_response.raise_for_status.return_value = None
    token_response.json.return_value = {
        "access_token": "new-access-token",
        "refresh_token": "new-refresh-token",
        "expires_in": 3600,
    }

    with patch(
        "backend.integrations.microsoft.requests.post",
        return_value=token_response,
    ) as token_request:
        result = refresh_oauth_tokens(
            "old-refresh-token",
            "test-client-id",
            "test-client-secret",
            "consumers",
        )

    assert result == {
        "access_token": "new-access-token",
        "refresh_token": "new-refresh-token",
        "expires_in": 3600,
    }

    token_request.assert_called_once_with(
        "https://login.microsoftonline.com/"
        "consumers/oauth2/v2.0/token",
        data={
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "refresh_token": "old-refresh-token",
            "grant_type": "refresh_token",
            "scope": (
                "openid profile offline_access "
                "User.Read Calendars.Read"
            ),
        },
        timeout=10,
    )

def test_execute_query_returns_data():
    graph_response = Mock()
    graph_response.raise_for_status.return_value = None
    graph_response.json.return_value = {
        "id": "user-1",
        "displayName": "Maya Chen",
    }

    with patch(
        "backend.integrations.microsoft.requests.get",
        return_value=graph_response,
    ) as graph_request:
        result = execute_query(
            "test-access-token",
            "/me",
        )

    assert result == {
        "id": "user-1",
        "displayName": "Maya Chen",
    }

    graph_request.assert_called_once_with(
        "https://graph.microsoft.com/v1.0/me",
        headers={
            "Authorization": "Bearer test-access-token",
            "Accept": "application/json",
        },
        params=None,
        timeout=10,
    )


def test_execute_query_rejects_invalid_response():
    graph_response = Mock()
    graph_response.raise_for_status.return_value = None
    graph_response.json.return_value = ["invalid"]

    with patch(
        "backend.integrations.microsoft.requests.get",
        return_value=graph_response,
    ):
        with pytest.raises(
            MicrosoftGraphError,
            match="invalid response",
        ):
            execute_query(
                "test-access-token",
                "/me",
            )


def test_get_current_user_returns_safe_metadata():
    with patch(
        "backend.integrations.microsoft.execute_query",
        return_value={
            "id": "microsoft-user-1",
            "displayName": "Roba Abdeta",
            "mail": "private@example.com",
            "userPrincipalName": "private@example.com",
        },
    ) as execute_request:
        result = get_current_user("test-access-token")

    execute_request.assert_called_once_with(
        "test-access-token",
        "/me",
        params={
            "$select": "id,displayName",
        },
    )

    assert result == {
        "id": "microsoft-user-1",
        "displayName": "Roba Abdeta",
    }

def test_get_calendar_events_returns_safe_metadata():
    with patch(
        "backend.integrations.microsoft.execute_query",
        return_value={
            "value": [
                {
                    "subject": "Private meeting title",
                    "bodyPreview": "Private meeting content",
                    "start": {
                        "dateTime": "2026-10-16T13:00:00Z",
                        "timeZone": "UTC",
                    },
                    "end": {
                        "dateTime": "2026-10-16T13:30:00Z",
                        "timeZone": "UTC",
                    },
                    "isCancelled": False,
                    "responseStatus": {
                        "response": "accepted",
                    },
                }
            ]
        },
    ) as execute_request:
        result = get_calendar_events(
            "test-access-token",
            "2026-09-17T00:00:00Z",
            "2026-10-17T00:00:00Z",
        )

    execute_request.assert_called_once_with(
        "test-access-token",
        "/me/calendar/calendarView",
        params={
            "startDateTime": "2026-09-17T00:00:00Z",
            "endDateTime": "2026-10-17T00:00:00Z",
            "$select": (
                "start,end,isCancelled,responseStatus"
            ),
            "$top": "1000",
        },
    )

    assert result == [
        {
            "start": "2026-10-16T13:00:00Z",
            "end": "2026-10-16T13:30:00Z",
            "isCancelled": False,
            "response": "accepted",
        }
    ]

def test_summarize_calendar_events():
    result = summarize_calendar_events(
        [
            {
                "start": "2026-10-16T13:00:00Z",
                "end": "2026-10-16T13:30:00Z",
                "isCancelled": False,
                "response": "accepted",
            },
            {
                "start": "2026-10-16T15:00:00Z",
                "end": "2026-10-16T16:00:00Z",
                "isCancelled": False,
                "response": "declined",
            },
            {
                "start": "2026-10-17T13:00:00Z",
                "end": "2026-10-17T13:30:00Z",
                "isCancelled": True,
                "response": "accepted",
            },
        ]
    )

    assert result == {
        "scheduledMeetingCount": 2,
        "acceptedMeetingCount": 1,
        "acceptedMeetingPercent": 50,
        "scheduledMeetingMinutes": 90,
        "measurementPeriodDays": 30,
    }