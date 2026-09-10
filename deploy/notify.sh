#!/usr/bin/env bash
#
# sh-notify — manda un mensaje a Telegram. No-op silencioso si no hay token,
# para que el resto del pipeline funcione aunque el A8 (bot) todavía no esté hecho.
#
# Uso: sh-notify "texto del mensaje"
set -euo pipefail

CONFIG_FILE="/etc/smarthouse/deploy.env"
[ -f "$CONFIG_FILE" ] && set -a && . "$CONFIG_FILE" && set +a

MSG="${1:-}"
[ -z "$MSG" ] && exit 0

# Sin credenciales todavía → no molestar, salir OK.
if [ -z "${TELEGRAM_BOT_TOKEN:-}" ] || [ -z "${TELEGRAM_CHAT_ID:-}" ]; then
    exit 0
fi

curl -fsS --max-time 10 \
    "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d chat_id="${TELEGRAM_CHAT_ID}" \
    -d text="${MSG}" \
    >/dev/null 2>&1 || true
