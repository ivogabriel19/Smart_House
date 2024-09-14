from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, send, emit
from apscheduler.schedulers.background import BackgroundScheduler
import requests, time, json, os

app = Flask(__name__)
socketio = SocketIO(app)

# Diccionario para almacenar la IP y el estado de los ESP32 registrados
esp32_devices = [
        # {   
        #     "ID": "Dummy ESP"
        #     "IP": "0.0.0.1",
        #     "MAC" : "00:00:00:00:00:01",
        #     "status": "non-existent",
        #     "type": "fictional",
        #     "last_seen" : time.time(),
        #     "data" : {}
        # }
]


# Directorio donde se guardarán los archivos JSON de los ítems
RUTA_ARCHIVO_ITEMS = './data/devices.json'

# Asegurarse de que el archivo JSON existe o crearlo
if not os.path.exists(RUTA_ARCHIVO_ITEMS):
    with open(RUTA_ARCHIVO_ITEMS, 'w') as file:
        json.dump([], file)  # Guardamos una lista vacía en el archivo json

# Intervalo de verificación en segundos (10 minutos)
CHECK_INTERVAL = 60 # 1 minutos
# Tiempo de espera para la respuesta del ESP32 (en segundos) cuando se verifica conexion
VERIFICATION_TIMEOUT = 10  

# Variables globales para valores de sensores
button_state = "OFF"

#WARNING: obsoleto
# Función para cargar los ítems en memoria al iniciar la aplicación
def cargar_items_en_memoria():
    global esp32_devices
    if os.path.exists(RUTA_ARCHIVO_ITEMS):
        with open(RUTA_ARCHIVO_ITEMS, 'r') as archivo:
            try:
                esp32_devices = json.load(archivo)
            except json.JSONDecodeError:
                esp32_devices = []  # Inicializa como lista vacía si el JSON está malformado
    else:
        esp32_devices = []  # Inicializa como lista vacía si el archivo no existe

#FIXME: obsoleto
# Función para guardar los ítems en memoria al archivo JSON
def guardar_items_en_memoria():
    with open(RUTA_ARCHIVO_ITEMS, 'w') as archivo:
        json.dump(esp32_devices, archivo, indent=4)

# Función auxiliar para leer todos los ítems del archivo JSON
def leer_items():   #OK.
    with open(RUTA_ARCHIVO_ITEMS, 'r') as archivo:
        return json.load(archivo)

def leer_item(device_id):   #OK.
    items = leer_items()
    
    # Buscar el ítem con el "device_id" especificado
    for item in items:
        if item.get('ID') == device_id:
            return item

# Función auxiliar para guardar todos los ítems en el archivo JSON
def guardar_items(items):   #OK.
    with open(RUTA_ARCHIVO_ITEMS, 'w') as archivo:
        json.dump(items, archivo, indent=4)

#funcion auxiliar para agregar un item al json
def guardar_item(item):   #OK.
    nuevo_item = item
    
    if not nuevo_item:
        return jsonify({"error": "No se recibieron datos"}), 400
    
    items = leer_items()
    items.append(nuevo_item)
    
    guardar_items(items)
    
    return jsonify({"message": "Ítem guardado exitosamente"}), 201

def actualizar_item(item):
    try:
        # Cargar el archivo JSON existente
        with open(RUTA_ARCHIVO_ITEMS, 'r') as file:
            devices = json.load(file)
        
        # Buscar el dispositivo por su ID y actualizar los valores
        for device in devices:
            if device["ID"] == item["ID"]:
                device.update(item)  # Actualiza los valores con el nuevo ítem
                break
        else:
            # Si el dispositivo no existe, opcionalmente podrías agregarlo
            print(f"Dispositivo con ID {item['ID']} no encontrado.")
            return

        # Guardar los cambios en el archivo JSON
        with open(RUTA_ARCHIVO_ITEMS, 'w') as file:
            json.dump(devices, file, indent=4)

        print(f"Dispositivo con ID {item['ID']} actualizado correctamente.")
    
    except Exception as e:
        print(f"Error al modificar el archivo JSON: {e}")

#FIXME: dar uso
# Endpoint para agregar un ítem nuevo al archivo JSON
@app.route('/guardar_item', methods=['POST'])
def guardar_item_received():
    return jsonify(guardar_item(request.json))

#FIXME: dar uso
# Endpoint para leer todos los ítems del archivo JSON
@app.route('/leer_items', methods=['GET'])
def leer_items_endpoint():
    items = leer_items()
    return jsonify(items), 200

#FIXME: dar uso
# Endpoint para leer un ítem específico por su "device_id"
@app.route('/leer_item/<string:device_id>', methods=['GET'])
def leer_item_endpoint(device_id):
    items = leer_items()
    
    # Buscar el ítem con el "device_id" especificado
    for item in items:
        if item.get('device_id') == device_id:
            return jsonify(item), 200
    
    # Si no se encuentra el ítem
    return jsonify({"error": f"No se encontró el ítem con device_id {device_id}"}), 404

#FIXME: dar uso
# Endpoint para modificar un ítem existente por su ID (o cualquier otro identificador)
@app.route('/modificar_item/<string:device_id>', methods=['PUT'])
def modificar_item(device_id):
    items = leer_items()
    
    for item in items:
        if item.get('device_id') == device_id:
            nuevos_datos = request.json
            if not nuevos_datos:
                return jsonify({"error": "No se recibieron datos para actualizar"}), 400
            item.update(nuevos_datos)
            guardar_items(items)
            return jsonify({"message": f"Ítem {device_id} actualizado exitosamente"}), 200
    
    return jsonify({"error": f"No se encontró el ítem con ID {device_id}"}), 404

