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
    5. Timestamp. Integer variable, always equals to 0.
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
Script PATH = path is located in this skill directory, `scripts` sub-directory

## Warning
In front of every $, you must use \ like \$

## Global variables naming convention
When is necessary to from one node to affect global variable from another node, naming convention needs to be followed.
    - in node x, global variable $y from node with index of z must be named like `$z$y`. Example of naming variable $var from node 4 in node 1 is `$4$var`. Example of naming variable $var from node 3 in node 6 is `$3$var`. So the rule is $ than index of node of origin, than full variable name.

## Variables named by agent
When agent has to create variable, this naming convention must be followed. Agent will always name its variables as $agent and then first available index like `$agent1`, `$agent2`, `$agent3` and so on, so that name of the variable will always be unique on the node level.

## How to initialize service
1. You are going to use `client.py` from Script PATH with python like `python PATH/client.py`. As first argument, you are always going to provide port number 11111. For second argument and on, you are going to use app functions and its arguments; for example, command would look like `python PATH/client.py 11111 read-variables 1`
2. get number of nodes from entire system by executing command `read-node-count`. keep in mind that nodes are enumerated from 1 on ...
3. for every node index execute command `read-header` with node index as argument in order to get header text. Structure of header text is better explained in skill documentation `header.md`. The most important piece of data for the beginning is the first argument of the header function. That piece of data will be called `Location`
4. memorize all of node names(Locations) and corresponding indexes. those information are necessary for all other processes.
5. second most important piece of data is called `property`. Property is the first argument of functions sensor, switch, trigger, list. You have to memorize all of those properties for the future use. for reading sensors, function `read-sensors` is going to be used, and for switches, triggers and lists, function `read-elements`. Both of those functions are using index of the Location as argument.
### How to pass arguments to client.py???
Arguments to client.py are passed in cli, not programming style, so if 2 arguments must be passed to client. py, do it like `python PATH/client.py argument1 argument2`

## Query analysis core rules
1. First thing that agent should do, regardless of exact demand of user is to determine locations that should be affected(node indices) and properties(exact switch, sensor, trigger, list or even program).
    - example: user's query is `I want to turn on second switch in the main room`. From the query, it is clear that location is `main room`. So, agent should look for node that in its header in the first argument holds some text that refers to the `main room`. Next in order to find out property, agent must check, what object should be affected by user's demand; in this query it is clear that that object is second switch, so we can conclude that our property is switch on the location that has in its first argument some value that refers `second switch`.
    - the previous query is simple, because single user's query can affect multiple locations and multiple properties like in case `Turn off light 1 in bathroom and turn on both lights on the main room`. in here, agent must realize that location `main room`, either has two switches designated as lights or there are two nodes that deal with lights in the main room.
2. Second thing that agent should realize from the query is exact action or actions that user demands.
    - switching or turning on and off, in most of cases deal with switch element.
    - reading values from sensors deals with sensors
    - transmitting or sending usually refers to transmitters
    - selecting values from some range or from group of values, usually refers to lists
    - if user wants some sequential switching, usually deal is with serial program
    - if user wants to have some value or event affected by time, time limit should be used
    - if user wants some value to affect some other value, val conditions should be used
3. What variables to affect? If user wants to create some program that is to affect the system, then programmable variables should be used. In case when user wants to make some direct change in regards of elements, force variable should be used. Difference is explained in docs directory, elements document.
4. When all previous steps are done, agent must know all nodes(names and indices) and all of variables that should be affected by the action.

## Specific situations
    - It could happen that user don't specify location. In this case, when necessary, agent should ask explicitly for location, but in another case, agent should look through all nodes in order to determine exact location.

## Program handling core rules

### Program writing location rule
- time limit program is going to be written in node where starting and ending time variables are defined
- serial program is going to be written in node where epoch, time stamp and last index variables are defined
- value condition program is going to be written in node where most of variables used to create this program are defined
In case of tie, use node 1.

### Program names rule
Program names for programs `valCondition` and `serial` are mandatory. If user don't provide those names, agent must ask explicitly. Rule for program name is maximum 20 characters, only alpha-numeric

