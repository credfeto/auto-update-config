# pylint: disable=missing-class-docstring
from build_personal import make_query


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
