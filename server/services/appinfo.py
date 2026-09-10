"""Información del proceso y del sistema para /health y /api/system.

Centralizado acá para que server.py (que arma la app) y el blueprint de
observabilidad compartan el mismo instante de arranque sin imports circulares.
"""
import os
import time
import json

# Instante de arranque del proceso y versión desplegada (la inyecta el
# desplegador vía SMARTHOUSE_VERSION; 'unknown' fuera de un deploy).
APP_START = time.time()
APP_VERSION = os.environ.get('SMARTHOUSE_VERSION', 'unknown')

# Archivo de estado del desplegador, montado read-only en el contenedor.
STATE_PATH = os.environ.get('SMARTHOUSE_STATE', '/app/state/state.json')


def app_uptime():
    """Segundos desde que arrancó el proceso de la app."""
    return round(time.time() - APP_START, 1)


def host_uptime():
    """Segundos desde que booteó la máquina, o None si no se puede leer.

    /proc/uptime refleja el host aunque se lea desde el contenedor (kernel
    compartido). En Windows no existe, así que devuelve None.
    """
    try:
        with open('/proc/uptime', 'r') as f:
            return round(float(f.read().split()[0]), 1)
    except (OSError, ValueError):
        return None


def deploy_state():
    """Contenido del state.json del desplegador, o None si todavía no hay."""
    try:
        with open(STATE_PATH, 'r') as f:
            return json.load(f)
    except (OSError, ValueError):
        return None
