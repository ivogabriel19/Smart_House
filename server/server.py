from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, send, emit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
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

# Intervalo de verificación en segundos (15 minutos)
CHECK_INTERVAL = 900 # 15 minutos
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

def guardar_historico_sensor(device_id, data):
    file_name = f"./data/{device_id}_historico.json"
    nuevo_registro = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "temperatura": data.get('temperatura'),
        "humedad": data.get('humedad')
    }
    
    try:
        with open(file_name, 'r') as file:
            historico = json.load(file)
    except FileNotFoundError:
        historico = []

    historico.append(nuevo_registro)
    
    with open(file_name, 'w') as file:
        json.dump(historico, file, indent=4)

    print(f"Datos guardados para {device_id}: {nuevo_registro}")

@app.route('/historico/<device_id>', methods=['GET'])
def get_historico(device_id):
    try:
        with open(f'./data/{device_id}_historico.json', 'r') as file:
            historico = json.load(file)
        return jsonify(historico)
    except FileNotFoundError:
        return jsonify({"error": "No data found for this device"}), 404

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
        if item.get('ID') == device_id:
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

@app.route('/device')
def device_page():
    return render_template('device.html')

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
        socketio.emit('add_ESP_to_List', new_device)

        # Crear archivo histórico para este dispositivo
        create_historic_file(device_id)
        
        return jsonify({"status": "success", "message": "Dispositivo registrado"}), 200
    else:
        print("Dispositivo ya registrado")
        return jsonify({"status": "error", "message": "ID de dispositivo ya registrado"}), 400

# Función para crear el archivo histórico
def create_historic_file(device_id):
    # Verificar que la carpeta "data" exista, si no, crearla
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Ruta del archivo histórico para este dispositivo
    file_path = os.path.join('data', f"{device_id}_historico.json")
    
    # Si el archivo no existe, crearlo con un array vacío
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump([], f, indent=4)  # Guarda un array vacío para empezar a registrar el historial
        print(f"Archivo histórico creado para {device_id}")
    else:
        print(f"Archivo histórico ya existe para {device_id}")

#ruta para devolver el listado harcodeado de ESPs
@app.route('/api/esp/list', methods=['GET'])
def get_esp_list():
    #print("ESP registrados: ")
    #print(leer_items())
    return jsonify(leer_items())

#ruta para recibir los "heartbeats"
@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    data = request.json
    esp_id = data.get('id')
    esp_ip = request.remote_addr  # Se obtiene la IP del dispositivo automáticamente
    

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
        return jsonify({"message": "Heartbeat recibido", "status": "OK"}), 200
    else:
        print("Heartbeat no corresponde a un dispositivo registrado")
        return jsonify({"message": "Heartbeat no corresponde a un dispositivo registrado", "status": "Failed"}), 400

def add_event_to_esp(esp_id, data):
    esp = leer_item(esp_id)
    esp["events"].append(data)
    actualizar_item(esp)

# Ruta para obtener los eventos de un ESP32 específico
@app.route('/get_esp_events/<string:device_id>', methods=['GET'])
def get_esp_events(device_id):
    try:
        # Cargar el archivo JSON de los dispositivos
        with open(RUTA_ARCHIVO_ITEMS, 'r') as f:
            devices = json.load(f)

        # Buscar el dispositivo por su ID
        for device in devices:
            if device['ID'] == device_id:
                # Si el dispositivo se encuentra, devolver sus eventos
                events = device.get('events', [])
                return jsonify({"device_id": device_id, "events": events}), 200

        # Si no se encuentra el dispositivo, devolver un error 404
        return jsonify({"error": "Device not found"}), 404
    
    except Exception as e:
        # Si ocurre algún error en la lectura o manejo del archivo JSON, devolver un error 500
        return jsonify({"error": str(e)}), 500

#ruta que actualiza el estado del boton proveniente del front
@app.route('/update_button', methods=['POST'])
def update_button():
    data = request.json  # Obtener los datos enviados desde el frontend
    button_state = data.get('state')  # Obtener el estado del botón
    esp_id = data.get('esp_id')
    esp = leer_item(esp_id)
    esp_ip = esp["IP"]
    
    print(f"Estado del botón recibido: {button_state} para el ESP {esp_id}")

    esp["data"]["switch"] = button_state
    actualizar_item(esp)

    if button_state:
        # Enviar el estado del botón al ESP32 TODO: falta que si el POST viene del ESP se actualice el estado del boton en el front
        if request.remote_addr != esp_ip:
            print("IP request: "+ str(request.remote_addr) +" IP esp: "+ str(esp_ip))
            try:
                response = requests.post(f"http://{esp_ip}/actuator", json={'state': button_state})
                return jsonify({'status': 'success', 'message': f'ESP32 responded with {response.text}'})
            except requests.exceptions.RequestException as e:
                return jsonify({'status': 'error', 'message': str(e)})
        return jsonify({'status': 'success', 'message': 'Actualizado desde el ESP por el boton'})
    
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

    guardar_historico_sensor(esp_id, esp['data'])

    print(f"Datos recibidos: Temperatura={temp} | Humedad={hum}")
    return jsonify({"message": "Temperatura y Humedad actualizadas"}), 200

