import re
import datetime
import time
import support
from pathlib import Path
import sys, os
from accessories.ks_node import node
from accessories.script_objects import *
from accessories.node_factory import nodeFactory
from accessories.ks_logger import logit

# 📎 this function is called initially in order to process script and to create all of necessary objects
def buildAll():
    support.factory = None
    support.nodes = None
    support.factory = nodeFactory()
    support.factory.buildNodes()
    support.nodes = support.factory.getNodes()

# 📎 this function is called both initially and on every rerun in order to process messages for all of nodes
def refresh():
    for node in support.nodes:
        for s in node.getSerials():
            v = node.getVariableValueByName(s.getElements())
            for i in v:
                node.setVariableValueByName(i, 0)

    for node in support.nodes:
        node.processNode()










def writeNode(index, text):
    ind = str(text).index(",")
    text = str(text)[ind+1: str(text).__len__()]
    if text[0]==" ":
        text = text[1:str(text).__len__()]
    if not text.startswith(str(index)):
        return "FORMAT EXEPTION"
    
    text= text.replace("}", "")
    
    file = open(support.scriptFile, "r")
    content = file.read()
    file.close()

    NODES = content.split("}")
    newContent = ""
    for i in range(0, NODES.__len__()):
        if not (NODES[i].__contains__("MASTER")) or (NODES[i].__contains__("SLAVE")):
            continue
        und = int(re.search("[0-9]+", NODES[i])[0])
        if und == int(index):
            NODES[i]= text
        if NODES[i].__contains__("}"):
            NODES[i]= NODES[i].replace("}","")
        newContent = f"{newContent}{NODES[i]}"
        newContent = newContent + "}"

    file = open(support.scriptFile, "w")
    file.write(newContent)
    file.close()

    while support.START == True:
        time.sleep(0.1)

    support.START = True
    buildAll()
    refresh()
    support.START = False

    return "UPDATED"






# 📎 this function removes serial program by provided name from node with provided index
def removeSerialProgram(index, name):
    try:
        n = support.factory.getNodeByIndex(int(index))
        result = n.removeSerialProgram(name)
        if result:
            return "UPDATED"
        else:
            return "ERROR"
    except Exception as e:
        logit(f"Error in function removeSerialProgram in script.py. Error text: {e}", 2)
        return "ERROR"

# 📎 this function creates serial program out of provided arguments and adds it to
# 📎 the program list of the node with provided index
def addSerialProgram(index, name, listOfSwitches, epoh, lastIndex, functionName = None):
    try:
        n = support.factory.getNodeByIndex(int(index))
        s= serial(name, listOfSwitches, epoh, "$opop", lastIndex, funName= functionName)
        result= n.addSerialProgram(s)
        if result:
            return "UPDATED"
        else:
            return "ERROR"
    except Exception as e:
        logit(f"Error in function addSerialProgram in script.py. Error text: {e}", 2)
        return "ERROR"

# 📎 this function removes time lim program from provided node index with provided fun variable name
def removeTimeLimProgram(index, funName):
    try:
        n = support.factory.getNodeByIndex(int(index))
        result = n.removeTimeLimit(funName)
        if result:
            return "UPDATED"
        else:
            return "ERROR"
    except Exception as e:
        logit(f"Error in function removeTimeLimProgram in script.py. Error text: {e}", 2)
        return "ERROR"

# 📎 this function creates a new timeLim program. it needs node index, function variable name, start and end time string variables
def addTimeLimProgram(index, funName, start, end):
    try:
        n = support.factory.getNodeByIndex(int(index))
        tl = timeLim(funName, start, end)
        result = n.addTimeLimit(tl)
        if result:
            return "UPDATED"
        else:
            return "ERROR"
    except Exception as e:
        logit(f"Error in function addTimeLimProgram in script.py. Error text: {e}", 2)
        return "ERROR"

# 📎 this functon needs 2 arguments; index of the node and name of val condtion program
def removeValConditionProgram(index, name):
    try:
        n = support.factory.getNodeByIndex(int(index))
        if name in n.getFunctionNames():
            n.removeFunctionNames(name)
        result = n.removeValueCondition(name)
        if result:
            return "UPDATED"
        else:
            raise Exception("Nothing is deleted")
    except Exception as e:
        text= f"Error with deleting val condition program {name} in node with index {index}"
        logit(text, 2)
        return "ERROR"

# 📎 this function adds provided val condition program to the val condition program list of the node with provided index
# 📎 if function name is present, that variable is going to be added to function name variable list of the provided node
def addValConditionProgram(index, valConditionProgram): 
    try:
        n = support.factory.getNodeByIndex(int(index))
        n.addValueCondition(valConditionProgram)
        if valConditionProgram.getFunName() != None:
            n.addFunctionName(valConditionProgram.getFunName())
        return "UPDATED"
    except Exception as e:
        text= f"Error with updating value condition program {valConditionProgram.getName()} in node with index {index}"
        logit(text, 2)
        return "ERROR"

