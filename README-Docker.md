# FinDisclosure — Docker setup

This directory adds a Docker / docker-compose environment for FinDisclosure.
It lets you run the Telegram bot in an isolated container and override every
`config.yaml` parameter through environment variables — including which remote
service the bot uses.

## Files added

| File | Purpose |
|------|---------|
| `Dockerfile` | Python 3.12-slim image, installs `requirements.txt`, runs the app under `tini` for proper signal handling. |
| `docker-entrypoint.sh` | Renders `/app/config.yaml` from environment variables at container start, then `exec`s `python main.py`. |
| `docker-compose.yml` | Single-service compose file. Pulls all variables from `.env`, persists `reports/` and `logs/` as bind-mounts. |
| `.env.example` | Documented template — copy to `.env` and fill in your real secrets. |
| `.dockerignore` | Keeps build context lean (excludes `.env`, `reports/`, `logs/`, generated `config.yaml`). |
| `app/core/constructor_facade.py` | Patched to read `REMOTE_SERVICE` env var (or `active_remote_services` config key) and activate only the services you select. Defaults to `raw`, preserving original behaviour. |

## How config is injected

The original project reads everything from `config.yaml` via
`Utils.get_config_file()`. We do **not** modify that code path. Instead the
entrypoint script builds `config.yaml` at container start from env vars:

```
.env  -->  docker-compose env  -->  docker-entrypoint.sh  -->  /app/config.yaml  -->  app
```

Each `config.yaml` key maps to exactly one env var (see `.env.example` for the
full table). To change a value, edit `.env` and `docker compose up -d` — no
rebuild required.

## Choosing a remote service

The bot supports three remote services (`raw`, `open`, `google`). Only the
ones listed in `REMOTE_SERVICE` are activated at startup.

| Goal | Set in `.env` |
|------|---------------|
| Default (custom HTTP service) | `REMOTE_SERVICE=raw` |
| Use OpenAI-compatible API | `REMOTE_SERVICE=open` |
| Use Google Gemini | `REMOTE_SERVICE=google` |
| Use both `open` and `google` (in order) | `REMOTE_SERVICE=open,google` |

Only fill in the credentials for the services you actually activate — the
others are simply not instantiated.

## Quick start

```bash
# 1. Copy the env template and fill in real values (esp. TELEGRAM_BOT_TOKEN
#    and the credentials for the remote service you chose).
cp .env.example .env
$EDITOR .env

# 2. Build and start in detached mode.
docker compose up --build -d

# 3. Tail logs.
docker compose logs -f

# 4. Stop / restart.
docker compose down
```

Generated `.docx` reports land in `./reports/`, application logs in
`./logs/`. Both survive container restarts thanks to the bind-mounts in
`docker-compose.yml`.

## Switching the database

The default `DATABASE_URL` is in-memory SQLite (matches `config_test.yaml`).
To run against a real database, set `DATABASE_URL` in `.env`, e.g.:

```
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/disclosure
```

You can also bring up Postgres as a second compose service and link them —
see the commented-out example block at the bottom of `docker-compose.yml`
(extend as needed).

## Verifying the generated config

To inspect what `config.yaml` the container will actually use, without
starting the bot:

```bash
docker compose run --rm --no-deps --entrypoint /bin/sh findisclosure \
  -c './docker-entrypoint.sh cat /app/config.yaml'
```

The entrypoint prints the generated YAML and exits.

## Troubleshooting

| Symptom | Fix |
|--------|-----|
| Bot starts but no responses in Telegram | Check `TELEGRAM_BOT_TOKEN` and `TELEGRAM_ALLOWED_USER_ID`. |
| `[OpenService_c]: api_key_v: False` | The activated service has no API key set in `.env`. |
| Container exits immediately | `docker compose logs` — usually a missing required env var. |
| Reports not appearing on host | Ensure `./reports/` exists and is writable by the container's UID. |

## Backward compatibility

If you run the app **outside** Docker (e.g. `python main.py` from the repo
root), nothing changes: the original `config.yaml` is still loaded the same
way. The patch in `constructor_facade.py` is fully backward-compatible —
when `REMOTE_SERVICE` is unset and `active_remote_services` is absent from
config, it defaults to `["raw"]` exactly as before.
