'''
    miniscript para simular el envio de heartbeats desde los ESP
'''

import time
import requests

REQUEST_URL = "http://localhost:5000/heartbeat"
CYCLE_TIME = 30
content = {"id": "Fake_ESP"}

def send_heartbeat():
    try:
        # Enviar "heartbeat" al servidor
        response = requests.post(REQUEST_URL, json=content)
        print(f"Heartbeat enviado, respuesta: {response.status_code}")
    except Exception as e:
        print(f"Error al enviar heartbeat: {e}")


while True:
    send_heartbeat()
    time.sleep(CYCLE_TIME)