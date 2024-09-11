from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# Ruta del archivo donde se guardarán los ítems
RUTA_ARCHIVO_ITEMS = './data/devices.json'

esp32_devices = {
    
        # "Dummy_ESP": {
        #     "IP": "0.0.0.1",
        #     "MAC" : "00:00:00:00:00:01",
        #     "status": "non-existent",
        #     "type": "fictional",
        #     "last_seen" : time.time()
        # }
}

# Asegurarse de que el archivo JSON existe o crearlo
if not os.path.exists(RUTA_ARCHIVO_ITEMS):
    with open(RUTA_ARCHIVO_ITEMS, 'w') as archivo:
        json.dump([], archivo)  # Guardamos una lista vacía

# Función auxiliar para leer todos los ítems del archivo JSON
def leer_items():
    with open(RUTA_ARCHIVO_ITEMS, 'r') as archivo:
        return json.load(archivo)

# Función auxiliar para guardar todos los ítems en el archivo JSON
def guardar_items(items):
    with open(RUTA_ARCHIVO_ITEMS, 'w') as archivo:
        json.dump(items, archivo, indent=4)

# Endpoint para agregar un ítem nuevo al archivo JSON
@app.route('/guardar_item', methods=['POST'])
def guardar_item():
    nuevo_item = request.json
    
    if not nuevo_item:
        return jsonify({"error": "No se recibieron datos"}), 400
    
    items = leer_items()
    items.append(nuevo_item)
    
    guardar_items(items)
    
    return jsonify({"message": "Ítem guardado exitosamente"}), 201

# Endpoint para leer todos los ítems del archivo JSON
@app.route('/leer_items', methods=['GET'])
def leer_items_endpoint():
    items = leer_items()
    return jsonify(items), 200

# Endpoint para leer un ítem específico por su "device_id"
@app.route('/leer_item/<string:device_id>', methods=['GET'])
def leer_item(device_id):
    items = leer_items()
    
    # Buscar el ítem con el "device_id" especificado
    for item in items:
        if item.get('device_id') == device_id:
            return jsonify(item), 200
    
    # Si no se encuentra el ítem
    return jsonify({"error": f"No se encontró el ítem con device_id {device_id}"}), 404


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
    
    return jsonify({"error": f"No se encontró el ítem con ID {item_id}"}), 404

# Endpoint para eliminar un ítem por su ID (o cualquier otro identificador)
@app.route('/eliminar_item/<string:device_id>', methods=['DELETE'])
def eliminar_item(device_id):
    items = leer_items()
    
    items_actualizados = [item for item in items if item.get('device_id') != device_id]
    
    if len(items) == len(items_actualizados):
        return jsonify({"error": f"No se encontró el ítem con ID {device_id}"}), 404
    
    guardar_items(items_actualizados)
    
    return jsonify({"message": f"Ítem {device_id} eliminado exitosamente"}), 200

if __name__ == '__main__':
    app.run(debug=True)
