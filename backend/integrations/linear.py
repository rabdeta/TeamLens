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

COMPLETED_ISSUE_METADATA_QUERY = """
query CompletedIssueMetadata($after: String) {
  issues(
    first: 100
    after: $after
    filter: {
      completedAt: { gt: "-P30D" }
    }
  ) {
    nodes {
      completedAt
      assignee {
        id
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""

def get_completed_task_counts(access_token):
    task_counts = {}
    after = None

    while True:
        data = execute_query(
            access_token,
            COMPLETED_ISSUE_METADATA_QUERY,
            {"after": after},
        )

        issues = data.get("issues")

        if not isinstance(issues, dict):
            raise LinearAPIError(
                "Linear returned invalid issue metadata"
            )

        issue_nodes = issues.get("nodes")
        page_info = issues.get("pageInfo")

        if not isinstance(issue_nodes, list) or not isinstance(
            page_info,
            dict,
        ):
            raise LinearAPIError(
                "Linear returned invalid issue metadata"
            )

        for issue in issue_nodes:
            assignee = issue.get("assignee")

            if isinstance(assignee, dict):
                assignee_id = assignee.get("id")

                if isinstance(assignee_id, str):
                    task_counts[assignee_id] = (
                        task_counts.get(assignee_id, 0) + 1
                    )

        if not page_info.get("hasNextPage"):
            break

        after = page_info.get("endCursor")

        if not isinstance(after, str):
            raise LinearAPIError(
                "Linear returned an invalid pagination cursor"
            )

    return task_counts