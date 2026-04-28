import json
import os
import pathlib
from typing import Any

from python_graphql_client import GraphqlClient

root = pathlib.Path(__file__).parent.resolve()

GITHUB_USER = "credfeto"
GITHUB_TOKEN = os.environ.get("SOURCE_PUSH_TOKEN", "")

EXCLUDED_REPOS = {
    "git@github.com:credfeto/opnsense-config.git",
    "git@github.com:credfeto/chains.git",
    "git@github.com:credfeto/infobeamer-browser.git",
    "git@github.com:credfeto/credfeto-batch-updates.git",
}


def make_query(after_cursor: str | None = None) -> str:
    after_value = f'"{after_cursor}"' if after_cursor else "null"
    return f"""
query {{
  viewer {{
    repositories(first: 100, affiliations:[OWNER], after:{after_value}) {{
      pageInfo {{
        hasNextPage
        endCursor
      }}
      nodes {{
        name
        sshUrl
        homepageUrl
        isArchived
        isFork
      }}
    }}
  }}
}}
"""


def is_excluded(ssh_url: str) -> bool:
    return ssh_url in EXCLUDED_REPOS


def is_updatable_repo(repo: dict[str, Any]) -> bool:
    if repo["isArchived"]:
        return False
    if repo["isFork"]:
        return False
    if is_excluded(repo["sshUrl"]):
        return False
    return True


def fetch_repos(graphql_client: GraphqlClient, oauth_token: str) -> list[str]:
    repositories = []
    has_next_page = True
    after_cursor = None

    while has_next_page:
        data = graphql_client.execute(
            query=make_query(after_cursor),
            headers={"Authorization": f"Bearer {oauth_token}"},
        )
        print()
        print(json.dumps(data, indent=4))
        print()
        viewer_repos = data["data"]["viewer"]["repositories"]
        for repo in viewer_repos["nodes"]:
            print(f"{repo['sshUrl']} => Archived = {repo['isArchived']} => IsFork = {repo['isFork']}")
            if is_updatable_repo(repo):
                repositories.append(repo["sshUrl"])

        page_info = viewer_repos["pageInfo"]
        has_next_page = page_info["hasNextPage"]
        after_cursor = page_info["endCursor"]

    return repositories


def update(graphql_client: GraphqlClient, token: str, output_file: pathlib.Path) -> None:
    repos = fetch_repos(graphql_client, token)
    output_file.write_text("\n".join(repos))


if __name__ == "__main__":
    if not GITHUB_TOKEN:
        raise ValueError("SOURCE_PUSH_TOKEN environment variable is not set")

    _client = GraphqlClient(endpoint="https://api.github.com/graphql")
    _output = root / "personal/repos.lst"
    update(_client, GITHUB_TOKEN, _output)
