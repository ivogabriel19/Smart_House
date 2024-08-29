#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "raspi";
const char* password = "raspiraspi";
const char* serverName = "http://192.168.1.116:5000";  // Dirección IP del servidor

String device_id = "ESP32_00x";  // Identificador único para cada ESP32
//int actuatorPin = 2;  // Pin al que está conectado el actuador (por ejemplo, un LED)

void setup() {
    Serial.begin(115200);
    //pinMode(actuatorPin, OUTPUT);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Conectando a WiFi...");
    }
    Serial.println("Conectado a la red WiFi");

    // Registro en el servidor
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient request;
        request.begin(String(serverName) + "/register");
        request.addHeader("Content-Type", "application/json");

        String postData = "{\"device_id\":\"" + device_id + "\"}";
        int httpResponseCode = request.POST(postData);

        if (httpResponseCode > 0) {
        String response = request.getString();
        Serial.println(httpResponseCode);
        Serial.println(response);
        } else {
        Serial.print("Error en la conexión: ");
        Serial.println(httpResponseCode);
        }
        request.end();
    }
}

void loop() {
    // getValorESP();
    delay(5000);  // Espera antes de verificar nuevamente
}



void getValorESP(){ //ejemplo de GET Request
  // Aquí se verifica si hay una nueva petición del servidor
    HTTPClient request;
    request.begin(String(serverName) + "/send_command/" + device_id);
    int httpResponseCode = request.GET();

    if (httpResponseCode > 0) {
        String payload = request.getString();
        Serial.println(payload);

        // Aquí se procesa el valor recibido para el actuador
        int value = payload.toInt();
        digitalWrite(actuatorPin, value);
    } else {
        Serial.print("Error en la conexión: ");
        Serial.println(httpResponseCode);
    }
    
    request.end();
}
