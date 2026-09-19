from unittest.mock import Mock, patch

import pytest

from backend.integrations.linear import (
    LinearAPIError,
    execute_query,
    get_workspace_members,
)

@patch("backend.integrations.linear.requests.post")
def test_execute_query_returns_data(mock_post):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "data": {
            "viewer": {
                "id": "linear-user-1",
            }
        }
    }
    mock_post.return_value = response

    data = execute_query(
        "test-access-token",
        "query { viewer { id } }",
    )

    assert data == {"viewer": {"id": "linear-user-1"}}

    request_headers = mock_post.call_args.kwargs["headers"]
    assert request_headers["Authorization"] == "Bearer test-access-token"


@patch("backend.integrations.linear.requests.post")
def test_execute_query_rejects_graphql_errors(mock_post):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "errors": [{"message": "Request failed"}]
    }
    mock_post.return_value = response

    with pytest.raises(LinearAPIError):
        execute_query(
            "test-access-token",
            "query { viewer { id } }",
        )

@patch("backend.integrations.linear.execute_query")
def test_get_workspace_members_returns_safe_metadata(mock_execute_query):
    mock_execute_query.return_value = {
        "users": {
            "nodes": [
                {
                    "id": "user-1",
                    "name": "Maya Chen",
                    "active": True,
                }
            ]
        }
    }

    members = get_workspace_members("test-access-token")

    assert members == [
        {
            "id": "user-1",
            "name": "Maya Chen",
            "active": True,
        }
    ]

    query = mock_execute_query.call_args.args[1].lower()

    assert "title" not in query
    assert "description" not in query
    assert "comment" not in query