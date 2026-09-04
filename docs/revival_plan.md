# Plan de Revival — Smart House

> Documento vivo. Última actualización: 2026-09-04.
> Punto de partida: repo parado desde el 8 de octubre de 2024.

---

## 0. Contexto y decisiones tomadas

Este plan retoma el proyecto después de ~2 años de inactividad. El análisis previo encontró que la arquitectura es sólida, que hay una refactorización terminada sin mergear en `origin/develop`, y que la mayoría de los problemas son de higiene o bugs de dos líneas — no de diseño.

### Decisiones de arquitectura (cerradas)

| Tema | Decisión | Motivo |
|------|----------|--------|
| Acceso remoto | **Tailscale** (VPN mesh, con Tailscale SSH) | Sin abrir puertos, sin DDNS, funciona detrás de CGNAT |
| Runtime en la Pi | **Docker + docker compose** | Entorno reproducible, base para sumar servicios |
| Despliegue | **Pull periódico de tags de release** | Rollback trivial, la Pi no necesita ser alcanzable desde afuera |
| Rama/versionado | **Tags `vX.Y.Z`** — la Pi nunca sigue una rama | Nada llega a producción sin un tag explícito |
| Descubrimiento del servidor | **mDNS: `smarthouse.local`** | Los ESP nunca más dependen de una IP hardcodeada |
| Observabilidad | **Telegram + página de estado + healthcheck con auto-reinicio** | Enterarse afuera, diagnosticar adentro, recuperarse solo |
| Persistencia | **Volumen Docker ahora**, backups en Etapa 5 | Se resuelve bien cuando exista un único archivo SQLite |
| SO de la Pi | **Reinstalación limpia** (Raspberry Pi OS Lite 64-bit) | Después de 2 años, partir limpio evita arrastrar basura |

### Los dos hitos que definen el plan

- **Fin de Etapa 1 → nunca más tocás la Raspberry.** Se conecta al router y se opera 100 % remoto.
- **Fin de Etapa 4 → nunca más reflasheás un ESP.** Por eso el firmware se toca *después* de congelar el contrato de la API, no antes.

### Mapa de versiones

| Tag | Qué representa |
|-----|----------------|
| `v0.1.0` | Etapa 1 — La app corre en Docker en la Pi, desplegada automáticamente |
| `v0.2.0` | Etapa 2 — Código consolidado, bugs corregidos, `develop` mergeado |
| `v0.3.0` | Etapa 3 — Contrato de API congelado y testeado |
| `v0.4.0` | Etapa 4 — Firmware definitivo desplegado |
| `v0.5.0` | Etapa 5 — SQLite, jobstore persistente, backups |
| `v1.0.0` | Etapa 6 — Autenticación: el sistema puede salir de la LAN |

---

## Índice de etapas

