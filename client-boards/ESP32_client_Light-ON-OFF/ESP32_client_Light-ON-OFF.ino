#include <WiFi.h>
#include <WiFiClient.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>

const char* ssid = "Dejen dormir";
const char* password = "0descensos";
const char* serverName = "http://192.168.0.19:5000";  // Dirección IP del servidor

String device_id = "ESP32_002";  // Identificador único para cada ESP32
String esp_type = "Actuador";  // Identificador del tipo de tarea del ESP32
int actuatorPin = 2;  // Pin al que está conectado el actuador (por ejemplo, un LED)

WebServer server(80);

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
        // Activar el actuador
        digitalWrite(actuatorPin, HIGH); // Suponiendo que el actuador está conectado al pin 5
        } else if (strcmp(state, "OFF") == 0) {
        // Desactivar el actuador
        digitalWrite(actuatorPin, LOW);
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
    Serial.println("Conectado a la red WiFi");

    // Registro en el servidor
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(String(serverName) + "/register");
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

    server.on("/actuator", HTTP_POST, handleActuator);
    server.begin();
}

void loop() {
    server.handleClient();
}
