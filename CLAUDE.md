# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Smart House is a distributed IoT home automation system with three layers:
- **Flask server** running on a Raspberry Pi (central coordinator)
- **ESP32/ESP8266 microcontroller clients** (sensors and actuators)
- **Web frontend** served by Flask (HTML/JS/CSS with Socket.IO and Chart.js)

## Running the Server

```bash
cd server
pip install -r requirements.txt
python server.py
```

The server runs on port 5000 by default. No build step — the frontend is served as static files by Flask.

## Simulating ESP Clients (for development)

Two helper scripts exist to simulate hardware without physical devices:

```bash
cd server/aux_code
python dummy_heartbeat.py       # Simulates ESP sending heartbeats
python dummy_sensor_temp.py     # Simulates temperature/humidity sensor data
```

## Architecture

### Communication Flow

```
Browser ──WebSocket/HTTP──► Flask Server (Raspberry Pi)
                                    │
                           HTTP POST/GET
                                    │
                    ┌───────────────┴───────────────┐
                ESP32 Actuators            ESP8266 Sensors
```

### Backend (`server/server.py`)

Single-file Flask app (~689 lines). Key responsibilities:
- **Device registry**: ESPs register at startup via `/register`, then send `/heartbeat` every 15s
- **Persistence**: JSON files at `./data/devices.json` (device state) and `./data/{device_id}_historico.json` (sensor history)
- **Event scheduling**: APScheduler jobs with three trigger types — `CronTrigger` (daily time), `DateTrigger` (one-time), `IntervalTrigger` (repeating)
- **Real-time frontend updates**: Emits Socket.IO events (`add_ESP_to_List`, `sensor_update`, `refresh_ESP_status`)
- **Background job**: Heartbeat check runs every 900s to mark unresponsive devices as "Offline"

Job IDs follow the pattern: `evento_{esp_id}_{event_alias}` (e.g., `evento_ESP32_001_mañana`)

### Device Data Model (`devices.json`)

```json
{
  "ID": "ESP32_001",
  "IP": "192.168.1.100",
  "MAC": "AA:BB:CC:DD:EE:FF",
  "status": "Online",        // "Online", "Offline", "Verificando"
  "type": "Sensor",          // "Sensor", "Actuador", "Basico"
  "last_seen": 1713429600.0,
  "data": {"temperatura": "25.5", "humedad": "60"},
  "events": [...]
}
```

### ESP Clients (`client-boards/`)

All clients share the same lifecycle:
1. Register with server at boot via POST `/register`
2. Send heartbeat every 15s to POST `/heartbeat`
3. Expose `/actuator` endpoint to receive control commands
4. (Sensors only) POST data to `/post-TyH`

`cliente-base/cliente-base.ino` is the template — copy it when creating a new client type. The `cod-fdp/` directory contains prototype/exploratory code, not production firmware.

### Frontend (`server/static/`, `server/templates/`)

- `index.html` / `script.js` — Dashboard: lists all devices, shows live sensor data
- `device.html` / `details.js` — Per-device detail: event management, historical charts
- Device selection between pages uses `sessionStorage` (`selectedDeviceID` key)
- Real-time updates handled entirely via Socket.IO (no polling)

## Key API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/register` | ESP device registration |
| POST | `/heartbeat` | ESP keep-alive |
| POST | `/post-TyH` | Sensor data ingestion |
| POST | `/update_button` | Control an actuator |
| POST | `/schedule-event` | Create a scheduled event |
| POST | `/delete_event` | Remove a scheduled event |
| GET  | `/api/esp/list` | List all devices (JSON) |
| GET  | `/checkESP` | Manual connectivity check |

## Language Notes

The codebase uses Spanish for domain language: device status values (`"Online"`, `"Offline"`, `"Verificando"`), action names (`"activar"`, `"desactivar"`), event types (`"horario"`, `"fecha"`, `"intervalo"`), and UI text.
