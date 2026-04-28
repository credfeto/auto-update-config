# pylint: disable=missing-class-docstring,too-few-public-methods,too-many-arguments,too-many-positional-arguments,unused-argument
import httpx
import pytest

from update_repos import (
    base_main_branch_protection_settings,
    have_branch_protection_settings_changed,
    has_existing_check,
    repo_url_to_owner_and_name,
    add_github_build,
    add_existing_github_check,
    get_branch_protection_settings,
    set_branch_protection_settings,
    invite_collaborators,
)
from github_client import GitHubClient


# ---------------------------------------------------------------------------
# repo_url_to_owner_and_name
# ---------------------------------------------------------------------------

class TestRepoUrlToOwnerAndName:
    def test_ssh_url(self):
        result = repo_url_to_owner_and_name("git@github.com:owner/repo.git")
        assert result == {"owner": "owner", "repo": "repo"}

    def test_https_url(self):
        result = repo_url_to_owner_and_name("https://github.com/owner/repo")
        assert result == {"owner": "owner", "repo": "repo"}

    def test_unknown_scheme_returns_none(self):
        result = repo_url_to_owner_and_name("svn://example.com/repo")
        assert result is None

    def test_ssh_url_with_org(self):
        result = repo_url_to_owner_and_name("git@github.com:my-org/my-repo.git")
        assert result == {"owner": "my-org", "repo": "my-repo"}


# ---------------------------------------------------------------------------
# has_existing_check
# ---------------------------------------------------------------------------

class TestHasExistingCheck:
    def _settings_with_checks(self, contexts):
        return {
            "required_status_checks": {
                "checks": [{"context": c, "app_id": 15368} for c in contexts]
            }
        }

    def test_found(self):
        settings = self._settings_with_checks(["build", "lint"])
        assert has_existing_check(settings, "build") is True

    def test_not_found(self):
        settings = self._settings_with_checks(["build", "lint"])
        assert has_existing_check(settings, "test") is False

    def test_missing_required_status_checks(self):
        assert has_existing_check({}, "build") is False

    def test_missing_checks_key(self):
        settings = {"required_status_checks": {"strict": True}}
        assert has_existing_check(settings, "build") is False


# ---------------------------------------------------------------------------
# have_branch_protection_settings_changed
# ---------------------------------------------------------------------------

def _wrap_bool(value):
    return {"enabled": value}


def _make_existing(strict=True, checks=None, dismiss_stale=True, code_owner=True,
                   approvals=1, required_sigs=False, enforce_admins=False,
                   linear_history=False, force_pushes=False, deletions=False,
                   conversation_resolution=True):
    return {
        "required_status_checks": {
            "strict": strict,
            "checks": checks or [{"context": "build", "app_id": 15368}],
        },
        "required_pull_request_reviews": {
            "dismiss_stale_reviews": dismiss_stale,
            "require_code_owner_reviews": code_owner,
            "required_approving_review_count": approvals,
        },
        "required_signatures": _wrap_bool(required_sigs),
        "enforce_admins": _wrap_bool(enforce_admins),
        "required_linear_history": _wrap_bool(linear_history),
        "allow_force_pushes": _wrap_bool(force_pushes),
        "allow_deletions": _wrap_bool(deletions),
        "required_conversation_resolution": _wrap_bool(conversation_resolution),
    }


class TestHaveBranchProtectionSettingsChanged:
    def _new_settings(self, checks=None):
        s = base_main_branch_protection_settings()
        if checks is not None:
            s["required_status_checks"]["checks"] = checks
        return s

    def test_identical_settings_no_change(self):
        new = self._new_settings()
        existing = _make_existing(
            strict=True,
            checks=new["required_status_checks"]["checks"],
            dismiss_stale=True,
            code_owner=True,
            approvals=1,
            required_sigs=False,
            enforce_admins=False,
            linear_history=False,
            force_pushes=False,
            deletions=False,
            conversation_resolution=True,
        )
        assert have_branch_protection_settings_changed(existing, new) is False

    def test_missing_required_status_checks_triggers_change(self):
        new = self._new_settings()
        assert have_branch_protection_settings_changed({}, new) is True

    def test_strict_change_detected(self):
        new = self._new_settings()
        existing = _make_existing(
            strict=False,
            checks=new["required_status_checks"]["checks"],
        )
        assert have_branch_protection_settings_changed(existing, new) is True

    def test_missing_check_detected(self):
        new = self._new_settings()
        existing = _make_existing(checks=[{"context": "build", "app_id": 15368}])
        assert have_branch_protection_settings_changed(existing, new) is True

    def test_different_app_id_detected(self):
        new = self._new_settings(checks=[{"context": "build", "app_id": 15368}])
        existing = _make_existing(checks=[{"context": "build", "app_id": 99999}])
        assert have_branch_protection_settings_changed(existing, new) is True

    def test_teamcity_check_app_id_none_no_change(self):
        new = self._new_settings(checks=[{"context": "tc-build", "app_id": -1}])
        existing = _make_existing(checks=[{"context": "tc-build", "app_id": None}])
        assert have_branch_protection_settings_changed(existing, new) is False

    def test_required_approvals_change_detected(self):
        new = self._new_settings()
        existing = _make_existing(
            checks=new["required_status_checks"]["checks"],
            approvals=2,
        )
        assert have_branch_protection_settings_changed(existing, new) is True

    def test_force_pushes_change_detected(self):
        new = self._new_settings()
        existing = _make_existing(
            checks=new["required_status_checks"]["checks"],
            force_pushes=True,
        )
        assert have_branch_protection_settings_changed(existing, new) is True


