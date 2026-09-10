"""Observabilidad: página de estado y su API.

/estado    → vista para diagnosticar el sistema desde adentro de la LAN.
/api/system → JSON que la alimenta: versión, uptimes, último deploy y ESPs.
"""
from flask import Blueprint, jsonify, render_template

from services import appinfo
from services.file_manager import leer_items

system_bp = Blueprint('system', __name__)


@system_bp.route('/api/system', methods=['GET'])
def system_info():
    devices = leer_items()
    resumen = {"total": len(devices), "online": 0, "offline": 0, "otros": 0}
    lista = []
    for d in devices:
        estado = d.get('status', 'Offline')
        if estado == 'Online':
            resumen['online'] += 1
        elif estado == 'Offline':
            resumen['offline'] += 1
        else:
            resumen['otros'] += 1
        lista.append({
            "ID": d.get('ID'),
            "type": d.get('type'),
            "status": estado,
            "last_seen": d.get('last_seen'),
        })

    return jsonify({
        "version": appinfo.APP_VERSION,
        "app_uptime": appinfo.app_uptime(),
        "host_uptime": appinfo.host_uptime(),
        "deploy": appinfo.deploy_state(),
        "devices": {"resumen": resumen, "lista": lista},
    }), 200


@system_bp.route('/estado', methods=['GET'])
def estado_page():
    return render_template('estado.html')
