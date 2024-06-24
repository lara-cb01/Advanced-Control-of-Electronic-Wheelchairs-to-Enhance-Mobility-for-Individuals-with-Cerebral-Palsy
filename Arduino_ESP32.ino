#include <Arduino.h>
#define ESP32
    #include <WiFi.h>
#include "fauxmoESP.h"
#define SERIAL_BAUDRATE 115200
// WiFi credentials
#define WIFI_SSID "<Wifi_name>"
#define WIFI_PASS "<Wifi_password>"

fauxmoESP fauxmo;
int arduinoPin = 2;

void wifiSetup(){
    WiFi.mode(WIFI_STA);
//    Serial.printf("[WIFI] Connecting t o %s" , WIFI_SSID);
    WiFi.begin(WIFI_SSID, WIFI_PASS);

    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
//        Serial.println("Connecting to WiFi...");
    }
    // Serial.printf("[WIFI] STATION Mode, SSID: %s, IP address: %s\n", 
    //                WiFi.SSID().c_str(), WiFi.localIP().toString().c_str());
}

void setup() {
    Serial.begin(SERIAL_BAUDRATE); // Initialize serial communication for debugging
    wifiSetup();

    fauxmo.createServer(true);
    fauxmo.setPort(80);
    fauxmo.enable(true);

    fauxmo.addDevice("Adelante");
    fauxmo.addDevice("Atras");
    fauxmo.addDevice("Izquierda");
    fauxmo.addDevice("Derecha");
    fauxmo.addDevice("Para");



    fauxmo.onSetState([](unsigned char device_id, const char * device_name, bool state, unsigned char value) {
        // Serial.print("Device ");
        // Serial.print(device_name);
        // Serial.print(" state: ");
        // Serial.println(state);

            // Send specific characters to Arduino
        if (strcmp(device_name, "Adelante") == 0) {
            if (state) {
                Serial.write('a'); // Send 'a' to Arduino to indicate Adelante is on
            } else {
                Serial.write('p'); // Send 'A' to Arduino to indicate Adelante is off
            }
        } else if (strcmp(device_name, "Atras") == 0) {
            if (state) {
                Serial.write('f'); // Send 'f' to Arduino to indicate Atras is on
            } else {
                Serial.write('p'); // Send 'F' to Arduino to indicate Atras is off
            }
        } else if (strcmp(device_name, "Izquierda") == 0) {
            if (state) {
                Serial.write('l'); // Send 'l' to Arduino to indicate Izquierda is on
            } else {
                Serial.write('p'); // Send 'L' to Arduino to indicate Izquierda is off
            }
        } else if (strcmp(device_name, "Derecha") == 0) {
            if (state) {
                Serial.write('r'); // Send 'r' to Arduino to indicate Derecha is on
            } else {
                Serial.write('p'); // Send 'R' to Arduino to indicate Derecha is off
            }
        } else if (strcmp(device_name, "Para") == 0) {
            if (state) {
                Serial.write('q'); // Send 'r' to Arduino to indicate Derecha is on
            } else {
                Serial.write('p'); // Send 'R' to Arduino to indicate Derecha is off
            }

        }
    });


}

void loop() {
    fauxmo.handle();
    static unsigned long last = millis();
    if (millis() - last > 5000) {
        last = millis();
//        Serial.printf("[MAIN] Free heap: %d bytes\n", ESP.getFreeHeap());
    }
}
