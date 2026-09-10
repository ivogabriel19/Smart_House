from flask import Blueprint, jsonify, request
from controllers.events_logic import get_events,print_events, programar_evento, eliminar_evento, get_device_events

events_bp = Blueprint('events', __name__)

@events_bp.route('/get-events', methods=['GET'])
def get_eventss():
    print_events()

    jobs = get_events()
    job_list = []

    for job in jobs:
        job_list.append({
            'id': job.id,
            'name': job.name,
        })

    return jsonify(job_list)

# Ruta para obtener los eventos de un ESP32 específico
@events_bp.route('/get_esp_events/<string:device_id>', methods=['GET'])
def get_esp_events(device_id):
    (res, cod) = get_device_events(device_id)
    return jsonify(res), cod

# Endpoint para eliminar un evento
@events_bp.route('/delete_event', methods=['DELETE'])
def delete_event():
    data = request.json
    device_id = data.get('device_id')
    job_id = data.get('job_id')
    (res, cod) = eliminar_evento(device_id, job_id)
    return jsonify(res), cod

@events_bp.route('/schedule-event', methods=['POST'])
def schedule_event():
    data = request.json
    esp_id = data.get('esp_id')
    event_alias = data.get('eventAlias')
    event_action = data.get('eventAction')
    event_type = data.get('eventType')
    event_data = data.get('eventData')
    job_id = f"evento_{esp_id}_{event_alias}"

    data = {
            "job_id" : job_id,
            "event_alias" : event_alias,
            "event_type" : event_type,
            "event_data" : event_data,
            "event_action" : event_action
        }
    
    (res, cod) = programar_evento(esp_id,data)

    return jsonify(res), cod
