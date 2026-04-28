# pylint: disable=missing-class-docstring
import httpx
import pytest

from github_client import GitHubClient, GITHUB_API_BASE_URL


def _client_with_transport(transport):
    http = httpx.Client(transport=transport)
    return GitHubClient("testuser", "testtoken", http_client=http)


class TestGitHubClientGet:
    def test_returns_parsed_json(self):
        payload = {"id": 1, "name": "repo"}
        transport = httpx.MockTransport(lambda req: httpx.Response(200, json=payload))
        client = _client_with_transport(transport)
        result = client.get("/repos/owner/repo")
        assert result == payload

    def test_sends_to_correct_url(self):
        seen_urls = []

        def handler(req):
            seen_urls.append(str(req.url))
            return httpx.Response(200, json={})

        client = _client_with_transport(httpx.MockTransport(handler))
        client.get("/repos/owner/repo")
        assert seen_urls[0] == f"{GITHUB_API_BASE_URL}/repos/owner/repo"

    def test_raises_on_4xx(self):
        transport = httpx.MockTransport(lambda req: httpx.Response(404, json={"message": "Not Found"}))
        client = _client_with_transport(transport)
        with pytest.raises(httpx.HTTPStatusError):
            client.get("/repos/owner/nonexistent")


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
