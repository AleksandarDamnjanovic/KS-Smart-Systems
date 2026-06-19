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
    2. Name of the variables(must start with $)
    3. Boolean argument that says whether variable is global or not; can be True or False
    4. variable type; can be int, string, fun, array, float
    5. value for the new variable

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
    5. Timestamp. Ingeger variable, always equals to 0.
    6. last selected index. this is basically the starting point
    7. function variable in the case when you need some function that is going to refer entire program. Default value is `None`

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
Script PATH ....................enter path in here(remove dots too :D)......................

## Warning
In front of every $, you must use \ like \$

## How to initialize service
1. You are going to use `client.py` from Script PATH with python like `python PATH/client.py`. As first argument, you are always going to provide port number 11111. For second argument and on, you are going to use app functions and its arguments; for example, command would look like `python PATH/client.py 11111 read-variables 1`
2. get number of nodes from entire system by executing command `read-node-count`. keep in mind that nodes are enumerated from 1 on ...
3. for every node index execute command `read-header` with node index as argument in order to get header text. Structure of header text is better explained in skill documentation `header.md`. The most important piece of data for the beginning is the first argument of the header function. That piece of data will be called `Location`
4. memorize all of node names(Locations) and corresponding indexes. those information are necessary for all other processes.
5. second most important piece of data is called `property`. Property is the first argument of functions sensor, switch, trigger, list. You have to memorize all of those properties for the future use. for reading sensors, function `read-sensors` is going to be used, and for switches, triggers and lists, function `read-elements`. Both of those functions are using index of the Location as argument.

## Exact procedure
1. In case of switches.
    1. In case of switches user can say something like `Turn on first light in my living room`, `Switch the first light in livin room` or `Turn livin room light 1 off` or any variation of those. Proceed to execution in this way:
    2. Understand what is location, what is property and what is action that needs to be performed. In our example, it is obvious that location is `living room`, object is `light1` and action is `turning switch` on or off(depends exactly what user needs)
    3. Now, when you know the location, first check what node name the best describes that location. If you have nodes like `dining room`, `living room`, `hool`, it is obvious that the switch is located in the node `living room`. Take into consideration the index of node `living room` because you are going to need it later on.
    4. now, you need to find exact element. elements are better described in skill documentation `elements.md`. Now, take into account only switches, because in this case, we don't need the rest. Find the switch with the name that best describes what user needs. For example if user needs `light 1` or `first light` look for the switch name that fits description. Memorize both exact switch name and the force variable(that is the last argument from the switch)
     5. now, you need to be sure what user actually wants, and basically in here, you have two different options
           - if he says that he wants to switch the light, than use command `turn-switch` and provide as arguments node index and switch name
           - if he says that he needs switch turned on or off, use command `write-variable` and provide as arguments 1. node index, 2. switch force variable name, 3. 1 or 0(in case of third argument, 1 is going to be provided if user wants switch turned on, or 0 if he wants switch turned off).
2. In case of sensors, user can ask 3 different things. First make sure that you understand what is location, what is property and what is action that should be taken.
    - User can ask you do deal with epoch in one of two ways
        - to update epoch value 
            1. After knowing exact sensor that should be dealt with, agent should look for the third argument of the sensor function, because third argument is name of variable that holds value for epoch.
            2. In second step, agent should use function `write-variable` with arguments of node index, epoch variable for the exact sensor and third new value for this variable that user provided.
        - to read epoch value 
            1. After knowing exact sensor that should be dealt with, agent should look for the third argument of the sensor function, because third argument is name of variable that holds value for epoch.
            2. In second step, agent should use function `read-var` with arguments of node index and epoch variable for the exact sensor.
    - User can ask to read value from the sensor. If user asks something like, `I would like to know value`(temperature, intensity… or simply value) `from some sensor`; example: `Give me temperature on the first floor`.
        1. After knowing exact sensor that should be dealt with, agent should look for the fourth argument of the sensor because fourth argument is name of variable that holds reading values from the sensor.
        2. Then agent should read value from the variable by using function read-var.
    - user can also have some general question about sensors
        1. `Get me a list of sensors from some node` or similar; in which case agent should execute `read-sensors` function for that particular location-node.
        2. `Give me data about sensor that reads value greater, less, or equals of x` ; in this case agent should execute `read-sensors` on all nodes. Than for every reading variable of particular sensor to execute `read-var` in order to get value. If value fulfills user's condition(greater, less or equals to x, where x is some value provided by the user), data about that sensor should be returned to the user as result, alongside the rest of sensors that fulfill the same condition.
        3. Taking into account second example from `reading sensor` case, user doesn't have to look through sensors by reading value only. It can have conditions based on name of sensor or index on working unit(second argument), or even about epoch. User can ask something like `give me all sensors that deals with temperature`; in this case, agent should execute `read-sensors` function on all nodes and all sensors with name that have something to do with temperature(like `temp`, `temp01`, `temperature`,`temperature`,`temperature-sensor`, `temp-readings` or anything else in the same fashion) should be returned to the user as the result.
