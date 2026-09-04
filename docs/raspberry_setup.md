# Preparación de la Raspberry Pi — Setup único

> Guía de ejecución de la **Etapa 1** de [`revival_plan.md`](revival_plan.md).
>
> **Objetivo:** configurar la Raspberry una sola vez, conectarla al lado del router y no volver a tocarla nunca más.

---

## El modelo de trabajo

Este documento está partido en dos partes deliberadamente distintas:

```text
PARTE A — Vos, con la placa en la mano            ~35 min
├─ Todo lo físico (flashear, enchufar)
├─ Todo lo que necesita un login en el navegador
└─ Todo lo que, mal hecho, te deja sin acceso
                    │
                    ▼
        ✅ La Pi responde SSH desde afuera de tu casa
                    │
                    ▼
PARTE B — El agente, por SSH desde tu PC          ~15 min
├─ Sistema base, Docker, mDNS
├─ Watchdogs, desplegador automático, timers
└─ Todo lo que es reproducible y verificable
```

**El criterio del corte:** la Parte A termina en el momento exacto en que dejás de necesitar la placa físicamente. Todo lo que viene después, si sale mal, se arregla por SSH. Todo lo que viene antes, si sale mal, te obliga a buscar un teclado.

### Reparto de tareas

| # | Tarea | Quién | Por qué |
|---|-------|-------|---------|
| A1 | Generar clave SSH | Vos | Tu clave privada no sale de tu PC |
| A2 | Cuenta de Tailscale | Vos | Login en el navegador |
| A3 | Flashear la SD | Vos | Físico + interfaz gráfica |
| A4 | Primer boot y SSH en la LAN | Vos | Es la puerta de entrada de todo lo demás |
| A5 | Tailscale en la Pi | Vos | Autorización por navegador, y es el paso que puede dejarte afuera |
| A6 | Prueba de acceso desde datos móviles | Vos | Punto de no retorno: se verifica antes de delegar |
| A7 | Reserva DHCP en el router | Vos | Interfaz web de tu router |
| A8 | Bot de Telegram y secretos | Vos | El token no debe pasar por el chat del agente |
| **B** | **Todo el resto** | **Agente** | Comandos de shell, reproducibles y verificables |

---

# PARTE A — Lo que hacés vos

> **Meta de esta parte:** que `ssh usuario@<ip-de-tailscale>` funcione desde tu celular con datos móviles. Nada más. Cuando eso ande, la placa se puede ir al router y el resto lo maneja el agente.

## Qué necesitás

- Raspberry Pi (3B+ o superior; Pi 4 recomendada) con su fuente
- microSD de 16 GB o más — **usá una nueva o de calidad**, es la pieza que más falla
- Cable de red al router *(mejor que WiFi: una placa que hace de servidor no debería depender de la señal inalámbrica)*
- Lector de SD en tu PC

> 💡 **Hacé toda la Parte A con la Pi al lado tuyo**, enchufada al cable de red pero sin monitor ni teclado. Verificás el acceso remoto mientras todavía tenés plan B a mano.

---

## A1 — Clave SSH en tu PC

Si ya tenés una, saltá al A2. Para crear una nueva, en **PowerShell**:

```powershell
ssh-keygen -t ed25519 -C "smarthouse"
```

Aceptá la ruta por defecto y poné una passphrase (opcional pero recomendable). Copiá la clave **pública**, que es la que vas a pegar en el Imager:

```powershell
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub
```

> Tu clave privada nunca sale de tu PC. El agente usa el mismo `ssh` de tu sistema, así que hereda este acceso sin que tengas que darle nada.

---

## A2 — Cuenta de Tailscale