#FIXME: dar uso
# Endpoint para eliminar un ítem por su ID (o cualquier otro identificador)
@app.route('/eliminar_item/<string:device_id>', methods=['DELETE'])
def eliminar_item(device_id):
    items = leer_items()
    
    items_actualizados = [item for item in items if item.get('ID') != device_id]
    
    if len(items) == len(items_actualizados):
        return jsonify({"error": f"No se encontró el ítem con ID {device_id}"}), 404
    
    guardar_items(items_actualizados)
    
    return jsonify({"message": f"Ítem {device_id} eliminado exitosamente"}), 200

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
    
    # Verificar si el dispositivo ya está registrado en la lista
    device_exists = any(device['ID'] == device_id for device in leer_items())
    
    if not device_exists:
        # Crear nuevo diccionario para el ESP
        new_device = {
            "ID": device_id,
            "IP": device_ip,
            "MAC": device_mac,
            "status": "Online",
            "last_seen": time.time(),
            "type": device_type,
            "data" : {}
        }

        if new_device["type"] == "Sensor":
            new_device["data"] = {"temperatura":"", "humedad":""}
        
        # Guardar nuevo ESP en memoria
        #esp32_devices.append(new_device)
        
        # Guardar nuevo ESP en archivo
        guardar_item(new_device)  # guarda el nuevo dispositivo en archivo
        
        # Enviar datos al front
        socketio.emit('add_ESP_to_List', new_device)
        
        return jsonify({"status": "success", "message": "Dispositivo registrado"}), 200
    else:
        print("Dispositivo ya registrado")
        return jsonify({"status": "error", "message": "ID de dispositivo ya registrado"}), 400

#ruta para devolver el listado harcodeado de ESPs
@app.route('/api/esp/list', methods=['GET'])
def get_esp_list():
    #print("ESP registrados: ")
    #print(leer_items())
    return leer_items()

#ruta para recibir los "heartbeats"
@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    data = request.json
    esp_id = data.get('id')

    # Cargar la lista de dispositivos desde el archivo
    dispositivos = leer_items()

    # Buscar el dispositivo en la lista de diccionarios
    dispositivo_encontrado = False
    for device in dispositivos:
        if device["ID"] == esp_id:
            # Actualizar last_seen y status
            device["last_seen"] = time.time()
            device["status"] = "Online"
            dispositivo_encontrado = True
            break

    if dispositivo_encontrado:
        # Guardar los cambios en el archivo JSON
        guardar_items(dispositivos)

        # Emitir un evento de actualización al frontend si es necesario
        #socketio.emit('refresh_ESP_list')

        print(f"Heartbeat recibido desde {esp_id}")
        return jsonify({"message": "Heartbeat recibido", "status": "OK"}), 200
    else:
        print("Heartbeat no corresponde a un dispositivo registrado")
        return jsonify({"message": "Heartbeat no corresponde a un dispositivo registrado", "status": "Failed"}), 400

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
    data = request.json  # Obtener los datos enviados desde el frontend
    esp_id = data.get('id')
    temp = data.get('temperatura')
    hum = data.get('humedad')

    esp = leer_item(esp_id)
    esp['data']['temperatura'] = temp
    esp['data']['humedad'] = hum
    actualizar_item(esp)

    # envia al front los datos recien recibidos
    socketio.emit('sensor_update', esp)

    print(f"Datos recibidos: Temperatura={temp} | Humedad={hum}")
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

@app.route('/checkESP', methods=['GET'])
def launch_check_esp_list():
    check_esp_status()
    #socketio.emit('refresh_ESP_list')
    return jsonify({}), 200

#funcion que checkea la conectividad de los ESP
def check_esp_status():
    print("Verificando estado de todos los ESP...")
    # Cargar la lista de dispositivos desde el archivo
    dispositivos = leer_items()
    for device in dispositivos:
        time_diff = time.time() - device['last_seen']
        if time_diff > CHECK_INTERVAL:
            device['status'] = 'Verificando'
            # socketio.emit('refresh_ESP_list')
            #verify_esp(device)
            print(f"ESP32 {device['ID']} no ha enviado un heartbeat en los últimos 10 minutos. Enviando solicitud de verificación.")
            device['status'] = verify_esp(device)
            if device['status'] == 'Online': device['last_seen'] = time.time()
    # Guardar los cambios en el archivo después de la verificación
    guardar_items(dispositivos)
    socketio.emit('refresh_ESP_status')
    print("Verificación terminada!")

#funcion que envia una solicitud get para checkear conectividad
def verify_esp(device):
    try:
        response = requests.get(f"http://{device['IP']}/status", timeout=VERIFICATION_TIMEOUT)
        if response.status_code == 200:
            device['status'] = 'Online'
            #device['last_seen'] = time.time()  # Actualizar el tiempo de la última respuesta
            print(f"{device['ID']} está en línea después de la verificación.")
        else:
            device['status'] = 'Offline'
    except requests.exceptions.RequestException:
        device['status'] = 'Offline'
        print(f"{device['ID']} está desconectado después de la verificación.")
    
    return device['status']


if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=5000)
#    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    #check_esp_status() #para iniciar mostrando el estado actual de los ESP
    scheduler = BackgroundScheduler()

    # Programa la tarea para ejecutarse cada 10 minutos
    scheduler.add_job(func=check_esp_status, trigger="interval", seconds=CHECK_INTERVAL)
    scheduler.start()

    try:
        # Iniciar la aplicación Flask
        #FIXME: realiza el llamado de las funciones dos veces cuando esta activado el debug por el reloader
        #--degub=false o use_reloader=False deberian solucionar el problema
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except (KeyboardInterrupt, SystemExit):
        # Apagar el cron job si la aplicación es cerrada
        scheduler.shutdown()