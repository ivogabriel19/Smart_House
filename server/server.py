from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# Diccionario para almacenar la IP y el estado de los ESP32 registrados
esp32_devices = {}

# Variable global para almacenar el estado del botón
button_state = "OFF"

@app.route('/')
def index():
    return render_template('index.html')  # Renderiza el archivo index.html desde la carpeta templates

#ruta para devolver el listado harcodeado de ESPs
@app.route('/api/esp/list', methods=['GET'])
def get_esp_list():
    return jsonify(esp32_devices)

@app.route('/register', methods=['POST'])
def register_device():
    data = request.json
    device_id = data.get('device_id')
    device_ip = request.remote_addr  # Se obtiene la IP del dispositivo automáticamente
    if device_id:
        esp32_devices[device_id] = {
            "ip": device_ip,
            "status": "connected"
        }
        return jsonify({"status": "success", "message": "Dispositivo registrado"}), 200
    else:
        return jsonify({"status": "error", "message": "ID de dispositivo faltante"}), 400

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

@app.route('/update_button', methods=['POST'])
def update_button():
    global button_state
    data = request.json  # Obtener los datos enviados desde el frontend
    button_state = data.get('state', 'OFF')  # Obtener el estado del botón
    print(f"Estado del botón recibido: {button_state}")
    return jsonify({"message": "Estado del botón actualizado", "state": button_state})


@app.route('/post-TyH', methods=['POST'])
def update_TyH():
    data = request.json  # Obtener los datos enviados desde el frontend
    datoTemp = data.get('temperatura')
    datoHum = data.get('humedad')
    print(f"Datos recibidos: Temperatura={datoTemp} | Humedad={datoHum}")
    return jsonify({"message": "Temperatura y Humedad actualizadas"}), 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
