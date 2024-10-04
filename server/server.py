from flask import Flask
from flask_socketio import SocketIO, emit

from routes.views import views_bp
from routes.files_CRUD import files_bp
from routes.devices import devices_bp
from routes.events import events_bp
from controllers.events_logic import scheduler_init, scheduler_shutdown
from services.socket_buffer import pass_socketio

app = Flask(__name__)
app.register_blueprint(views_bp)  # Registrar el blueprint
app.register_blueprint(files_bp)  # Registrar el blueprint
app.register_blueprint(devices_bp)  # Registrar el blueprint
app.register_blueprint(events_bp)  # Registrar el blueprint
socketio = SocketIO(app) 
pass_socketio(socketio)

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