### Serial program pause rule
If user needs some pause in between two switches, that can't be done directly but by using certain procedure. First of all, if value of pause is divided by value of the epoch, the result must be integer. Variable of type integer with default value of 0 must be created for the purpose of pause(dummy variable). In switching array, whenever pause is necessary, name of dummy variable is going to be placed; name of dummy variable is going to be placed (length of pause)/epoch times.
    - example: if user wants serial program to affect switches light 1 and light 2 where epoch value is 2 seconds, and user wants pause of 2 seconds in between light 1 and light 2, and user needs pause of 6 seconds after light 2 is done, switching array for this program is going to be like(taking into account that programmable variable for light 1 is named `$ss1` and for light 2 is `$ss2`. In this same case, dummy variable is named `$pause`) `$ss1`, `$pause`, `$ss2`, `$pause`, `$pause`,`$pause`; so in this case we are going to get, light 1 that is going to be turned on for 2 seconds, than 2 seconds pause, than 2 seconds light 2 is going go be turned on, and finally we are going to have 3 pauses of 2 seconds each.

### Serial program multiplication of active state rule
If user needs some switch to be active longer that others, same principle like in serial program pause rule. Once again, length of activity of one switch, when divided by epoch, must be integer. So, if user needs light 1(programmable variable name `$ss1`) to be active for 2 seconds and light 2(programmable variable name `$ss2`) to be active for 4 seconds in case when epoch value is 2 seconds, switching array would look like `$ss1`, `$ss2`, `$ss2`.

### Rest of program handling rules
1. After query is properly analyzed and agent determines that the next step is dealing with program, first step in that process is to determine, with what kind of program agent must work.
2. Next step is to create all of necessary variables.
    - For time limits program
        - first functional variable that is going to hold the result(initial value is always 0)
        - starting time(string variable that is going to represent time in 24 hours format like `16:45`)
        - ending time(same formatting style as with starting time)
    - For serial program
       - before continuing to creation of rest of necessary variables, agent must check whether user needs to create a pause in between some switches. If that is true, agent must act according to predefined rules.
       - next is epoch variable, of course integer that is going to hold pause length in seconds
       - time stamp, again integer with value of 0
       - function variable, default value is None.
    - For value condition program
        - function name and that only if user ask for it explicitly 

## Exact procedure
In all of cases, always first perform `Query analysis core rules`, and in case of programs `Program handling core rules` must be implemented too.
1.  In case of switches user can say something like `Turn on first light in my living room`, `Switch the first light in livin room` or `Turn livin room light 1 off` or any variation of those.
    - now, you need to be sure what user actually wants, and basically in here, you have two different options
           - if he says that he wants to switch the light, than use command `turn-switch` and provide as arguments node index and switch name
           - if he says that he needs switch turned on or off, use command `write-variable`
2. In case of sensors, user can ask 3 different things.
    - User can ask you do deal with epoch in one of two ways
        - to update epoch value agent should use function `write-variable` with arguments of node index, epoch variable for the exact sensor and new value for this variable that user provided.
        - to read epoch value agent should use function `read-var` with arguments of node index and epoch variable for the exact sensor.
    - User can ask to read value from the sensor. If user asks something like, `I would like to know value`(temperature, intensity… or simply value) `from some sensor`; example: `Give me temperature on the first floor`.
        1. Agent should look for the fourth argument of the sensor because fourth argument is name of variable that holds reading values from the sensor.
        2. Then agent should read value from the variable by using function read-var.
    - user can also have some general question about sensors
        1. `Get me a list of sensors from some node` or similar; in which case agent should execute `read-sensors` function for that particular location-node.
        2. `Give me data about sensor that reads value greater, less, or equals of x` ; in this case agent should execute `read-sensors` on all nodes. Than for every reading variable of particular sensor to execute `read-var` in order to get value. If value fulfills user's condition(greater, less or equals to x, where x is some value provided by the user), data about that sensor should be returned to the user as result, alongside the rest of sensors that fulfill the same condition.
        3. Taking into account second example from `reading sensor` case, user doesn't have to look through sensors by reading value only. It can have conditions based on name of sensor or index on working unit(second argument), or even about epoch. User can ask something like `give me all sensors that deals with temperature`; in this case, agent should execute `read-sensors` function on all nodes and all sensors with name that have something to do with temperature(like `temp`, `temp01`, `temperature`,`temperature`,`temperature-sensor`, `temp-readings` ) should be returned to the user as the result.
