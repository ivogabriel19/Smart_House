'''
    miniscript para simular un ESP Sensor que envia temperatura y humedad
'''

import time
import requests
from datetime import datetime


SERVER_URL = "http://localhost:5000"
CYCLE_TIME = 30
contentRegister = { "device_id" : "Fake_Sensor_ESP", "MAC" : "24:0A:C4:1A:2B:3C","type": "Sensor"}
contentHeartbeat = {"id": "Fake_Sensor_ESP"}
contentData = {"id": "Fake_Sensor_ESP", "temperatura":"25", "humedad":"15" }

def register():
    try:
        # Enviar "heartbeat" al servidor
        response = requests.post(SERVER_URL+"/register", json=contentRegister)
        print(f"ESP regitrado, respuesta: {response.status_code}")
    except Exception as e:
        print(f"Error al registrarse en el server: {e}")


def send_heartbeat():
    try:
        # Enviar "heartbeat" al servidor
        response = requests.post(SERVER_URL+"/heartbeat", json=contentHeartbeat)
        print(f"Heartbeat enviado, respuesta: {response.status_code} Marca de tiempo: " + str(datetime.now().time()))
    except Exception as e:
        print(f"Error al enviar heartbeat: {e}")

def send_data():
    try:
        # Enviar "heartbeat" al servidor
        response = requests.post(SERVER_URL+"/post-TyH", json=contentData)
        print(f"Datos enviados, respuesta: {response.status_code} Marca de tiempo: " + str(datetime.now().time()))
    except Exception as e:
        print(f"Error al enviar heartbeat: {e}")

if __name__ == '__main__':
    register()
    while True:
        send_heartbeat()
        send_data()
        time.sleep(CYCLE_TIME)