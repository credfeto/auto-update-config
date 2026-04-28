# pylint: disable=missing-class-docstring
from build_personal import is_updatable_repo, EXCLUDED_REPOS


class TestIsUpdatableRepo:
    def _repo(self, archived=False, fork=False, url="git@github.com:credfeto/my-repo.git"):
        return {"isArchived": archived, "isFork": fork, "sshUrl": url}

    def test_normal_repo_is_updatable(self):
        assert is_updatable_repo(self._repo()) is True

    def test_archived_repo_not_updatable(self):
        assert is_updatable_repo(self._repo(archived=True)) is False

    def test_fork_not_updatable(self):
        assert is_updatable_repo(self._repo(fork=True)) is False

    def test_excluded_not_updatable(self):
        url = next(iter(EXCLUDED_REPOS))
        assert is_updatable_repo(self._repo(url=url)) is False

    def test_archived_fork_not_updatable(self):
        assert is_updatable_repo(self._repo(archived=True, fork=True)) is False
