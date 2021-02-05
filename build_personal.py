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
      }
    }
  }
}
""".replace(
        "AFTER", '"{}"'.format(after_cursor) if after_cursor else "null"
    )


def fetch_repos(oauth_token):
    repos = []
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
            if repo["isArchived"] != 'true':
                repos.append(repo["sshUrl"])

        has_next_page = data["data"]["viewer"]["repositories"]["pageInfo"][
            "hasNextPage"
        ]
        after_cursor = data["data"]["viewer"]["repositories"]["pageInfo"]["endCursor"]
    return repos


if __name__ == "__main__":
    reposlist = root / "personal/repos.lst"
    repos = fetch_repos(TOKEN)

    md = "\n".join(repos)

    #print(md)
    
    reposlist.open("w").write(md)
