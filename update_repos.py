import os
import pathlib
from urllib.parse import urlparse

from github_client import GitHubClient

root = pathlib.Path(__file__).parent.resolve()

GITHUB_USER = "credfeto"
GITHUB_TOKEN = os.environ.get("SOURCE_PUSH_TOKEN", "")
ALWAYS_COLLABORATORS = os.environ.get("ALWAYS_COLLABORATORS", "")


def repo_url_to_owner_and_name(repo_url: str) -> dict | None:
    if repo_url.startswith("git@github.com:"):
        parts = repo_url[15:-4].split("/")
        return {"owner": parts[0], "repo": parts[1]}
    parsed = urlparse(repo_url)
    if parsed.scheme in ("http", "https") and parsed.netloc == "github.com":
        path_parts = parsed.path.strip("/").split("/")
        return {"owner": path_parts[0], "repo": path_parts[1]}
    return None


def update_repo_settings(client: GitHubClient, owner: str, name: str) -> None:
    repo_settings = {
        "has_issues": True,
        "has_projects": True,
        "has_wiki": False,
        "allow_squash_merge": False,
        "allow_merge_commit": True,
        "allow_rebase_merge": False,
        "allow_auto_merge": True,
        "delete_branch_on_merge": True,
        "allow_update_branch": True,
        "archive-program-opt-out-feature": True,
        "merge_commit_title": "PR_TITLE",
        "merge_commit_message": "PR_BODY",
    }
    client.patch(f"/repos/{owner}/{name}", repo_settings)


def update_repo_actions_workflow_permissions(client: GitHubClient, owner: str, name: str) -> None:
    try:
        client.put(f"/repos/{owner}/{name}/actions/permissions/workflow", {"can_approve_pull_request_reviews": True})
    except Exception as exc:
        print(exc)
        print("############################################################")


def invite_collaborators(client: GitHubClient, owner: str, name: str, collaborators: list[str]) -> None:
    print(f"Inviting collaborators to {owner}/{name}: {collaborators}")
    for collaborator in collaborators:
        try:
            result = client.put(f"/repos/{owner}/{name}/collaborators/{collaborator}", {"permission": "push"})
            print(f"Invited collaborator: {collaborator} -> {result}")
        except Exception as exc:
            print(f"Failed to invite collaborator: {collaborator}")
            print(exc)
            print("############################################################")


def update(client: GitHubClient, collaborators: list[str], repos: list[str]) -> None:
    for repo in repos:
        print("*****************************************************************************")
        print(repo)

        repo_parts = repo_url_to_owner_and_name(repo)
        if not repo_parts:
            continue

        owner = repo_parts["owner"]
        name = repo_parts["repo"]

        update_repo_settings(client, owner, name)
        update_repo_actions_workflow_permissions(client, owner, name)
        if collaborators:
            invite_collaborators(client, owner, name, collaborators)


if __name__ == "__main__":
    if not GITHUB_TOKEN:
        raise ValueError("SOURCE_PUSH_TOKEN environment variable is not set")

    parsed_collaborators = [c.strip() for c in ALWAYS_COLLABORATORS.split(",") if c.strip()]
    print(f"ALWAYS_COLLABORATORS raw: '{ALWAYS_COLLABORATORS}'")
    print(f"Parsed collaborators: {parsed_collaborators}")

    repository_list_file = root / "personal/repos.lst"
    print(repository_list_file)

    parsed_repos = repository_list_file.read_text().splitlines()
    print(parsed_repos)

    update(GitHubClient(GITHUB_USER, GITHUB_TOKEN), parsed_collaborators, parsed_repos)
