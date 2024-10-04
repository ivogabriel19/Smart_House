from flask import request
import requests, time
from services.file_manager import guardar_item, guardar_items, leer_item, leer_items, actualizar_item, create_historic_file, guardar_historico_sensor
from services.socket_buffer import socket_emit

# Intervalo de verificación en segundos (15 minutos)
CHECK_INTERVAL = 900 # 15 minutos

# Tiempo de espera para la respuesta del ESP32 (en segundos) cuando se verifica conexion
VERIFICATION_TIMEOUT = 10 

def esp_list():
    return leer_items(), 200

def register_esp(device_id, device_mac, device_type, device_ip):
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
            "data" : {},
            "events" : []
        }

        if new_device["type"] == "Sensor":
            new_device["data"] = {"temperatura":"", "humedad":""}
        if new_device["type"] == "Actuador":
            new_device["data"] = {"switch":"OFF"}
        
        # Guardar nuevo ESP en memoria
        #esp32_devices.append(new_device)
        
        # Guardar nuevo ESP en archivo
        guardar_item(new_device)  # guarda el nuevo dispositivo en archivo
        
        # Enviar datos al front
        socket_emit('add_ESP_to_List', new_device)

        # Crear archivo histórico para este dispositivo
        create_historic_file(device_id)
        
        return {"status": "success", "message": "Dispositivo registrado"}, 200
    else:
        print("Dispositivo ya registrado")
        return {"status": "error", "message": "ID de dispositivo ya registrado"}, 400

def receive_heartbeat(esp_id, esp_ip):
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
            if device["IP"] != esp_ip:
                device["IP"] = esp_ip
            break

    if dispositivo_encontrado:
        # Guardar los cambios en el archivo JSON
        guardar_items(dispositivos)

        # Emitir un evento de actualización al frontend si es necesario
        #socketio.emit('refresh_ESP_list')

        print(f"Heartbeat recibido desde {esp_id}")
        return {"message": "Heartbeat recibido", "status": "OK"}, 200
    else:
        print("Heartbeat no corresponde a un dispositivo registrado")
        return {"message": "Heartbeat no corresponde a un dispositivo registrado", "status": "Failed"}, 400

def add_event_to_esp(esp_id, data):
    esp = leer_item(esp_id)
    esp["events"].append(data)
    actualizar_item(esp)

def change_btn(esp_id, button_state):
    esp = leer_item(esp_id)
    esp_ip = esp["IP"]
    esp["data"]["switch"] = button_state

    print(f"Estado del botón recibido: {button_state} para el ESP {esp_id}")
    actualizar_item(esp)

    if button_state:
        # Enviar el estado del botón al ESP32 TODO: falta que si el POST viene del ESP se actualice el estado del boton en el front
        if request.remote_addr != esp_ip:
            print("IP request: "+ str(request.remote_addr) +" IP esp: "+ str(esp_ip))
            try:
                response = requests.post(f"http://{esp_ip}/actuator", json={'state': button_state})
                return {'status': 'success', 'message': f'ESP32 responded with {response.text}'}, 200
            except requests.exceptions.RequestException as e:
                return {'status': 'error', 'message': str(e)}, 500
        return {'status': 'success', 'message': 'Actualizado desde el ESP por el boton'}, 200
    
    return {'status': 'error', 'message': 'Invalid state received'}, 400

def post_tyh(esp_id, temp, hum):
    esp = leer_item(esp_id)
    esp['data']['temperatura'] = temp
    esp['data']['humedad'] = hum
    actualizar_item(esp)

    # envia al front los datos recien recibidos
    socket_emit('sensor_update', esp)

    guardar_historico_sensor(esp_id, esp['data'])

    print(f"Datos recibidos: Temperatura={temp} | Humedad={hum}")
    return {"message": "Temperatura y Humedad actualizadas"}, 200


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
    socket_emit('refresh_ESP_status')
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
