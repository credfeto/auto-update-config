import httpx

GITHUB_API_BASE_URL = "https://api.github.com"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.56"
)


class GitHubClient:
    """HTTP client for the GitHub REST API."""

    def __init__(self, user: str, token: str, http_client: httpx.Client | None = None):
        self._user = user
        self._token = token
        self._http = http_client or httpx.Client()
        self._headers = {
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        }

    def get(self, path: str) -> dict:
        url = GITHUB_API_BASE_URL + path
        print(f"GET {url}")
        response = self._http.get(url, auth=(self._user, self._token), headers=self._headers)
        response.raise_for_status()
        return response.json()

    def put(self, path: str, data: dict) -> dict:
        url = GITHUB_API_BASE_URL + path
        print(f"PUT {url}")
        response = self._http.put(url, auth=(self._user, self._token), headers=self._headers, json=data)
        response.raise_for_status()
        return response.json()

    def patch(self, path: str, data: dict) -> dict:
        url = GITHUB_API_BASE_URL + path
        print(f"PATCH {url}")
        response = self._http.patch(url, auth=(self._user, self._token), headers=self._headers, json=data)
        response.raise_for_status()
        return response.json()
