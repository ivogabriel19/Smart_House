#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ArduinoJson.h>
#include <ESP8266HTTPClient.h>

#define HEARTBEAT_FRECUENCY 15000 // 15 segundos

const char* ssid = "raspiraspi";
const char* password = "raspi";
const char* serverName = "http://192.168.1.138:5000";  // Dirección IP del servidor

String device_id = "ESP01";  // Identificador único para el ESP01
String esp_type = "Actuador";  // Tipo de dispositivo (en este caso, actuador)
int actuatorPin = 0;  // Pin al que está conectado el actuador (LED en GPIO2)

ESP8266WebServer server(80);
WiFiClient wifiClient;

// Función para manejar la solicitud POST y controlar el actuador
void handleActuator() {
    if (server.hasArg("plain")) {
        String body = server.arg("plain");
        StaticJsonDocument<200> jsonDoc;
        deserializeJson(jsonDoc, body);

        const char* state = jsonDoc["state"];
        Serial.print("Received state: ");
        Serial.println(state);

        // Control del actuador basado en el estado recibido
        if (strcmp(state, "ON") == 0) {
            // Activar el actuador (LED encendido)
            digitalWrite(actuatorPin, LOW);
        } else if (strcmp(state, "OFF") == 0) {
            // Desactivar el actuador (LED apagado)
            digitalWrite(actuatorPin, HIGH);
        }

        server.send(200, "application/json", "{\"status\":\"success\"}");
    } else {
        server.send(400, "application/json", "{\"status\":\"error\",\"message\":\"Invalid request\"}");
    }
}

void setup() {
    Serial.begin(115200);
    pinMode(actuatorPin, OUTPUT);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Conectando a WiFi...");
    }
    Serial.print("Conectado a WiFi. Dirección IP: ");
    Serial.println(WiFi.localIP());

    register_in_server();  // Registra el dispositivo en el servidor
    send_heartbeat();  // Envía el primer "heartbeat"

    server.on("/actuator", HTTP_POST, handleActuator);  // Ruta para controlar el actuador
    server.begin();  // Iniciar el servidor web
}

void loop() {
    static unsigned long marca = 0;

    server.handleClient();  // Procesar solicitudes del cliente

    if (millis() - marca > HEARTBEAT_FRECUENCY) {
        marca = millis();
        send_heartbeat();  // Enviar "heartbeat" periódico
    }
}

void register_in_server() {
    // Registro en el servidor
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(wifiClient, String(serverName) + "/register");
        http.addHeader("Content-Type", "application/json");

        String postData = "{\"device_id\":\"" + device_id + "\", \"MAC\":\"" + String(WiFi.macAddress()) + "\", \"type\":\"" + esp_type + "\"}";
        int httpResponseCode = http.POST(postData);

        if (httpResponseCode > 0) {
            String response = http.getString();
            Serial.println(httpResponseCode);
            Serial.println(response);
        } else {
            Serial.print("Error en la conexión: ");
            Serial.println(httpResponseCode);
        }
        http.end();
    }
}

void send_heartbeat() {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(wifiClient, String(serverName) + "/heartbeat");
        http.addHeader("Content-Type", "application/json");

        String postData = "{\"id\":\""+device_id+"\"}";  // Envía el ID del ESP01

        int httpResponseCode = http.POST(postData);

        if (httpResponseCode > 0) {
            String response = http.getString();
            Serial.println(httpResponseCode);
            Serial.println(response);
        } else {
            Serial.print("Error on sending POST: ");
            Serial.println(httpResponseCode);
        }

        http.end();
    }
}
