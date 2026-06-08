help = '''
Entire administrative protocol has 20 functions. Argumens like index and name are common. Index is used for node index and
name as name of the particular element. Arguments should follow function name like in example section.
Keep in mind that in most of casses, you can't pass value but variable name. Variable that you want to affect with some
function, must be already present in the script. If variable is not present, you have to create it before you use it
in some function.

write-var index name value\t\t\t sets a new value to existing variable. with value arguments, a new value is provided

change-trigger-value index  name triggerValue\t\t\t with triggerValue argument, a new value for trigger is provided

change-list-value index name listValue\t\t\t with listValue argument, new value from the list is selected. In here, you should not provide value for the trigger but index from the list

turn-switch index name\t\t\t changes value from 0 to 1 and vice versa on selected switch

create-variable index name globalVar varType varValue\t\t\t creates new variable. globalVar is boolean argument that says whether variable is global or not. varType sets variable type and varValue, starting value for the new variable

remove-variable index name\t\t\t removes variable with provided name from the node with provided index

add-val-condition-program index name numOfConditions numOfResults 5 arguments for every condition, 5 arguments for every result, funVariableName\t\t\t this is the most complicated case because num of results and num of conditions is not fix. there are 5 arguments for every condition and result. left side, left type, right side, right tyle and sign

remove-val-condition-program index name\t\t\t removes val condition program by provided name and from node with provided index

add-time-lim-program index name start end\t\t\t creates new time limit program where start and end are the starting and ending time

remove-time-lim-program index name\t\t\t removes time limit program by privided name from node with provided index

add-serial-program index name listOfSwitches epoh lastIndex functionName=None\t\t\t creates new serial program. Argument listOfSwitches must be array that holds all of switches that should be affected by this program. epoh is time when change is commited. first switch that is going to be activated is one after last index. function name is name of function variable that could be connected to this program and used in later code

remove-serial-program index name\t\t\t removes serial program by provided name and from node with provided index

get-sensor-readings index name\t\t\t returns readings from the sensor by provided name and from node by provided index

read-var index name\t\t\t reads variable by provided name and from node by provided index

read-node-count\t\t\t returns number of existing nodes

read-programs index\t\t\t reads all of programs from the node-index

read-elements index\t\t\t reads all of elements from the node-index

read-sensors index\t\t\t reads all of sensors from the node-index

read-variables index\t\t\t reads all of variables from the node-index

read-header index\t\t\t reads header from the node-index

Example:
\t add-serial-program 2 mySerialProgram $lst $eph $lstind None
\t read-programs 3
\t get-sensor-reading 2 sensor1
\t read-var 4 $opop
'''

arguments = '''
KS Administrative Unit provides two modes.
    1. CLI mode with stdin/stdout stream. Design to be used by user directly.
        - in order to use the app with this mode, provide argument 'cli'
    2. TCP mode limited only to local machine for the security reasons. Purpose of the second mode is to be used for an AI integration.
        - in order to use the app with this mode, provide the first argument 'tcp', and the second argument is port where the service is going to listen on
'''