3. In case of variables
    1. User can ask `I want all of variables on certain location or node`; in this case agent should execute `read-variables` with argument of node(locations) index in order to get list of all variables.
    2. User can have more specific demand like, getting variables under some condition like `all of variables of certain variable type` in what case, user should execute `read-variables` function with argument of node(location) index for certain node(if user demands variables only from one node) or for all nodes(if user wants variables from entire script. In this case, agent should specify at the end, what variable belongs to what node). User can also specify other conditions like local or global variables, arrays that hold certain elements, numerical value that is greater, less or equal to some specific value or string variable with some specific content.
    3. User can ask you to create a new variable. In this case, agent should call function `create-variable`. For this function arguments, user must provide exact values. Agent must know index of node, where variable is created(first argument), variable name for second argument, `True` or `False` value for third argument(True if variable is global, False if variable is local), variable type for fourth argument and initial value for fifth argument.
    4. User can ask for existing variable deletion. However, for deletion, some conditions must be fulfilled in order not to break the system.
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
4. In case of triggers. When user wants to deal with triggers, it is going to ask for some value to be transmitted or some value to be sent. Trigger is basically, value transmitted.
    1. User can ask for list of triggers. It can ask triggers from one node or from multiple if not all of nodes. Or it can ask for triggers by some specific condition. In all of cases, agent should use function `read-elements` and that from all of elements to take only trigger functions. If user wants triggers from one node, function `read-elements` should be executed only for node in question. If user wants triggers from multiple nodes, `read-elements` function should be executed for all necessary nodes. If user provide some condition, first all of triggers must be read from all of requested locations(nodes) and than from that list, must be removed all of triggers that are not fulfilling users conditions.
    2. User can ask about some specifics in regards of one trigger. Example `get me trigger value for red color component in light in bathroom`
        1. Start always with performing query analysis core rules on given case
        2. Than agent should execute function `read-elements` for that particular node and take into consideration only trigger elements from this response.
        3. Than from all of triggers in this list, take into consideration only the one that has logical connection with user's demand; in this case that is name like `red color`, `red light`, `red` or something in similar fashion.
        4. At the end, use function `read-var` for third argument of the selected trigger and forth argument of the selected trigger. This is important in order to see both value for programmable variable and force variable.
        5. User can also ask about trigger index on the unit itself; in that case, agent should check second argument from the selected trigger.
    3. User can ask to update trigger value. If that is the case, agent should keep in check that if value of a trigger is updated directly, then that should be by using fourth argument of trigger function, or force value. So take variable name from fourth argument and use function `write-var` in order to update its value to value desired by the user.
