'''
    miniscript para simular el envio de heartbeats desde los ESP
'''

import time
import requests

SERVER_URL = "http://localhost:5000"
CYCLE_TIME = 90
contentRegister = { "device_id" : "Fake_ESP", "MAC" : "24:0A:C4:1A:2B:3C","type": "fictional"}
contentHeartbeat = {"id": "Fake_ESP"}

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
        print(f"Heartbeat enviado, respuesta: {response.status_code}")
    except Exception as e:
        print(f"Error al enviar heartbeat: {e}")


if __name__ == '__main__':
    register()
    while True:
        send_heartbeat()
        time.sleep(CYCLE_TIME)