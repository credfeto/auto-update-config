import base64
import urllib.parse

import feedparser
import httpx
import json
import gzip
import pathlib
import re
import os
from urllib.request import Request, urlopen

root = pathlib.Path(__file__).parent.resolve()
github_api_base_url = "https://api.github.com"

GITHUB_USER = "credfeto"
GITHUB_TOKEN = os.environ.get("SOURCE_PUSH_TOKEN", "")
TEAMCITY_TOKEN = os.environ.get("TEAMCITY_READ_API_KEY", "")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.56"


def base_main_branch_protection_settings():
    return {
        "required_status_checks": {
            "strict": True,
            "checks": [
                {
                    "context": "does-not-contain-secrets",
                    "app_id": 15368
                },
                {
                    "context": "has-no-merge-conflicts",
                    "app_id": 15368
                },
                {
                    "context": "include-changelog-entry",
                    "app_id": 15368
                },
                {
                    "context": "no-ignored-files",
                    "app_id": 15368
                },
                {
                    "context": "has-no-file-or-folder-case-sensitivity-issues",
                    "app_id": 15368
                },
                {
                    "context": "change-log-entry-is-in-unreleased",
                    "app_id": 15368
                },
                {
                    "context": "lint-code",
                    "app_id": 15368
                },
                {
                    "context": "dependency-review",
                    "app_id": 15368
                }
            ]
        },
        "required_pull_request_reviews": {
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": True,
            "required_approving_review_count": 1
        },
        "restrictions": None,
        "required_signatures": False,
        "enforce_admins": False,
        "required_linear_history": False,
        "allow_force_pushes": False,
        "allow_deletions": False,
        "required_conversation_resolution": True
    }


def have_branch_protection_settings_changed(existing_settings, new_settings):

    if "required_status_checks" not in existing_settings:
        return True

    # Branch Must Be Up-to date
    if existing_settings["required_status_checks"]["strict"] != new_settings["required_status_checks"]["strict"]:
        print("required_status_checks:strict different")
        return True

    # checks [ check each context ]
    existing_checks = []
    if "checks" in existing_settings["required_status_checks"]:
        existing_checks = existing_settings["required_status_checks"]["checks"]

    new_checks = new_settings["required_status_checks"]["checks"]
    for new_check in new_checks:

        existing_check = None
        for candidate in existing_checks:
            if candidate["context"] == new_check["context"]:
                existing_check = candidate
                break

        if not existing_check:
            print("required_status_checks:checks:" + new_check["context"] + " different (missing)")
            return True

        existing_app_id = existing_check["app_id"]
        new_app_id = new_check["app_id"]
        if new_app_id == -1:
            if existing_app_id is not None:
                print("required_status_checks:checks:" + new_check["context"] + " different (app_id: target)")
                return True
        else:
            if existing_app_id is None:
                print("required_status_checks:checks:" + new_check["context"] + " different (app_id: source)")
                return True
            if existing_app_id != new_app_id:
                print("required_status_checks:checks:" + new_check["context"] + " different (app_id: different ids)")
                return True

    if existing_settings["required_status_checks"]["checks"] != new_settings["required_status_checks"]["checks"]:
        print("required_status_checks:checks different")
        return True

    # required_pull_request_reviews : dismiss_stale_reviews
    if existing_settings["required_pull_request_reviews"]["dismiss_stale_reviews"] != new_settings["required_pull_request_reviews"]["dismiss_stale_reviews"]:
        print("required_pull_request_reviews:dismiss_stale_reviews different")
        return True

    # required_pull_request_reviews : require_code_owner_reviews
    if existing_settings["required_pull_request_reviews"]["require_code_owner_reviews"] != new_settings["required_pull_request_reviews"]["require_code_owner_reviews"]:
        print("required_pull_request_reviews:require_code_owner_reviews different")
        return True

    # required_pull_request_reviews : required_approving_review_count
    if existing_settings["required_pull_request_reviews"]["required_approving_review_count"] != new_settings["required_pull_request_reviews"]["required_approving_review_count"]:
        print("required_pull_request_reviews:required_approving_review_count different")
        return True

    # required_signatures
    if existing_settings["required_signatures"]["enabled"] != new_settings["required_signatures"]:
        print("required_signatures different")
        return True

    # enforce_admins
    if existing_settings["enforce_admins"]["enabled"] != new_settings["enforce_admins"]:
        print("enforce_admins different")
        return True

    # required_linear_history
    if existing_settings["required_linear_history"]["enabled"] != new_settings["required_linear_history"]:
        return True

    # allow_force_pushes
    if existing_settings["allow_force_pushes"]["enabled"] != new_settings["allow_force_pushes"]:
        return True

    # allow_deletions
    if existing_settings["allow_deletions"]["enabled"] != new_settings["allow_deletions"]:
        return True

    # required_conversation_resolution
    if existing_settings["required_conversation_resolution"]["enabled"] != new_settings["required_conversation_resolution"]:
        return True

    return False


def get_branch_protection_settings(owner, repo, branch):

    try:
        settings = get_github("/repos/" + owner + "/" + repo + "/branches/"+branch+"/protection")
    except Exception:
        return None

    return settings


def set_branch_protection_settings(owner, repo, branch, settings):
    try:
        settings = put_github("/repos/" + owner + "/" + repo + "/branches/"+branch+"/protection", settings)
    except Exception as e:

        print(e)
        print("############################################################")
        return False

    print(settings)
    return True


