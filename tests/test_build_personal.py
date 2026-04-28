# pylint: disable=missing-class-docstring
import pathlib
import tempfile

import pytest

from build_personal import (
    is_excluded,
    is_updatable_repo,
    make_query,
    EXCLUDED_REPOS,
)


class TestIsExcluded:
    def test_excluded_repo_returns_true(self):
        for url in EXCLUDED_REPOS:
            assert is_excluded(url) is True

    def test_normal_repo_returns_false(self):
        assert is_excluded("git@github.com:credfeto/some-project.git") is False

    def test_empty_string_returns_false(self):
        assert is_excluded("") is False


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


class TestMakeQuery:
    def test_no_cursor_uses_null(self):
        query = make_query()
        assert "after:null" in query

    def test_with_cursor_uses_quoted_value(self):
        query = make_query("abc123")
        assert 'after:"abc123"' in query

    def test_query_contains_viewer(self):
        assert "viewer" in make_query()

    def test_query_contains_ssh_url(self):
        assert "sshUrl" in make_query()
