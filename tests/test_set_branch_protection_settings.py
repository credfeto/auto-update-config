# pylint: disable=missing-class-docstring
import httpx

from github_client import GitHubClient
from update_repos import set_branch_protection_settings


def _make_client(transport):
    http = httpx.Client(transport=transport)
    return GitHubClient("user", "token", http_client=http)


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
