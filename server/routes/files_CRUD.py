from flask import Blueprint, jsonify, request
from services.file_manager import guardar_item, guardar_items, leer_item, leer_items
import json

files_bp = Blueprint('files_CRUD', __name__)

@files_bp.route('/historico/<device_id>', methods=['GET'])
def get_historico(device_id):
    try:
        with open(f'./data/{device_id}_historico.json', 'r') as file:
            historico = json.load(file)
        return jsonify(historico)
    except FileNotFoundError:
        return jsonify({"error": "No data found for this device"}), 404

#FIXME: dar uso
# Endpoint para agregar un ítem nuevo al archivo JSON
@files_bp.route('/guardar_item', methods=['POST'])
def guardar_item_received():
    return jsonify(guardar_item(request.json)), 201

#FIXME: dar uso
# Endpoint para leer todos los ítems del archivo JSON
@files_bp.route('/leer_items', methods=['GET'])
def leer_items_endpoint():
    items = leer_items()
    return jsonify(items), 200

#FIXME: dar uso
# Endpoint para leer un ítem específico por su "device_id"
@files_bp.route('/leer_item/<string:device_id>', methods=['GET'])
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
@files_bp.route('/modificar_item/<string:device_id>', methods=['PUT'])
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
@files_bp.route('/eliminar_item/<string:device_id>', methods=['DELETE'])
def eliminar_item(device_id):
    items = leer_items()
    
    items_actualizados = [item for item in items if item.get('ID') != device_id]
    
    if len(items) == len(items_actualizados):
        return jsonify({"error": f"No se encontró el ítem con ID {device_id}"}), 404
    
    guardar_items(items_actualizados)
    
    return jsonify({"message": f"Ítem {device_id} eliminado exitosamente"}), 200
