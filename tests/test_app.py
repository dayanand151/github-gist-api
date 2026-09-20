from unittest.mock import Mock, patch

import pytest
import requests

from app import app
from github_client import GitHubError, fetch_user_gists


@pytest.fixture
def client():
    return app.test_client()


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


@patch("app.fetch_user_gists")
def test_octocat(mock_fetch, client):
    mock_fetch.return_value = [
        {"id": "6cad326836d38bd3a7ae", "description": "Hello world!"}
    ]
    r = client.get("/octocat")
    assert r.status_code == 200
    body = r.get_json()
    assert body[0]["id"] == "6cad326836d38bd3a7ae"
    mock_fetch.assert_called_with("octocat")


def test_bad_username(client):
    r = client.get("/not_valid")
    assert r.status_code == 400


@patch("app.fetch_user_gists")
def test_github_down(mock_fetch, client):
    mock_fetch.side_effect = GitHubError("GitHub unavailable", 503)
    r = client.get("/octocat")
    assert r.status_code == 503


@patch("github_client.requests.get")
def test_calls_github(mock_get):
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = []

    fetch_user_gists("octocat")

    url = mock_get.call_args[0][0]
    assert url == "https://api.github.com/users/octocat/gists"
    assert mock_get.call_args[1]["timeout"] == 10


@patch("github_client.requests.get", side_effect=requests.Timeout)
def test_timeout(mock_get):
    with pytest.raises(GitHubError) as err:
        fetch_user_gists("octocat")
    assert err.value.status_code == 503