3. In case of variables
    1. User can ask `I want all of variables on certain location or node`; in this case agent should execute `read-variables` with argument of node(locations) index in order to get list of all variables.
    2. User can have more specific demand like, getting variables under some condition like `all of variables of certain variable type` in what case, user should execute `read-variables` function with argument of node(location) index for certain node(if user demands variables only from one node) or for all nodes(if user wants variables from entire script. In this case, agent should specify at the end, what variable belongs to what node). User can also specify other conditions like local or global variables, arrays that hold certain elements, numerical value that is greater, less or equal to some specific value or string variable with some specific content.
    3. User can ask you to create a new variable. In this case, agent should call function `create-variable`. For this function arguments, user must provide exact values. Agent must know index of node, where variable is created(first argument), variable name(must start with $) for second argument, `True` or `False` value for third argument(True if variable is global, False if variable is local), variable type for fourth argument and initial value for fifth argument.
    4. User can ask for existing variable deletion. However, for deletion, some conditions must be fulfilled in order not to break the system. Be aver that if variable is named like $var in node with index of 5, if is global, that variable is going to be called `$5$var` in all other nodes except node with index of 5.
        1. If variable that user wants to delete is global, agent must check first:
            1. All of array type variables in the entire script by executing `read-variables` function. All of array variables that hold variable name for deletion as array member must be remembered for the future use.
            2. Later in the text, we are going to talk about how agent should process programs, but in here first I will explain, how to deal with programs in regards of deleting global variable. Agent must read all of programs in the entire script by execution function `read-programs` with argument of index node for every node. Every program that holds any reference to variable for deletion(either it has deletion variable as argument or has array variable as arguments that has deletion variable as its element) is going to be remembered for later use.
            3. Global variable for deletion must apply all of conditions for local variable too, and conditions for local variable are going to be provided later in the text.
        2. If variable that user wants to delete is local
            - Agent must check presence of variable for deletion in all of sensors by executing `read-sensors` for local node(node where variable is located), in all of elements by executing `read-elements` for local node and in all of programs by executing `read-programs` for local node. Every occurrence of variable for deletion must be remembered for later use.
        3. When presence of variable for deletion is known, agent must determine whether variable for deletion is essential or system variable or not. Essential of system variables are those variables that are present as argument in sensors, switches, triggers or lists. If variable for deletion is essential, it can not be deleted by agent by any means. In this case, agent must inform user that variable that user wants to delete is essential variable and it can not be deleted by agent. The only way for this variable to be deleted is to be deleted by system administrator directly. All other steps in regards of variable deletion process, can be jump over in this case.
        4. If variable for deletion is present in programs but not essential, it can be deleted, but user must be informed that variable for deletion is used in specific programs and before deleting of the variable, those programs that hold variable as argument or that hold array variable that has variable for deletion as element, must be deleted first. If user persist that variable for deletion must be deleted, agent must delete all of programs that have some reference to variable for deletion(detail explanation of how to delete programs are going to be found later in the text), before proceeding to variable deletion.
        5. Before proceeding to variable deletion, the same variable must be remove from all of arrays where is contained as element. Agent should do that by updating array with new value, where variable for deletions is excluded. For this, function `write-variable` must be used.
        6. Variable deletion is going to be performed by calling function `remove-variable` with arguments of node index where variable for deletion is located and name of the variable itself.
    5.  User can ask to update value of existing variable. In this case `write-variable` function should be used with arguments of node index, existing variable name and new value respectively.
