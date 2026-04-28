# pylint: disable=missing-class-docstring
import httpx
import pytest

from github_client import GitHubClient


def _client_with_transport(transport):
    http = httpx.Client(transport=transport)
    return GitHubClient("testuser", "testtoken", http_client=http)


class TestGitHubClientPut:
    def test_returns_parsed_json(self):
        payload = {"status": "ok"}
        transport = httpx.MockTransport(lambda req: httpx.Response(200, json=payload))
        client = _client_with_transport(transport)
        result = client.put("/repos/owner/repo/branches/main/protection", {"strict": True})
        assert result == payload

    def test_sends_put_method(self):
        methods = []

        def handler(req):
            methods.append(req.method)
            return httpx.Response(200, json={})

        client = _client_with_transport(httpx.MockTransport(handler))
        client.put("/some/path", {"key": "value"})
        assert methods[0] == "PUT"

    def test_raises_on_422(self):
        transport = httpx.MockTransport(
            lambda req: httpx.Response(422, json={"message": "Unprocessable Entity"})
        )
        client = _client_with_transport(transport)
        with pytest.raises(httpx.HTTPStatusError):
            client.put("/repos/owner/repo/branches/main/protection", {})
