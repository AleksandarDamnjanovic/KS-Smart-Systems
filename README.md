![](logo.png)

# KS Smart System

## Intro
KS Smart System is built with idea for more abstract approach to building of smart home and other smart systems. When building smart home, engineer usually have to worry about both electric, electronics and computer elements of the system. With this solution, after system is set up from hardware perspective, everithing else is going to be dealt with from KST script. You can consider KST script as programming language for your smart home for the purpose that you will not have to worry any more about voltage and pins, but about switches, transmitters and sensors, meaning script primitives which define your system.

What all of this means? Means that once you finish with setting up of your nodes, you can do all sorts of tweeks and changes without having to handle soldering iron or multimeter, or having to reprogram your microcontrollers.

## What this solution contains
Inside of this solution, you are going to find two projects. 

- First is **AAU**, written in python. This is interpreter for kst script and the core part of the solution. AAU delegates instructions to nodes, according to the script; receives responses from nodes and applies 
received values. AAU has access to all mqtt topics(communication channels). In addition AAU has access to admin topic that can be used to send direct commands in real time to AAU and change working script without restarting of entire system. This last functionality can be use for further developlent of API.

- Second is **KS_NODE**. This is application for esp32 and eps8266 microcontrollers written with arduino framework in Visual Studio Code and Platform IO. Before uploading this code to your devices, make sure that you set all proper values in the node.hpp file.

## How it works
Mosquitto MQTT server is used for entire communication exchange. Every node has access only to its own topic named after name of the node itself. Every node has to have its unique index that is used as identificator in the script and in instructions. AAU has access to all topics + admin topic and it processes both incoming and outgoing messages according to rules set in kst script.

Entire comminication is encrypted. By default, self-signed certificate is used.

There are multiple types of nodes, although at the moment only one type is implemented (MASTER is implemented).

- **MASTER**; this type of node, has direct access to its own topic and its messages are processed directly by AAU.

- **SHUNT**; same as master type, but with additional functionality. In case when smart system has some remote group of nodes shunt serves as communication node towards remote group from the server side. All of messages for the shunt, bridge and other slave nodes in the remote group are grouped in single message on the AAU and sent to the shunt. Shunt removes from this message only those instructions with its own index and all the rest are sent to the bridge.

- **BRIDGE**; is same as shunt just on the side of remote group. It receives message from the shunt, splits all of instructions by the index and reform messages for slaves connected to it. While shunt acts as a master, bridge acts as a slave. Responses from those slaves are again grouped together and as a single message sent back to the shunt that passes that message from entire remote group to the AAU.
- **SLAVE**; slave is just an node in the remote group that has no direct access to the AAU but comunicates with it through BRIDGE and SHUNT channel.

## How to install it
For everything to work, first you will need private key and certificate. By default, self-signed certificate is used.

After you properly install Mosquitto server, make sure that you have all of settings in AAU/support.py set correctly. Place script.kst in directory with path that you defined in AAU/support.py and run the app with python3 ./base.py. For any serious usage, consider turning this app into a service; with systemd on linux or service on windows.

On the side of nodes, make sure that all of data into node.hpp is set properly and upload the code to your microcontroller.

If you are using mqtt explorer, ideally you should be able to se communication between the node and AAU right away.