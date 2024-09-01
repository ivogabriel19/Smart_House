#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "nombre_de_tu_red";
const char* password = "contraseña_de_tu_red";
const char* serverName = "http://192.168.1.100:5000";  // Dirección IP del servidor

String device_id = "ESP32_00x";  // Identificador único para cada ESP32
String esp_type = "Dummy";  // Identificador del tipo de tarea del ESP32
int actuatorPin = 2;  // Pin al que está conectado el actuador (por ejemplo, un LED)

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
        http.begin(serverName + "/register");
        http.addHeader("Content-Type", "application/json");

        String postData = "{\"device_id\":\"" + device_id + "\", 
                            \"MAC\":\"" + String(WiFi.macAddress()) + "\", 
                            \"type\":\"" + esp_type + "\"}";
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

void loop() {
  // Aquí se verifica si hay una nueva petición del servidor
    HTTPClient http;
    http.begin(serverName + "/send_command/" + device_id);
    int httpResponseCode = http.GET();

    if (httpResponseCode > 0) {
        String payload = http.getString();
        Serial.println(payload);

        // Aquí se procesa el valor recibido para el actuador
        int value = payload.toInt();
        digitalWrite(actuatorPin, value);
    } else {
        Serial.print("Error en la conexión: ");
        Serial.println(httpResponseCode);
    }
    
    http.end();

    delay(5000);  // Espera antes de verificar nuevamente
}
