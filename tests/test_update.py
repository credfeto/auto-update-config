# pylint: disable=missing-class-docstring,too-few-public-methods
from build_personal import update


class _StubGraphqlClient:
    def __init__(self, repos):
        self._repos = repos

    def execute(self, query, headers):  # pylint: disable=unused-argument
        return {
            "data": {
                "viewer": {
                    "repositories": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "nodes": [
                            {
                                "name": name,
                                "sshUrl": ssh_url,
                                "homepageUrl": None,
                                "isArchived": False,
                                "isFork": False,
                            }
                            for name, ssh_url in self._repos
                        ],
                    }
                }
            }
        }


class TestUpdate:
    def test_output_file_ends_with_trailing_newline(self, tmp_path):
        output_file = tmp_path / "repos.lst"
        client = _StubGraphqlClient([("repo-one", "git@github.com:credfeto/repo-one.git")])

        update(client, "token", output_file)

        assert output_file.read_text() == "git@github.com:credfeto/repo-one.git\n"

    def test_each_repo_on_its_own_line(self, tmp_path):
        output_file = tmp_path / "repos.lst"
        client = _StubGraphqlClient(
            [
                ("repo-one", "git@github.com:credfeto/repo-one.git"),
                ("repo-two", "git@github.com:credfeto/repo-two.git"),
            ]
        )

        update(client, "token", output_file)

        assert output_file.read_text() == (
            "git@github.com:credfeto/repo-one.git\n"
            "git@github.com:credfeto/repo-two.git\n"
        )
