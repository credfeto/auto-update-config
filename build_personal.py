from python_graphql_client import GraphqlClient
import feedparser
import httpx
import json
import pathlib
import re
import os

root = pathlib.Path(__file__).parent.resolve()
client = GraphqlClient(endpoint="https://api.github.com/graphql")


TOKEN = os.environ.get("SOURCE_PUSH_TOKEN", "")


def make_query(after_cursor=None):
    return """
query {
  viewer {
    repositories(first: 100, affiliations:[OWNER], after:AFTER) {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        name
        sshUrl
        homepageUrl
        isArchived
        isFork
      }
    }
  }
}
""".replace(
        "AFTER", '"{}"'.format(after_cursor) if after_cursor else "null"
    )


def is_excluded(ssh_url):
    if ssh_url == 'git@github.com:credfeto/opnsense-config.git':
        return True

    if ssh_url == 'git@github.com:credfeto/chains.git':
        return True
        
    if ssh_url == 'git@github.com:credfeto/infobeamer-browser.git':
        return True

    return False


def is_updatable_repo(repo):
    if repo["isArchived"]:
        return False

    if repo["isFork"]:
        return False

    if is_excluded(repo["sshUrl"]):
        return False

    return True


def fetch_repos(oauth_token):
    repositories = []
    has_next_page = True
    after_cursor = None

    while has_next_page:
        data = client.execute(
            query=make_query(after_cursor),
            headers={"Authorization": "Bearer {}".format(oauth_token)},
        )
        print()
        print(json.dumps(data, indent=4))
        print()
        for repo in data["data"]["viewer"]["repositories"]["nodes"]:
            print(repo["sshUrl"] + " => Archived = " + str(repo["isArchived"]) + " => IsFork = " + str(repo["isFork"]))
            if is_updatable_repo(repo):
                repositories.append(repo["sshUrl"])

        has_next_page = data["data"]["viewer"]["repositories"]["pageInfo"][
            "hasNextPage"
        ]
        after_cursor = data["data"]["viewer"]["repositories"]["pageInfo"]["endCursor"]
    return repositories


def update():
    repository_list_file = root / "personal/repos.lst"
    repos = fetch_repos(TOKEN)

    md = "\n".join(repos)

    repository_list_file.open("w").write(md)


if __name__ == "__main__":
    update()
