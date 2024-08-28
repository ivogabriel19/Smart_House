# Smart Home Control System

Este proyecto consiste en un sistema de control para una casa inteligente utilizando una Raspberry Pi 4 como servidor central y múltiples ESP32 como clientes. 
Todos los dispositivos deben encontrarse en la misma red local, la Raspberry (o donde se hostee el servidor) debe tener un IP fija configurada, los ESP32 conociendo dicha IP se conectan y se registran en el servidor, a partir de ahi se comunican mutuamente por peticiones HTTP y actúan en consecuencia, por ejemplo, controlando actuadores como luces del hogar, el servidor a su vez provee de una interfaz web para su control y visualizacion de informacion y estadisticas.

## Características

- **Servidor central en Raspberry Pi 4**: Implementado en Python usando Flask, que se comunica tanto con los ESP como con el front.
- **ESP32 como clientes**: Se conectan al servidor Flask para recibir instrucciones y controlar actuadores.
- **Comunicación HTTP**: Los ESP32 intercambian peticiones HTTP con el servidor.
- **Frontend simple**: La interfaz web está construida con HTML, CSS y JavaScript puro, sin frameworks adicionales.
- **Sistema para Red de area local**: La Raspberry Pi está configurada para tener una IP dentro de la subred 192.168.1.x la cual buscaran los ESP32 para iniciar la comunicacion.

## Funcionalidades
#### Front-end

- Visualizacion de clientes ESP32 registrados y sus datos ✔
- Logueo de usuario ⏳
- Visualizacion de datos por ambiente ⏳
- Visualizacion de datos del control de acceso ⏳
- Visualizacion de datos de consumo de dispositivos ⏳
- Control para iluminacion del hogar ⏳
- Control para controlar luces RGB ⏳
- Control para controlar LEDs Neopixel ⏳
- Visualizacion de datos de plantas ⏳
- Control para dispositivos IR ⏳

#### Back-end
- Recepcion de registro de ESPs ✔
- Usuarios ⏳
- Persistencia de informacion ⏳
- Respuesta a las solicitudes del Front ✔
- Back para monitoreo de ambiente ⏳
- Back para control de acceso ⏳
- Back para monitoreo de consumo de dispositivos ⏳
- Back para controlar iluminacion del hogar ⏳
- Back para controlar luces RGB ⏳
- Back para controlar LEDs Neopixel ⏳
- Back para monitorear plantas ⏳
- Back para controlar dispositivos IR ⏳

#### ESP
- Registro en servidor central ✔
- Recibir datos desde el servidor ⏳
- Codigo para monitoreo de ambiente (Luz, movimiento, temperatura, humedad, aire) ⏳
- Codigo para control de acceso ⏳
- Codigo para monitoreo de consumo de dispositivos ⏳
- Codigo para controlar iluminacion del hogar ⏳
- Codigo para controlar luces RGB ⏳
- Codigo para controlar LEDs Neopixel ⏳
- Codigo para monitorear plantas (humedad, sol) ⏳
- Codigo para controlar dispositivos IR ⏳

## Estructura del Repositorio

```plaintext
├── server/
│   ├── app.py             # Código principal del servidor Flask
│   ├── requirements.txt   # Dependencias del proyecto
│   ├── static/            # Archivos estáticos (CSS, JS, imagenes)
│   └── templates/         # Páginas del frontend
│
├── esp32_clients/         # Código para los distintos ESP32
│
└── README.md              # Documentación del proyecto
