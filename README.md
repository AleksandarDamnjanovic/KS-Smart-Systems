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

If you are using mqtt explorer, ideally you should be able to see communication between the node and AAU right away.

## How communication works
On every 10 seconds, by default, node sends its own updated state to the mosqutitto server on topic with the same name as node itself. It sends confirmations for all of its sensors and switches splited by space. Message lookst like: 

- **Cr_11_C_0_1 Cr_11_R_0_27.5 Cr_11_R_1_70**.

What are those? Pieces of data are separated by _. Cr stands for confirmation, number 11 is the index of node itself, C stands for switch and R stands for readings(from the sensor, real or virtual one). Next number is index of element(switch or sensor) and final number is value from that element.

When some action is necessary, AAU sends instruction to all nodes at once. Command can look like:

- **I_11_C_0_0 I_11_S_0 I_11_S_1 I_11_T_0_70**

Once again, what is this? I stands for instruction, 11 is index of node that should accept that instruction, C stands for switch, S for sensor and T for transmitter. Next number represents index of the affected element and the last number is value that should be applied to that element. Of course, you can see that sensors doesn't have value to apply, because sensor is used only for reading.

You can see that there is no confirmation for transmitter's value. That is because, transmitter is used only to send value. If you want to get present value back, you can write the code on microcontroller directly to copy value from the transmitter to virtual or dummy sensor, and therefore, that value will be read on every message exchange.

## KST script
### Header
Script is used to describe nodes and to program their functionality. You can deal with multiple nodes per script. Every node starts with header:

**1("my first node", "myFirstNode", [MASTER] ){**

**}**

1 is index of the node, "my first node" is name of the node in human readable format, and "myFirstNode" is name of the node that will be used for technical part(topic that this node is going to use for message excange will use this name), and finally [MASTER] defines the type of the node. Everything else about this node is going to be writter in between curly brackets.

### Sections
There are four sections that define a node, all of of those are wrapper in XML style.

- **\<variables> \</variables>**
- **\<sensors>\</sensors>**
- **\<elements>\</elements>**
- **\<programs>\</programs>**

### Variables
Variables in .kst can be divided in two main groups; local and global. Local variables are used only inside local node, and global can be seen in the entire script. Every variable name starts with $ sign. If you want to refere to gloabal variable from your script you have to use sign $ then index of the node that variable is from and at the end name of variable itseld. For example $2$c5 is gloabal variable named $c5 from node with index of 5. Global variable is defined with global type.

Variable can be of type, int for integer, float, string where value is wrapped with "" or array. 

Values for array must be in angle brackets, splitted by comma. If value is of string type, must be wrapped with "". Array can also contain range of values like 0-255.

Variable should be defined in single row like:

- **global int $e1 = 10**
- **array $b1 = ["hey", "ho"]**

***Semicolon is necessary at the end of elements, programs and sensors, but not at the end of variable declaration.***

### Sensors
Sensors are defined in the fashion, sensor per line. Function sensor looks like:

- **sensor("red", 0, $e1, $red);**

First argument is name of the sensor in human readable form. Second argument is index of that sensor on microcotroller. Third argument is epoh(reading period). And fourth argument is variable that is going to store read value.

### Elements
There are three types of elements. Lists, triggers and switches.

- **switch("light", 0, $c1, $fc1);** Same as with sensors, first argument of function switch is name of the switch in human readable format. Second argument is index of the switch. Third is variable that holds the state of the switch; 0 for off and 1 for on. Fourth argument is force state and by default this value is 0; Force state overrides third argument with on state. So if third argument says 1 and fourth argument says 0, switch is going to be on. But if third argument says 0 and fourth argument says 1, switch is going to be on. This is useful in cases when you control some switches using programs but from time to time you need to take manual control without rewriting program.

- **trigger("AC switch", 1, $t1, $ft1);** Trigger is very similar to switch with few notable differences. First, arguments of the function trigger are the same as arguments of the function switch. While, function switch deals with switches, function trigger deals with transmitters. Here, transmitted values are also 0 and 1. When value of the trigger is switched it signalize some change. While with switches present state is important, with triggers is not. Triggers are very useful if you want to have some delayed effect. For example, at one moment you want to change some value from a list, but the change could take effect only when triggered with the value change.

- **list("AC modes", 0, $acModes, $acModeNames, $ACselectedMode, $fl1);** For function list, first argument is again name of the list in human readable format. Second argument is index of affected transmitter. Third argument is an array of numeric values(list of indexes per all of selectable options). Forth argument is an array in textual form(all options in textual form). Fift argument is option selected at the moment. And sixt argument is selected option in force mode.