| # | Etapa | Objetivo | Esfuerzo |
|---|-------|----------|----------|
| 1 | [La Pi autónoma](#etapa-1--la-pi-autónoma) | Cero contacto físico con la Raspberry | 1-2 días |
| 2 | [Consolidación del código](#etapa-2--consolidación-del-código) | Mergear `develop`, matar los bugs | 2-3 días |
| 3 | [Contrato de API y tests](#etapa-3--contrato-de-api-y-tests) | Congelar el protocolo antes de reflashear | 3-4 días |
| 4 | [El firmware definitivo](#etapa-4--el-firmware-definitivo) | Cero contacto físico con los ESP | 2-3 días |
| 5 | [Cimientos de datos](#etapa-5--cimientos-de-datos) | SQLite, jobstore persistente, backups | 1 semana |
| 6 | [Seguridad y usuarios](#etapa-6--seguridad-y-usuarios) | Auth: salir de la LAN | 1 semana |
| 7 | [Crecer](#etapa-7--crecer) | Las features pendientes del README | Continuo |

---

# Etapa 1 — La Pi autónoma

> **Objetivo:** conectar la Raspberry al router y no volver a tocarla nunca más. Todo se opera por SSH sobre Tailscale, los cambios se despliegan solos desde tags de release.

**Definición de hecho:** desconectás teclado y monitor, la Pi queda atrás del router, y desde tu notebook en cualquier lugar del mundo podés entrar por SSH, ver el dashboard, desplegar una versión nueva y hacer rollback. Si algo se cae, se reinicia solo y te avisa por Telegram.

**Guía de ejecución paso a paso:** [`raspberry_setup.md`](raspberry_setup.md)

---

## 1.1 — Preparar el repo para ser desplegable

Es el mínimo indispensable para que exista algo que se pueda taggear y correr en un contenedor. **No** incluye el merge de `develop` ni los arreglos de bugs: eso es Etapa 2.

### 1.1.1 Higiene del repositorio *(bloqueante)*

- [ ] Reemplazar el `.gitignore` (hoy es la plantilla de C++ de GitHub) por uno de Python: `__pycache__/`, `*.pyc`, `entornoVirtual/`, `venv/`, `.env`, `data/`, `*.db`
- [ ] Sacar el virtualenv del índice: `git rm -r --cached server/entornoVirtual` → elimina **3318 de los 3370 archivos** versionados (29 MB, 942 `.pyc`)
- [ ] Sacar `server/data/devices.json` del índice (tiene MAC e IP reales de tu casa) y versionar en su lugar un `devices.json.example`
- [ ] Decidir sobre el historial: si el repo es público, `git filter-repo` para purgar el venv y las credenciales del historial. Si no te importa el tamaño, con sacarlo del HEAD alcanza.

### 1.1.2 Congelar las dependencias *(bloqueante)*

- [ ] Reconstruir un venv limpio con Python 3.11+ y versiones que funcionen entre sí
- [ ] `pip freeze > server/requirements.txt` — hoy son 4 líneas **sin una sola versión fijada**, lo que significa que hoy probablemente ni levanta
- [ ] Sumar `gunicorn` y `eventlet` (necesarios para servir Flask-SocketIO en producción)

### 1.1.3 Hacer que la app arranque fuera de `python server.py` *(bloqueante)*

El servidor hoy **solo** puede correr con `python server.py`: la variable `scheduler` se define dentro de `if __name__ == '__main__'` ([`server.py:676`](../server/server.py#L676)) pero la usan funciones a nivel de módulo. Bajo gunicorn eso es un `NameError` en el primer evento.

- [ ] Mover `scheduler = BackgroundScheduler()` a nivel de módulo
- [ ] Encapsular el arranque en una `scheduler_init()` invocable desde el factory *(`origin/develop` ya lo tiene resuelto así — si preferís, adelantá el merge de Etapa 2)*
- [ ] Convertir las rutas relativas (`./data/devices.json`) en rutas absolutas basadas en `__file__`, para que no importe el directorio desde el que se ejecuta

> ⚠️ **Trampa: gunicorn debe correr con un solo worker.**
> `gunicorn -k eventlet -w 1`. Con más de un worker tenés N schedulers en paralelo y **cada evento programado se dispara N veces**, además de N copias del estado en memoria. El `-w 1` no es una optimización: es un requisito de corrección.

### 1.1.4 Endpoint de salud

- [ ] `GET /health` → `200 {"status": "ok", "version": "<tag>", "uptime": <s>}`
- [ ] Sin autenticación, sin tocar disco, respuesta en milisegundos (lo consultan Docker y el watchdog cada 30 s)

### 1.1.5 Dockerizar

- [ ] `server/Dockerfile` — base `python:3.11-slim-bookworm` (arm64), usuario no-root, `CMD ["gunicorn", "-k", "eventlet", "-w", "1", "-b", "0.0.0.0:5000", "server:app"]`
- [ ] `docker-compose.yml` en la raíz con:
  - `network_mode: host` ← **obligatorio, ver abajo**
  - `restart: unless-stopped`
  - `healthcheck` apuntando a `/health`
  - volumen persistente para `server/data`
  - `env_file: /etc/smarthouse/app.env`
- [ ] `.dockerignore` (que no entre el venv, `.git`, ni `cod-fdp/`)

> 🔴 **`network_mode: host` es obligatorio, no una preferencia.**
> El servidor aprende la IP de cada ESP leyendo `request.remote_addr` en `/register` ([`server.py:222`](../server/server.py#L222)) y `/heartbeat`. En modo bridge, `remote_addr` es la gateway de Docker (`172.17.0.1`) para **todos** los dispositivos: cada ESP se registraría con la IP equivocada y el servidor no podría mandarle un solo comando. Host networking también es lo que permite que mDNS y los broadcast de la LAN funcionen.

### 1.1.6 Primer tag

- [ ] `git tag -a v0.1.0 -m "Primer despliegue containerizado"` y push del tag

---

## 1.2 — Provisionar la Raspberry

Ejecución detallada en [`raspberry_setup.md`](raspberry_setup.md). Resumen de lo que se instala:

### 1.2.1 Sistema base
- [ ] Raspberry Pi OS Lite 64-bit, flasheada con el Imager preconfigurando hostname `smarthouse`, usuario, **clave SSH pública** y WiFi
- [ ] Primer boot sin teclado ni monitor: se entra directo por SSH
- [ ] `apt update && full-upgrade`, zona horaria, locale

### 1.2.2 Acceso remoto — Tailscale
- [ ] Instalar Tailscale y `tailscale up --ssh`
- [ ] **Desactivar la expiración de clave del nodo** en la consola de Tailscale

> ⚠️ **Esto es lo que más silenciosamente rompe la promesa de "no tocarla más".**
> Por defecto las claves de nodo expiran a los 180 días. Si expira, perdés el acceso remoto y tenés que ir físicamente hasta la Pi — exactamente lo que este plan busca evitar. Se desactiva con dos clicks y solo se puede hacer desde la consola web.

### 1.2.3 Descubrimiento — mDNS
- [ ] `avahi-daemon` instalado y habilitado, hostname `smarthouse` → resuelve `smarthouse.local`
- [ ] Verificar la resolución desde otra máquina de la LAN

> ⚠️ **Puente temporal hasta la Etapa 4.**
> Los ESP todavía tienen la IP hardcodeada, y encima inconsistente entre placas (`192.168.1.138` en unas, `192.168.0.222` en otras). Hasta completar el reflasheo de la Etapa 4, fijá en el router una reserva DHCP que le dé a la Pi **la IP que ya está hardcodeada en el firmware** que quieras mantener vivo. Es una muleta, y se retira en la Etapa 4.

### 1.2.4 Docker
- [ ] Docker Engine + plugin `compose` desde el repositorio oficial (no el de Debian)
- [ ] Usuario en el grupo `docker`
- [ ] Docker habilitado al boot

### 1.2.5 Secretos en la Pi
- [ ] `/etc/smarthouse/deploy.env` (0600, root) — token del bot de Telegram y chat id
- [ ] `/etc/smarthouse/app.env` (0600) — configuración de la app
- [ ] Ninguno de los dos entra jamás al repositorio

---

## 1.3 — Pipeline de despliegue por tags

### 1.3.1 El script de deploy
- [ ] `deploy/deploy.sh` en el repo, instalado en la Pi. Lógica:
  1. `git fetch --tags --prune --prune-tags`
  2. Resolver el tag `v*` más alto por orden de versión
  3. Si es igual al desplegado (leído del archivo de estado) → salir sin hacer nada
  4. Guardar el tag actual como *previo* (para rollback)
  5. `git checkout <tag>` → `docker compose build` → `docker compose up -d`
  6. Sondear `/health` hasta 60 s
  7. Éxito → escribir estado, notificar por Telegram
  8. Fallo → **rollback automático** al tag previo, notificar el fallo
- [ ] Estado en `/var/lib/smarthouse/state.json`: tag desplegado, tag previo, timestamp, resultado, hash del commit

### 1.3.2 Automatización
- [ ] `smarthouse-deploy.service` (oneshot) + `smarthouse-deploy.timer` cada 5 minutos
- [ ] `smarthouse deploy --now` para forzarlo sin esperar el timer cuando estás iterando
- [ ] `smarthouse rollback` para volver al tag anterior a mano

### 1.3.3 Acceso al repositorio
- [ ] Repo público → clone por HTTPS, sin credenciales
- [ ] Repo privado → **deploy key de solo lectura** (nunca tu clave personal en la Pi)

---

## 1.4 — Observabilidad y auto-recuperación

Las tres capas elegidas, que cubren cosas distintas.

### 1.4.1 Auto-recuperación (que se arregle solo)
- [ ] `restart: unless-stopped` → cubre crashes del proceso y reinicios de la Pi
- [ ] `healthcheck` en compose contra `/health` cada 30 s
- [ ] **Watchdog de contenedor**: timer de systemd que cada minuto revisa el estado de salud con `docker inspect` y reinicia si está `unhealthy`

> ⚠️ Docker marca un contenedor como `unhealthy` pero **no lo reinicia solo** (eso es Swarm). Sin este watchdog, un proceso vivo pero colgado se queda colgado para siempre.

- [ ] **Watchdog de hardware**: habilitar el watchdog del SoC vía `RuntimeWatchdogSec=15` en `/etc/systemd/system.conf` → si el kernel se cuelga entero, la Pi se reinicia sola. Es la última red antes de tener que ir físicamente.

### 1.4.2 Alertas (que te enteres afuera)
- [ ] Bot de Telegram vía BotFather, credenciales en `/etc/smarthouse/deploy.env`
- [ ] `deploy/notify.sh` — wrapper de `curl` a la Bot API
- [ ] Eventos que notifican:
  - despliegue exitoso (tag nuevo)
  - despliegue fallido + rollback ejecutado
  - contenedor reiniciado por el watchdog
  - la Pi terminó de bootear (te avisa si hubo corte de luz)
  - *(desde Etapa 2)* un ESP lleva más de N horas offline

### 1.4.3 Página de estado (que puedas diagnosticar adentro)
- [ ] Vista `/estado` en el dashboard, alimentada por `GET /api/system`
- [ ] Muestra: versión desplegada y hace cuánto, uptime del contenedor y de la Pi, resultado del último deploy, salud de los servicios, tabla de ESPs con `last_seen`, y las últimas líneas del log de deploy
- [ ] Lee `/var/lib/smarthouse/state.json` montado como volumen de solo lectura

### 1.4.4 Salud del sistema
- [ ] `unattended-upgrades` para parches de seguridad automáticos
- [ ] `log2ram` para reducir escrituras a la SD
- [ ] Rotación de logs de Docker (`max-size: 10m`, `max-file: 3`) en `/etc/docker/daemon.json`

> ⚠️ **La SD es la pieza que más falla en una Raspberry, y este código la castiga.**
> `guardar_historico_sensor()` ([`server.py:117`](../server/server.py#L117)) **reescribe el archivo de histórico completo en cada muestra**, y cada heartbeat reescribe `devices.json` entero. Con varios sensores eso es desgaste constante. `log2ram` ayuda al margen; la solución real es la migración a SQLite de la Etapa 5.

---

## 1.5 — Verificación de cierre de etapa

- [ ] Reiniciar la Pi y confirmar que todo levanta solo, sin intervención
- [ ] Pushear un tag `v0.1.1` de prueba y ver que se despliega y te llega el Telegram
- [ ] Forzar un deploy roto a propósito y confirmar que hace rollback solo
- [ ] Matar el contenedor a mano y confirmar que el watchdog lo levanta
- [ ] Entrar por SSH desde afuera de tu red (datos móviles) vía Tailscale
- [ ] **Desconectar teclado y monitor. Fin de la etapa.**

---

# Etapa 2 — Consolidación del código

> **Objetivo:** mergear el trabajo abandonado, matar los bugs conocidos y sacar los secretos del repo.
> **Depende de:** Etapa 1 (necesitás poder desplegar para validar lo que arreglás).

## 2.1 — Mergear `origin/develop` *(bloqueante, primero que todo)*

`origin/develop` está **17 commits adelante** de `main` con una modularización terminada: Blueprints, controllers, services, models, herencia de templates Jinja, y el JS partido en módulos. `main` solo aporta el README y el `CLAUDE.md`, así que el merge es casi trivial.

Cada línea que escribas sobre `main` antes de este merge es trabajo que después hay que portar.

- [ ] Mergear `origin/develop` → `main`, resolviendo el conflicto de README/CLAUDE.md a favor de `main`
- [ ] Limpiar los `.pyc` que `develop` trae versionados (su `.gitignore` ya suma `__pycache__`)
- [ ] Verificar que el server arranca con la estructura nueva y desplegar a la Pi
- [ ] Borrar las ramas remotas ya fusionadas o muertas (`Front`, `ft--sockets`, `ft--heartbeat`, `ft--store-json-to-file`, `ft--schedule-events`, `modularizacion`)
- [ ] **Reescribir `CLAUDE.md`**: hoy documenta el monolito de 689 líneas, o sea, la rama menos avanzada

> ✅ El merge arregla gratis dos bugs: el del scheduler global y el de los intervalos.

## 2.2 — Bugs de comportamiento

Ver el [inventario completo](#apéndice-a--inventario-de-bugs) al final. Por prioridad:

- [ ] **Los eventos hacen lo contrario de lo que pedís.** `event_relay_on` manda `"OFF"` ([`server.py:548`](../server/server.py#L548)) y `event_relay_off` manda `"ON"` ([`server.py:560`](../server/server.py#L560)). Están cruzados. Dos líneas.
- [ ] `/get-TyH` devuelve 500 siempre ([`server.py:400`](../server/server.py#L400)): `global temp`/`global hum` nunca se asignan. Es código muerto → borrarlo junto a `fetchSensorData()` en el front, que ya ni se invoca.
- [ ] `/modificar_item` nunca encuentra nada ([`server.py:183`](../server/server.py#L183)): busca `item.get('device_id')` pero el campo del modelo es `ID`.
- [ ] `if button_state:` no valida nada ([`server.py:364`](../server/server.py#L364)): cualquier string no vacío es truthy, `"OFF"` incluido. La rama de "Invalid state" es inalcanzable.
- [ ] `ESP01` tiene los valores de SSID y password intercambiados entre sí respecto del resto de las placas ([`ESP01...ino:8`](../client-boards/ESP01_client_light_ON-OFF/ESP01_client_light_ON-OFF.ino#L8)). Esa placa nunca se conectó.

## 2.3 — Secretos fuera del repositorio *(bloqueante)*

Hay **credenciales de WiFi reales commiteadas en 5 archivos de firmware**.

- [ ] Extraer a un `secrets.h` ignorado por git, con un `secrets.h.example` versionado
- [ ] Purgarlas del historial si el repo es público
- [ ] **Cambiar la clave del WiFi.** Una vez que estuvo en un repo público, quedó expuesta; sacarla del HEAD no la des-expone.

## 2.4 — Robustez mínima

- [ ] **`threading.Lock` global** alrededor de toda lectura/escritura del JSON. Hoy cada heartbeat reescribe el archivo entero sin lock, con APScheduler y Socket.IO en otros hilos: hay ventana real de corrupción. ~10 líneas que eliminan toda una clase de bugs intermitentes imposibles de reproducir. *(Solución definitiva: Etapa 5.)*
- [ ] Escritura atómica (escribir a `.tmp` + `os.replace`) para que un corte de luz a mitad de un `json.dump` no deje el archivo truncado
- [ ] `data-device-id` en las tarjetas en lugar de IDs HTML duplicados (`#esp-id`, `#sensor-id` y `#esp-id-estado` se repiten por cada tarjeta), y eliminar los hacks tipo `btn.parentElement.textContent.slice(0, -1)` que eso obliga

**Cierre de etapa:** tag `v0.2.0`.

---

# Etapa 3 — Contrato de API y tests

> **Objetivo:** dejar el protocolo servidor↔ESP estable y testeado **antes** de reflashear.
> **Depende de:** Etapa 2.
> **Por qué acá:** en la Etapa 4 vas a flashear las placas por última vez. Todo lo que el firmware necesite del servidor tiene que estar decidido y congelado antes.

## 3.1 — Generalizar la ingesta de sensores

Hoy `/post-TyH` solo entiende temperatura y humedad, y el firmware del plantpot postea a `/post_plantpot`, **un endpoint que no existe** — ese sensor nunca entregó un dato.

- [ ] Reemplazar `/post-TyH` por `/post-data`, que acepte `{"id": ..., "data": {...}}` con un diccionario arbitrario. El modelo del servidor ya guarda `data` como dict libre y el firmware del plantpot ya manda exactamente ese formato.
- [ ] Mantener `/post-TyH` como alias temporal hasta terminar la Etapa 4
- [ ] Que el histórico y los gráficos manejen claves dinámicas en vez de temp/hum fijas

> Son ~20 líneas y desbloquean el plantpot y cualquier sensor futuro sin volver a tocar el servidor. Es el mayor desbloqueo por línea escrita que tiene el proyecto.

## 3.2 — Congelar el contrato

- [ ] Documentar en `docs/api_contract.md` cada endpoint que consume un ESP: `/register`, `/heartbeat`, `/post-data`, `/update_button`, y el `/status` del lado del ESP
- [ ] Validación de entrada en todos ellos (hoy no hay ninguna)
- [ ] Versionar el protocolo: que el ESP mande su `fw_version` al registrarse, para poder diagnosticar sin tener la placa en la mano

## 3.3 — Tests y CI

- [ ] `pytest` sobre `/register`, `/heartbeat`, `/schedule-event`, `/post-data`, `/health`. Ya sabés simular un ESP: los scripts de `aux_code/` son la mitad del trabajo hecho.
- [ ] Test de regresión específico para la inversión ON/OFF del bug 2.2
- [ ] GitHub Actions: lint + tests en cada push
- [ ] Que el CI **impida crear un tag** si los tests fallan — es lo que hace segura la promesa de despliegue automático de la Etapa 1

**Cierre de etapa:** tag `v0.3.0`.

---

# Etapa 4 — El firmware definitivo

> **Objetivo:** la última vez que conectás un ESP por USB.
> **Depende de:** Etapa 3 (protocolo congelado).

## 4.1 — Librería `SmartHouseClient`

Los 5 firmwares repiten el mismo bloque de registro/heartbeat copiado y pegado. Extraerlo hace que sumar un dispositivo sean 20 líneas en vez de 120, y que un bug de protocolo se arregle en un lugar y no en cinco. Es el equivalente en firmware a lo que `develop` ya hizo en el backend.

- [ ] `client-boards/lib/SmartHouseClient/` con `begin()`, `registerDevice()`, `heartbeat()`, `postData()`, `handleActuator()`
- [ ] Compatible con ESP32 y ESP8266 (`#ifdef ESP8266`)
- [ ] Reescribir los 5 clientes sobre la librería
- [ ] Completar `RGB-controll.ino`, que hoy es un archivo vacío

## 4.2 — Descubrimiento por mDNS

- [ ] Resolver `smarthouse.local` al bootear (`ESPmDNS.h` / `ESP8266mDNS.h`, `MDNS.queryHost()`)
- [ ] **Cachear la IP resuelta** en `Preferences` (ESP32) / EEPROM (ESP8266)
- [ ] Usar la IP cacheada si el mDNS falla, y re-resolver después de N fallos HTTP seguidos

> ⚠️ El mDNS en ESP8266 es caprichoso. El caché con re-resolución no es paranoia: es lo que hace que "nunca más reflashear" sea cierto y no una expresión de deseo. Si el mDNS falla sin caché, la placa queda muerta y volvés al destornillador.

## 4.3 — Robustez de campo

- [ ] Reconexión de WiFi con backoff (hoy `while (WiFi.status() != WL_CONNECTED)` en `setup()` bloquea para siempre si el router está apagado al arrancar — típico tras un corte de luz)
- [ ] Watchdog del ESP para reiniciar si el loop se cuelga
- [ ] Reintentos con backoff en los POST

## 4.4 — OTA (opcional pero muy recomendable)

- [ ] `ArduinoOTA` o `ESPhttpUpdate` para actualizar el firmware por WiFi
- [ ] Sin esto, "nunca más reflashear" depende de que nunca encuentres un bug de firmware. Con esto, la promesa es real.

## 4.5 — Cierre

- [ ] Reflashear las 5 placas *(la única intervención física de todo el plan)*
- [ ] **Retirar la muleta**: eliminar la reserva DHCP temporal de la Etapa 1.2.3 y confirmar que todo sigue funcionando por nombre
- [ ] Eliminar el alias `/post-TyH`

**Cierre de etapa:** tag `v0.4.0`.

---

# Etapa 5 — Cimientos de datos

> **Objetivo:** sacar el techo estructural del proyecto.
> **Depende de:** Etapa 3.

## 5.1 — Migrar de JSON a SQLite *(la decisión de fondo del proyecto)*

Los archivos JSON son el límite real de todo lo demás. SQLite en una Raspberry con un puñado de dispositivos es exactamente la herramienta correcta: cero servidor, un solo archivo, transaccional, y resuelve de un saque concurrencia, histórico ilimitado y consultas por rango.

- [ ] Esquema: `devices`, `events`, `readings` (con índice por `device_id, timestamp`)
- [ ] Script de migración que importe los JSON existentes sin perder histórico
- [ ] Reemplazar `file_manager.py` por una capa de repositorio
- [ ] Habilitar modo WAL (mejor concurrencia y menos escrituras a la SD)

Resuelve de una sola vez: las condiciones de carrera de la 2.4, la reescritura O(n) del histórico en cada muestra, el desgaste de la SD, y habilita los gráficos por rango de fechas.

## 5.2 — Jobstore persistente

- [ ] `SQLAlchemyJobStore` en APScheduler — una línea de configuración
- [ ] Los jobs sobreviven al reinicio solos, y `verificar_consistencia_eventos()` pasa a ser una red de seguridad en vez de ser la única red

## 5.3 — Configuración externalizada

- [ ] `.env` para `PORT`, `CHECK_INTERVAL`, `HEARTBEAT_TIMEOUT`, rutas, credenciales
- [ ] Nada de constantes de despliegue hardcodeadas en el código

## 5.4 — Backups *(diferido desde la Etapa 1)*

Ahora que hay un único archivo que respaldar, se vuelve trivial.

- [ ] Job diario: `sqlite3 .backup` → comprimir → subir fuera de la Pi
- [ ] Retención de 30 días, y notificación por Telegram si el backup falla
- [ ] **Probar la restauración una vez.** Un backup no probado no es un backup.

**Cierre de etapa:** tag `v0.5.0`.

---

# Etapa 6 — Seguridad y usuarios

> **Objetivo:** que el sistema pueda existir fuera de la LAN.
> **Depende de:** Etapa 5.

Hoy no hay autenticación, ni CORS, ni `SECRET_KEY`, ni validación, y el servidor escucha en `0.0.0.0`. Cualquiera en tu red prende y apaga tus luces o borra dispositivos. Es aceptable como decisión consciente para una LAN doméstica — el problema es que hoy no es una decisión, simplemente no está. Tu propio README ya marca el login de usuarios como pendiente.

- [ ] `Flask-Login` + hash de contraseñas, y un decorador `@login_required` en todo endpoint de control
- [ ] Distinguir endpoints de dispositivo (los que usan los ESP) de endpoints de usuario, con un token compartido para los primeros
- [ ] `SECRET_KEY` desde el entorno, cookies seguras
- [ ] Rate limiting en login
- [ ] Exposición externa: HTTPS vía Tailscale Serve (certificado automático, sin abrir puertos)
- [ ] Log de auditoría: quién prendió qué y cuándo

**Cierre de etapa:** tag `v1.0.0`.

---

# Etapa 7 — Crecer

Recién acá las features nuevas son incrementos y no apuestas: hay base de datos, tests, autenticación y despliegue automático. Del README, en orden de menor a mayor esfuerzo:

- [ ] Visualización de datos del plantpot (el firmware y la ingesta ya existen desde la Etapa 4)
- [ ] Control de luces RGB y LEDs Neopixel
- [ ] Agrupación de dispositivos por ambiente
- [ ] Control de dispositivos IR
- [ ] Monitoreo de consumo
- [ ] Control de acceso
- [ ] Escenas y automatizaciones condicionales (*si la temperatura baja de X, encender Y*) — la evolución natural del scheduler que ya tenés

---

# Apéndice A — Inventario de bugs

| # | Severidad | Descripción | Ubicación | Etapa |
|---|-----------|-------------|-----------|-------|
| 1 | 🔴 Alta | Eventos invertidos: `relay_on` manda `"OFF"` y `relay_off` manda `"ON"` | [`server.py:548`](../server/server.py#L548), [`:560`](../server/server.py#L560) | 2.2 |
| 2 | 🔴 Alta | Intervalos cambian de unidad al reiniciar: se crean en minutos, se reprograman en segundos | [`server.py:529`](../server/server.py#L529) vs [`:589`](../server/server.py#L589) | 2.1 ✅ |
| 3 | 🔴 Alta | `scheduler` definido dentro de `__main__` → `NameError` bajo gunicorn | [`server.py:676`](../server/server.py#L676) | 1.1.3 / 2.1 ✅ |
| 4 | 🟠 Media | Escrituras concurrentes al JSON sin lock; cada heartbeat reescribe el archivo entero | `leer_items`/`guardar_items` | 2.4 → 5.1 |
| 5 | 🟠 Media | El histórico se reescribe completo en cada muestra: O(n) por escritura, crecimiento ilimitado | [`server.py:117`](../server/server.py#L117) | 5.1 |
| 6 | 🟠 Media | El plantpot postea a `/post_plantpot`, que no existe → nunca entregó un dato | [`ESP32_plantpot.ino`](../client-boards/ESP32_plantpot/ESP32_plantpot.ino) | 3.1 |
| 7 | 🟡 Baja | `/get-TyH` devuelve 500 siempre: `global temp`/`hum` nunca asignados | [`server.py:400`](../server/server.py#L400) | 2.2 |
| 8 | 🟡 Baja | `/modificar_item` busca `device_id` en vez de `ID` → siempre 404 | [`server.py:183`](../server/server.py#L183) | 2.2 |
| 9 | 🟡 Baja | `if button_state:` no valida: `"OFF"` y `"basura"` son truthy | [`server.py:364`](../server/server.py#L364) | 2.2 |
| 10 | 🟡 Baja | ESP01 con SSID y password invertidos → nunca se conectó | [`ESP01...ino:8`](../client-boards/ESP01_client_light_ON-OFF/ESP01_client_light_ON-OFF.ino#L8) | 2.2 |
| 11 | 🟡 Baja | IDs HTML duplicados por tarjeta, con hacks de `.slice(0,-1)` para compensar | `script.js`, `details.js` | 2.4 |
| 12 | 🟡 Baja | El WiFi bloquea para siempre en `setup()` si el router no está al arrancar | todos los `.ino` | 4.3 |

---

# Apéndice B — Deuda de higiene

| Ítem | Detalle | Etapa |
|------|---------|-------|
| Virtualenv versionado | 3318 de 3370 archivos, 29 MB, 942 `.pyc` | 1.1.1 |
| `.gitignore` equivocado | Es la plantilla de C++: ignora `*.o` y `*.dll`, nada de Python | 1.1.1 |
| Credenciales WiFi en el repo | 5 archivos con SSID y password reales | 2.3 |
| `devices.json` versionado | MAC e IP reales de la casa | 1.1.1 |
| Dependencias sin fijar | 4 líneas, cero versiones | 1.1.2 |
| Ramas sin limpiar | 7 remotas, la mayoría muertas desde 2024 | 2.1 |
| `cod-fdp/` sin marcar | Es documentación intencional (código fuera de producción), pero nada en el árbol lo indica: agregar un `README.md` propio y excluirlo del `.dockerignore` y del linter | 2.1 |
| README desactualizado | Describe `server/app.py`, `docs/`, `esp32_clients/` — ninguno existe así | 2.1 |
| `CLAUDE.md` desactualizado | Documenta el monolito, no la estructura de `develop` | 2.1 |
| Duplicación en el front | `add_ESP_card` y `add_sensor_card` copiadas entre archivos | 2.1 ✅ |
| Sin tests, sin CI | — | 3.3 |

*✅ = lo resuelve el merge de `develop`.*
