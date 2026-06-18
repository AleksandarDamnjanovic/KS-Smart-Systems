![](banner.jpg)

# KS Smart System

## News
As of jun 07. 2026, KS Smart Systems support AI integration. Integration tested with Hermes and OpenCode, with various local models like Gemma 3 and Nemotron 3 Nano. At this moment, AI integration is still in early experimental phase; only switching is implemented.
As of jun 11. 2026, installation helper scripts are added to the project.
As of jun 17. 2026, some bugs are fixed, AI integration is simplified, and video tutorials are published.
As of jun 18. 2026, AI skill supports more function. Future update are expected to finish AI program handling.

## Video tutorials
1. [Basic explanations](https://youtu.be/n6Ak4GIscVg)
2. [Installation tutorial for version 0.3.0](https://youtu.be/pGiK0WKn_74)
3. [AI integration with Hermes Agent and LM Studio local model via Telegram channel](https://youtu.be/Vrgk4hY9c7Y)

## Intro
KS Smart System is built with idea for more abstract approach to building of smart home and other smart systems. When building smart home, engineer usually have to worry about both electric, electronics and computer elements of the system. With this solution, after system is set up from hardware perspective, everything else is going to be dealt with from KST script. You can consider KST script as programming language for your smart home for the purpose that, you will not have to worry, any more, about voltage and pins, but about switches, transmitters and sensors, meaning script primitives which define your system.

What all of this means? Means that once you finish with setting up of your nodes, you can do all sorts of tweaks and changes without having to handle soldering iron or multi-meter, or having to flash your micro controllers.

## What this solution contains
Inside of this solution, you are going to find two projects. 

- **AAU**, written in python. This is interpreter for .kst script and the core part of the solution. AAU(or 2AU) delegates instructions to nodes, according to the script; receives responses from nodes and applies 
received values. AAU has access to all MQTT topics(communication channels). In addition, AAU has access to admin topic that can be used to send direct commands in real time to AAU and changes working script without restarting of entire system. This last functionality can be use for further development of API.

- **KS_NODE**. This is application for esp32 and eps8266 micro-controllers written with Arduino framework in Visual Studio Code and Platform IO. Before uploading this code to your devices, make sure that you set all proper values in the node.hpp file.

- **Administrative Unit or AU** is also built in python. This is standalone app that communicates with AAU via MQTT admin channel. The purpose of this app is to narrow possibilities for security and other errors and to allow AI integration. It works in two modes; cli and tcp. In cli mode background functionality is supported with cli interface where client communicates with AAU via stdin/stdou stream. Second mode is tcp; in this mode fronend cli is replaced by tcp server. More about this in [more about AU](#au)

- **ks-smart-systems-skill** AI skill tested with Hermes and OpenCode. 

## How it works
Mosquitto MQTT server is used for entire communication exchange. Every node has access only to its own topic named after name of the node itself. Every node has to have its unique index that is used as identification in the script and in instructions. AAU has access to all topics + admin topic and it processes both incoming and outgoing messages according to rules set in .kst script.

Entire communication is encrypted. By default, self-signed certificate is used.

There are multiple types of nodes, although at the moment only one type is implemented (MASTER is implemented).

- **MASTER**; this type of node, has direct access to its own topic and its messages are processed directly by AAU.

- **SHUNT**(not yet implemented); same as master type, but with additional functionality. In case when smart system has some remote group of nodes shunt serves as communication node towards remote group from the server side. All of messages for the shunt, bridge and other slave nodes in the remote group are grouped in single message on the AAU and sent to the shunt. Shunt removes from this message only those instructions with its own index and all the rest are sent to the bridge.

- **BRIDGE**(not yet implemented); is same as shunt just on the side of remote group. It receives message from the shunt, splits all of instructions by the index and reform messages for slaves connected to it. While shunt acts as a master, bridge acts as a slave. Responses from those slaves are again grouped together and as a single message sent back to the shunt that passes that message from entire remote group to the AAU.

- **SLAVE**(not yet implemented); slave is just an node in the remote group that has no direct access to the AAU but communicates with it through BRIDGE and SHUNT channel.

## How to install it

First install mosquitto server.
Use helper scripts if you are using Linux:
1. **createCerts.sh** creates self signed certificate and deploys them to appropriate directories across the project.
2. **removeCerts.sh** removes all of, by previous command, created certs
3. **setupMosquitto.sh**(needs sudo) sets up mosquitto server after installation. This script needs one argument; mosquitto broker's IP address.
4. **removeOldMosquittoConf.sh**(needs sudo) removes all done bu setupMosquitto.sh.
Make sure that you have all of settings in AAU/support.py set correctly.

Place script.kst in directory with path that you defined in AAU/support.py and run the app with python3 ./base.py. For any serious usage, consider turning this app into a service; with systemd on Linux or service on Windows.
On the side of nodes, make sure that all of data into node.hpp is set properly and upload the code to your micro controller.
If you are using mqtt explorer, ideally you should be able to see communication between the node and AAU right away.

Usage is explained in section [AU](#au).

## How communication works
On every 10 seconds, by default, node sends its own updated state to the mosqutitto server on topic with the same name as node itself. It sends confirmations for all of its sensors and switches split by space. Message looks like: 

- **Cr_11_C_0_1 Cr_11_R_0_27.5 Cr_11_R_1_70**.

What are those? Pieces of data are separated by _. Cr stands for confirmation, number 11 is the index of node itself, C stands for switch and R stands for readings(from the sensor, real or virtual one). Next number is index of element(switch or sensor) and final number is value from that element.

When some action is necessary, AAU sends instruction to all nodes at once. Command can look like:

- **I_11_C_0_0 I_11_S_0 I_11_S_1 I_11_T_0_70**

Once again, what is this? I stands for instruction, 11 is index of node that should accept that instruction, C stands for switch, S for sensor and T for transmitter. Next number represents index of the affected element and the last number is value that should be applied to that element. Of course, you can see that sensors doesn't have value to apply, because sensor is used only for reading.

You can see that there is no confirmation for transmitter's value. That is because, transmitter is used only to send value. If you want to get present value back, you can write the code on micro controller directly to copy value from the transmitter to virtual or dummy sensor, and therefore, that value will be read on every message exchange.

## Communication over the administrative channel

Now, we are in completely different dimension. Now, we are talking about sending commands to AAU over the administrative channel, or how to communicate with AAU in commanding way 👮🏻

At the moment, there are 20 functions that you can sent to admin channel on your mqtt server in order to make AAU to obey.

In all of cases argument index is index of the node that is affected. name is actual element that is affected like switch or variable.

1. **writeVar**(index, name, value) sets a new value to existing variable. *with value arguments, a new value is provided*
2. **changeTriggerValue**(index, name, triggerValue) *with triggerValue argument, a new value for trigger is provided*
3. **changeListValue**(index, name, listValue) *with listValue argument, new value from the list is selected. In here, you should not provide value for the trigger but index from the list*
4. **turnSwitch**(index, name) *changes value from 0 to 1 and vice versa on selected switch*
5. **createVariable**(index, name, globalVar, varType, varValue) *creates new variable. globalVar is boolean argument that says whether variable is global or not. varType sets variable type and varValue, starting value for the new variable*
6. **removeVariable**(index, name) *removes variable with provided name from the node with provided index*
7. **addValConditionProgram**(index, name, numOfConditions, numOfResults, 5 arguments for every condition, 5 arguments for every result, funVariableName) *this is the most complicated case because num of results and num of conditions is not fix. there are 5 arguments for every condition and result. left side, left type, right side, right tyle and sign*
8. **removeValConditionProgram**(index, name) *removes val condition program by provided name and from node with provided index*
9. **addTimeLimProgram**(index, name, start, end) *creates new time limit program where start and end are the starting and ending time*
10. **removeTimeLimProgram**(index, name) *removes time limit program by privided name from node with provided index*
11. **addSerialProgram**(index, name, listOfSwitches, epoh, lastIndex, functionName=None) *creates new serial program. Argument listOfSwitches must be array that holds all of switches that should be affected by this program. epoh is time when change is commited. first switch that is going to be activated is one after last index. function name is name of function variable that could be connected to this program and used in later code*
12. **removeSerialProgram**(index, name) *removes serial program by provided name and from node with provided index*
13. **getSensorReadings**(index, name) *returns readings from the sensor by provided name and from node by provided index*
14. **readVar**(index, name) *reads variable by provided name and from node by provided index*
15. **readNodeCount**() *returns number of existing nodes*
16. r**eadPrograms**(index) *reads all of programs from the node-index*
17. **readElements**(index) *reads all of elements from the node-index*
18. **readSensors**(index) *reads all of sensors from the node-index*
19. **readVariables**(index) *reads all of variables from the node-index*
20. **readHeader**(index) *reads header from the node-index*

## KST Script

### Overview
As is said in previous paragraph, AAU functionalities are based on script that is called kst script, and understanding of how this script works in necessary for agent to be able to operate with the entire system.
First of all, scrip is divided in nodes. Every node starts with header, than { opening swirly brackets, than variable section that is contained in between opening <variables> and closing </variables> tags, than sensors section that is contained in between opening <sensors> and closing </sensors> tags, than elements section that is contained in between opening <elements> and closing </elements> tag and finally programs section that is contained in between opening <programs> and closing </programs> tag. After closing programs tag, must be closing \} bracket in order to signalize the end of node.
### Header
Header always starts with node index and then ( opening bracket, than in the form of argument wrapped with quotation marks is name of the node in human readable form, comma in between the arguments, than another argument also wrapped in quotation marks is name of the node that is going to be used for machine communication(this name can't contain empty spaces or special signs), comma again and at the end of header must be enclosed with angle brackets, a type of node(possible values are MASTER, SLAVE, SHUNT and BRIDGE)
EXAMPLE: `1("First floor", "1f", [MASTER])` so if user asks of agent to do something on the first floor by using KS smart systems, agent should know that order is about this node.
As you can see, the first argument in the header is there to help agent to determine what node should be affected by command.
### Variables
The purpose of variables is to hold values that are going to be used by the system.
- **naming** Variable name always starts with $ dollar sign like `$hey`, `$iamvarname`, `$onemoreexample`. When global variable is called from another node, node index of called variable must be used; for example, if you want to refer some global variable(local name of that variable is let's say `$hey`) from another node(let's say that the variable that you want to refer is in node with index of 5) you are going to call it `$5$hey` which means variable `$hey` from node with index of 5. By the same logic, variable `$7$myint` would mean that this is variable with name of `$myint` from node with index of 7. Variable names can't hold empty spaces.
- **definition** there is a rule that says, one variable per one line like
```
    global int    $hey      = 10
           string $haha     = "haha"
           array  $nums     = [1, 2, 3]
```
- **global modifier** Variable can be local or global(if variable declaration has modifier "global", that is global variable. If variable doesn't have "global" modifier, that is local variable). Local variable can be used only in the same node, while global variable can be used from another node too. Example of global variable: `global int $op = 25`, Example of local variable: `int $op = 10`
- **types** .kst script supports multiple types of variables.
    1. int(integer, whole number) example `int $me = 50`
    2. float(number with decimal point) example `float $hey = 23.20`
    3. string(textual values), strings values must be wrapped with quotation marks like `string $bob = "bob the builder"`
    4. array can hold both, integers(`array $intarray = [0, 1, 2]`), strings(`array $stringarray = ["hi", "hey", "ho"]`) and other variable names(`array $varnames = [$c1, $c2, $d8]`). also, array can hold a range of integer values like `array $rangeexample = [0-255]`.
    5. fun, this is a special case variable. Variables of this type can't be global variables and it can store only integer type of values. This kind of variables are used solely to hold result from some function and are provided as function name arguments.
Example of entire Variables section
```
<variables>
    global int    $hey      = 10
           string $haha     = "haha"
           array  $nums     = [1, 2, 3]
           fun    $myfun    = 0
</variables>
```
### Sensors
Sensors are also defined by principle, sensor per line. Values from sensors are used only for readings. `sensor("temp", 0, $e1, $red)` In this example, you can see that sensor is defined by the function of the same name. First argument is the name of the sensor; agent is going to use this name as reference in its work; for example if client says **Give me the temperature in the dining room!**, agent should look for node that has `dining room` or some reference of it in its name and in it, the sensor with name of temperature of `temp`, `temperature` or some other reference. If you want to have multiple words in this name, you can use _ or - or capital and small letters to do so; example would be like `my_room`, `living-room`, `bathroomLight`. Next argument is index of this sensor on micro-controller or some other controlled unit(not in any interest of agent or user; system administrator should worry about this part). Next argument is epoch or name of integer variable that holds value in seconds of how long in between two readings. And finally, name of integer variable where readings are stored. Basically when agent or user want to read value from sensor, this variable is read.

### Elements
Apart from sensors, elements are those members of the node that can be both read from and write to, and in here we have 3 different types of it.

- **switch("light", 0, $c1, $fc1)** switch function is logical representation of real life switch. It can have only two different states; on and off or in our case 1(ON) and 0(OFF). The first argument of this function is name in human readable form. Second argument is index of the switch on controlled unit. Third argument is variable that holds programmable value and fourth argument is variable that holds force value. And what is the difference in between the last two. Third argument is going to be changed by programs defined in the script, but force variable will be used by user or agent in order to overwrite instructions from the program. Basically force variable is dominant state.
- **trigger("ACswitch", 1, $t1, $ft1)** trigger is value that is constantly transmitter to the controlled unit; you can call it transmitter if you like. First argument is name of the trigger in human readable form. Second is index of the transmitter on the physical unit or micro controller. Third and fourth arguments are, programmable value and forced value.
- **list("ACmodes", 0, $acModes, $acModeNames, $ACselectedMode, $fl1)** list is basically same as trigger but with one difference. While value from trigger is taken directly on controlled unit, value of list is taken as index. For example, with trigger you send value of 150 that should be used to set red element of your light; with list you have like 3 different modes of work like in the case of AC [off, heating, cooling]; when you send value 0 with list transmitter, micro controller option off is going to be selected because that option corresponds with index 0 from the provided list. First argument is the name of the list in human readable form. Second argument is index of this transmitter on the controlled unit. Third is the list of select-able elements in indexes or integers like [0, 1, 2]; forth is the same list but now in strings like [off, heating, cooling]. Fifth and sixth arguments are selected index in programmable mode and in force mode.

### Programs
Programs are where true power of .kst lies. At the moment, there are three types of programs. `valCondition`, `serial` and `timeLim`. `valCondition` and `serial` can be named, while `timeLim` can't. Type of variable that is used to name a program is fun.

- **valCondition(textName, conditions, result)**;
```
$example = valCondition(
    "temp on",
    $res01 < $tempLimDown
    $c1 == 0, 
    $c1 = 1
    $tempState = 1
);
```
In this case $example is name of this functions. Type of variable is fun and type of function is `valCondition`. If you don't need named function, simply don't name it; just write `valCondition(` without `$example` = part.
`valCondition` function has three arguments, or better to say three groups of arguments. First argument is function name in human readable form. Second argument is one or more conditions separated by new line; all of conditions must be true in order result to be executed. Result can also have one or more statements separated by new line.

- **serial(textName, listOfSwitches, epoh, timeStamp, lastIndex);**
        Program serial have purpose to turn on one switch from provided list of switches, when time comes. Program starts from switch with index provided in fifth argument, and keeps it on till the epoch provided in third argument in seconds ends. Then `timeStamp` provided in forth argument changes to current time and the new epoch starts from the beginning turning on next switch from the list... so on till the end of the list. When list ends, it starts from the beginning in the same fashion. Timestamp default value is 0, so always when you define `timeStamp` variable, you are going to set it with value of 0;
```
$fun01= serial("two switches", $listOfSwitches, $switchEp, $sTime, $lastIndex);
```
Function naming applies here too. Function of type serial is written in a single line with ; at the end.

- **timeLim(function, start, end);**
```
timeLim($fun01, $start, $end);
```
With function `timeLim`, you are able to define execution time of some other function. For example, if you want your serial program or conditional program to be executed only between 12:00 and 14:00, as a first argument to the `timeLim` function, you are going to provide function name of the function you want to limit by time, as second argument you are going to provide string variable that hold value of "12:00" and as third argument, string variable that holds value of "14:00".
Therefore default value of variable of type fun that hold function name of the function you want to limit by time is 1. That means that function is going to be executed by default except if it is provided to `timeLim` function. `timeLim` function keeps value of fun variable to 1 only in selected time; in other case, it keeps it to 0. If value of naming variable is 0 that means that that function is going to be ignored; if is 1 it is going to be executed.

Exampe of entire node:
```
1("First floor", "1f", [MASTER]){
    
    <variables>
        global      int         $e1 =               10
        global      float       $res01 =            0.0
        global      float       $res02 =            0.0
        global      int         $c1 =               0
        global      int         $c2 =               0
                    int         $f1 =               0
                    int         $f2 =               0
                    string      $t1 =               "3"
                    string      $ft1 =              ""
                    string      $start =            "19:20"
                    string      $end =              "6:00"
                    fun         $lightsON =         0
                    int         $opop =             0
                    array       $ha =               [$c1, $c2]
                    int         $haha =             4
                    int         $bo =               0
                    array       $listOfSwitches =   [$c1, $c2]
                    int         $switchEp =         3
                    int         $time =             0
                    int         $lastIndex =        0
                    array       $lv =               [0, 1, 2]
                    array       $ln =               ["off", "cooling", "heating"]
                    int         $l1 =               1
                    string      $lf1 =              "1"

    </variables>

    <sensors>
        sensor("temp", 0, $e1, $res01)
        sensor("moist", 1, NULL, $res02)
    </sensors>

    <elements>
        switch("light0", 0, $c1, $f1)
        switch("light1", 1, $c2, $f2)
        trigger("TempValue", 0, $t1, $ft1)
        list("lista", 1, $lv, $ln, $l1, $lf1)
    </elements>

    <programs>
        valCondition(
            "light on",
            $lightsON == 1,
            $c1 = 1
        );
        valCondition(
            "light off",
            $lightsON == 0,
            $c1 = 0
        );
        timeLim($lightsON, $start, $end);
        serial("entire row", $listOfSwitches, $switchEp, $time, $lastIndex);
    </programs>

}
```
## AU
As is already said in [Section **What this solution contains**](#what-this-solution-contains) AU can work in two modes; cli and tcp. If you want to start it in cli mode, run command au directory `python au.py cli`. If instead you wish to use it in tcp mode run `python au.py tcp 11111` where 11111 is port number. Port number 11111 is mandatory if you intent to use AI integration because ai skill is written around that port number. If you intent to use it by manually calling client.py or creating your own app, you can use any port number by your choosing.

If you want to use it with cli and to list available commands run it with `python au.py help`. With cli already running, you can run command `help` in the app terminal to get list of available functions. Command `exit` can be used to shut AU down.

List of available AU commands:
1. **write-variable** sets a new value to existing variable.
   1. index of node where variable is located
   2. name of variable itself
   3. new value.
2. **change-trigger-value** sets new value for a trigger.
    1. index of node where trigger is located
    2. name of trigger itself
    3. new trigger value.
3. **change-list-value** sets new list selected index.
    1. index of node where list is located
    2. name of list itself
    3. new index value to be selected
4. **turn-switch** changes value from 0 to 1 and vice versa on selected switch.
    1. index of node where switch is located
    2. name of the switch itself
5. **create-variable** creates new variable.
    1. index of node where variable is located
    2. Boolean argument that says whether variable is global or not; can be True or False
    3. variable type; can be int, string, fun, array, float
    4. value for the new variable
6. **remove-variable**(index, name) removes variable.
    1. index of node where variable is located
    2. name of the variable
7. **add-value-condition-program** creates value condition program; sort of if else statement for .kst script.
    1. index of node where program is located
    2. name of the program in human readable form
    3. number of conditions
    4. number of results
    5. for every condition, additional 5 arguments must be provided
        1. left side variable
        2. left side variable type (one of variable types of .kst script)
        3. right side variable
        4. right side variable type
        5. sign(operation); can be > < ==
    6. for every result, additional 5 arguments must be provided
        1. left side variable
        2. left side variable type (one of variable types of .kst script)
        3. right side variable
        4. right side variable type
        5. sign(operation); can be > < =
    7. function name. this is used only if you want to have some variable that refers entire function. Default value is `None`
8. **remove-value-condition-program** removes val condition program
    1. index of node where the program is located
    2. name of program itself
9. **add-time-limit-program** creates new time limit program.
    1. index of node where the program is located
    2. name of program itself
    3. string variable that holds starting time
    4. string variable that holds ending time
10. **remove-time-limit-program** removes time limit program
    1. index of node where the program is located
    2. name of program itself
11. **add-serial-program** creates new serial program.
    1. index of node where the program is located
    2. name of program itself
    3. array variable that holds list of switches
    4. epoch variable. this variable holds value in seconds of pause in between two activation(switching). After the epoch ends, next switch from the list of switches is going to be activated while all the rest are going to be shut down.
    5. last selected index. this is basically the starting point
    6. function variable in the case when you need some function that is going to refer entire program. Default value is `None`
12. **remove-serial-program** removes serial program.
    1. index of node
    2. name of the program
13. **get-sensor-readings** returns readings from the sensor
    1. index of the node
    2. name of the sensor
14. **read-var** reads variable
    1. node index
    2. variable name
15. **read-node-count** returns number of existing nodes. No arguments needed.
16. **read-programs** reads all of programs from the node.
    1. node index
17. **read-elements** reads all of elements from the node.
    1. node index
18. **read-sensors** _reads all of sensors from the node
    1. node index
19. **read-variables** reads all of variables from the node
    1. node index
20. **read-header** reads header from the node
    1. node index

Although tcp mode is built for the purpose of AI integration and, possibly, APIs, you can use it manually with client.py from the same directory; if you want to do so, first make sure that both KS AAU and KS AU are running and then use python to run client.py with arguments of port number, AU is operating on, and, finally, command and command's arguments line in following example `python client.py 11111 write-variable 1 \$varName 1` or `python client.py 11111 exit`

## AI skill
Skill is tested with Hermes and OpenCode. In order to install it, just copy entire skill directory to skill location of you agent. This directory contains SKILL.md and directories docs and scripts.