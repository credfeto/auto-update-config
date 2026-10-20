# pylint: disable=missing-class-docstring,too-few-public-methods
from build_personal import update


class _StubGraphqlClient:
    def __init__(self, *pages):
        self._pages = pages
        self._next_page = 0

    def execute(self, query, headers):  # pylint: disable=unused-argument
        page_number = self._next_page
        self._next_page += 1
        has_next_page = self._next_page < len(self._pages)
        return {
            "data": {
                "viewer": {
                    "repositories": {
                        "pageInfo": {
                            "hasNextPage": has_next_page,
                            "endCursor": f"cursor-{page_number}" if has_next_page else None,
                        },
                        "nodes": [
                            {
                                "name": name,
                                "sshUrl": ssh_url,
                                "homepageUrl": None,
                                "isArchived": False,
                                "isFork": False,
                            }
                            for name, ssh_url in self._pages[page_number]
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

    def test_repos_written_in_case_insensitive_sorted_order(self, tmp_path):
        output_file = tmp_path / "repos.lst"
        client = _StubGraphqlClient(
            [
                ("zeta", "git@github.com:credfeto/zeta.git"),
                ("Beta", "git@github.com:credfeto/Beta.git"),
                ("alpha", "git@github.com:credfeto/alpha.git"),
                ("Gamma", "git@github.com:credfeto/Gamma.git"),
            ]
        )

        update(client, "token", output_file)

        assert output_file.read_text() == (
            "git@github.com:credfeto/alpha.git\n"
            "git@github.com:credfeto/Beta.git\n"
            "git@github.com:credfeto/Gamma.git\n"
            "git@github.com:credfeto/zeta.git\n"
        )

    def test_repos_sorted_across_pages(self, tmp_path):
        output_file = tmp_path / "repos.lst"
        client = _StubGraphqlClient(
            [
                ("zeta", "git@github.com:credfeto/zeta.git"),
                ("Beta", "git@github.com:credfeto/Beta.git"),
            ],
            [
                ("alpha", "git@github.com:credfeto/alpha.git"),
                ("Gamma", "git@github.com:credfeto/Gamma.git"),
            ],
        )

        update(client, "token", output_file)

        assert output_file.read_text() == (
            "git@github.com:credfeto/alpha.git\n"
            "git@github.com:credfeto/Beta.git\n"
            "git@github.com:credfeto/Gamma.git\n"
            "git@github.com:credfeto/zeta.git\n"
        )
