# pylint: disable=missing-class-docstring
import httpx

from github_client import GitHubClient
from update_repos import get_branch_protection_settings


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
