/*
*************** Name: KS Node
*************** Part of: KS Smart Systems
*************** Author: Aleksandar Damnjanovic AKA Kind Spirit
*************** YouTube channel: Kind Spirit Technology
*************** Date: 26.11.2024.
*************** Location: Kragujevac, Serbia
*/

#ifndef NODE_H
#define NODE_H

#include <Arduino.h>

#define NODE_NO_SLAVE   -1
#define NODE_MASTER      0
#define NODE_SLAVE       1
#define NODE_SHUNT       2
#define NODE_BRIDGE      3

#define NODE_FINGERPRINT         "73 8A DF 2F 95 12 3C 8F 1D 88 D8 71 DD DC C5 8D DA 6C 4F 49"
#define NODE_WLAN_SSID           "I'm_Iron_Man"
#define NODE_WLAN_PASSWORD       "svarun444svarun"

#define NODE_SERVER_ADDRESS      "192.168.0.24"
#define NODE_SERVER_PORT         8883

#define NODE_MQTT_USERNAME       "1f"
#define NODE_MQTT_PASSWORD       "00004444"

class NODE{
    public:
        NODE(int type, 
            int slaveTo, 
            int *switches,
            int nodeIndex, 
            boolean *switchStates, 
            String *transmitters, 
            float *sensors,
            int numOfSwitches,
            int numOfSensors,
            int numOfTransmitters);

        int getSwitchByIndex(int index);
        boolean getSwitchStateByIndex(int index);
        String getTransmitterByIndex(int index);
        float getSensorByIndex(int index);
        String compileMessage();
        int getNodeIndex();
        int getType();
        int getSlaveTo();

        String getResponse();
        boolean validate();
        boolean processSensors();
        boolean processSwitches(int index, char* value);
        boolean processTransmitters(int index, char* value);
        boolean processInstruction(char* instruction);
        void processMessage(String message);
        void setSwitchState(int index, int value);
        void setTransmitterValue(int index, String value);
        void sensorRead(int index);

    private:
        int numOfSwitches;
        int numOfSensors;
        int numOfTransmitters;
        boolean *switchStates;
        int *switches;
        String *transmitters;
        float *sensors;
        int type;
        int slaveTo;
        int nodeIndex;
};

#endif