5. If user wants to handle lists, it is usually going to say something in regards of selection some option or changing some selection, or mode. In case of lists, all of steps like in case of triggers are the same, just apply it for lists instead of trigger. There is only one difference to take into consideration. Function list has 6 arguments instead of 4. Note that first and second argument in trigger and list are the same, fifth and sixth from list are the same as third and fourth from trigger. So only third and fourth argument of list function are new in here. Third argument of list function is array that holds indexes for selection(basically some range of numbers), while fourth argument is also array, but this array holds strings corresponding with numbers from previous array. In some cases, fourth argument can also hold numbers but the point is that arrays from third and fourth argument of list function must have the same number of arguments.
6. Case of programs. You can find file programs.md in docs directory of the skill for more info.
    1. Program `serial` are generally used when user wants to have multiple switches turning on sequentially. User's demand could be something like
        -  `I want light in living room, then light on the balcony and light in bathroom to be turned on sequentially or one ofter the another.`
        -   `I need heater on firts pannel than heater on second pannel and then heater in bedroom to be turned one after the another.`
    The key point is that multiple switches have to be turned on and off, one after the another.
        - another key feature of serial program is that user needs to provide an epoch. Epoch is actually time of, how long one switch is going to be turned on, before it turns off and next one is turned on.
        - agent must know that serial program is basically a infinite loop. When last switch from the array is off, first switch is going to be turned on again.
        - at the end, when all of data is gathered and all of necessary variables are created, agent will call function add-serial-program with arguments
            1. node of index where program is going to be created
            2. name of program that user defined at the start of this process
            3. switching array
            4. epoch variable
            5. timestamp variable
            6. last index variable
            7. None for functional variable(going to be explained later in the text)
    2. If user wants to delete serial program, it's gonna provide request in a fashion of `I want to remove sequential switching of switch in my bathroom and switch in my living room`. When agent determine what serial program should be deleted, it must ask user by using serial program name for confirmation.
    3. User can also ask for some changes or updates to serial program.
            - If user said something like `I want to add one switch to list of switches` it is clear that user wants to update list of switches by adding one more switch. Then if user didn't already, agent must ask for exact switch and how change is going to look. When all of changes that user wants to make are clear, agent should use write-variable function to update switching array to desirable content.
            - if user says that it wants to update epoch to a new value. agent should use write-variable function to change epoch variable to desirable value.
            - user can also ask to change last index variable in order to change default starting point. in that case, agent should also use write-variable function to change value of last index variable to desired value. Desired value in this case is index in the switching list of programmable variable of the switch that user wants to be used as default starting point.
    4. User can ask of agent to make a program to change some value if some condition arise. For that purpose is used valCondition program. This program is something like if else statement in various programming languages. One of most used case in regards of KS Smart Systems is with time limit programs that is going to be explained later in the text when we will have a word about timeLim programs.
        - user can ask to create a program in order to turn on some switch or to change some other value if some other value changes in some way. Example of it can be if user asks that if reading value from sensor goes over some limit that some switch should be turned on and according to that if value of the same sensor goes bellow some limit, that switch that is previously turned on, will be turned off. Example `If temperature in my living room goes below 21 degrees, turn on header number 1 in my living room` in this case, if user don't specify, agent should ask for turning off condition; acceptable option in this case would be 20 degrees.
        - user can also have multiple condition that could produce multiple results. It could ask for something like this `If temperature both in my living room and in my bathroom go below 21 degree, turn on heaters in my entire top floor.` In this case it is easy to realize that user wants to check values from two different sensors that are in most cases located on different nodes, and if, for example, there are 3 different heaters on the top floor, all 3 heaters must be turned on if conditions are fulfilled. So in this case, we would have two conditions and three results. Ways of getting variable for next step are explained in previous example.
        - now agent must determine exact operators that are going to be used in order program to be created.
            - if user says something like `if temperature is 21 degree` or `if temperature equals 21 degree` or something in fashion that means that value should be equal to demanded, than operator is `==`
            - if user says something like `if temperature is bellow 21 degree` or `temperature is not yet 21 degree` or anything in fashion that means that value that we compare is less than value that user gave as reference, operator will be `<`
            - if user demands something opposite that in previous case like `if temperature is bigger or greater than 12 degrees`, operator will be `>`
        - as you have seen, in case of conditions we have 3 different operators in regards of situation. In case of results, operator is always `=`.
        - now, we are going to list all of values, agent must know before proceeding to program creation
            - index of node where program is going to be written to.
            - name of the program in human readable form.
            - number of conditions
            - number of results
            - and now, per every condition 5 arguments sequentially
                - variable that is compared
                - compared variable type
                - variable or value for comparison
                - right side variable or value type(must be the same with compared variable)
                - operator
            - and now, per every result 5 arguments sequentially
                - variable that is compared
                - compared variable type
                - variable or value for comparison
                - right side variable or value type(must be the same with compared variable)
                - operator
            - function variable name(by default value `None` should be provided). If user explicitly don't say that it wants function variable name to be set, agent should provide default value.
        - When all of values are prepared, agent should use function add-value-condition-program with all prepared following arguments.
    5.  User can ask of agent to remove some val condition program. When program that should be delete is determined, function remove-value-condition-program
    6.  User can ask of agent to make some correction in val condition program. The same like in previous case, agent should first find program that should be changed and what variable or value should be changed. Change is going to be achieved by changing value of variable that user wants to affect
    7. User can ask to create time limit or timeLim program. This kind of program has purpose to change value of some fun variable in regards of time. Detail explanation is in docs but in simple words timeLim program has 3 arguments; first is functional variable that is affected by time, second is string representation of starting time and third is string representation of ending time.
           - user can ask something like `I want light in the main holl to be turned on in between 2 and 4 am.` In order this program to be created, function add-time-limit-program must be used.
           - But in order for result that user requested to be achieved, agent must create two val condition programs. One that is going to set switch variable to 0 when functional variable from this time limit program turns to 1 and other that is going to be set switch programmable variable to 0 when functional variable from this time limit program gets to 0.
    8. Changes to time limit program can be done in the sense of changing value of starting and ending time. For that function write-variable must be used.
7. At the end, when you get the result from the terminal, inform user about it.
    