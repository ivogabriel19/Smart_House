#!/usr/bin/env bash
#
# sh-watchdog — reinicia el contenedor si Docker lo marca unhealthy o si se cayó.
#
# Docker marca 'unhealthy' pero NO reinicia solo (eso es Swarm). Este watchdog,
# corrido por un timer cada minuto, cubre el caso del proceso vivo pero colgado.
# Los crashes y los reinicios de la Pi los cubre restart: unless-stopped.
set -euo pipefail

CONFIG_FILE="/etc/smarthouse/deploy.env"
[ -f "$CONFIG_FILE" ] && set -a && . "$CONFIG_FILE" && set +a

REPO_DIR="${REPO_DIR:-/opt/smarthouse}"
STATE_FILE="${STATE_FILE:-/var/lib/smarthouse/state.json}"
NOTIFY="${NOTIFY:-/usr/local/bin/sh-notify}"
CONTAINER="smarthouse"
COMPOSE="docker compose -f ${REPO_DIR}/docker-compose.yml"

# Preservar la versión desplegada: si el watchdog tiene que recrear el
# contenedor con 'up -d', que /health siga reportando el tag y no 'unknown'.
export SMARTHOUSE_VERSION="$(jq -r '.deployed // "unknown"' "$STATE_FILE" 2>/dev/null || echo unknown)"

notify() { [ -x "$NOTIFY" ] && "$NOTIFY" "$@" || true; }

status="$(docker inspect -f '{{.State.Health.Status}}' "$CONTAINER" 2>/dev/null || echo missing)"

case "$status" in
    healthy|starting)
        exit 0
        ;;
    unhealthy)
        docker restart "$CONTAINER" >/dev/null 2>&1 || $COMPOSE up -d
        notify "♻️ Smart House: contenedor unhealthy, reiniciado por el watchdog."
        ;;
    *)
        # missing / exited: intentar levantarlo.
        $COMPOSE up -d >/dev/null 2>&1 || true
        notify "♻️ Smart House: contenedor caído, levantado por el watchdog."
        ;;
esac
