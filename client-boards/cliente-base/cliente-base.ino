#include <WiFi.h>
#include <WiFiClient.h>
#include <WebServer.h>
//#include <ArduinoJson.h>
#include <HTTPClient.h>

//#define HEARTBEAT_FRECUENCY 300000 // 300.000ms = 5min
#define HEARTBEAT_FRECUENCY 120000 // 120.000ms = 2min

const char* ssid = "Dejen dormir";
const char* password = "0descensos";
const char* serverName = "http://192.168.0.19:5000";  // Dirección IP del servidor

String device_id = "ESP32_001";  // Identificador único para cada ESP32
String esp_type = "Basico";  // Identificador del tipo de tarea del ESP32

WebServer server(80);

void handleStatus() {
    server.send(200, "text/plain", "ESP32 OK");
}

void setup() {
    Serial.begin(115200);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Conectando a WiFi...");
    }
    Serial.println("Conectado a la red WiFi");

    server.on("/status", handleStatus);
    server.begin();

    register_in_server();
    send_heartbeat();
}

void loop() {

    static unsigned long marca = 0;

    server.handleClient();

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