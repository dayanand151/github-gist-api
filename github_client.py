import os

import requests

GITHUB = "https://api.github.com"
TIMEOUT = 10


class GitHubError(Exception):
    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code


def fetch_user_gists(username):
    url = f"{GITHUB}/users/{username}/gists"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        # github 403s if this is missing
        "User-Agent": "gists-api",
    }

    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
    except requests.RequestException:
        raise GitHubError("GitHub unavailable", 503)

    if resp.status_code == 200:
        return resp.json()

    if resp.status_code == 404:
        raise GitHubError("user not found", 404)

    if resp.status_code in (403, 429):
        raise GitHubError("rate limited", 503)

    raise GitHubError("GitHub request failed", 502)
