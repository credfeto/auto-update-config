# pylint: disable=missing-class-docstring
import httpx

from github_client import GitHubClient


def _client_with_transport(transport):
    http = httpx.Client(transport=transport)
    return GitHubClient("testuser", "testtoken", http_client=http)


class TestGitHubClientPatch:
    def test_returns_parsed_json(self):
        payload = {"full_name": "owner/repo"}
        transport = httpx.MockTransport(lambda req: httpx.Response(200, json=payload))
        client = _client_with_transport(transport)
        result = client.patch("/repos/owner/repo", {"has_issues": True})
        assert result == payload

    def test_sends_patch_method(self):
        methods = []

        def handler(req):
            methods.append(req.method)
            return httpx.Response(200, json={})

        client = _client_with_transport(httpx.MockTransport(handler))
        client.patch("/some/path", {"key": "value"})
        assert methods[0] == "PATCH"
