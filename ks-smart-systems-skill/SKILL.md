---
name: ks-smart-systems-skill
description: deals with ks smart systems automation
version: 0.0.1
platforms: [linux, macos, windows]
metadata:
  hermes:
  tags: [autonomous-ai-agents]
  requires_toolsets: [terminal, python]
---

# KS Smart Systems skill

## When is used
Whenever user asks to do something with its home or company automation that is based on KS Smart Systems. Demand could be something like "Turn on the light in the living room", "Turn off heater in the dining room." , "Make lights more red in the penthouse", "Get me temperature from the terrace"

## Additional documentation
All of necessary documentation is supplied to the skill in `skill path`/docs

## App functions
App can take 20 different commands with or without arguments in order to process user's request. Arguments are provided in the way `command` `firstArgument` `secondArgument`; examples `write-variable 1 $var1 25`, `change-list-value 3 $newVal 2`. Down is provided list of functions(commands) with arguments.

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

## Script path and execution
Script PATH ....................enter path ih here(remove dots too :D)......................

## Warning
In front of every $, you must use \ like \$

## How to initialize service
1. You are going to use `client.py` from Script PATH with python like `python PATH/client.py`. As first argument, you are always going to provide port number 11111. For second argument and on, you are going to use app functions and its arguments; for example, command would look like `python PATH/client.py 11111 read-variables 1`
2. get number of nodes from entire system by executing command `read-node-count`. keep in mind that nodes are enumerated from 1 on ...
3. for every node index execute command `read-header` with node index as argument in order to get header text. Structure of header text is better explained in skill documentation `header.md`
4. memorize all of node names and corresponding indexes. those information are necessary for all other processes.

## Exact procedure
1. Listen the request from the user.
    1. In case of switches user can say something like `Turn on first light in my living room`, `Switch the first light in livin room` or `Turn livin room light 1 off` or any variation of those. Proceed to execution in this way:
    2. Understand what is location, what is object and what is action that needs to be performed. In our example, it is obvious that location is `living room`, object is `light1` and action is `turning switch` on or off(depends exactly what user needs)
    3. Now, when you know the location, first check what node name the best describes that location. If you have nodes like `dining room`, `living room`, `hool`, it is obvious that the switch is located in the node `living room`. Take into consideration the index of node `living room` because you are going to need it later on.
    4. now, you need to find exact element. elements are better described in skill documentation `elements.md`. you are going to execute command `read-elements` with the node index in order to get all of elements from the node. Now, take into account only switches, because in this case, we don't need the rest. Find the switch with the name that best describes what user needs. For example if user needs `light 1` or `first light` look for the switch name that fits description. Memorize both exact switch name and the force variable(that is the last argument from the switch)
     5. now, you need to be sure what user actually wants, and basically in here, you have two different options
           - if he says that he wants to switch the light, than use command `turn-switch` and provide as arguments node index and switch name
           - if he says that he needs switch turned on or off, use command `write-variable` and provide as arguments 1. node index, 2. switch force variable name, 3. 1 or 0(in case of third argument, 1 is going to be provided if user wants switch turned on, or 0 if he wants switch turned off). 
2. At the end, when you get the result from the terminal, inform user about it.
