#!/usr/bin/env bash
#
# sh-deploy — despliega el tag de release v* más alto y hace rollback si falla.
#
# Uso:
#   sh-deploy            # despliega si hay un tag más nuevo que el actual
#   sh-deploy --force    # redespliega el tag más alto aunque ya esté puesto
#
# Se ejecuta como root desde el timer de systemd (cada 5 min) o a mano.
# La configuración vive en /etc/smarthouse/deploy.env.
set -euo pipefail

# --- Configuración (con defaults; deploy.env puede sobreescribir) -------------
CONFIG_FILE="/etc/smarthouse/deploy.env"
[ -f "$CONFIG_FILE" ] && set -a && . "$CONFIG_FILE" && set +a

REPO_DIR="${REPO_DIR:-/opt/smarthouse}"
STATE_FILE="${STATE_FILE:-/var/lib/smarthouse/state.json}"
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:5000/health}"
HEALTH_TIMEOUT="${HEALTH_TIMEOUT:-60}"
NOTIFY="${NOTIFY:-/usr/local/bin/sh-notify}"

FORCE=0
[ "${1:-}" = "--force" ] && FORCE=1

COMPOSE="docker compose -f ${REPO_DIR}/docker-compose.yml"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }
notify() { [ -x "$NOTIFY" ] && "$NOTIFY" "$@" || true; }

# --- Resolver el tag más alto por orden de versión ---------------------------
cd "$REPO_DIR"
git config --global --add safe.directory "$REPO_DIR" 2>/dev/null || true
log "Fetch de tags…"
git fetch --tags --prune --prune-tags --quiet origin

LATEST_TAG="$(git tag -l 'v*' | sort -V | tail -n1 || true)"
if [ -z "$LATEST_TAG" ]; then
    log "No hay ningún tag v* en el repositorio. Nada para desplegar."
    exit 0
fi

# --- Tag actualmente desplegado (del archivo de estado) ----------------------
CURRENT_TAG=""
if [ -f "$STATE_FILE" ]; then
    CURRENT_TAG="$(jq -r '.deployed // ""' "$STATE_FILE" 2>/dev/null || echo "")"
fi

if [ "$LATEST_TAG" = "$CURRENT_TAG" ] && [ "$FORCE" -eq 0 ]; then
    log "Ya está desplegado $CURRENT_TAG y no hay uno más nuevo. Sin cambios."
    exit 0
fi

log "Desplegando ${LATEST_TAG} (actual: ${CURRENT_TAG:-ninguno})…"

# --- Desplegar ---------------------------------------------------------------
deploy_tag() {
    local tag="$1"
    git checkout --quiet --force "tags/${tag}"
    export SMARTHOUSE_VERSION="$tag"
    $COMPOSE build
    $COMPOSE up -d
}

health_ok() {
    local deadline=$(( $(date +%s) + HEALTH_TIMEOUT ))
    while [ "$(date +%s)" -lt "$deadline" ]; do
        if curl -fsS --max-time 5 "$HEALTH_URL" >/dev/null 2>&1; then
            return 0
        fi
        sleep 3
    done
    return 1
}

write_state() {
    local result="$1" deployed="$2" previous="$3"
    mkdir -p "$(dirname "$STATE_FILE")"
    local commit
    commit="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
    jq -n \
        --arg deployed "$deployed" \
        --arg previous "$previous" \
        --arg result "$result" \
        --arg commit "$commit" \
        --arg ts "$(date -Iseconds)" \
        '{deployed:$deployed, previous:$previous, result:$result, commit:$commit, timestamp:$ts}' \
        > "$STATE_FILE"
}

if deploy_tag "$LATEST_TAG" && health_ok; then
    log "✅ ${LATEST_TAG} desplegado y saludable."
    write_state "success" "$LATEST_TAG" "$CURRENT_TAG"
    notify "✅ Smart House: desplegado ${LATEST_TAG} (commit $(git rev-parse --short HEAD))."
    exit 0
fi

# --- Fallo → rollback --------------------------------------------------------
log "❌ ${LATEST_TAG} no pasó el healthcheck."
if [ -n "$CURRENT_TAG" ]; then
    log "Rollback a ${CURRENT_TAG}…"
    if deploy_tag "$CURRENT_TAG" && health_ok; then
        log "↩️  Rollback a ${CURRENT_TAG} exitoso."
        write_state "rolled_back" "$CURRENT_TAG" "$LATEST_TAG"
        notify "❌ Smart House: ${LATEST_TAG} falló el healthcheck. Rollback a ${CURRENT_TAG} OK."
        exit 1
    fi
    log "⚠️  El rollback a ${CURRENT_TAG} también falló."
    write_state "rollback_failed" "$CURRENT_TAG" "$LATEST_TAG"
    notify "🚨 Smart House: ${LATEST_TAG} falló Y el rollback a ${CURRENT_TAG} también. Requiere intervención."
    exit 2
fi

log "⚠️  Sin versión previa para hacer rollback (era el primer despliegue)."
write_state "failed" "" "$LATEST_TAG"
notify "🚨 Smart House: el primer despliegue de ${LATEST_TAG} falló y no hay a dónde volver."
exit 2
