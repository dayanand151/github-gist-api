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

## Dockerfiles

There are two files. Both are two-stage builds on `python:3.12-slim`.

**`Dockerfile`** — simple one. Builder makes a venv and installs `requirements.txt`. Final image copies the venv, `app.py` and `github_client.py`, then runs gunicorn as `appuser`.

**`Dockerfile.secure`** — same app, tighter runtime. User `appuser` (uid 10001) is in `appgroup`, has no home and no login shell (`/usr/sbin/nologin`). App files stay root-owned and are not writable. There is a health check on `/health`.

`EXPOSE 8080` is just documentation. Gunicorn actually listens on `0.0.0.0:8080`. It has to be `0.0.0.0` or you can't reach it from outside the container.

`.dockerignore` keeps `.venv`, tests and `.git` out of the build.

## Build and run

From this folder:

```bash
docker build -t gists-api .
docker run --rm -p 8080:8080 gists-api
```

`-p 8080:8080` is host port → container port. `--rm` deletes the container when you stop it.

Secure image (read-only disk, `/tmp` in memory, no extra Linux capabilities):

```bash
docker build -f Dockerfile.secure -t gists-api:secure .
docker run --rm --read-only --tmpfs /tmp \
  --cap-drop ALL --security-opt no-new-privileges \
  -p 8080:8080 gists-api:secure
```

```bash
curl http://localhost:8080/health
curl http://localhost:8080/octocat
```

If 8080 is already in use:

```bash
docker run --rm -p 8081:8080 gists-api
curl http://localhost:8081/octocat
```

GitHub token (optional, helps with rate limits):

```bash
docker run --rm -p 8080:8080 -e GITHUB_TOKEN=your_token gists-api
```

## CI

On push to `solution`, GitHub Actions runs the tests (with coverage), builds the image, scans it with Trivy, then pushes it to Docker Hub.

Coverage (`coverage.xml`, `htmlcov/`) and the Trivy report are uploaded as workflow artifacts.

You need two repo secrets: `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`.