### Programs
Programs are where true power of .kst lies. At the moment, there are three types of programs. valCondition, serial and timeLim. valCondition and serial can be named, while timeLim can't. Type of variable that is used to name a program is fun, and this type can't be global.



#### valCondition(textName, conditions, result);
    $example = valCondition(
        "temp on",
        $res01 < $tempLimDown
        $c1 == 0, 
        $c1 = 1
        $tempState = 1
    );

In this case $example is name of this functions. Type of variable is fun and type of function is valCondition. If you don't need named function, simply don't name it; just write *valCondition(...* without $example = part. 

valCondition function has three arguments, or better to say three groups of arguments. First argument is function name in human readable format. Second argument is one or more conditions separated by new line; all of conditions must be true in order result to be executed. Result can also have one or more statements separated by new line.

#### serial(textName, listOfSwitches, epoh, timeStamp, lastIndex);

Program serial have purpose to turn on one switch from provided list of switches, when time comes. Program starts from switch with index provided in fifth argument, and keeps it on till the epoch provided in third argument in seconds ends. Then timeStamp provided in forth argument changes to current time and the new epoh starts from the beginning turning on next switch from the list... so on till the end of the list. When list ends, it starts from the beginning in the same fashion. Timestamp default value is 0, so always when you define timeStamp variable, you are going to set it with value of 0;

    $fun01= serial("two switches", $listOfSwitches, $switchEp, $sTime, $lastIndex);

Function naming applies here too. Function of type serial is written in a single line with ; at the end.

#### timeLim(function, start, end);

    timeLim($fun01, $start, $end);

With function timeLim, you are able to define execution time of some other function. For example, if you want your serial program or conditional program to be executed only between 12:00 and 14:00, as a first argument to the timeLim function, you are goint to provide function name of the function you want to limit by time, as second argument you are goint to provide string variable that hold value of "12:00" and as third argument, string variable that holds value of "14:00".

Therefore default value of variable of type fun that hold function name of the function you want to limit by time is 1. That means that function is going to be executed by default exept if it is provided to timeLim function. timeLim function keeps value of fun variable to 1 only in selected time; in other case, it keeps it to 0. If value of naming variable is 0 that measn that that function is going to be ignored; if is 1 it is going to be executed.

### Example

    1("North entrance", "northEntrance", [SLAVE, 5])    {
        
        <variables>
            
            global float   $res01 =            0.0
            global float   $res02 =            0.0
            global int     $current =          0
            global int     $mode =             0
            global int     $button =           0
            global array   $acModeNames =       ["OFF", "COOLING", "HEATING"]
            global array   $acModes =          [0,  1, 2]
            global array   $ttest =             [0-152]
            global int     $ACselectedMode =   0
            global string  $t1 =               "0"
            global int     $c1 =               0
            global string  $fl1 =              ""
            global string  $ft1 =              ""
            global int     $fc1 =              0
            global int     $c2 =               0
    
            int     $e1 =               10
            int     $switchEp =         3
            float   $tempLimUp =        24.0
            float   $tempLimDown =      21.0
            int     $tempState =        0
            string  $start =            "20:00"
            string  $end =              "5:00"
            int     $sTime =            0
            string  $start1 =           "5:00"
            string  $end1 =             "4:45"
            int     $sTime1 =           0
            int     $lastIndex =        0
            int     $lastIndex1 =       0
            array   $listOfSwitches =   [$1$c1,     $1$c2]
            fun     $example =          1
            fun     $fun01 =            1
            fun     $fun02 =            1
        </variables>
    
        <sensors>
            sensor("temp", 0, $e1, $res01);
            sensor("moist", 1, NULL, $res02);
            sensor("current", 2, NULL, $current);
            sensor("AC mode", 3, NULL, $mode);
            sensor("AC button", 5, NULL, $button);
        </sensors>
    
        <elements>
            list("AC modes", 0, $acModes,   $acModeNames, $ACselectedMode, $fl1);
            trigger("AC switch", 1, $t1, $ft1);
            switch("light", 0, $c1, $fc1);
        </elements>
    
        <programs>
            $example = valCondition(
                "temp on",
                $res01 < $tempLimDown
                $c1 == 0, 
                $c1 = 1
                $tempState = 1
            );
            valCondition(
                "temp off",
                $res01 > $tempLimUp
                $tempState == 1,
                $c1 = 0
                $tempState = 0
            );
            $fun01= serial("two switches",  $listOfSwitches, $switchEp, $sTime,  $lastIndex);
            $fun02= serial("two switches copy",     $listOfSwitches, $switchEp, $sTime1,    $lastIndex1);
            serial("two switches copy 2",   $listOfSwitches, $switchEp, $sTime1,  $lastIndex1);
            timeLim($fun01, $start, $end);
            timeLim($fun02, $start1, $end1);
        </programs>
    
    }


