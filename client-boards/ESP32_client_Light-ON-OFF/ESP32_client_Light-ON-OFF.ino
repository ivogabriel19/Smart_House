#include <WiFi.h>
#include <WiFiClient.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>

#define HEARTBEAT_FRECUENCY 15000 // 15000ms = 3min - 120.000ms = 2min
#define BUTTON_PIN 4  // Pin al que está conectado el botón físico
#define DEBOUNCE_DELAY 50 // Retardo de "debounce" en milisegundos

const char* ssid = "raspi";
const char* password = "raspiraspi";
const char* serverName = "http://192.168.1.138:5000";  // Dirección IP del servidor

String device_id = "ESP32_002";  // Identificador único para cada ESP32
String esp_type = "Actuador";  // Identificador del tipo de tarea del ESP32
int actuatorPin = 2;  // Pin al que está conectado el actuador (por ejemplo, un LED)

WebServer server(80);
bool actuatorState = false;  // Estado actual del actuador (LED)
bool lastButtonState = LOW;  // Estado anterior del botón
unsigned long lastDebounceTime = 0;  // Tiempo de último rebote

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
            actuatorState = true;
        } else if (strcmp(state, "OFF") == 0) {
            actuatorState = false;
        }

        digitalWrite(actuatorPin, actuatorState ? HIGH : LOW);
        
        server.send(200, "application/json", "{\"status\":\"success\"}");
    } else {
        server.send(400, "application/json", "{\"status\":\"error\",\"message\":\"Invalid request\"}");
    }
}

// Función para enviar el estado del actuador al servidor
void send_state_to_server() {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(String(serverName) + "/update");
        http.addHeader("Content-Type", "application/json");

        String postData = "{\"device_id\":\"" + device_id + "\", \"state\":\"" + (actuatorState ? "ON" : "OFF") + "\"}";
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


void handleButtonPress() {
    bool reading = digitalRead(BUTTON_PIN);

    if (reading != lastButtonState) {
        lastDebounceTime = millis();
    }

    if ((millis() - lastDebounceTime) > DEBOUNCE_DELAY) {
        if (reading == LOW) {
            actuatorState = !actuatorState;  // Cambiar el estado del actuador
            digitalWrite(actuatorPin, actuatorState ? HIGH : LOW);
            send_state_to_server();  // Enviar el nuevo estado al servidor
        }
    }

    lastButtonState = reading;
}

void setup() {
    Serial.begin(115200);
    pinMode(actuatorPin, OUTPUT);
    pinMode(BUTTON_PIN, INPUT_PULLUP);


    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Conectando a WiFi...");
    }
    Serial.print("Conectado a WiFi. Dirección IP: ");
    Serial.println(WiFi.localIP());

    register_in_server();
    send_heartbeat();

    server.on("/actuator", HTTP_POST, handleActuator);
    server.begin();
}

void loop() {

    static unsigned long marca = 0;

    server.handleClient();
    handleButtonPress();  // Verificar si el botón fue presionado

    if (millis() - marca > HEARTBEAT_FRECUENCY){
        marca = millis();
        send_heartbeat();
    }
}
void register_in_server(){
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
}

void send_heartbeat(){
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(String(serverName) + "/heartbeat");
        http.addHeader("Content-Type", "application/json");
        
        String postData = "{\"id\":\""+device_id+"\"}";  // Envía el ID del ESP32

        int httpResponseCode = http.POST(postData);

        if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.println(httpResponseCode);
        Serial.println(response);
        }
        else {
        Serial.print("Error on sending POST: ");
        Serial.println(httpResponseCode);
        }
        
        http.end();
    }
}