4. In case of triggers
    1. User can ask for list of triggers. It can ask triggers from one node or from multiple if not all of nodes. Or it can ask for triggers by some specific condition. In all of cases, agent should use function `read-elements` and that from all of elements to take only trigger functions. If user wants triggers from one node, function `read-elements` should be executed only for node in question. If user wants triggers from multiple nodes, `read-elements` function should be executed for all necessary nodes. If user provide some condition, first all of triggers must be read from all of requested locations(nodes) and than from that list, must be removed all of triggers that are not fulfilling users conditions.
    2. User can ask about some specifics in regards of one trigger. Example `get me trigger value for red color component in light in bathroom`
        1. In this case, agent should look first for node that describe the location and take its index for future use; if data is not already present in the agent's memory, agent should use function `read-header` for all nodes in the system(script).
        2. Than agent should execute function `read-elements` for that particular node and take into consideration only trigger elements from this response.
        3. Than from all of triggers in this list, take into consideration only the one that has logical connection with user's demand; in this case that is name like `red color`, `red light`, `red` or something in similar fashion.
        4. At the end, use function `read-var` for third argument of the selected trigger and forth argument of the selected trigger. This is important in order to see both value for programmable variable and force variable.
        5. User can also ask about trigger index on the unit itself; in that case, agent should check second argument from the selected trigger.
    3. User can ask to update trigger value. If that is the case, agent should keep in check that if value of a trigger is updated directly, then that should be by using fourth argument of trigger function, or force value. So take variable name from fourth argument and use function `write-var` in order to update its value to value desired by the user.
