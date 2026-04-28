# pylint: disable=missing-class-docstring
from update_repos import base_main_branch_protection_settings, add_existing_github_check


class TestAddExistingGithubCheck:
    def test_adds_when_present_in_existing(self):
        existing = {"required_status_checks": {"checks": [{"context": "tc-build", "app_id": None}]}}
        new = base_main_branch_protection_settings()
        original_len = len(new["required_status_checks"]["checks"])
        add_existing_github_check(existing, new, "tc-build")
        assert len(new["required_status_checks"]["checks"]) == original_len + 1

    def test_skips_when_absent_in_existing(self):
        existing = {"required_status_checks": {"checks": []}}
        new = base_main_branch_protection_settings()
        original_len = len(new["required_status_checks"]["checks"])
        add_existing_github_check(existing, new, "tc-build")
        assert len(new["required_status_checks"]["checks"]) == original_len
