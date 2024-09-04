from flask import Flask, request, jsonify, render_template
import requests
from flask_socketio import SocketIO, send, emit
import time
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)
socketio = SocketIO(app)

# Diccionario para almacenar la IP y el estado de los ESP32 registrados
esp32_devices = {
    
        "Dummy_ESP": {
            "IP": "0.0.0.1",
            "MAC" : "00:00:00:00:00:01",
            "status": "non-existent",
            "type": "fictional",
            "last_seen" : time.time()
        }
}

# Diccionario para almacenar la última vez que se recibió un heartbeat de cada ESP32
#esp_status = {}

# Intervalo de verificación en segundos (10 minutos)
CHECK_INTERVAL = 600 #10 minutos
# Tiempo de espera para la respuesta del ESP32 (en segundos) cuando se verifica conexion
VERIFICATION_TIMEOUT = 10  

# Variables globales para valores de sensores
button_state = "OFF"

temp = 0.0
hum = 0.0

@app.route('/')
def index():
    return render_template('index.html')  # Renderiza el archivo index.html desde la carpeta templates

#ruta para que se registren los ESP
@app.route('/register', methods=['POST'])
def register_device():
    data = request.json
    device_id = data.get('device_id')
    device_mac = data.get('MAC')
    device_type = data.get('type')
    device_ip = request.remote_addr  # Se obtiene la IP del dispositivo automáticamente
    if device_id:
        esp32_devices[device_id] = {
            "IP": device_ip,
            "MAC" : device_mac,
            "status": "Online",
            "last_seen": time.time(),
            "type": device_type
        }

        esp = {}
        esp[device_id] = {
            "IP": device_ip,
            "MAC" : device_mac,
            "status": "Online",
            "last_seen": time.time(),
            "type": device_type
        }

        # envia al front los datos recien recibidos
        socketio.emit('add_ESP_to_List', esp)

        return jsonify({"status": "success", "message": "Dispositivo registrado"}), 200
    else:
        return jsonify({"status": "error", "message": "ID de dispositivo faltante"}), 400

#ruta para devolver el listado harcodeado de ESPs
@app.route('/api/esp/list', methods=['GET'])
def get_esp_list():
    print("ESP registrados: ")
    print(esp32_devices)
    return jsonify(esp32_devices)

#ruta para recibir los "heartbeats"
@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    data = request.json
    esp_id = data.get('id')
    if esp_id in esp32_devices.keys():
        esp32_devices[esp_id]["last_seen"] = time.time()
        esp32_devices[esp_id]["status"] = "Online"
        print("Heartbeat recibido desde " + esp_id)
        return jsonify({"message": "Heartbeat recibido", "status": "OK"}), 200
    else:
        print("Heartbeat no corresponde a un dispositivo registrado")
        return jsonify({"message": "Heartbeat recibido", "status": "Failed"}), 400

# FIXME: la estructura de los datos en general, tanto aca como en los ESP
@app.route('/send_command/<device_id>', methods=['POST'])
def send_command(device_id):
    if device_id in esp32_devices:
        esp32_ip = f"http://{esp32_devices[device_id]['ip']}:80/actuate"
        command_value = request.json.get("value")

        # Se envía el comando al ESP32 con el valor para el actuador
        try:
            response = requests.post(esp32_ip, json={"value": command_value})
            return jsonify({"status": "success", "response": response.text}), 200
        except requests.exceptions.RequestException as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "error", "message": "Dispositivo no encontrado"}), 404

#ruta que actualiza el estado del boton proveniente del front
@app.route('/update_button', methods=['POST'])
def update_button():
    global button_state
    data = request.json  # Obtener los datos enviados desde el frontend
    button_state = data.get('state', 'OFF')  # Obtener el estado del botón
    esp_ip = data.get('destination_ip')
    print(f"Estado del botón recibido: {button_state}")
        # Enviar el estado del botón al ESP32
    if button_state:
        try:
            response = requests.post(f"http://{esp_ip}/actuator", json={'state': button_state})
            return jsonify({'status': 'success', 'message': f'ESP32 responded with {response.text}'})
        except requests.exceptions.RequestException as e:
            return jsonify({'status': 'error', 'message': str(e)})
    
    return jsonify({'status': 'error', 'message': 'Invalid state received'})

#ruta que recibe los valores de temperatura y humedad de un ESP
@app.route('/post-TyH', methods=['POST'])
def update_TyH():
    global temp
    global hum
    data = request.json  # Obtener los datos enviados desde el frontend
    temp = data.get('temperatura')
    hum = data.get('humedad')
    datoTemp = temp
    datoHum = hum

    # envia al front los datos recien recibidos
    socketio.emit('sensor_update', data)

    print(f"Datos recibidos: Temperatura={datoTemp} | Humedad={datoHum}")
    return jsonify({"message": "Temperatura y Humedad actualizadas"}), 200

@app.route('/get-TyH', methods=['GET'])
def send_TyH():
    global temp
    global hum
    return jsonify({"temperatura": str(temp) + "º", "humedad": str(hum) + "%"}), 200

# Evento para conexión
@socketio.on('connect')
def handle_connect():
    print('Cliente conectado mediante sockets')
    emit('connected', {'data': 'Conectado al servidor Flask'})

# Evento para desconexión
@socketio.on('disconnect')
def handle_disconnect():
    print('Cliente desconectado')

#funcion que checkea la conectividad de los ESP
def check_esp_status():
    global esp32_devices
    print("Verificando estado de todos los ESP...")
    for esp_id, esp_info in esp32_devices.items():
        time_diff = time.time() - esp_info['last_seen']
        if time_diff > CHECK_INTERVAL:
            esp32_devices[esp_id]['status'] = 'Verificando'
            verify_esp(esp_id, esp_info)
            print(f"ESP32 {esp_id} no ha enviado un heartbeat en los últimos 10 minutos. Enviando solicitud de verificación.")
    print("Verificacion terminada!")


#funcion que envia una solicitud get para checkear conectividad
def verify_esp(esp_id, esp_info):
    try:
        response = requests.get(f"http://{esp_info['IP']}/status", timeout=VERIFICATION_TIMEOUT)
        if response.status_code == 200:
            esp32_devices[esp_id]['status'] = 'Online'
            esp32_devices[esp_id]['last_seen'] = time.time()  # Actualizar el tiempo de la última respuesta
            print(f"{esp_id} está en línea después de la verificación.")
        else:
            esp32_devices[esp_id]['status'] = 'Offline'
    except requests.exceptions.RequestException:
        esp32_devices[esp_id]['status'] = 'Offline'
        print(f"{esp_id} está desconectado después de la verificación.")


if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=5000)
#    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    esp32_devices["Dummy_ESP"]["last_seen"] = time.time()
    scheduler = BackgroundScheduler()
    # Programa la tarea para ejecutarse cada 10 minutos
    scheduler.add_job(func=check_esp_status, trigger="interval", seconds=CHECK_INTERVAL)
    scheduler.start()

    try:
        # Iniciar la aplicación Flask
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except (KeyboardInterrupt, SystemExit):
        # Apagar el cron job si la aplicación es cerrada
        scheduler.shutdown()