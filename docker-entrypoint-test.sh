#!/bin/sh
# ---------------------------------------------------------------------------
# docker-entrypoint.sh
#
# Generates /app/config.yaml from environment variables at container start,
# then execs the original application entrypoint (main.py).
#
# Every parameter that the project reads from config.yaml is mapped to an
# environment variable so you can override it without touching the image.
#
# Env precedence (highest -> lowest):
#   1. explicitly set env var
#   2. value from .env file (loaded by docker-compose)
#   3. built-in default defined below
# ---------------------------------------------------------------------------
set -eu

APP_DIR="${APP_DIR:-/app}"
CONFIG_FILE="${CONFIG_FILE:-${APP_DIR}/config.yaml}"

# Helper: return env value or default.
val() { eval "echo \"\${${1}:-${2}}\""; }

# --- system ----------------------------------------------------------------
SYS_NAME="$(val SYSTEM_NAME 'Disclosure-helper')"
SYS_VERSION="$(val SYSTEM_VERSION '0.1')"

# --- telegram --------------------------------------------------------------
TG_BOT_TOKEN="$(val TELEGRAM_BOT_TOKEN '')"
TG_BOT_NAME="$(val TELEGRAM_BOT_NAME '')"
# allowed_user_id is a comma-separated list in the env, emitted as a YAML list.
TG_ALLOWED_RAW="$(val TELEGRAM_ALLOWED_USER_ID '')"
if [ -n "${TG_ALLOWED_RAW}" ]; then
    TG_ALLOWED_YAML="$(printf '%s\n' "${TG_ALLOWED_RAW}" | tr ',' '\n' | sed 's/^/    - /')"
else
    TG_ALLOWED_YAML="    []"
fi

# --- database --------------------------------------------------------------
# Default: in-memory SQLite (matches config_test.yaml). Override with a real
# URL, e.g. postgresql+asyncpg://user:pass@db:5432/disclosure
DB_URL="$(val DATABASE_URL 'sqlite+aiosqlite:///file:mem_db?mode=memory&cache=shared&uri=true')"

# --- remote services: open_service / raw_service / google_service ----------
OPEN_MODEL="$(val OPEN_SERVICE_MODEL '')"
OPEN_URL="$(val OPEN_SERVICE_URL '')"
OPEN_KEY="$(val OPEN_SERVICE_API_KEY '')"

RAW_MODEL="$(val RAW_SERVICE_MODEL '')"
RAW_URL="$(val RAW_SERVICE_URL '')"
RAW_KEY="$(val RAW_SERVICE_API_KEY '')"

GOOGLE_MODEL="$(val GOOGLE_SERVICE_MODEL '')"
GOOGLE_KEY="$(val GOOGLE_SERVICE_API_KEY '')"

# --- directory / dictionary ------------------------------------------------
DIRECTORY_PATH="$(val DIRECTORY_PATH 'questions.json')"

# --- mail ------------------------------------------------------------------
MAIL_HOST="$(val MAIL_HOST '')"
MAIL_PORT="$(val MAIL_PORT 465)"
MAIL_USERNAME="$(val MAIL_USERNAME '')"
MAIL_PASSWORD="$(val MAIL_PASSWORD '')"
MAIL_SENDER="$(val MAIL_SENDER '')"
MAIL_USE_TLS="$(val MAIL_USE_TLS true)"
MAIL_TO_RAW="$(val MAIL_TO '')"
if [ -n "${MAIL_TO_RAW}" ]; then
    MAIL_TO_YAML="$(printf '%s\n' "${MAIL_TO_RAW}" | tr ',' '\n' | sed 's/^/    - /')"
else
    MAIL_TO_YAML="    []"
fi

# --- doc_writer ------------------------------------------------------------
DOC_OUTPUT_DIR="$(val DOC_OUTPUT_DIR './reports')"

# --- delay -----------------------------------------------------------------
DELAY_SECOND="$(val DELAY_SECOND 7)"

# --- which remote service(s) are active (read by constructor_facade.py) ----
# Either REMOTE_SERVICE env var or ACTIVE_REMOTE_SERVICES config key.
# Comma-separated list, e.g. "raw" or "open,google".
REMOTE_SERVICE_VAL="$(val REMOTE_SERVICE 'raw')"
if echo "${REMOTE_SERVICE_VAL}" | grep -q ','; then
    REMOTE_SERVICES_YAML="$(printf '%s\n' "${REMOTE_SERVICE_VAL}" | tr ',' '\n' | sed 's/^/    - /')"
else
    REMOTE_SERVICES_YAML="    - ${REMOTE_SERVICE_VAL}"
fi

echo "[entrypoint] writing config to ${CONFIG_FILE}"
cat > "${CONFIG_FILE}" <<EOF
system:
  name: "${SYS_NAME}"
  version: "${SYS_VERSION}"

telegram:
  bot_token: "${TG_BOT_TOKEN}"
  bot_name: "${TG_BOT_NAME}"
  allowed_user_id:
${TG_ALLOWED_YAML}

database:
  url: "${DB_URL}"

open_service:
  model: "${OPEN_MODEL}"
  url: "${OPEN_URL}"
  api_key: "${OPEN_KEY}"

raw_service:
  model: "${RAW_MODEL}"
  url: "${RAW_URL}"
  api_key: "${RAW_KEY}"

google_service:
  model: "${GOOGLE_MODEL}"
  api_key: "${GOOGLE_KEY}"

# Injected by docker-entrypoint.sh — consumed by ConstructorFacade to pick
# which remote service(s) to activate. Overridden by the REMOTE_SERVICE env
# var when present. Tokens: raw | open | google (comma-separated).
active_remote_services:
${REMOTE_SERVICES_YAML}

directory:
  path: "${DIRECTORY_PATH}"

mail:
  host: "${MAIL_HOST}"
  port: ${MAIL_PORT}
  username: "${MAIL_USERNAME}"
  password: "${MAIL_PASSWORD}"
  sender: "${MAIL_SENDER}"
  use_tls: ${MAIL_USE_TLS}
  to:
${MAIL_TO_YAML}

doc_writer:
  output_dir: "${DOC_OUTPUT_DIR}"

delay:
  second: ${DELAY_SECOND}
EOF

echo "[entrypoint] config generated. Starting application..."
echo "[entrypoint] active remote service(s): ${REMOTE_SERVICE_VAL}"
exec "$@"
