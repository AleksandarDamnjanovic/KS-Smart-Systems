/*
*************** Name: KS Node
*************** Part of: KS Smart Systems
*************** Author: Aleksandar Damnjanovic AKA Kind Spirit
*************** YouTube channel: Kind Spirit Technology
*************** Date: 26.11.2024.
*************** Location: Kragujevac, Serbia
*/

#include <Arduino.h>
#include <Adafruit_MQTT.h>
#include <Adafruit_MQTT_Client.h>
#include <ESP8266WiFi.h>
#include <WiFiClientSecure.h>
#include "node.hpp"

WiFiClientSecure cl;
Adafruit_MQTT_Client *mqtt;
Adafruit_MQTT_Publish *publishing;
Adafruit_MQTT_Subscribe *subscribing;

NODE *node;
int switches[2]={D7, D8};
boolean states[2]= {false, false};
String transmitters[2] = {"none", "none"};
float sensors[2]={0.0, 0.0}; 

void MQTT_CONNECT();

void setup() {
    cl.setFingerprint(NODE_FINGERPRINT);
    mqtt = new Adafruit_MQTT_Client(&cl, NODE_SERVER_ADDRESS, NODE_SERVER_PORT, NODE_MQTT_USERNAME, NODE_MQTT_PASSWORD);
    publishing = new Adafruit_MQTT_Publish(mqtt, NODE_MQTT_USERNAME, 1);
    subscribing = new Adafruit_MQTT_Subscribe(mqtt, NODE_MQTT_USERNAME, 1);

    Serial.begin(9600);
    Serial.println();
    Serial.println("Connecting...");

    WiFi.begin(NODE_WLAN_SSID, NODE_WLAN_PASSWORD);
    while(WiFi.status() != WL_CONNECTED){
        delay(500);
        Serial.print("*");
    }
    Serial.println();
    Serial.print("Connected to wifi with address of ");
    Serial.println(WiFi.localIP());

    mqtt->subscribe(subscribing);

    for(int n:switches){
        pinMode(n, OUTPUT);
        digitalWrite(n, LOW);
    }

    node = new NODE(NODE_MASTER, 
                    NODE_NO_SLAVE,
                    switches,
                    11,
                    states,
                    transmitters,
                    sensors,
                    2,
                    2,
                    2);
}

long t = 0;
void loop() {
    
    if(t==0)
        t= millis();

    MQTT_CONNECT();

    Adafruit_MQTT_Subscribe *sub;
    while((sub= mqtt->readSubscription(1000)))
        if(sub==subscribing){
            String message = String((char*)subscribing->lastread);
            if(message.startsWith("Cr"))
                break;
            node->processMessage(message);
            String response = node->getResponse();
            const char* mess = response.c_str();
                if(!publishing->publish(mess)){
                    Serial.println("error posting to mqtt");
                }else{
                    Serial.println("Message sent");
                }
            t= millis();
        }

    if(millis() - t > 10000){
        String response = node->getResponse();
        const char* mess = response.c_str();
        if(!publishing->publish(mess)){
            Serial.println("error posting to mqtt");
        }else{
            Serial.println("Message sent");
        }
        t= millis();
    }

}

void MQTT_CONNECT(){
    int ret;

    if(mqtt->connected())
        return;

    int counter =5;
    while((ret= mqtt->connect())!=0){
        Serial.println(mqtt->connectErrorString(ret));
        Serial.print("Return code: ");
        Serial.println(ret);
        Serial.println(cl.getLastSSLError());
        mqtt->disconnect();
        delay(3000);
        counter--;
        if(counter==0)
            break;
    }

    Serial.println("MQTT connection is established...");
}