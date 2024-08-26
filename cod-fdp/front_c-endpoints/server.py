from flask import Flask, jsonify, render_template
import json

app = Flask(__name__)

# Simulated sensor data
sensors_data = {
    "rooms": {
        "living_room": {"temperature": 22.5, "humidity": 45, "lightOn": True, "lightColor": "#ffffff", "brightness": 80},
        "bedroom": {"temperature": 20.0, "humidity": 50, "lightOn": False, "lightColor": "#ffff00", "brightness": 60},
        "kitchen": {"temperature": 23.5, "humidity": 55, "lightOn": True, "lightColor": "#00ff00", "brightness": 100}
    },
    "garden": {"sunlight": 75, "soilMoisture": 60},
    "accessLog": [
        {"time": "08:00", "event": "Puerta Desbloqueada", "rfid": "RFID-001"},
        {"time": "12:30", "event": "Ventana Abierta", "rfid": "RFID-002"},
        {"time": "18:45", "event": "Puerta Bloqueada", "rfid": "RFID-001"}
    ],
    "energyData": [
        {"name": "Lun", "energy": 4},
        {"name": "Mar", "energy": 3},
        {"name": "Mié", "energy": 5},
        {"name": "Jue", "energy": 2},
        {"name": "Vie", "energy": 4},
        {"name": "Sáb", "energy": 6},
        {"name": "Dom", "energy": 3}
    ]
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/sensors')
def get_sensors():
    return jsonify(sensors_data)

@app.route('/api/control_lighting', methods=['POST'])
def control_lighting():
    # Aquí se recibirían datos para controlar la iluminación
    # Puedes implementar el control de luces y devolver el estado actualizado
    return jsonify({"status": "success"})

@app.route('/api/start_watering', methods=['POST'])
def start_watering():
    # Aquí se activaría el sistema de riego
    return jsonify({"status": "watering started"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
