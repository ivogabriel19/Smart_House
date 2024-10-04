from flask import Blueprint, render_template

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    return render_template('index.html')  # Renderiza el archivo index.html desde la carpeta templates

@views_bp.route('/device')
def device_page():
    return render_template('device.html')

@views_bp.route('/events')
def events_page():
    return render_template('events.html')