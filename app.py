import re

from flask import Flask, jsonify

from github_client import GitHubError, fetch_user_gists

app = Flask(__name__)

# letters, numbers, hyphens. max 39 chars.
USERNAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]{0,38}$")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/<username>")
def gists(username):
    if not USERNAME_RE.match(username) or username.endswith("-"):
        return jsonify({"error": "invalid username"}), 400

    try:
        data = fetch_user_gists(username)
    except GitHubError as e:
        return jsonify({"error": str(e)}), e.status_code

    return jsonify(data)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)


