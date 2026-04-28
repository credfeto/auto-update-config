# pylint: disable=missing-class-docstring,too-few-public-methods
from update_repos import base_main_branch_protection_settings, add_github_build


class TestAddGithubBuild:
    def test_appends_check(self):
        settings = base_main_branch_protection_settings()
        original_len = len(settings["required_status_checks"]["checks"])
        add_github_build(settings, "my-build")
        checks = settings["required_status_checks"]["checks"]
        assert len(checks) == original_len + 1
        assert checks[-1] == {"context": "my-build", "app_id": 15368}
