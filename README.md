# Gists API

This is a small HTTP API. You pass a GitHub username in the URL and it comes back with that user's public gists.

`GET /octocat` calls GitHub (`GET /users/octocat/gists`) and returns the JSON list as-is. There is also `GET /health` so you can see the process is up.

Nothing is stored here. GitHub is the source of the data.

## What I used

| Thing | Version | What for |
|---|---|---|
| Python | 3.12 (in the image) | language |
| Flask | 3.1.2 | HTTP routes |
| requests | 2.32.5 | calling GitHub |
| gunicorn | 23.0.0 | serves the app in Docker |
| pytest | 8.4.2 | tests |

Versions are pinned in `requirements.txt`.

## Run it locally

Use a venv so you don't install packages on the system Python.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python app.py
```

That starts Flask on http://127.0.0.1:8080. In another terminal:

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/octocat
```

Ctrl+C stops it.

Tests (venv still on):

```bash
pytest
```

They mock GitHub, so they don't need the network.

## Dockerfile

Two stages.

**Builder** — `python:3.12-slim`, make a venv at `/venv`, `pip install -r requirements.txt`.

**Final image** — another slim Python. Copy the venv over, then `app.py` and `github_client.py`. Create `appuser` and switch to that user so gunicorn isn't root.

`EXPOSE 8080` is just documentation. The real listen address is in `CMD`: gunicorn on `0.0.0.0:8080`. Has to be `0.0.0.0` or you can't reach it from outside the container.

`.dockerignore` keeps `.venv`, tests and `.git` out of the build.

## Build the image

From this folder:

```bash
docker build -t gists-api .
```

## Run the image

```bash
docker run --rm -p 8080:8080 gists-api
```

`-p 8080:8080` is host port → container port. `--rm` deletes the container when you stop it.

```bash
curl http://localhost:8080/octocat
curl http://localhost:8080/health
```

If 8080 is already in use on your machine:

```bash
docker run --rm -p 8081:8080 gists-api
curl http://localhost:8081/octocat
```

If you have a GitHub token (optional, helps with rate limits):

```bash
docker run --rm -p 8080:8080 -e GITHUB_TOKEN=your_token gists-api
```
