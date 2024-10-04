from datetime import datetime
import json, os

# Directorio donde se guardarán los archivos JSON de los ítems
RUTA_ARCHIVO_ITEMS = './data/devices.json'

# Asegurarse de que el archivo JSON existe o crearlo
if not os.path.exists(RUTA_ARCHIVO_ITEMS):
    with open(RUTA_ARCHIVO_ITEMS, 'w') as file:
        json.dump([], file)  # Guardamos una lista vacía en el archivo json

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
        #return jsonify({"error": "No se recibieron datos"}), 400
        return {"error": "No se recibieron datos"}
    
    items = leer_items()
    items.append(nuevo_item)
    
    guardar_items(items)
    
    #return jsonify({"message": "Ítem guardado exitosamente"}), 201
    return {"message": "Ítem guardado exitosamente"}

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
