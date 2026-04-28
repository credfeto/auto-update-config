# pylint: disable=missing-class-docstring,too-many-arguments,too-many-positional-arguments
from update_repos import base_main_branch_protection_settings, have_branch_protection_settings_changed


def _wrap_bool(value):
    return {"enabled": value}


def _make_existing(strict=True, checks=None, dismiss_stale=True, code_owner=True,
                   approvals=1, required_sigs=False, enforce_admins=False,
                   linear_history=False, force_pushes=False, deletions=False,
                   conversation_resolution=True):
    return {
        "required_status_checks": {
            "strict": strict,
            "checks": checks or [{"context": "build", "app_id": 15368}],
        },
        "required_pull_request_reviews": {
            "dismiss_stale_reviews": dismiss_stale,
            "require_code_owner_reviews": code_owner,
            "required_approving_review_count": approvals,
        },
        "required_signatures": _wrap_bool(required_sigs),
        "enforce_admins": _wrap_bool(enforce_admins),
        "required_linear_history": _wrap_bool(linear_history),
        "allow_force_pushes": _wrap_bool(force_pushes),
        "allow_deletions": _wrap_bool(deletions),
        "required_conversation_resolution": _wrap_bool(conversation_resolution),
    }


class TestHaveBranchProtectionSettingsChanged:
    def _new_settings(self, checks=None):
        s = base_main_branch_protection_settings()
        if checks is not None:
            s["required_status_checks"]["checks"] = checks
        return s

    def test_identical_settings_no_change(self):
        new = self._new_settings()
        existing = _make_existing(
            strict=True,
            checks=new["required_status_checks"]["checks"],
            dismiss_stale=True,
            code_owner=True,
            approvals=1,
            required_sigs=False,
            enforce_admins=False,
            linear_history=False,
            force_pushes=False,
            deletions=False,
            conversation_resolution=True,
        )
        assert have_branch_protection_settings_changed(existing, new) is False

    def test_missing_required_status_checks_triggers_change(self):
        new = self._new_settings()
        assert have_branch_protection_settings_changed({}, new) is True

    def test_strict_change_detected(self):
        new = self._new_settings()
        existing = _make_existing(
            strict=False,
            checks=new["required_status_checks"]["checks"],
        )
        assert have_branch_protection_settings_changed(existing, new) is True

    def test_missing_check_detected(self):
        new = self._new_settings()
        existing = _make_existing(checks=[{"context": "build", "app_id": 15368}])
        assert have_branch_protection_settings_changed(existing, new) is True

    def test_different_app_id_detected(self):
        new = self._new_settings(checks=[{"context": "build", "app_id": 15368}])
        existing = _make_existing(checks=[{"context": "build", "app_id": 99999}])
        assert have_branch_protection_settings_changed(existing, new) is True

    def test_teamcity_check_app_id_none_no_change(self):
        new = self._new_settings(checks=[{"context": "tc-build", "app_id": -1}])
        existing = _make_existing(checks=[{"context": "tc-build", "app_id": None}])
        assert have_branch_protection_settings_changed(existing, new) is False

    def test_required_approvals_change_detected(self):
        new = self._new_settings()
        existing = _make_existing(
            checks=new["required_status_checks"]["checks"],
            approvals=2,
        )
        assert have_branch_protection_settings_changed(existing, new) is True

    def test_force_pushes_change_detected(self):
        new = self._new_settings()
        existing = _make_existing(
            checks=new["required_status_checks"]["checks"],
            force_pushes=True,
        )
        assert have_branch_protection_settings_changed(existing, new) is True
