# pylint: disable=missing-class-docstring,unused-argument
import httpx

from github_client import GitHubClient
from update_repos import invite_collaborators


def _make_client(transport):
    http = httpx.Client(transport=transport)
    return GitHubClient("user", "token", http_client=http)


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
