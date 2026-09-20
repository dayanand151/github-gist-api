FROM python:3.12-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN python -m venv /venv \
    && /venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /venv /venv
COPY app.py github_client.py ./

RUN useradd -m appuser
USER appuser

EXPOSE 8080

# bind 0.0.0.0 or nothing outside the container can reach it
CMD ["/venv/bin/gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
