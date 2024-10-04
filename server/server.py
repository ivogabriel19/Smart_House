from flask import Flask
from flask_socketio import SocketIO, send, emit
from apscheduler.schedulers.background import BackgroundScheduler

from routes.views import views_bp
from routes.files_CRUD import files_bp
from routes.devices import devices_bp
from routes.events import events_bp
from controllers.events_logic import scheduler_init, scheduler_shutdown

app = Flask(__name__)
app.register_blueprint(views_bp)  # Registrar el blueprint
app.register_blueprint(files_bp)  # Registrar el blueprint
app.register_blueprint(devices_bp)  # Registrar el blueprint
app.register_blueprint(events_bp)  # Registrar el blueprint
socketio = SocketIO(app)

# Intervalo de verificación en segundos (15 minutos)
CHECK_INTERVAL = 900 # 15 minutos

# Tiempo de espera para la respuesta del ESP32 (en segundos) cuando se verifica conexion
VERIFICATION_TIMEOUT = 10  

def socket_emit(event, data):
    socketio.emit(event, data)

# Evento para conexión
@socketio.on('connect')
def handle_connect():
    print('Cliente conectado mediante sockets')
    emit('connected', {'data': 'Conectado al servidor Flask'})

# Evento para desconexión
@socketio.on('disconnect')
def handle_disconnect():
    print('Cliente desconectado')

if __name__ == '__main__':
    scheduler_init()

    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except (KeyboardInterrupt, SystemExit):
        scheduler_shutdown()