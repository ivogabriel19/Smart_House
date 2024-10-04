from flask import Blueprint, request, jsonify
from controllers.devices_logic import check_esp_status, register_esp, receive_heartbeat, change_btn, post_tyh, esp_list

devices_bp = Blueprint('devices', __name__)

#ruta para que se registren los ESP
@devices_bp.route('/register', methods=['POST'])
def register_device():
    data = request.json
    device_id = data.get('device_id')
    device_mac = data.get('MAC')
    device_type = data.get('type')
    device_ip = request.remote_addr  # Se obtiene la IP del dispositivo automáticamente
    
    (res, cod) = register_esp(device_id, device_mac, device_type, device_ip)

    return jsonify(res), cod

#ruta para devolver el listado harcodeado de ESPs
@devices_bp.route('/api/esp/list', methods=['GET'])
def get_esp_list():
    (res, cod) = esp_list()
    return jsonify(res), cod

#ruta para recibir los "heartbeats"
@devices_bp.route('/heartbeat', methods=['POST'])
def heartbeat():
    data = request.json
    esp_id = data.get('id')
    esp_ip = request.remote_addr  # Se obtiene la IP del dispositivo automáticamente

    (res, cod) = receive_heartbeat(esp_id, esp_ip)
    return jsonify(res), cod

#ruta que actualiza el estado del boton proveniente del front
@devices_bp.route('/update_button', methods=['POST'])
def update_button():
    data = request.json  # Obtener los datos enviados desde el frontend
    button_state = data.get('state')  # Obtener el estado del botón
    esp_id = data.get('esp_id')
    
    (cod, res) = change_btn(esp_id, button_state)
    return jsonify(cod), res
    
#ruta que recibe los valores de temperatura y humedad de un ESP
@devices_bp.route('/post-TyH', methods=['POST'])
def update_TyH():
    data = request.json  # Obtener los datos enviados desde el frontend
    esp_id = data.get('id')
    temp = data.get('temperatura')
    hum = data.get('humedad')

    (cod, res) = post_tyh(esp_id, temp, hum)
    return jsonify(res), cod

@devices_bp.route('/get-TyH', methods=['GET'])
def send_TyH():
    return jsonify(), 200

@devices_bp.route('/checkESP', methods=['GET'])
def launch_check_esp_list():
    check_esp_status()
    #socketio.emit('refresh_ESP_list')
    return jsonify({}), 200