@app.route('/get-TyH', methods=['GET'])
def send_TyH():
    global temp
    global hum
    return jsonify({"temperatura": str(temp) + "º", "humedad": str(hum) + "%"}), 200

@app.route('/get-events', methods=['GET'])
def get_events():
    scheduler.print_jobs()
    return jsonify({"size:" : str(len(scheduler.get_jobs())),
                    "jobs":str(scheduler.get_jobs())}), 200

#@app.route('/inconsistencias', methods=['GET'])
def verificar_consistencia_eventos():
    # Cargar el archivo JSON que contiene los ESP y eventos
    with open(RUTA_ARCHIVO_ITEMS, 'r') as file:
        devices = json.load(file)

    # Obtener todos los trabajos programados actualmente en el Scheduler
    trabajos_programados = scheduler.get_jobs()

    # Crear un set con los IDs de los trabajos en el Scheduler para comparación rápida
    trabajos_programados_ids = {job.id for job in trabajos_programados}

    inconsistencias = []

    # Iterar sobre cada dispositivo en el JSON
    for device in devices:
        device_id = device['ID']
        eventos_guardados = device.get('events', [])

        # Iterar sobre los eventos de cada dispositivo
        for evento in eventos_guardados:
            job_id = evento['job_id']

            # Verificar si el job_id está en el Scheduler
            if job_id not in trabajos_programados_ids:
                print(f"Reprogramando evento {job_id} para el dispositivo {device_id}")
                programar_evento(device_id, evento)
                inconsistencias.append({
                    'device_id': device_id,
                    'job_id': job_id,
                    'problema': 'Evento en JSON no está en el Scheduler'
                })

        # por ahora solo verifico que lo que hay en los json no falte en el scheduler
        # Verificar si el Scheduler tiene trabajos adicionales no presentes en el JSON
        # for job in trabajos_programados:
        #     if job.id not in {e['job_id'] for e in eventos_guardados} and job.id != 'checkeo_ESPs':
        #         #print(f"Eliminando trabajo {job.id} del Scheduler para el dispositivo {device_id}")
        #         #scheduler.remove_job(job.id)
        #         inconsistencias.append({
        #             'device_id': device_id,
        #             'job_id': job.id,
        #             'problema': 'Evento en el Scheduler no está en el JSON'
        #         })

    # Mostrar o manejar las inconsistencias
    if inconsistencias:
        print("Inconsistencias encontradas:")
        for inconsistencia in inconsistencias:
            print(f"Dispositivo: {inconsistencia['device_id']} - Job ID: {inconsistencia['job_id']} - Problema: {inconsistencia['problema']}")
    else:
        print("No se encontraron inconsistencias entre el JSON y el Scheduler.")

    #return jsonify({"inconsistencias":str(inconsistencias)}), 200

# Endpoint para eliminar un evento
@app.route('/delete_event', methods=['DELETE'])
def delete_event():
    data = request.json
    device_id = data.get('device_id')
    job_id = data.get('job_id')

    if not device_id or not job_id:
        return jsonify({"error": "device_id y job_id son necesarios"}), 400

    # Cargar el archivo JSON
    try:
        with open(RUTA_ARCHIVO_ITEMS, 'r') as file:
            devices = json.load(file)
    except FileNotFoundError:
        return jsonify({"error": "Archivo de dispositivos no encontrado"}), 500

    # Buscar el dispositivo
    dispositivo_encontrado = None
    for device in devices:
        if device['ID'] == device_id:
            dispositivo_encontrado = device
            break

    if not dispositivo_encontrado:
        return jsonify({"error": f"Dispositivo con ID {device_id} no encontrado"}), 404

    # Buscar y eliminar el evento del dispositivo
    evento_encontrado = None
    for evento in dispositivo_encontrado['events']:
        if evento['job_id'] == job_id:
            evento_encontrado = evento
            dispositivo_encontrado['events'].remove(evento)
            break

    if not evento_encontrado:
        return jsonify({"error": f"Evento con job_id {job_id} no encontrado en el dispositivo {device_id}"}), 404

    # Guardar el archivo JSON actualizado
    with open(RUTA_ARCHIVO_ITEMS, 'w') as file:
        json.dump(devices, file, indent=4)

    # Eliminar el evento del Scheduler
    job = scheduler.get_job(job_id)
    if job:
        scheduler.remove_job(job_id)
    else:
        return jsonify({"error": f"Job con ID {job_id} no encontrado en el Scheduler"}), 404

    return jsonify({"success": f"Evento con job_id {job_id} eliminado del dispositivo {device_id} y del Scheduler"}), 200