5. In case of lists, all of steps like in case of triggers are the same, just apply it for lists instead of trigger. There is only one difference to take into consideration. Function list has 6 arguments instead of 4. Note that first and second argument in trigger and list are the same, fifth and sixth from list are the same as third and fourth from trigger. So only third and fourth argument of list function are new in here. Third argument of list function is array that holds indexes for selection(basically some range of numbers), while fourth argument is also array, but this array holds strings corresponding with numbers from previous array. In some cases, fourth argument can also hold numbers but the point is that arrays from third and fourth argument of list function must have the same number of arguments.
6. In case of programs, dealing with programs is not that complicated. More concerning is actually when to do it. First you must recognize when user actually wants to deal with programs and in what way. You can find file programs.md in docs directory of the skill for more info, but now, we are going to discuss, actually when to deal with it.
    1. Program `serial` are generally used when user wants to have multiple switches turning on sequentially. User's demand could be something like
        -  `I want light in living room, then light on the balcony and light in bathroom to be turned on sequentially or one ofter the another.`
        -   `I need heater on firts pannel than heater on second pannel and then heater in bedroom to be turned one after the another.`
    or anything in similar fashion. The key point is that multiple switches have to be turned on and off, one after the another.
        - another key feature of serial program is that user needs to provide an epoch. Epoch is actually time of, how long one switch is going to be turned on, before it turns off and next one is turned on.
        - so if user demands something that can be considered request for serial program, if user don't provide epoch value in seconds and name of the program(string that is going to serve as reference or depiction of this program functionality. if name of the program contains multiple words, use `_` instead of empty spaces in between words and do not allow longer names that 20 characters, and no special characters, only letters and numbers) than agent must ask for those two pieces of information before continuing to program creation.
        - next step is for agent to determine exact location and properties, meaning node indices and switches(actually programmable variable of the switch; that is third argument of switch function)
        - if all of switches are located on single node, in that case serial program is going to be written to that very same node. In other case; if switches are located in multiple nodes, new serial program is going to be written in first node or node with index of 1.
        - if switches are from different nodes, as we said, the serial program is going to be written to node 1, but in that case, all of programmable variables from switches from other nodes than node 1, their names must be provided in its global form. global form of variable name is $ than node index where variable is defined, and variable name with $ at the beginning; example if we want global variable name for variable named $hey from node 5, its global name would be `$5$hey`
        - agent must know that serial program is basically a infinite loop. When last switch from the array is off, first switch is going to be turned on again.
        - there is one more question to consider before we continue to the next step. User can demand to have a pause in between some switches. That pause can't be coded into the program, but there is a trick to do it. If user wants a pause in between let's say switch 1 and switch 2; let's say that programmable variable of those two are $s1 and $s2 respectively; agent should create one more local variable of type integer and give it initial value of 0(procedure of variable creation is given in this text already. name of this variable will be `$agentVar` with first available free index so the name of the variable must be genuine on the level of the node; example `$agentVar0`, `$agentVar1` and so on), so the array would look like $s1, $agentVar0, $s2. In the next step when I explain array creation, agent should use this variable whenever user needs pause. This single variable can be used multiple times in single array; not being connected to any actual switch, it will make no harm. Agent can put this pause variable multiple times in a row if user needs longer pause. There are two limitations.
           - Pause in this way can be multiplied only by the value of epoch.
           - One pause variable can't be used in multiple programs.
        - When all previous steps are cleared, now agent must create the switching array. Switching array is local variable of type array with name given in already predefined fashion(name of this variable will be `$agentVar` with first available free index so the name of the variable must be genuine on the level of the node; example `$agentVar0`, `$agentVar1` and so on). Elements of newly created array will be programmable variables from all switches that are included in user's demand with pause variable present in all positions where user demands a pause. Example: if programmable variables(third argument of switch function) that user wants in serial program are `$s1`, `$s2` and `$s3`, and user wants single pause in between $s1 and $s2 and double pause after $s3, and agent has already created pause variable named `$agentVar1`, and let's say that variable $s2 is from node 3 and $s3 is from node 5(in here, we are presuming that variable $s1 is from node 1 where serial program is going to be written to. in that case, only variable $s1 doesn't have to be in its global form), in that case, switching array would look like `$s1, $agentVar1, $3$s2, $5$s3, $agentVar1, $agentVar1`. At the end agent should create this array variable in the way described in section of this text that deals with creation of variables.
        - next variable that user needs to create is local integer variable that is going to hold value of epoch that is provided by the user. naming of agent created variables and procedure of variable creation is already given in this text.
        - next variable that user needs to create is local integer variable that is going to hold timestamp. agent is going to provide initial value of 0 to this variable. naming of agent created variables and procedure of variable creation is already given in this text.
        - next variable that user needs to create is local integer variable that is going to hold value of last index. if user don't say explicitly what index he wants to start from, initial value of this variable is going to be 0. naming of agent created variables and procedure of variable creation is already given in this text.
        - at the end, when all of data is gathered and all of necessary variables are created, agent will call function add-serial-program with arguments
            1. node of index where program is going to be created(if all of switches are from single node than that node index is going to be provide, else 1)
            2. name of program that user defined at the start of this process
            3. switching array
            4. epoch variable
            5. timestamp variable
            6. last index variable
            7. None for functional variable(going to be explained later in the text)
    2. If user wants to delete serial program, it's gonna provide request in a fashion of `I want to remove sequential switching of switch in my bathroom and switch in my living room`
        1. First move of agent is to determine exact location(node or nodes) and property, switches.
        2. Than should be checked node 1 for serial program in case that switches are from multiple different nodes.
        3. Basically, serial program that user wants to delete must contain switching variable that contains programmable variables of switches that user mentioned in its request.
        4. When agent determine what serial program should be deleted, it must ask user by using serial program name(first argument) for confirmation.
7. At the end, when you get the result from the terminal, inform user about it.