# 📎 this function removes variable in node with provided index
# 📎 provided arguments are node index and variable name
def removeVariable(index, varName):
    text= f"There is no variable {varName} in node with index {index}"
    try:
        n = support.factory.getNodeByIndex(int(index))
        result = n.removeVariableByName(varName)

        if not result:
            raise Exception(text)

        support.factory.removeGlobalVariable(index, varName)
        return "UPDATED"
    except Exception as e:
        logit(text, 2)
        return "ERROR"

# 📎 this function creates new variable in node with provided index
# 📎 provided arguments are node index, variable name, boolean that defines whether variable is global or not
# 📎 variable type and variable value
def createVariable(index, varName, globalVar, varType, varValue):
    try:
        n = support.factory.getNodeByIndex(int(index))
        gVar = None
        if globalVar:
            varType = f"global {varType}"
            gVar = globalVariable(varType, varName, varValue, index)
            support.factory.appendToGlobalVariables(gVar)
        var= variable(varType, varName, varValue)
        n = support.factory.getNodeByIndex(int(index))
        n.appendVariableToTheNode(var)
        return "UPDATED"
    except Exception as e:
        text= f"unsuccessfull creation of variable {varName} on node with index {index}"
        logit(text, 2)
        return "ERROR"

# 📎 this function affects only LISTS. when called, it changes selected value from the list
# 📎 then, newly selected value is going to be transmitter to the node
def changeListValue(index, listName, listValue):
    n = support.factory.getNodeByIndex(int(index))
    LIST = n.getListByName(listName)
    var = LIST.getState()
    val = n.getVariableValueByName(var)

    if(LIST==None):
        text= f"list with name of {triggerName} on node with index {index} not existing"
        logit(text, 2)
        return text

    writeVar(index, var, listValue)
    val1 = n.getVariableValueByName(var)

    if str(listValue) == str(val1):
        return "UPDATED"
    else:
        return "ERROR"

# 📎 this function affects only SENSORS. when called it returns value from memory variable of the named sensor
def getSensorReadings(index, sensorName):
    n = support.factory.getNodeByIndex(int(index))
    sensor = n.getSensorByName(sensorName)
    readings = sensor.getReadings()
    val = n.getVariableValueByName(readings)

    if(readings==None or readings==""):
        text= f"sensor with name of {sensorName} on node with index {index} not existing"
        logit(text, 2)
        return text

    return val

# 📎 this function affects only TRIGGERS. when called, it changes value of its regular variable
def changeTriggerValue(index, triggerName, triggerValue):
    n = support.factory.getNodeByIndex(int(index))
    trigger = n.getTriggerByName(triggerName)
    var = trigger.getValue()
    val = n.getVariableValueByName(var)

    if(trigger==None):
        text= f"trigger with name of {triggerName} on node with index {index} not existing"
        logit(text, 2)
        return text

    writeVar(index, var, triggerValue)
    val1 = n.getVariableValueByName(var)

    if str(triggerValue) == str(val1):
        return "UPDATED"
    else:
        return "ERROR"

# 📎 this function affects only switches. when called it changes value of its force variable
def turnSwitch(index, switchName):
    n = support.factory.getNodeByIndex(int(index))
    switch = n.getSwitchByName(switchName)
    
    if(switch==None):
        text= f"switch with name of {switchName} on node with index {index} not existing"
        logit(text, 2)
        return text

    var = switch.getForce()
    val = n.getVariableValueByName(var)
    val = int(val)
    if val == 1:
        writeVar(index, var, 0)
    else:
        writeVar(index, var, 1)

    val1 = int(n.getVariableValueByName(var))

    if str(val) != str(val1):
        return "UPDATED"
    else:
        return "ERROR"

# 📎 this function updates value of variable by providing node index, variable name and the new value
def writeVar(index, varName, varValue):
    n = support.factory.getNodeByIndex(int(index))
    variable = n.getVariable(varName)
    type= variable.getType()
    try:
        if (type.__contains__("string")):
            varValue = str(varValue)
        elif (type.__contains__("int")):
            varValue = int(varValue)
        elif (type.__contains__("float")):
            varValue = float(varValue)
    except Exception as e:
        errorText= f"for node with index {index}, variable name {varName}, provided value {varValue} is not of proper data type"
        logit(errorText, 2)
        return errorText
    n.setVariableValueByName(varName, varValue)
    val = n.getVariableValueByName(varName)
    if str(val) == str(varValue):
        return "UPDATED"
    else:
        return "ERROR"