def basic_auth(user, password):
    message = user + ":" + password
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')

    return base64_message


def get_github(path):
    url = github_api_base_url + path

    print("Connect to GET " + url)
    #    print("Token: " + TEAMCITY_TOKEN)

    token = basic_auth(GITHUB_USER, GITHUB_TOKEN)

    request = Request(url)
    request.add_header('Accept', 'application/json')
    request.add_header('Accept-Encoding', 'deflate, gzip')
    request.add_header('Authorization', 'BASIC ' + token)
    request.add_header('User-Agent', USER_AGENT)

    response = urlopen(request)

    content = response.read()
    try:
        content = gzip.decompress(content)
    except gzip.BadGzipFile as e:
        return json.loads(content)

    return json.loads(content)


def put_github(path, data):
    url = github_api_base_url + path

    print("Connect to PUT " + url)
    #    print("Token: " + TEAMCITY_TOKEN)

    token = basic_auth(GITHUB_USER, GITHUB_TOKEN)

    json_data = json.dumps(data)
    print(json_data)
    post_data = json_data.encode()

    request = Request(url=url, data=post_data, method='PUT')

    request.add_header('Accept', 'application/json')
    request.add_header('Accept-Encoding', 'deflate, gzip')
    request.add_header('Content-Type', 'application/json')
    request.add_header('Authorization', 'BASIC ' + token)
    request.add_header('User-Agent', USER_AGENT)
    print(request.get_method())

    response = urlopen(request)

    content = response.read()
    try:
        content = gzip.decompress(content)
    except gzip.BadGzipFile as e:
        return json.loads(content)

    return json.loads(content)


def patch_github(path, data):
    url = github_api_base_url + path

    print("Connect to PATCH " + url)
    #    print("Token: " + TEAMCITY_TOKEN)

    token = basic_auth(GITHUB_USER, GITHUB_TOKEN)

    json_data = json.dumps(data)
    print(json_data)
    post_data = json_data.encode()

    request = Request(url=url, data=post_data, method='PATCH')

    request.add_header('Accept', 'application/json')
    request.add_header('Accept-Encoding', 'deflate, gzip')
    request.add_header('Content-Type', 'application/json')
    request.add_header('Authorization', 'BASIC ' + token)
    request.add_header('User-Agent', USER_AGENT)
    print(request.get_method())

    response = urlopen(request)

    content = response.read()
    try:
        content = gzip.decompress(content)
    except gzip.BadGzipFile as e:
        return json.loads(content)

    return json.loads(content)


def repo_url_to_owner_and_name(repo_url):
    # git@github.com:funfair-tech/funfair-games.git
    # https://github.com/funfair-tech/funfair-labs-tictactoe-server

    if repo_url.startswith("git@github.com:"):
        split = repo_url[15:-4].split("/")
        return {
            "owner": split[0],
            "repo": split[1]
        }

    if repo_url.startswith("https://github.com/"):
        split = repo_url[8:].split("/")
        return {
            "owner": split[1],
            "repo": split[2]
        }

    return None


def add_teamcity_build(settings, project_name):
    settings["required_status_checks"]["checks"].append({"context": project_name, "app_id": -1})


def add_github_build(settings, project_name):
    settings["required_status_checks"]["checks"].append({"context": project_name, "app_id": 15368})


def has_existing_check(existing_settings, name):

    if "required_status_checks" not in existing_settings:
        return False

    if "checks" not in existing_settings["required_status_checks"]:
        return False

    checks = existing_settings["required_status_checks"]["checks"]
    for check in checks:
        if check["context"] == name:
            return True

    return False


def update_repo_settings(owner, name):
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
        "security_and_analysis": {
           "advanced_security": {
               "status": "enabled"
           }
       }
    }

    patch_github("/repos/" + owner + "/" + name, repo_settings)


def add_existing_github_check(existing_settings, new_settings, build_name):
    if has_existing_check(existing_settings, build_name):
        print("****** Found Matching Build: " + build_name)
        add_github_build(new_settings, build_name)
        print(new_settings)


def update():
    if GITHUB_TOKEN == "":
        raise "Invalid Github token"

    repository_list_file = root / "personal/repos.lst"
    print(repository_list_file)

    repos = repository_list_file.open("r").read().splitlines()
    print(repos)

    for repo in repos:
        print("*****************************************************************************")
        print(repo)

        repo_parts = repo_url_to_owner_and_name(repo)
        if repo_parts:
            update_repo_settings(repo_parts["owner"], repo_parts["repo"])

            if repo == 'git@github.com:credfeto/auto-update-config.git':
                continue

            if repo == 'git@github.com:credfeto/credfeto.git':
                continue

            new_settings = base_main_branch_protection_settings()
            print(new_settings)

            existing_settings = get_branch_protection_settings(repo_parts["owner"], repo_parts["repo"], 'main')
            print(existing_settings)

            if existing_settings:
                add_existing_github_check(existing_settings, new_settings, "build-contracts")

                print("**** CHECK UPDATE")
                changed = have_branch_protection_settings_changed(existing_settings, new_settings)
                if changed:
                    set_branch_protection_settings(repo_parts["owner"], repo_parts["repo"], 'main', new_settings)
            else:
                set_branch_protection_settings(repo_parts["owner"], repo_parts["repo"], 'main', new_settings)

        # ABORT AT FIRST ONE FOR NOW
        # break


if __name__ == "__main__":
    update()
