import os
import pathlib
from urllib.parse import urlparse

from github_client import GitHubClient

root = pathlib.Path(__file__).parent.resolve()

GITHUB_USER = "credfeto"
GITHUB_TOKEN = os.environ.get("SOURCE_PUSH_TOKEN", "")
ALWAYS_COLLABORATORS = os.environ.get("ALWAYS_COLLABORATORS", "")


def base_main_branch_protection_settings() -> dict:
    return {
        "required_status_checks": {
            "strict": True,
            "checks": [
                {"context": "does-not-contain-secrets", "app_id": 15368},
                {"context": "has-no-merge-conflicts", "app_id": 15368},
                {"context": "include-changelog-entry", "app_id": 15368},
                {"context": "no-ignored-files", "app_id": 15368},
                {"context": "has-no-file-or-folder-case-sensitivity-issues", "app_id": 15368},
                {"context": "change-log-entry-is-in-unreleased", "app_id": 15368},
                {"context": "lint-code", "app_id": 15368},
                {"context": "dependency-review", "app_id": 15368},
                {"context": "build-pre-release", "app_id": 15368},
            ],
        },
        "required_pull_request_reviews": {
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": True,
            "required_approving_review_count": 1,
        },
        "restrictions": None,
        "required_signatures": False,
        "enforce_admins": False,
        "required_linear_history": False,
        "allow_force_pushes": False,
        "allow_deletions": False,
        "required_conversation_resolution": True,
    }


def repo_url_to_owner_and_name(repo_url: str) -> dict | None:
    if repo_url.startswith("git@github.com:"):
        parts = repo_url[15:-4].split("/")
        return {"owner": parts[0], "repo": parts[1]}
    parsed = urlparse(repo_url)
    if parsed.scheme in ("http", "https") and parsed.netloc == "github.com":
        path_parts = parsed.path.strip("/").split("/")
        return {"owner": path_parts[0], "repo": path_parts[1]}
    return None


def has_existing_check(existing_settings: dict, name: str) -> bool:
    if "required_status_checks" not in existing_settings:
        return False
    if "checks" not in existing_settings["required_status_checks"]:
        return False
    return any(c["context"] == name for c in existing_settings["required_status_checks"]["checks"])


def have_branch_protection_settings_changed(existing_settings: dict, new_settings: dict) -> bool:
    if "required_status_checks" not in existing_settings:
        return True

    existing_sc = existing_settings["required_status_checks"]
    new_sc = new_settings["required_status_checks"]

    if existing_sc["strict"] != new_sc["strict"]:
        print("required_status_checks:strict different")
        return True

    existing_checks = existing_sc.get("checks", [])
    for new_check in new_sc["checks"]:
        existing_check = next((c for c in existing_checks if c["context"] == new_check["context"]), None)
        if not existing_check:
            print(f"required_status_checks:checks:{new_check['context']} different (missing)")
            return True
        existing_app_id = existing_check["app_id"]
        new_app_id = new_check["app_id"]
        if new_app_id == -1:
            if existing_app_id is not None:
                print(f"required_status_checks:checks:{new_check['context']} different (app_id: target)")
                return True
        else:
            if existing_app_id is None:
                print(f"required_status_checks:checks:{new_check['context']} different (app_id: source)")
                return True
            if existing_app_id != new_app_id:
                print(f"required_status_checks:checks:{new_check['context']} different (app_id: different ids)")
                return True

    if len(existing_checks) != len(new_sc["checks"]):
        print("required_status_checks:checks different")
        return True

    existing_pr = existing_settings["required_pull_request_reviews"]
    new_pr = new_settings["required_pull_request_reviews"]
    if existing_pr["dismiss_stale_reviews"] != new_pr["dismiss_stale_reviews"]:
        print("required_pull_request_reviews:dismiss_stale_reviews different")
        return True
    if existing_pr["require_code_owner_reviews"] != new_pr["require_code_owner_reviews"]:
        print("required_pull_request_reviews:require_code_owner_reviews different")
        return True
    if existing_pr["required_approving_review_count"] != new_pr["required_approving_review_count"]:
        print("required_pull_request_reviews:required_approving_review_count different")
        return True

    if existing_settings["required_signatures"]["enabled"] != new_settings["required_signatures"]:
        print("required_signatures different")
        return True
    if existing_settings["enforce_admins"]["enabled"] != new_settings["enforce_admins"]:
        print("enforce_admins different")
        return True
    if existing_settings["required_linear_history"]["enabled"] != new_settings["required_linear_history"]:
        return True
    if existing_settings["allow_force_pushes"]["enabled"] != new_settings["allow_force_pushes"]:
        return True
    if existing_settings["allow_deletions"]["enabled"] != new_settings["allow_deletions"]:
        return True
    if existing_settings["required_conversation_resolution"]["enabled"] != new_settings["required_conversation_resolution"]:
        return True

    return False


def get_branch_protection_settings(client: GitHubClient, owner: str, repo: str, branch: str) -> dict | None:
    try:
        return client.get(f"/repos/{owner}/{repo}/branches/{branch}/protection")
    except Exception:
        return None


def set_branch_protection_settings(client: GitHubClient, owner: str, repo: str, branch: str, settings: dict) -> bool:
    try:
        result = client.put(f"/repos/{owner}/{repo}/branches/{branch}/protection", settings)
        print(result)
        return True
    except Exception as exc:
        print(exc)
        print("############################################################")
        return False


def update_repo_settings(client: GitHubClient, owner: str, name: str) -> None:
    repo_settings = {
        "has_issues": True,
        "has_projects": False,
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


def add_github_build(settings: dict, project_name: str) -> None:
    settings["required_status_checks"]["checks"].append({"context": project_name, "app_id": 15368})


def add_existing_github_check(existing_settings: dict, new_settings: dict, build_name: str) -> None:
    if has_existing_check(existing_settings, build_name):
        print(f"****** Found Matching Build: {build_name}")
        add_github_build(new_settings, build_name)
        print(new_settings)


SKIP_BRANCH_PROTECTION_REPOS = {
    "git@github.com:credfeto/auto-update-config.git",
    "git@github.com:credfeto/credfeto.git",
}


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

        if repo in SKIP_BRANCH_PROTECTION_REPOS:
            continue

        new_settings = base_main_branch_protection_settings()
        print(new_settings)

        existing_settings = get_branch_protection_settings(client, owner, name, "main")
        print(existing_settings)

        if existing_settings:
            add_existing_github_check(existing_settings, new_settings, "build-contracts")
            print("**** CHECK UPDATE")
            if have_branch_protection_settings_changed(existing_settings, new_settings):
                set_branch_protection_settings(client, owner, name, "main", new_settings)
        else:
            set_branch_protection_settings(client, owner, name, "main", new_settings)


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
