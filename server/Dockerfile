# Imagen base liviana. Python 3.11: eventlet 0.36 es incompatible con 3.13.
FROM python:3.11-slim-bookworm

# .pyc fuera, stdout sin buffer, y server/ en el path para los imports
# top-level (routes.*, controllers.*, services.*).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Dependencias primero, para aprovechar la cache de capas.
COPY server/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Código de la app.
COPY server/ /app/

# Usuario no-root y directorio de datos con permisos correctos.
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

# -w 1 es obligatorio: con varios workers habría N schedulers y cada evento
# se dispararía N veces. -k eventlet es lo que sirve Flask-SocketIO.
CMD ["gunicorn", "-k", "eventlet", "-w", "1", "-b", "0.0.0.0:5000", "server:app"]
