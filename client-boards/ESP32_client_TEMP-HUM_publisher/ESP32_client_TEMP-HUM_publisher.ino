#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"

const char* ssid = "raspi";
const char* password = "raspiraspi";
const char* serverName = "http://192.168.1.116:5000";  // Dirección IP del servidor

String device_id = "ESP32_003";  // Identificador único para cada ESP32
//int actuatorPin = 2;  // Pin al que está conectado el actuador (por ejemplo, un LED)

#define DHTPIN 15     // Digital pin connected to the DHT sensor
#define DHTTYPE DHT22   // DHT 22  (AM2302)

DHT sensor_DHT(DHTPIN, DHTTYPE);

void setup() {
    Serial.begin(115200);
    
    sensor_DHT.begin();
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

        String postData = "{\"device_id\":\"" + device_id + "\", \"MAC\":\"" + String(WiFi.macAddress()) + "\"}";
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
    postTempHum();
    delay(5000);  // Espera antes de verificar nuevamente
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
        String postData = "{\"temperatura\":\""+ String(t) +"\",\"humedad\": "+ String(h) +"}";

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
