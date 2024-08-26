from flask import Flask, jsonify

app = Flask(__name__)

# Ejemplo de datos de ESP conectados
esp_list = [
    {"id": "ESP1", "ip": "192.168.1.101"},
    {"id": "ESP2", "ip": "192.168.1.102"},
    {"id": "ESP3", "ip": "192.168.1.103"},
]

@app.route('/api/esp/list', methods=['GET'])
def get_esp_list():
    return jsonify(esp_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
