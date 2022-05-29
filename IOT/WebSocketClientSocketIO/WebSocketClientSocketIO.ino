/*      
 *    
 *  Created on: 04.09.2022
 *
 */

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ArduinoJson.h>
#include <WebSocketsClient.h>
#include <SocketIOclient.h>
#include <Hash.h>
#include "DHT.h"

ESP8266WiFiMulti WiFiMulti;
SocketIOclient socketIO;
DHT dht(2, DHT11);
 
#define USE_SERIAL Serial

void socketIOEvent(socketIOmessageType_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case sIOtype_DISCONNECT:
            USE_SERIAL.printf("[IOc] Disconnected!\n");
            break;
        case sIOtype_CONNECT:
            USE_SERIAL.printf("[IOc] Connected to url: %s\n", payload);

            // join default namespace (no auto join in Socket.IO V3)
            socketIO.send(sIOtype_CONNECT, "/");
            break;
        case sIOtype_EVENT:
            {
            USE_SERIAL.printf("[IOc] get event: %s\n", payload);
            StaticJsonDocument<128> doc;
            deserializeJson(doc, payload);
            String msg = doc[1];
            USE_SERIAL.print(msg);
            if(msg == "High" && digitalRead(D3) == LOW){
              digitalWrite(D3,HIGH);
              USE_SERIAL.print("D3 is HIGH");
            }else if(msg == "Low" && digitalRead(D3) == HIGH){
              digitalWrite(D3,LOW);
              USE_SERIAL.print("D3 is LOW");
            }
            break;
            }
        case sIOtype_ACK:
            USE_SERIAL.printf("[IOc] get ack: %u\n", length);
            hexdump(payload, length);
            break;
        case sIOtype_ERROR:
            USE_SERIAL.printf("[IOc] get error: %u\n", length);
            hexdump(payload, length);
            break;
        case sIOtype_BINARY_EVENT:
            USE_SERIAL.printf("[IOc] get binary: %u\n", length);
            hexdump(payload, length);
            break;
        case sIOtype_BINARY_ACK:
            USE_SERIAL.printf("[IOc] get binary ack: %u\n", length);
            hexdump(payload, length);
            break;
    }
}

void setup() {
    // USE_SERIAL.begin(921600);
    USE_SERIAL.begin(115200);
    dht.begin();
    pinMode(D3, OUTPUT);
    //Serial.setDebugOutput(true);
    USE_SERIAL.setDebugOutput(true);

    USE_SERIAL.println();
    USE_SERIAL.println();
    USE_SERIAL.println();

      for(uint8_t t = 4; t > 0; t--) {
          USE_SERIAL.printf("[SETUP] BOOT WAIT %d...\n", t);
          USE_SERIAL.flush();
          delay(1000);
      }

    // disable AP
    if(WiFi.getMode() & WIFI_AP) {
        WiFi.softAPdisconnect(true);
    }

    WiFiMulti.addAP("my_ssid", "password");

    //WiFi.disconnect();
    while(WiFiMulti.run() != WL_CONNECTED) {
        delay(100);
    }

    String ip = WiFi.localIP().toString();
    USE_SERIAL.printf("[SETUP] WiFi Connected %s\n", ip.c_str());

    // socketio server address, port and URL
    socketIO.begin("IP_address", 8000, "/socket.io/?EIO=4");

    // event handler
    socketIO.onEvent(socketIOEvent);
}

unsigned long messageTimestamp = 0;
void loop() {
    socketIO.loop();
    
    float h = dht.readHumidity();
    float t = dht.readTemperature();

    // Use this way(if statement)to delay emit message
    uint64_t now = millis();
    if(now - messageTimestamp > 2000) {
        messageTimestamp = now;
       // creat JSON message for Socket.IO (event)
       DynamicJsonDocument doc(1024);
       JsonArray array = doc.to<JsonArray>();
        
       // add evnet name
       // Hint: socket.on('event_name', ....
       array.add("getHT");
      
      // add payload (parameters) for the event
      JsonObject param1 = array.createNestedObject();
      param1["h"] = h;
      param1["t"] = t;

      // JSON to String (serializion)
      String output;
      serializeJson(doc, output);

      // Send event        
      socketIO.sendEVENT(output);
      // Print JSON for debugging
      USE_SERIAL.println(output);
    }
}
