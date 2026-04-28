# pylint: disable=missing-class-docstring
from update_repos import repo_url_to_owner_and_name


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