1. Creá una cuenta en [tailscale.com](https://tailscale.com) (podés entrar con Google o GitHub). El plan gratuito cubre hasta 100 dispositivos.
2. Instalá el cliente en tu **notebook** y en tu **celular**.

> Sin al menos un cliente tuyo conectado, la Pi va a estar en la red privada pero no vas a tener desde dónde entrar.

---

## A3 — Flashear la tarjeta SD

Acá se decide si vas a necesitar teclado y monitor. Bien configurado, la placa arranca lista para recibir SSH y **no le conectás nada**.

1. Descargá **Raspberry Pi Imager** de [raspberrypi.com/software](https://www.raspberrypi.com/software/).
2. Elegí:
   - **Dispositivo:** tu modelo de Pi
   - **Sistema operativo:** `Raspberry Pi OS (other)` → **`Raspberry Pi OS Lite (64-bit)`**
   - **Almacenamiento:** tu tarjeta SD

> Elegí **Lite** (sin escritorio) a propósito: menos superficie de ataque, menos consumo de RAM y de SD, y no vas a conectar un monitor nunca más.

3. Antes de escribir, entrá a **⚙️ Editar ajustes**. Esto es lo importante de todo el paso:

| Campo | Valor |
|-------|-------|
| Nombre de host | `smarthouse` |
| Usuario | el que quieras (ej. `ivo`) |
| Contraseña | una robusta, la vas a usar poco |
| Configurar WLAN | solo si vas por WiFi; si usás cable, salteálo |
| País de WLAN | `AR` |
| Zona horaria | `America/Argentina/Buenos_Aires` |
| Distribución de teclado | `es` o `latam` |

4. En la pestaña **Servicios**:
   - ✅ **Activar SSH**
   - Seleccioná **"Permitir autenticación de clave pública"** y pegá la clave pública del A1

> 🔴 **`smarthouse` como hostname no es decorativo.** Es lo que hace que la placa sea alcanzable como `smarthouse.local`, y es el nombre que van a resolver los ESP en la Etapa 4. Si ponés otro, tenés que ser consistente en todo el resto del proyecto.

5. Escribí la imagen y esperá la verificación.

---

## A4 — Primer arranque y primer SSH

1. Poné la SD en la Pi, conectá el cable de red y después la alimentación.
2. Esperá **2 o 3 minutos**: el primer boot expande el sistema de archivos y reinicia solo.
3. Desde PowerShell:

```powershell
ssh ivo@smarthouse.local
```

Aceptá la huella del host cuando pregunte.

**Si no resuelve `smarthouse.local`:** buscá la IP en la lista de clientes DHCP de tu router y entrá por IP (`ssh ivo@192.168.x.x`). El mDNS lo deja firme el agente en la Parte B.

✅ **Punto de control:** estás dentro de la placa sin haberle conectado teclado ni monitor.

---

## A5 — Tailscale (el paso sensible)

Esto es lo que te deja entrar desde afuera de tu casa sin abrir un solo puerto en el router. Lo hacés vos porque necesita autorización por navegador y porque **es el único paso cuyo error te deja sin acceso remoto**.

Dentro de la Pi:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --ssh
```

Te imprime una URL. Abrila, iniciá sesión y autorizá el dispositivo.

```bash
tailscale status
tailscale ip -4     # ⭐ ANOTÁ ESTA IP
```

> Guardá esa IP en algún lado accesible desde el celular. Es tu vía de entrada cuando el mDNS o la LAN no colaboren.

### 🔴 Desactivar la expiración de clave — no te saltees esto

1. Entrá a [login.tailscale.com/admin/machines](https://login.tailscale.com/admin/machines)
2. Buscá `smarthouse`
3. Menú `⋯` → **Disable key expiry**

> **Por qué importa tanto:** por defecto las claves de nodo **expiran a los 180 días**. Si expira, la placa desaparece de tu red privada y perdés el acceso remoto de golpe, teniendo que ir físicamente con un teclado — exactamente lo que todo este documento evita. Son dos clicks y solo se pueden hacer desde la consola web, así que ningún agente puede hacerlo por vos.

---

## A6 — Prueba de no-lockout ⭐

**Este es el punto de no retorno del setup.** No delegues nada hasta que esto funcione.

Desde tu **celular con datos móviles** (WiFi apagado), con Tailscale conectado, entrá por SSH usando la IP de Tailscale del A5.

Si entrás, tenés acceso remoto real y todo lo que venga después es recuperable. Si no entrás, resolvelo ahora que tenés la placa al lado.

---

## A7 — Reserva DHCP (puente temporal)

Los ESP todavía tienen la IP del servidor hardcodeada, y encima inconsistente entre placas (`192.168.1.138` en unas, `192.168.0.222` en otras). Hasta el reflasheo de la Etapa 4, van a seguir buscando esa IP.

Sacá la MAC de la Pi:

```bash
ip link show eth0 | grep ether
```

Entrá a tu router, buscá "Reserva DHCP" o "DHCP estático", y asignale a esa MAC **la IP que ya está hardcodeada** en el firmware que quieras mantener vivo.

> Es una muleta consciente. Se retira en la Etapa 4, cuando los ESP resuelvan `smarthouse.local` por nombre.

---

## A8 — Bot de Telegram y secretos

Podés hacerlo **en paralelo mientras el agente trabaja en la Parte B**. Lo hacés vos por una razón concreta: si le pasás el token al agente, queda en el historial de la conversación.

1. En Telegram, buscá **@BotFather** y mandale `/newbot`
2. Elegí nombre y usuario (el usuario tiene que terminar en `bot`)
3. Guardá el **token**: se ve como `7123456789:AAF-xxxxxxxxxxxxxxxxx`
4. **Mandale un mensaje cualquiera a tu bot** (ej. `hola`) — sin esto no puede escribirte
5. Abrí en el navegador, con tu token:

   ```
   https://api.telegram.org/bot<TU_TOKEN>/getUpdates
   ```

6. Buscá `"chat":{"id":123456789`. Ese número es tu **chat id**

Después, **vos** por SSH escribís el archivo de secretos:

```bash
sudo mkdir -p /etc/smarthouse
sudo nano /etc/smarthouse/deploy.env
```

Con este contenido (pegando tus valores reales):

```bash
TELEGRAM_BOT_TOKEN=tu_token_aca
TELEGRAM_CHAT_ID=tu_chat_id_aca
REPO_DIR=/opt/smarthouse
STATE_FILE=/var/lib/smarthouse/state.json
HEALTH_URL=http://127.0.0.1:5000/health
```

```bash
sudo chmod 600 /etc/smarthouse/deploy.env
```

> Si `getUpdates` devuelve una lista vacía, es porque no le mandaste el mensaje del punto 4.

---

## ✅ Checklist de la Parte A

- [ ] `ssh ivo@smarthouse.local` funciona desde la LAN
- [ ] `ssh ivo@<ip-tailscale>` funciona **desde datos móviles**
- [ ] La expiración de clave está desactivada en la consola de Tailscale
- [ ] Tengo anotada la IP de Tailscale en algún lado accesible desde el celular
- [ ] Hay una reserva DHCP en el router para la MAC de la Pi
- [ ] *(puede quedar para después)* Tengo el token y el chat id del bot

**Con esto tildado, la placa ya se puede ir al lado del router.** Todo lo que sigue se hace en remoto.

---

# PARTE B — Lo que hace el agente

> **Requisito:** la Parte A completa. El agente corre en tu PC y usa el mismo `ssh` de tu sistema, así que hereda tu clave sin que tengas que darle credenciales.

## Qué va a instalar y configurar

| Bloque | Contenido |
|--------|-----------|
| Sistema base | `apt full-upgrade`, `git curl jq`, zona horaria |
| Descubrimiento | `avahi-daemon` → `smarthouse.local` |
| Contenedores | Docker Engine + plugin compose, rotación de logs |
| Protecciones | Watchdog de hardware, `unattended-upgrades`, `log2ram` |
| Repositorio | Clone en `/opt/smarthouse` |
| Notificaciones | `sh-notify` + aviso de boot |
| Despliegue | `sh-deploy` con rollback + timer cada 5 min |
| Auto-recuperación | `sh-watchdog` de contenedores + timer cada minuto |

El detalle exacto de cada script está en el [Apéndice](#apéndice--qué-instala-la-parte-b) al final, para que puedas auditarlo o ejecutarlo a mano si preferís.

## Cómo lanzarlo

Desde Claude Code en tu PC, algo así:

```
Provisioná la Raspberry siguiendo la Parte B de docs/raspberry_setup.md.
Conectate por SSH a ivo@smarthouse.local (o a <ip-tailscale> si el mDNS no responde).
No toques la configuración de Tailscale ni la de SSH.
El archivo /etc/smarthouse/deploy.env ya existe y tiene los secretos: no lo pises.
Al terminar, mostrame el resultado de la verificación de cierre.
```

> 💡 Para evitar que te pregunte permiso en cada comando, podés allowlistear `ssh` con `/permissions`.

### Alternativa: script único

En vez de que el agente ejecute los comandos uno por uno, puede escribir un `deploy/provision.sh` **idempotente** y versionarlo en el repo. Tu intervención se reduce a:

```bash
ssh ivo@smarthouse.local
curl -fsSL https://raw.githubusercontent.com/ivogabriel19/Smart_House/main/deploy/provision.sh | bash
```

Idempotente significa que si se corta a la mitad, lo volvés a correr y sigue donde estaba — que es justo lo que querés cuando estás lidiando con una SD que se corrompió o una conexión que se cayó. **Es la opción recomendada**, porque deja el provisionamiento versionado y repetible en vez de vivir en el historial de un chat.

## 🚫 Lo que el agente no debe tocar

Está anotado acá para que puedas pedírselo explícitamente:

- **Configuración de Tailscale.** Ya funciona y verificaste que funciona. Cualquier cambio arriesga tu única vía de acceso remoto.
- **`sshd_config` y las claves autorizadas.** Endurecer SSH es buena idea, pero hacelo *después* del checklist de cierre, y con una sesión SSH abierta de respaldo mientras probás.
- **`/etc/smarthouse/deploy.env`.** Lo escribiste vos en el A8 y tiene el token.
- **Reglas de firewall.** No hacen falta: no hay puertos abiertos hacia internet.

## ✅ Verificación de cierre — la hacés vos

El agente puede correr todo esto, pero **leé vos el resultado**. Es lo que separa "el script terminó sin error" de "el sistema realmente funciona".

- [ ] `http://smarthouse.local:5000` muestra el dashboard
- [ ] `curl http://localhost:5000/health` devuelve `200`
- [ ] Llegan los mensajes del bot de Telegram
- [ ] `systemctl list-timers | grep smarthouse` muestra los dos timers activos
- [ ] `ls /dev/watchdog` existe
- [ ] **Prueba de reinicio:** `sudo reboot` → a los 3 min todo levantó solo y llegó el aviso de boot
- [ ] **Prueba de despliegue:** pusheás un tag `v0.1.1` y a los 5 min se despliega solo, con aviso
- [ ] **Prueba de rollback:** pusheás un tag roto a propósito y vuelve solo al anterior
- [ ] **Prueba de watchdog:** `docker stop` al contenedor → vuelve solo
- [ ] Seguís entrando por SSH desde datos móviles

> ⚠️ **La prueba de reinicio es la más importante de todas.** Es la única que demuestra que la placa se recupera sola de un corte de luz, que es el escenario real que vas a enfrentar cuando esté atrás del router y vos no estés en casa.

---

# Operación de acá en adelante

Todo por SSH, estés donde estés — vos o el agente.

### Desplegar una versión nueva

```bash
# En tu máquina:
git tag -a v0.2.0 -m "Descripción de los cambios"
git push origin v0.2.0
# Se despliega solo en 5 minutos, o forzalo desde la Pi con: sudo sh-deploy
```

### Comandos frecuentes

| Qué querés | Comando |
|------------|---------|
| Forzar un despliegue ya | `sudo sh-deploy` |
| Redesplegar el mismo tag | `sudo sh-deploy --force` |
| Ver qué versión corre | `cat /var/lib/smarthouse/state.json \| jq` |
| Logs de la aplicación | `docker compose -f /opt/smarthouse/docker-compose.yml logs -f` |
| Logs del desplegador | `journalctl -u smarthouse-deploy -n 50` |
| Reiniciar la app | `docker compose -f /opt/smarthouse/docker-compose.yml restart` |
| Estado de los timers | `systemctl list-timers \| grep smarthouse` |
| Temperatura y disco | `vcgencmd measure_temp && df -h /` |

### Volver a una versión anterior

```bash
cd /opt/smarthouse
git checkout v0.1.0
docker compose up -d --build
```

Ojo: el timer va a volver a subirte al tag más alto en la siguiente corrida. Para quedarte fijo en una versión vieja, parás el timer (`sudo systemctl stop smarthouse-deploy.timer`) o borrás el tag problemático del remoto.

---

# Si algo sale mal

### Escalera de acceso

De menos a más invasivo. Los tres primeros son remotos:

1. **IP de Tailscale** — no depende del mDNS ni de tu LAN. Es la más confiable.
2. `ssh usuario@smarthouse.local` desde la LAN
3. SSH por IP local (la ves en la lista de clientes del router)
4. Monitor y teclado *(rompe la promesa, pero existe)*
5. Sacar la SD, montarla en tu PC y editar los archivos de arranque

> **Prevención:** desactivar la expiración de clave en Tailscale (A5) elimina la causa más común de perder acceso.

### El contenedor no levanta

```bash
docker compose -f /opt/smarthouse/docker-compose.yml logs --tail 100
journalctl -u smarthouse-deploy -n 100
```

Sospechas más probables, en orden:
1. Falta una variable en `/etc/smarthouse/app.env`
2. El `Dockerfile` no compila para arm64
3. El puerto 5000 ya está ocupado
4. Permisos del volumen de `data/`

### Los ESP dejaron de conectarse

Hasta la Etapa 4 buscan una **IP hardcodeada**. Si cambió la de la Pi:

```bash
ip addr show eth0 | grep 'inet '
```

Compará con la IP de los `.ino` y arreglá la reserva DHCP del router. Es exactamente el problema que la Etapa 4 elimina para siempre.

### Se corrompió la SD

Es el fallo más probable a largo plazo y **hoy no hay backups** (planificados para la Etapa 5). Reflasheá desde el A3: el código se recupera entero del repositorio y la Parte B se vuelve a correr sola. Lo único que se pierde es el histórico de sensores.

> Si el histórico te importa, adelantá la sección 5.4 del plan.

---

# Qué queda pendiente

Diferido concientemente a etapas posteriores:

| Pendiente | Etapa | Por qué se difiere |
|-----------|-------|--------------------|
| Backups de los datos | 5.4 | Es trivial cuando exista un único archivo SQLite |
| Los ESP resuelven por nombre | 4.2 | Requiere reflashear, y el protocolo se congela antes |
| Autenticación en el dashboard | 6 | Hoy cualquiera en la LAN controla las luces |
| Página `/estado` | 1.4.3 | Necesita cambios de código, no de infraestructura |
| Alerta de ESP offline | 1.4.2 | Necesita cambios de código, no de infraestructura |
| Endurecer SSH (solo claves) | — | Hacelo después del checklist de cierre, con una sesión de respaldo abierta |

---

---

# Apéndice — Qué instala la Parte B

Referencia completa de lo que ejecuta el agente. Está acá para que puedas auditarlo, ejecutarlo a mano, o usarlo como base del `provision.sh`.

> ⚠️ Los bloques B5 en adelante asumen que el repositorio ya tiene `Dockerfile`, `docker-compose.yml` y un endpoint `/health` — es la sección **1.1** del plan. Sin eso, el desplegador se instala pero no tiene nada que desplegar.

## B1 — Sistema base

```bash
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y git curl ca-certificates jq

timedatectl
sudo timedatectl set-timezone America/Argentina/Buenos_Aires
```

Reiniciar si el upgrade tocó el kernel.

## B2 — mDNS

```bash
sudo apt install -y avahi-daemon
sudo systemctl enable --now avahi-daemon
hostname       # debe imprimir: smarthouse
```

Verificar desde otra máquina: `ping smarthouse.local`

## B3 — Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Requiere reconectar la sesión SSH para que tome el grupo
docker run --rm hello-world
docker compose version
```

Rotación de logs, para que Docker no llene la SD:

```bash
sudo tee /etc/docker/daemon.json > /dev/null <<'EOF'
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" }
}
EOF
sudo systemctl restart docker
```

## B4 — Protecciones del sistema

### Watchdog de hardware

Si el kernel se cuelga entero, reinicia la placa sola. Es la última red antes de la intervención física.

```bash
sudo sed -i 's/^#*RuntimeWatchdogSec=.*/RuntimeWatchdogSec=15/' /etc/systemd/system.conf
sudo sed -i 's/^#*RebootWatchdogSec=.*/RebootWatchdogSec=2min/' /etc/systemd/system.conf
sudo systemctl daemon-reexec
ls -l /dev/watchdog*
```

Si no aparece el dispositivo, agregar `dtparam=watchdog=on` a `/boot/firmware/config.txt` y reiniciar.

### Actualizaciones de seguridad

```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### Desgaste de la SD

```bash
echo "deb [signed-by=/usr/share/keyrings/azlux.gpg] http://packages.azlux.fr/debian/ bookworm main" | sudo tee /etc/apt/sources.list.d/azlux.list
sudo wget -O /usr/share/keyrings/azlux.gpg https://azlux.fr/repo.gpg
sudo apt update && sudo apt install -y log2ram
```

> La SD es la pieza que más falla en una Raspberry, y este código la castiga: cada muestra de sensor reescribe el histórico completo, y cada heartbeat reescribe `devices.json` entero. `log2ram` ayuda al margen; la solución de fondo es la migración a SQLite de la Etapa 5.

## B5 — Repositorio

```bash
sudo mkdir -p /opt/smarthouse
sudo chown $USER:$USER /opt/smarthouse
git clone https://github.com/ivogabriel19/Smart_House.git /opt/smarthouse
git config --global --add safe.directory /opt/smarthouse
```

**Si el repositorio es privado**, generar una clave dedicada y cargarla en GitHub como *Deploy key* de solo lectura:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/deploy_key -N ""
cat ~/.ssh/deploy_key.pub
# GitHub → repo → Settings → Deploy keys → Add deploy key (sin acceso de escritura)
```

> Nunca la clave personal en la Pi. Una deploy key de solo lectura limita el daño si algún día alguien accede a la placa.

## B6 — Configuración de la app

`/etc/smarthouse/deploy.env` ya lo creaste vos en el A8. Falta el de la aplicación:

```bash
sudo tee /etc/smarthouse/app.env > /dev/null <<'EOF'
FLASK_ENV=production
PORT=5000
CHECK_INTERVAL=900
TZ=America/Argentina/Buenos_Aires
EOF

sudo chmod 600 /etc/smarthouse/app.env
sudo mkdir -p /var/lib/smarthouse
```

## B7 — Notificaciones

```bash
sudo tee /usr/local/bin/sh-notify > /dev/null <<'EOF'
#!/usr/bin/env bash
# Envía un mensaje por Telegram. Uso: sh-notify "texto"
set -u
[ -f /etc/smarthouse/deploy.env ] && . /etc/smarthouse/deploy.env
[ -z "${TELEGRAM_BOT_TOKEN:-}" ] && exit 0
curl -sS -m 10 -o /dev/null \
  -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d chat_id="${TELEGRAM_CHAT_ID}" \
  -d parse_mode="HTML" \
  --data-urlencode "text=🏠 <b>$(hostname)</b>
$*" || true
EOF

sudo chmod +x /usr/local/bin/sh-notify
sudo sh-notify "Provisionamiento en curso: las notificaciones funcionan ✅"
```

### Aviso al bootear

Te enterás si hubo un corte de luz aunque no estés en casa.

```bash
sudo tee /etc/systemd/system/smarthouse-boot-notify.service > /dev/null <<'EOF'
[Unit]
Description=Avisar por Telegram que la Pi booteo
After=network-online.target tailscaled.service
Wants=network-online.target

[Service]
Type=oneshot
ExecStartPre=/bin/sleep 20
ExecStart=/usr/local/bin/sh-notify "La Raspberry termino de bootear."

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable smarthouse-boot-notify.service
```

## B8 — Desplegador automático

Sigue el tag de release más alto. Si falla el healthcheck, vuelve solo al anterior.

```bash
sudo tee /usr/local/bin/sh-deploy > /dev/null <<'EOF'
#!/usr/bin/env bash
# Despliega el tag de release mas alto. Rollback automatico si falla el healthcheck.
set -uo pipefail
. /etc/smarthouse/deploy.env

cd "$REPO_DIR" || exit 1
FORCE="${1:-}"

git fetch --tags --prune --prune-tags --quiet origin

TARGET=$(git tag -l 'v*' | sort -V | tail -1)
[ -z "$TARGET" ] && { echo "Sin tags de release."; exit 0; }

CURRENT=""
[ -f "$STATE_FILE" ] && CURRENT=$(jq -r '.deployed // ""' "$STATE_FILE" 2>/dev/null)

if [ "$TARGET" = "$CURRENT" ] && [ "$FORCE" != "--force" ]; then
    echo "Ya desplegado: $TARGET"
    exit 0
fi

echo "Desplegando $TARGET (actual: ${CURRENT:-ninguno})"

deploy_tag() {
    git checkout --quiet --force "$1" || return 1
    docker compose build || return 1
    docker compose up -d --remove-orphans || return 1
    for _ in $(seq 1 30); do
        curl -fsS -m 3 "$HEALTH_URL" > /dev/null 2>&1 && return 0
        sleep 2
    done
    return 1
}

if deploy_tag "$TARGET"; then
    jq -n --arg d "$TARGET" --arg p "$CURRENT" --arg t "$(date -Is)" \
       '{deployed:$d, previous:$p, at:$t, result:"ok"}' > "$STATE_FILE"
    sh-notify "✅ Desplegado <b>$TARGET</b>"
    echo "OK: $TARGET"
else
    echo "FALLO el despliegue de $TARGET"
    if [ -n "$CURRENT" ] && deploy_tag "$CURRENT"; then
        sh-notify "❌ Fallo <b>$TARGET</b> — rollback a <b>$CURRENT</b> exitoso"
    else
        sh-notify "🔥 Fallo <b>$TARGET</b> y el rollback tambien. Requiere intervencion."
    fi
    jq -n --arg d "$CURRENT" --arg f "$TARGET" --arg t "$(date -Is)" \
       '{deployed:$d, failed:$f, at:$t, result:"rollback"}' > "$STATE_FILE"
    exit 1
fi
EOF

sudo chmod +x /usr/local/bin/sh-deploy
```

### Timer

```bash
sudo tee /etc/systemd/system/smarthouse-deploy.service > /dev/null <<'EOF'
[Unit]
Description=Desplegar el ultimo tag de Smart House
After=network-online.target docker.service
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/sh-deploy
EOF

sudo tee /etc/systemd/system/smarthouse-deploy.timer > /dev/null <<'EOF'
[Unit]
Description=Buscar nuevos releases de Smart House cada 5 minutos

[Timer]
OnBootSec=2min
OnUnitActiveSec=5min
Unit=smarthouse-deploy.service

[Install]
WantedBy=timers.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now smarthouse-deploy.timer
```

## B9 — Watchdog de contenedores

Docker marca un contenedor como `unhealthy` pero **no lo reinicia solo** — eso solo pasa en modo Swarm. Sin este watchdog, un proceso vivo pero colgado se queda colgado indefinidamente.

```bash
sudo tee /usr/local/bin/sh-watchdog > /dev/null <<'EOF'
#!/usr/bin/env bash
# Reinicia los contenedores que Docker marca como unhealthy.
set -uo pipefail
for c in $(docker ps -q --filter health=unhealthy); do
    name=$(docker inspect --format '{{.Name}}' "$c" | tr -d '/')
    docker restart "$c" > /dev/null 2>&1 \
      && sh-notify "🔄 Contenedor <b>${name}</b> reiniciado por el watchdog" \
      || sh-notify "🔥 No se pudo reiniciar <b>${name}</b>"
done
EOF

sudo chmod +x /usr/local/bin/sh-watchdog

sudo tee /etc/systemd/system/smarthouse-watchdog.service > /dev/null <<'EOF'
[Unit]
Description=Watchdog de contenedores de Smart House
After=docker.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/sh-watchdog
EOF

sudo tee /etc/systemd/system/smarthouse-watchdog.timer > /dev/null <<'EOF'
[Unit]
Description=Revisar la salud de los contenedores cada minuto

[Timer]
OnBootSec=3min
OnUnitActiveSec=1min
Unit=smarthouse-watchdog.service

[Install]
WantedBy=timers.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now smarthouse-watchdog.timer
```

## B10 — Primer despliegue

Desde tu máquina de desarrollo, con la sección 1.1 del plan completa:

```bash
git tag -a v0.1.0 -m "Primer despliegue containerizado"
git push origin v0.1.0
```

En la Pi, sin esperar los 5 minutos del timer:

```bash
sudo sh-deploy
docker compose -f /opt/smarthouse/docker-compose.yml ps
curl -s http://localhost:5000/health
cat /var/lib/smarthouse/state.json
```

Y desde tu navegador: `http://smarthouse.local:5000`
