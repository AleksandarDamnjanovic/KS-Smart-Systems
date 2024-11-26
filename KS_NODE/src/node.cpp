/*
*************** Name: KS Node
*************** Part of: KS Smart Systems
*************** Author: Aleksandar Damnjanovic AKA Kind Spirit
*************** YouTube channel: Kind Spirit Technology
*************** Date: 26.11.2024.
*************** Location: Kragujevac, Serbia
*/

#include "node.hpp"
#include <Arduino.h>
#include <string.h>

NODE::NODE(int type, 
            int slaveTo, 
            int *switches,
            int nodeIndex, 
            boolean *switchStates, 
            String *transmitters, 
            float *sensors,
            int numOfSwitches,
            int numOfSensors,
            int numOfTransmitters){
    NODE::type = type;
    NODE::slaveTo = slaveTo;
    NODE::switches = switches;
    NODE::switchStates = switchStates;
    NODE::transmitters = transmitters;
    NODE::sensors = sensors;
    NODE::nodeIndex = nodeIndex;
    NODE::numOfSwitches = numOfSwitches;
    NODE::numOfSensors = numOfSensors;
    NODE::numOfTransmitters = numOfTransmitters;
}

String NODE::getResponse(){
    String response = "";
    for(int i = 0; i < NODE::numOfSwitches; i++){
        char part[20];
        memset(part, '\0', 20);
        sprintf(part, "Cr_%d_C_%d_%d ", getNodeIndex(), i, NODE::switchStates[i]?1:0);
        response = response + String(part);
    }
    for(int i = 0; i < NODE::numOfSensors; i++){
        char part[20];
        memset(part, '\0', 20);
        sprintf(part, "Cr_%d_R_%d_%0.1f ", getNodeIndex(), i, NODE::sensors[i]);
        response = response + String(part);
    }
    return response;
}

boolean NODE::validate(){
    for(int i = 0; i < NODE::numOfSwitches; i++)
        digitalWrite(NODE::switches[i], NODE::switchStates[i]?HIGH:LOW);

    //all that is necessary to process transmitters should be done in here

    return true;
}

boolean NODE::processSensors(){
    // all that is necessary to read sensors should be done in here
    return true;
}

boolean NODE::processSwitches(int index, char* value){
    int val = atoi(value);
    bool v = val==1?true:false;
    for(int i=0; i < NODE::numOfSwitches; i++)
        if(i==index)
            if(NODE::switchStates[i]!=v)
                NODE::switchStates[i] = v;
    return true;
}

boolean NODE::processTransmitters(int index, char* value){
    for(int i = 0; i < NODE::numOfTransmitters; i++)
        if(i == index)
            NODE::transmitters[i] = String(value);
    return true;
}

boolean NODE::processInstruction(char* instruction){
    char inst[2] = {'\0', '\0'};
    char ind[4] = {'\0', '\0', '\0', '\0'};
    int index;
    char type[2] = {'\0', '\0'};
    char elementIndex[4]= {'\0', '\0', '\0', '\0'};
    int element;
    char value[20];
    memset(value, '\0', 20);

    char *token = strtok(instruction, "_");
    strcpy(inst, token);
    token = strtok(NULL, "_");
    strcpy(ind, token);
    index = atoi(ind);

    if(index != getNodeIndex())
        return false; 

    token = strtok(NULL, "_");

    strcpy(type, token);   

    token = strtok(NULL, "_");
    strcpy(elementIndex, token);

    element = atoi(elementIndex);

    if(type[0]=='S')
        return true;

    token = strtok(NULL, "_");
    strcpy(value, token);

    if(type[0]=='C')
        processSwitches(element, value);
    else if(type[0]=='T')
        processTransmitters(element, value);

    return true;
}

void NODE::processMessage(String message){
    int len = message.length() + 1;
    char first[len];
    char second[len];
    memset(first, '\0', len);
    memset(second, '\0', len);
    strcpy(first, message.c_str());
    strcpy(second, message.c_str());

    int counter = 0;
    char *token= strtok(first, " ");
    
    while(token!=NULL){
        counter +=1;
        token = strtok(NULL, " ");
    }

    if(counter==0)
        return;

    char instructions[counter][35];
    for(int i = 0; i < counter; i++)
        memset(instructions[i], '\0', 35);

    token= strtok(second, " ");

    int count = 0;
    while(token!=NULL){
        strcpy(instructions[count], token);
        token = strtok(NULL, " ");
        count += 1;
    }

    for(int i = 0; i < counter; i++)
        processInstruction(instructions[i]);

    processSensors();
    validate();
}

int NODE::getType(){
    return NODE::type;
}

int NODE::getSlaveTo(){
    return NODE::slaveTo;
}

int NODE::getNodeIndex(){
    return NODE::nodeIndex;
}