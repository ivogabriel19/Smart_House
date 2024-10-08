#include <WiFi.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include "DHT.h"

#define HEARTBEAT_FRECUENCY 15000 // 15000ms = 3min - 120.000ms = 2min
#define PUBLISH_FRECUENCY 900000  // 900.000ms = 15min

const char* ssid = "Dejen dormir";
const char* password = "0descensos";
const char* serverName = "http://192.168.0.222:5000";  // Dirección IP del servidor

String device_id = "ESP32_SensorTemp";  // Identificador único para cada ESP32
String esp_type = "Sensor";  // Identificador del tipo de tarea del ESP32

#define DHTPIN 15     // Digital pin connected to the DHT sensor
#define DHTTYPE DHT22   // DHT 22  (AM2302)

DHT sensor_DHT(DHTPIN, DHTTYPE);
WebServer server(80);

void setup() {
    Serial.begin(115200);
    
    sensor_DHT.begin();
    //pinMode(actuatorPin, OUTPUT);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Conectando a WiFi...");
    }
    Serial.print("Conectado a WiFi. Dirección IP: ");
    Serial.println(WiFi.localIP());

    server.on("/status", handleStatus);
    server.begin();

    register_in_server();
    send_heartbeat();
}

void loop() {
    static unsigned long lastHeartBeat = 0;
    static unsigned long lastTyH = 0;

    if (millis() - lastHeartBeat > HEARTBEAT_FRECUENCY){
        lastHeartBeat = millis();
        send_heartbeat();
    }

    if (millis() - lastTyH > PUBLISH_FRECUENCY){
        lastTyH = millis();
        postTempHum();
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

void postTempHum(){ 
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
    float h = sensor_DHT.readHumidity();
  // Read temperature as Celsius (the default)
    float t = sensor_DHT.readTemperature();

    // Check if any reads failed and exit early (to try again).
    if (isnan(h) || isnan(t)) {
        Serial.println(F("Failed to read from DHT sensor!"));
        return;
    }

    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient request;
        request.begin(String(serverName) + "/post-TyH");
        request.addHeader("Content-Type", "application/json"); // Añade el tipo de contenido a la solicitud

        // Datos que quieres enviar (JSON)
        String postData = "{\"id\":\"" + device_id + "\", \"temperatura\":\""+ String(t) +"\",\"humedad\": "+ String(h) +"}";

        int httpCode = request.POST(postData); // Realiza la solicitud POST

        if (httpCode > 0) {
        String payload = request.getString(); // Obtiene el cuerpo de la respuesta
        Serial.println(payload); // Imprime la respuesta en la consola
        } else {
            Serial.println("Error en la solicitud POST");
        }

        request.end(); // Cierra la conexión
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

void handleStatus() {
    server.send(200, "text/plain", "ESP32 OK");
}