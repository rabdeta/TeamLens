from unittest.mock import Mock, patch

import pytest

from backend.integrations.microsoft import (
    MicrosoftGraphError,
    execute_query,
    get_current_user,
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