#!/usr/bin/env bash
#
# provision.sh — deja la Raspberry lista para correr Smart House y desplegar sola.
# Idempotente: se puede volver a correr sin romper nada (retoma donde quedó).
#
# Uso (desde la Pi, o por SSH):
#   curl -fsSL https://raw.githubusercontent.com/ivogabriel19/Smart_House/main/deploy/provision.sh | sudo bash
#
# Qué hace: sistema base, Docker, clona el repo, instala el desplegador por
# tags + su timer, el aviso de boot, y despliega el tag v* más alto.
set -euo pipefail

REPO_URL="https://github.com/ivogabriel19/Smart_House.git"
REPO_DIR="/opt/smarthouse"
ETC_DIR="/etc/smarthouse"
STATE_DIR="/var/lib/smarthouse"
TARGET_USER="${SUDO_USER:-ivogabriel}"

log() { echo -e "\n\033[1;34m==>\033[0m $*"; }

if [ "$(id -u)" -ne 0 ]; then
    echo "Este script necesita root. Corré:  curl -fsSL <url> | sudo bash" >&2
    exit 1
fi

# --- 1. Sistema base ---------------------------------------------------------
log "Sistema base (apt update + paquetes)…"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq git curl jq ca-certificates >/dev/null

# --- 2. Docker Engine + compose ---------------------------------------------
if ! command -v docker >/dev/null 2>&1; then
    log "Instalando Docker Engine…"
    curl -fsSL https://get.docker.com | sh
else
    log "Docker ya está instalado ($(docker --version))."
fi
systemctl enable --now docker >/dev/null 2>&1 || true
if ! id -nG "$TARGET_USER" | grep -qw docker; then
    log "Agregando $TARGET_USER al grupo docker…"
    usermod -aG docker "$TARGET_USER"
    echo "   (⚠️  $TARGET_USER debe cerrar sesión y volver a entrar para usar docker sin sudo)"
fi

# Rotación de logs de Docker, para no castigar la SD.
if [ ! -f /etc/docker/daemon.json ]; then
    log "Configurando rotación de logs de Docker…"
    mkdir -p /etc/docker
    cat > /etc/docker/daemon.json <<'JSON'
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" }
}
JSON
    systemctl restart docker
fi

# --- 3. Directorios y secretos ----------------------------------------------
log "Directorios y configuración…"
mkdir -p "$ETC_DIR" "$STATE_DIR"

# --- 4. Repositorio ----------------------------------------------------------
if [ -d "$REPO_DIR/.git" ]; then
    log "Actualizando repo en $REPO_DIR…"
    git config --global --add safe.directory "$REPO_DIR" 2>/dev/null || true
    git -C "$REPO_DIR" fetch --tags --prune --quiet origin
else
    log "Clonando repo en $REPO_DIR…"
    git clone --quiet "$REPO_URL" "$REPO_DIR"
    git config --global --add safe.directory "$REPO_DIR" 2>/dev/null || true
fi

# El tooling (deploy/) vive en main. Un despliegue previo pudo dejar el repo
# en un tag (HEAD detached, sin deploy/ en el árbol); volver a main garantiza
# que los scripts y unidades estén presentes para instalarlos. sh-deploy vuelve
# a hacer checkout del tag de la app más abajo.
git -C "$REPO_DIR" checkout --quiet -B main origin/main

# Secretos/config: crear desde los ejemplos solo si no existen (no pisar).
if [ ! -f "$ETC_DIR/deploy.env" ]; then
    cp "$REPO_DIR/deploy/deploy.env.example" "$ETC_DIR/deploy.env"
    chmod 600 "$ETC_DIR/deploy.env"
    echo "   Creado $ETC_DIR/deploy.env (completá Telegram en el A8)."
fi
if [ ! -f "$ETC_DIR/app.env" ]; then
    cp "$REPO_DIR/deploy/app.env.example" "$ETC_DIR/app.env"
    chmod 600 "$ETC_DIR/app.env"
    echo "   Creado $ETC_DIR/app.env."
fi

# --- 5. Instalar scripts del pipeline ---------------------------------------
log "Instalando sh-deploy, sh-notify y sh-watchdog…"
install -m 755 "$REPO_DIR/deploy/deploy.sh"   /usr/local/bin/sh-deploy
install -m 755 "$REPO_DIR/deploy/notify.sh"   /usr/local/bin/sh-notify
install -m 755 "$REPO_DIR/deploy/watchdog.sh" /usr/local/bin/sh-watchdog

# --- 6. Unidades systemd -----------------------------------------------------
# Se instalan y se habilita el aviso de boot, pero los timers de deploy y
# watchdog se activan DESPUÉS del primer despliegue: si se activaran ahora, su
# OnBootSec ya cumplido los dispararía al instante y el watchdog crearía el
# contenedor por su cuenta, chocando con el primer deploy.
log "Instalando unidades de systemd…"
install -m 644 "$REPO_DIR"/deploy/systemd/*.service /etc/systemd/system/
install -m 644 "$REPO_DIR"/deploy/systemd/*.timer   /etc/systemd/system/
systemctl daemon-reload
systemctl enable smarthouse-boot-notify.service >/dev/null 2>&1 || true

# --- 7. Primer despliegue ----------------------------------------------------
log "Primer despliegue (build + up; puede tardar unos minutos)…"
/usr/local/bin/sh-deploy

# --- 7.5 Activar los timers (recién ahora, con el contenedor ya arriba) -------
log "Activando timers de deploy y watchdog…"
systemctl enable --now smarthouse-deploy.timer >/dev/null 2>&1 || true
systemctl enable --now smarthouse-watchdog.timer >/dev/null 2>&1 || true

# --- 8. Verificación ---------------------------------------------------------
log "Verificación:"
sleep 2
if curl -fsS --max-time 5 http://127.0.0.1:5000/health >/dev/null 2>&1; then
    echo "   ✅ /health responde. Dashboard en http://smarthouse.local:5000"
    curl -fsS http://127.0.0.1:5000/health; echo
else
    echo "   ⚠️  /health no responde todavía. Revisá:  docker compose -f $REPO_DIR/docker-compose.yml logs --tail 50"
fi
echo
echo "Estado del despliegue: $(jq -r '"\(.deployed) (\(.result))"' "$STATE_DIR/state.json" 2>/dev/null || echo desconocido)"
systemctl list-timers --no-pager 2>/dev/null | grep smarthouse || true
log "Listo."
