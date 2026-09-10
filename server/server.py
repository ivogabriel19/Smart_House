from flask import Flask
from flask_socketio import SocketIO, emit

from routes.views import views_bp
from routes.files_CRUD import files_bp
from routes.devices import devices_bp
from routes.events import events_bp
from routes.system import system_bp
from controllers.events_logic import scheduler_init, scheduler_shutdown, scheduler
from services.socket_buffer import pass_socketio
from services import appinfo

app = Flask(__name__)
app.register_blueprint(views_bp)  # Registrar el blueprint
app.register_blueprint(files_bp)  # Registrar el blueprint
app.register_blueprint(devices_bp)  # Registrar el blueprint
app.register_blueprint(events_bp)  # Registrar el blueprint
app.register_blueprint(system_bp)  # Observabilidad: /health, /api/system, /estado
socketio = SocketIO(app)
pass_socketio(socketio)


# Endpoint de salud: sin autenticación, sin tocar disco, respuesta en ms.
# Lo consultan el healthcheck de Docker y el watchdog cada 30 s.
@app.get('/health')
def health():
    return {
        "status": "ok",
        "version": appinfo.APP_VERSION,
        "uptime": appinfo.app_uptime(),
    }, 200


# Evento para conexión
@socketio.on('connect')
def handle_connect():
    print('Cliente conectado mediante sockets')
    emit('connected', {'data': 'Conectado al servidor Flask'})

# Evento para desconexión
@socketio.on('disconnect')
def handle_disconnect():
    print('Cliente desconectado')


# Arrancar el scheduler al ensamblar la app, para que también corra bajo
# gunicorn (donde __main__ nunca se ejecuta). Con `-w 1` hay un solo worker
# y por lo tanto un solo scheduler: es un requisito de corrección, no una
# optimización (ver revival_plan 1.1.3).
if not scheduler.running:
    scheduler_init()


if __name__ == '__main__':
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except (KeyboardInterrupt, SystemExit):
        scheduler_shutdown()