# ---------------------------------------------------------------------------
# add_github_build / add_existing_github_check
# ---------------------------------------------------------------------------

class TestAddGithubBuild:
    def test_appends_check(self):
        settings = base_main_branch_protection_settings()
        original_len = len(settings["required_status_checks"]["checks"])
        add_github_build(settings, "my-build")
        checks = settings["required_status_checks"]["checks"]
        assert len(checks) == original_len + 1
        assert checks[-1] == {"context": "my-build", "app_id": 15368}


class TestAddExistingGithubCheck:
    def test_adds_when_present_in_existing(self):
        existing = {"required_status_checks": {"checks": [{"context": "tc-build", "app_id": None}]}}
        new = base_main_branch_protection_settings()
        original_len = len(new["required_status_checks"]["checks"])
        add_existing_github_check(existing, new, "tc-build")
        assert len(new["required_status_checks"]["checks"]) == original_len + 1

    def test_skips_when_absent_in_existing(self):
        existing = {"required_status_checks": {"checks": []}}
        new = base_main_branch_protection_settings()
        original_len = len(new["required_status_checks"]["checks"])
        add_existing_github_check(existing, new, "tc-build")
        assert len(new["required_status_checks"]["checks"]) == original_len


# ---------------------------------------------------------------------------
# GitHubClient-dependent functions (using httpx mock transport)
# ---------------------------------------------------------------------------

def _make_client(transport):
    http = httpx.Client(transport=transport)
    return GitHubClient("user", "token", http_client=http)


class TestGetBranchProtectionSettings:
    def test_returns_json_on_success(self):
        payload = {"required_status_checks": {"strict": True, "checks": []}}
        transport = httpx.MockTransport(
            lambda req: httpx.Response(200, json=payload)
        )
        client = _make_client(transport)
        result = get_branch_protection_settings(client, "owner", "repo", "main")
        assert result == payload

    def test_returns_none_on_http_error(self):
        transport = httpx.MockTransport(
            lambda req: httpx.Response(404, json={"message": "Not Found"})
        )
        client = _make_client(transport)
        result = get_branch_protection_settings(client, "owner", "repo", "main")
        assert result is None


class TestSetBranchProtectionSettings:
    def test_returns_true_on_success(self):
        transport = httpx.MockTransport(
            lambda req: httpx.Response(200, json={"url": "https://api.github.com/repos/owner/repo/branches/main/protection"})
        )
        client = _make_client(transport)
        result = set_branch_protection_settings(client, "owner", "repo", "main", {})
        assert result is True

    def test_returns_false_on_http_error(self):
        transport = httpx.MockTransport(
            lambda req: httpx.Response(422, json={"message": "Unprocessable Entity"})
        )
        client = _make_client(transport)
        result = set_branch_protection_settings(client, "owner", "repo", "main", {})
        assert result is False


class TestInviteCollaborators:
    def test_puts_each_collaborator(self):
        requests_seen = []

        def handler(req):
            requests_seen.append(req.url.path)
            return httpx.Response(201, json={})

        transport = httpx.MockTransport(handler)
        client = _make_client(transport)
        invite_collaborators(client, "owner", "repo", ["alice", "bob"])
        assert any("alice" in p for p in requests_seen)
        assert any("bob" in p for p in requests_seen)

    def test_continues_on_failure(self):
        call_count = [0]

        def handler(req):
            call_count[0] += 1
            return httpx.Response(422, json={"message": "error"})

        transport = httpx.MockTransport(handler)
        client = _make_client(transport)
        invite_collaborators(client, "owner", "repo", ["alice", "bob"])
        assert call_count[0] == 2
