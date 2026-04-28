# pylint: disable=missing-class-docstring
from update_repos import has_existing_check


class TestHasExistingCheck:
    def _settings_with_checks(self, contexts):
        return {
            "required_status_checks": {
                "checks": [{"context": c, "app_id": 15368} for c in contexts]
            }
        }

    def test_found(self):
        settings = self._settings_with_checks(["build", "lint"])
        assert has_existing_check(settings, "build") is True

    def test_not_found(self):
        settings = self._settings_with_checks(["build", "lint"])
        assert has_existing_check(settings, "test") is False

    def test_missing_required_status_checks(self):
        assert has_existing_check({}, "build") is False

    def test_missing_checks_key(self):
        settings = {"required_status_checks": {"strict": True}}
        assert has_existing_check(settings, "build") is False
