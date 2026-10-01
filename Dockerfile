# syntax=docker/dockerfile:1.7
#
# Dockerfile for FinDisclosure
# https://github.com/ewanytken/FinDisclosure
#
# The container starts via docker-entrypoint.sh, which materialises
# /app/config.yaml from environment variables before launching main.py.
# This means every config.yaml parameter is overridable from docker-compose
# / .env without rebuilding the image.

FROM python:3.12-slim AS base

# --- system packages -------------------------------------------------------
#   build-essential  : needed by some wheels (lxml, etc.) if no prebuilt wheel
#   libxml2/libxslt  : lxml runtime deps
#   curl             : healthcheck / debugging
#   tini              : proper PID 1 signal handling for asyncio apps
#   ca-certificates  : TLS for outgoing HTTPS calls (LLM providers, mail)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libxml2 \
        libxslt1.1 \
        curl \
        tini \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# --- python deps -----------------------------------------------------------
WORKDIR /app

# Install requirements first to maximise Docker layer caching.
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# --- application code -------------------------------------------------------
COPY . .

# Make sure the runtime entrypoint is executable (git may drop the +x bit).
RUN chmod +x docker-entrypoint.sh

# Directories the app writes to at runtime. Mount these as volumes in
# docker-compose.yml so reports/logs survive container restarts.
RUN mkdir -p /app/reports /app/logs /app/documents

# --- runtime ---------------------------------------------------------------
# Default remote service selection. Override in .env / docker-compose.yml.
ENV APP_DIR=/app \
    CONFIG_FILE=/app/config.yaml \
    REMOTE_SERVICE=raw \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Generated config.yaml lives here (entrypoint writes it on each start).
# Reports and logs are also persisted on these volumes.
VOLUME ["/app/reports", "/app/logs"]

ENTRYPOINT ["/usr/bin/tini", "--", "/app/docker-entrypoint.sh"]
CMD ["python", "main.py"]

# Lightweight healthcheck: container is up if the python process exists.
# (aiogram long-polling does not expose a port, so we check the process tree.)
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD pgrep -f "python main.py" > /dev/null || exit 1
