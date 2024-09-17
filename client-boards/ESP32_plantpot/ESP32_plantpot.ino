#include <WiFi.h>
#include <HTTPClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <DHT.h>

#define HEARTBEAT_FRECUENCY 15000 // 15000ms = 3min - 120.000ms = 2min
#define PUBLISH_FRECUENCY 30000

const char *ssid = "raspi";
const char *password = "raspiraspi";
const char *serverName = "http://192.168.1.138:5000"; // Dirección IP del servidor

String device_id = "ESP32_003"; // Identificador único para cada ESP32
String esp_type = "Sensor";     // Identificador del tipo de tarea del ESP32

// Pines de los sensores
#define DHTTYPE DHT22        // DHT 22  (AM2302)
#define DHTPIN 15            // DHT22 conectado al pin 5
#define ONE_WIRE_BUS 4       // DS18B20 conectado al pin 4
#define SOIL_MOISTURE_PIN 34 // HL-69 conectado al pin A2
#define LDR_PIN 35           // LDR conectado al pin A3
#define RAIN_PIN 32          // MH-DR conectado al pin A4

// Definiciones para los sensores
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature soilTempSensor(&oneWire);
DHT sensor_DHT(DHTPIN, DHTTYPE);

void setup()
{
    Serial.begin(115200);

    soilTempSensor.begin();
    sensor_DHT.begin();
    // pinMode(actuatorPin, OUTPUT);

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(1000);
        Serial.println("Conectando a WiFi...");
    }
    Serial.println("Conectado a la red WiFi");

    register_in_server();
    send_heartbeat();
}

void loop()
{
    static unsigned long lastHeartBeat = 0;
    static unsigned long lastTyH = 0;

    if (millis() - lastHeartBeat > HEARTBEAT_FRECUENCY)
    {
        lastHeartBeat = millis();
        send_heartbeat();
    }

    if (millis() - lastTyH > PUBLISH_FRECUENCY)
    {
        lastTyH = millis();
        postData();
    }
}

void register_in_server()
{
    // Registro en el servidor
    if (WiFi.status() == WL_CONNECTED)
    {
        HTTPClient http;
        http.begin(String(serverName) + "/register");
        http.addHeader("Content-Type", "application/json");

        String postData = "{\"device_id\":\"" + device_id + "\", \"MAC\":\"" + String(WiFi.macAddress()) + "\", \"type\":\"" + esp_type + "\"}";
        int httpResponseCode = http.POST(postData);

        if (httpResponseCode > 0)
        {
            String response = http.getString();
            Serial.println(httpResponseCode);
            Serial.println(response);
        }
        else
        {
            Serial.print("Error en la conexión: ");
            Serial.println(httpResponseCode);
        }
        http.end();
    }
}

// Función para postear los datos de los sensores
void postData()
{
    if (WiFi.status() == WL_CONNECTED)
    {
        // Leer temperatura del suelo (DS18B20)
        soilTempSensor.requestTemperatures();
        float soilTemp = soilTempSensor.getTempCByIndex(0);

        // Leer humedad y temperatura del aire (DHT22)
        float airTemp = sensor_DHT.readTemperature();
        float airHumidity = sensor_DHT.readHumidity();

        // Check if any reads failed and exit early (to try again).
        if (isnan(airTemp) || isnan(airHumidity))
        {
            Serial.println(F("Failed to read from DHT sensor!"));
            return;
        }

        // Leer humedad del suelo (HL-69)
        int soilMoistureValue = analogRead(SOIL_MOISTURE_PIN);
        float soilMoisturePercent = map(soilMoistureValue, 4095, 0, 0, 100); // Conversión a porcentaje

        // Leer luz solar (LDR)
        int ldrValue = analogRead(LDR_PIN);
        float lightIntensity = map(ldrValue, 0, 4095, 0, 100); // Conversión a porcentaje

        // Leer sensor de lluvia (MH-DR)
        int rainValue = digitalRead(RAIN_PIN); // Retorna 0 si está lloviendo, 1 si no

        // Crear JSON con los datos
        String postData = "{\"id\":\""+device_id+"\",\"data\":{";
        postData += "\"temperatura_suelo\":\"" + String(soilTemp) + "\",";
        postData += "\"humedad_suelo\":\"" + String(soilMoisturePercent) + "\",";
        postData += "\"temperatura_aire\":\"" + String(airTemp) + "\",";
        postData += "\"humedad_aire\":\"" + String(airHumidity) + "\",";
        postData += "\"intensidad_luz\":\"" + String(lightIntensity) + "\",";
        postData += "\"lluvia\":\"" + String(rainValue == 0 ? "true" : "false") + "\"";
        postData += "}}";

        HTTPClient http;
        http.begin(serverName + "/post_plantpot");
        http.addHeader("Content-Type", "application/json");

        int httpResponseCode = http.POST(postData);

        if (httpResponseCode == 200)
        {
            Serial.println("Datos enviados con éxito");
        }
        else
        {
            Serial.println("Error enviando datos: " + String(httpResponseCode));
        }

        http.end();
    }
}

void send_heartbeat()
{
    if (WiFi.status() == WL_CONNECTED)
    {
        HTTPClient http;
        http.begin(String(serverName) + "/heartbeat");
        http.addHeader("Content-Type", "application/json");

        String postData = "{\"id\":\"" + device_id + "\"}"; // Envía el ID del ESP32

        int httpResponseCode = http.POST(postData);

        if (httpResponseCode > 0)
        {
            String response = http.getString();
            Serial.println(httpResponseCode);
            Serial.println(response);
        }
        else
        {
            Serial.print("Error on sending POST: ");
            Serial.println(httpResponseCode);
        }

        http.end();
    }
}