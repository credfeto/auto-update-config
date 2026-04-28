# pylint: disable=missing-class-docstring
from build_personal import is_excluded, EXCLUDED_REPOS


class TestIsExcluded:
    def test_excluded_repo_returns_true(self):
        for url in EXCLUDED_REPOS:
            assert is_excluded(url) is True

    def test_normal_repo_returns_false(self):
        assert is_excluded("git@github.com:credfeto/some-project.git") is False

    def test_empty_string_returns_false(self):
        assert is_excluded("") is False
