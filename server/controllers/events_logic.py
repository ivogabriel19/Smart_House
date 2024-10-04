from services.file_manager import leer_item, leer_items, guardar_items
from controllers.devices_logic import check_esp_status, add_event_to_esp, CHECK_INTERVAL

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import requests

scheduler = BackgroundScheduler()

def scheduler_init():
    # Programa la tarea para ejecutarse cada 10 minutos
    scheduler.add_job(id="checkeo_ESPs",func=check_esp_status, trigger="interval", seconds=CHECK_INTERVAL)
    scheduler.start()
    verificar_consistencia_eventos()

def scheduler_shutdown():
    scheduler.shutdown()

def get_events():
    return scheduler.get_jobs()

def print_events():
    scheduler.print_jobs()

# Función para reprogramar un evento en el Scheduler basado en el evento guardado
def programar_evento(device_id, evento):
    job_id = evento['job_id']
    event_type = evento['event_type']
    event_data = evento['event_data']
    event_action = evento['event_action']

    if event_type == 'intervalo':
        intervalo = int(event_data['interval'])
        # Programar un evento repetitivo en intervalos
        trigger = IntervalTrigger(minutes=int(intervalo))
        
    elif event_type == 'horario':
        time_str = event_data['time']  # Supongamos que es formato 'HH:MM'
        hora, minuto = map(int, time_str.split(":"))
        trigger = CronTrigger(hour=hora, minute=minuto)

    elif event_type == 'fecha':
        #fecha_str = event_data['date']  # Supongamos que es formato 'YYYY-MM-DD HH:MM'
        time = event_data.get('time')
        date = event_data.get('date')
        # Programar el evento en una fecha específica
        trigger = DateTrigger(run_date=f"{date} {time}")

    func = event_relay_on if event_action == 'activar' else event_relay_off
    scheduler.add_job(func=lambda:func(device_id), trigger=trigger, id=job_id, replace_existing=True)
    
    add_event_to_esp(device_id, evento);

    return {"status": "success", "message": f"Evento para {device_id} programado exitosamente."}, 200



def eliminar_evento(device_id, job_id):
    if not device_id or not job_id:
        return {"error": "device_id y job_id son necesarios"}, 400

    # Cargar el archivo JSON
    try:
        # Cargar el archivo JSON de los dispositivos
        devices = leer_items()
    except FileNotFoundError:
        return {"error": "Archivo de dispositivos no encontrado"}, 500

    # Buscar el dispositivo
    dispositivo_encontrado = None
    for device in devices:
        if device['ID'] == device_id:
            dispositivo_encontrado = device
            break

    if not dispositivo_encontrado:
        return {"error": f"Dispositivo con ID {device_id} no encontrado"}, 404

    # Buscar y eliminar el evento del dispositivo
    evento_encontrado = None
    for evento in dispositivo_encontrado['events']:
        if evento['job_id'] == job_id:
            evento_encontrado = evento
            dispositivo_encontrado['events'].remove(evento)
            break

    if not evento_encontrado:
        return {"error": f"Evento con job_id {job_id} no encontrado en el dispositivo {device_id}"}, 404

    # Guardar el archivo JSON actualizado
    guardar_items(devices)

    # Eliminar el evento del Scheduler
    job = scheduler.get_job(job_id)
    if job:
        scheduler.remove_job(job_id)
    else:
        return {"error": f"Job con ID {job_id} no encontrado en el Scheduler"}, 404

    return {"success": f"Evento con job_id {job_id} eliminado del dispositivo {device_id} y del Scheduler"}, 200


#@app.route('/inconsistencias', methods=['GET'])
def verificar_consistencia_eventos():
    # Cargar el archivo JSON que contiene los ESP y eventos
    # Cargar el archivo JSON de los dispositivos
    devices = leer_items()

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

def get_device_events(device_id):
    try:
        # Cargar el archivo JSON de los dispositivos
        devices = leer_items()

        # Buscar el dispositivo por su ID
        for device in devices:
            if device['ID'] == device_id:
                # Si el dispositivo se encuentra, devolver sus eventos
                events = device.get('events', [])
                return {"device_id": device_id, "events": events}, 200

        # Si no se encuentra el dispositivo, devolver un error 404
        return {"error": "Device not found"}, 404
    
    except Exception as e:
        # Si ocurre algún error en la lectura o manejo del archivo JSON, devolver un error 500
        return {"error": str(e)}, 500

def event_relay_on(esp_id):
    esp = leer_item(esp_id)
    esp_ip = esp["IP"]

    try:
        response = requests.post(f"http://{esp_ip}/actuator", json={'state': "OFF"})
        #return ({'status': 'success', 'message': f'ESP32 responded with {response.text}'})
        print({'status': 'success', 'message': f'ESP32 responded with {response.text}'})
    except requests.exceptions.RequestException as e:
        #return ({'status': 'error', 'message': str(e)})   
        print({'status': 'error', 'message': f'error trying to execute the event'})     

def event_relay_off(esp_id):
    esp = leer_item(esp_id)
    esp_ip = esp["IP"]

    try:
        response = requests.post(f"http://{esp_ip}/actuator", json={'state': "ON"})
        #return ({'status': 'success', 'message': f'ESP32 responded with {response.text}'})
        print({'status': 'success', 'message': f'ESP32 responded with {response.text}'})
    except requests.exceptions.RequestException as e:
        #return ({'status': 'error', 'message': str(e)})   
        print({'status': 'error', 'message': f'error trying to execute the event'})     