# Función para reprogramar un evento en el Scheduler basado en el evento guardado
def programar_evento(device_id, evento):
    job_id = evento['job_id']
    event_type = evento['event_type']
    event_data = evento['event_data']
    event_action = evento['event_action']

    func = event_relay_on if event_action == 'activar' else event_relay_off

    if event_type == 'intervalo':
        intervalo = int(event_data['interval'])
        scheduler.add_job(func=lambda: func(device_id),
                            trigger=IntervalTrigger(seconds=intervalo),
                            id=job_id, replace_existing=True)
    elif event_type == 'horario':
        time_str = event_data['time']  # Supongamos que es formato 'HH:MM'
        hora, minuto = map(int, time_str.split(":"))
        scheduler.add_job(func=lambda: func(device_id),
                            trigger=CronTrigger(hour=hora, minute=minuto),
                            id=job_id, replace_existing=True)
    elif event_type == 'fecha':
        fecha_str = event_data['date']  # Supongamos que es formato 'YYYY-MM-DD HH:MM'
        scheduler.add_job(func=lambda: func(device_id),
                            trigger=DateTrigger(run_date=fecha_str),
                            id=job_id, replace_existing=True)

def event_relay_on(esp_id):
    esp = leer_item(esp_id)
    esp_ip = esp["IP"]

    try:
        response = requests.post(f"http://{esp_ip}/actuator", json={'state': "OFF"})
        #return ({'status': 'success', 'message': f'ESP32 responded with {response.text}'})
        print({'status': 'success', 'message': f'ESP32 responded with {response.text}'})
    except requests.exceptions.RequestException as e:
        #return ({'status': 'error', 'message': str(e)})   
        print({'status': 'success', 'message': f'ESP32 responded with {response.text}'})     

def event_relay_off(esp_id):
    esp = leer_item(esp_id)
    esp_ip = esp["IP"]

    try:
        response = requests.post(f"http://{esp_ip}/actuator", json={'state': "ON"})
        #return ({'status': 'success', 'message': f'ESP32 responded with {response.text}'})
        print({'status': 'success', 'message': f'ESP32 responded with {response.text}'})
    except requests.exceptions.RequestException as e:
        #return ({'status': 'error', 'message': str(e)})   
        print({'status': 'success', 'message': f'ESP32 responded with {response.text}'})     


@app.route('/schedule-event', methods=['POST'])
def schedule_event():
    data = request.json
    esp_id = data.get('esp_id')
    event_alias = data.get('eventAlias')
    event_action = data.get('eventAction')
    event_type = data.get('eventType')
    event_data = data.get('eventData')

    if event_type == 'horario':
        time = event_data.get('time')
        # Programar el evento en un horario específico
        trigger = CronTrigger(hour=int(time.split(':')[0]), minute=int(time.split(':')[1]))
    elif event_type == 'fecha':
        time = event_data.get('time')
        date = event_data.get('date')
        # Programar el evento en una fecha específica
        trigger = DateTrigger(run_date=f"{date} {time}")
    elif event_type == 'intervalo':
        interval = event_data.get('interval')
        # Programar un evento repetitivo en intervalos
        trigger = IntervalTrigger(minutes=int(interval))
    
    # Aquí puedes definir la lógica para enviar comandos al ESP


    job_id = f"evento_{esp_id}_{event_type}"

    if event_action == "activar":
        # Agregar el evento al scheduler llamando a la funcion que corresponda
        scheduler.add_job(func=lambda:event_relay_on(esp_id), trigger=trigger, id=job_id, replace_existing=True)
        print(f"Evento {job_id} creado para {event_data}")
    
    if event_action == "desactivar":
        # Agregar el evento al scheduler llamando a la funcion que corresponda
        scheduler.add_job(func=lambda:event_relay_off(esp_id), trigger=trigger, id=job_id, replace_existing=True)
        print(f"Evento {job_id} creado para {event_data}")
    
    
    data = {
        "job_id" : job_id,
        "event_alias" : event_alias,
        "event_type" : event_type,
        "event_data" : event_data,
        "event_action" : event_action
    }

    add_event_to_esp(esp_id, data);

    return jsonify({"status": "success", "message": f"Evento para {esp_id} programado exitosamente."}), 200

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
    scheduler.add_job(id="checkeo_ESPs",func=check_esp_status, trigger="interval", seconds=CHECK_INTERVAL)
    scheduler.start()
    verificar_consistencia_eventos()

    try:
        # Iniciar la aplicación Flask
        #FIXME: realiza el llamado de las funciones dos veces cuando esta activado el debug por el reloader
        #--degub=false o use_reloader=False deberian solucionar el problema
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except (KeyboardInterrupt, SystemExit):
        # Apagar el cron job si la aplicación es cerrada
        scheduler.shutdown()