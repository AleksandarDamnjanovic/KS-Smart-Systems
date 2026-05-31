import support
import re
from accessories.ks_logger import logit
import sys
import script
import os
from accessories.script_objects import valCondition, statement

'''
    This document processes administrative instructions

1     writeVar(index, name, value)
2     changeTriggerValue(index, triggerName, triggerValue)
3     changeListValue(index, listName, listValue)
4     turnSwitch(index, switchName)
5     createVariable(index, varName, globalVar, varType, varValue)
6     removeVariable(index, varName)
7     addValConditionProgram(index, progName, numOfConditions, numOfResults, 5 arguments for every condition, 5 arguments for every result, funVariableName)
8     removeValConditionProgram(index, name)
9     addTimeLimProgram(index, funName, start, end)
10    removeTimeLimProgram(index, funName)
11    addSerialProgram(index, name, listOfSwitches, epoh, lastIndex, functionName=None)
12    removeSerialProgram(index, name)
13    getSensorReadings(ind, sensorName)
14    readVar(ind, name)
15    readNodeCount()
16    readPrograms(ind)
17    readElements(ind)
18    readSensors(ind)
19    readVariables(ind)
20    readHeader(ind)
'''

def processAdmin(text):
    message = ""

    try:
        # 📎 reads header data from node by providing index of the node throught the function
        if text.__contains__("readHeader("):
            ind = re.findall("[\\d]+", text)
            if ind != None:
                ind = int(ind[0])
                if ind > 0 and ind < len(support.factory.getNodes()) + 1:
                    message = support.factory.readHeader(ind)
                else:
                    logit(f"index {ind} received by querry, is out of limits", 2)
                    message = "--no result--"
        
        # 📎 returns entire <variable> section from the node by providing the node index
        elif text.__contains__("readVariables"):
            tokens = re.findall(r"[\$a-z0-9A-Z\.]+", text)
            ind = int(tokens[1])
            if ind != None:
                if ind > 0 and ind < len(support.factory.getNodes()) + 1:
                    message = support.factory.readVariables(ind)
                else:
                    logit(f"index {ind} received by querry, is out of limits", 2)
                    message = "--no result--"
        
        # 📎 returns entire <sensors> section from the node by providing the node index
        elif text.__contains__("readSensors("):
            ind = re.findall("[\\d]+", text)
            if ind != None:
                ind = int(ind[0])
                if ind > 0 and ind < len(support.factory.getNodes()) + 1:
                    message = support.factory.readSensors(ind)
                else:
                    logit(f"index {ind} received by querry, is out of limits", 2)
                    message = "--no result--"

        # 📎 returns entire <elements> section from the node by providing the node index
        elif text.__contains__("readElements("):
            ind = re.findall("[\\d]+", text)
            if ind != None:
                ind = int(ind[0])
                if ind > 0 and ind < len(support.factory.getNodes()) + 1:
                    message = support.factory.readElements(ind)
                else:
                    logit(f"index {ind} received by querry, is out of limits", 2)
                    message = "--no result--"

        # 📎 returns entire <programs> section from the node by providing the node index
        elif text.__contains__("readPrograms("):
            ind = re.findall("[\\d]+", text)
            if ind != None:
                ind = int(ind[0])
                if ind > 0 and ind < len(support.factory.getNodes()) + 1:
                    message = support.factory.readPrograms(ind)
                else:
                    logit(f"index {ind} received by querry, is out of limits", 2)
                    message = "--no result--"

        # 📎 returns number of nodes present in the script
        elif text.__contains__("readNodeCount("):
            message = support.factory.readNodeCount()

        # 📎 returns variable value by providing node index and variable name
        elif text.__contains__("readVariableValue("): 
            ind = int(re.findall("[\\d]+", text)[0])
            if ind != None:
                name = re.findall("\\$[a-zA-Z0-9]+", text)[0]
                if ind > 0 and ind < len(support.factory.getNodes()) + 1:
                    message = support.factory.readVar(ind, name)
                else:
                    logit(f"index {ind} received by querry, is out of limits", 2)
                    message = "--no result--"

        # 📎 this command requests two arguments, node index and sensor name
        # 📎 both arguments are forwarded to getSensorReadings function in script.py
        # 📎 the point is to get value from the particular sensor directly             
        elif text.__contains__("getSensorReadings"):
            tokens = re.findall(r"[\$a-z0-9A-Z\.]+", text)
            if tokens.__len__() != 3:
                logit(f"received message {text} in function getSensorReadings, not properly formated", 2)
                message = "--message not properly formated--"
                return message
            ind = int(tokens[1])
            if ind != None:
                sensorName = tokens[2]
                if ind > 0 and ind < len(support.factory.getNodes()) + 1:
                    message = script.getSensorReadings(ind, sensorName)
                else:
                    logit(f"index {ind} received by querry, is out of limits", 2)
                    message = "--no result--"

        # 📎 this function needs only two arguments. first is node index and second is name of serial program to be remvoed
        elif text.__contains__("removeSerialProgram"):
            tokens = re.findall(r"[\$a-z0-9A-Z\.]+", text)

            try:
                if tokens.__len__() != 3:
                    raise Exception("incorect number of arguments")

                index = int(tokens[1])
                name = tokens[2]

                if index != None:
                    if index > 0 and index < len(support.factory.getNodes()) + 1:
                        message = script.removeSerialProgram(index, name)
                    else:
                        logit(f"index {ind} received by querry, is out of limits", 2)
                        message = "--no result--"

            except Exception as e:
                logit(f"received message {text} in function removeSerialProgram is not properly formated\r\n\t{e}", 2)
                message = "--message not properly formated--"
                return message

        # 📎 this function adds serial program to program list in particular node
        # 📎 necessary arguments are node index, name, list of switches, switch epoh, last index and function name
        # 📎 time stamp is not provided as argument. it is presumed to be 0
        elif text.__contains__("addSerialProgram"):
            tokens = re.findall(r"[\$a-z0-9A-Z\.]+", text)

            try:
                if tokens.__len__() != 7:
                    raise Exception("incorect number of arguments")

                index = int(tokens[1])
                name = tokens[2]
                listOfSwitches = tokens[3]
                epoh = tokens[4]
                lastIndex = tokens[5]
                funName = tokens[6]
                if funName == "None":
                    funName = None

                if index != None:
                    if index > 0 and index < len(support.factory.getNodes()) + 1:
                        message = script.addSerialProgram(index, name, listOfSwitches, epoh, lastIndex, functionName=funName)
                    else:
                        logit(f"index {ind} received by querry, is out of limits", 2)
                        message = "--no result--"

            except Exception as e:
                logit(f"received message {text} in function addSerialProgram is not properly formated\r\n\t{e}", 2)
                message = "--message not properly formated--"
                return message

        # 📎 this function calls removeTimeLimProgram from script.py
        # 📎 necessary arguments are node index and function variable name
        elif text.__contains__("removeTimeLimProgram"):
            tokens = re.findall(r"[\$a-z0-9A-Z\.]+", text)

            try:
                if tokens.__len__() != 3:
                    raise Exception("incorect number of arguments")

                index = int(tokens[1])
                funName = tokens[2]

                if index != None:
                    if index > 0 and index < len(support.factory.getNodes()) + 1:
                        message = script.removeTimeLimProgram(index, funName)
                    else:
                        logit(f"index {ind} received by querry, is out of limits", 2)
                        message = "--no result--"

            except Exception as e:
                logit(f"received message {text} in function removeTimeLimProgram is not properly formated\r\n\t{e}", 2)
                message = "--message not properly formated--"
                return message

        # 📎 this function calls functon with the same name from script.py and passes all of arguments
        # 📎 function name variable must be already existing in order for this program to work
        # 📎 therefore is recomended to call variable creating function or manually changing the script before
        # 📎 calling addTimeLimProgram function
        elif text.__contains__("addTimeLimProgram"):
            tokens = re.findall(r"[\$a-z0-9A-Z\.]+", text)

            try:
                if tokens.__len__() != 5:
                    raise Exception("incorect number of arguments")

                index = int(tokens[1])
                funName = tokens[2]
                start = tokens[3]
                end = tokens[4]

                if index != None:
                    if index > 0 and index < len(support.factory.getNodes()) + 1:
                        message = script.addTimeLimProgram(index, funName, start, end)
                    else:
                        logit(f"index {ind} received by querry, is out of limits", 2)
                        message = "--no result--"

            except Exception as e:
                logit(f"received message {text} in function addTimeLimProgram is not properly formated\r\n\t{e}", 2)
                message = "--message not properly formated--"
                return message

        # 📎 this function removes val condition program from the node with provided index by function name
        # 📎 first argument is node index and second argument is val condition program name that should be removed
        elif text.__contains__("removeValConditionProgram"):
            tokens = re.findall(r"[\$a-z0-9A-Z\.]+", text)
            
            try:
                index = int(tokens[1])
                name = tokens[2]

                if index != None:
                    if index > 0 and index < len(support.factory.getNodes()) + 1:
                        message = script.removeValConditionProgram(index, name)
                    else:
                        logit(f"index {ind} received by querry, is out of limits", 2)
                        message = "--no result--"

            except Exception as e:
                logit(f"received message {text} in function removeValConditionProgram is not properly formated", 2)
                message = "--message not properly formated--"
                return message

        # 📎 provided arguments are node index and variable name, number of conditions and number of results
        # 📎 then for every condition we are going to have 5 arguments= left variable, left variable type,
        # 📎 right side variable, right side variable type and sign
        # 📎 those 5 arguments are going to represent condition in script like $a, ==, $b (in script $a == $b) 
        # 📎 for every result, we are also going to have 5 arguments in the same fashion like in previous case
        # 📎 the last argument is function name. if you don't want function name, you will have to pass None
        # 📎 at the end, with all arguments reformed, function addValConditionProgran from script.py will be called
        elif text.__contains__("addValConditionProgram"):
            tokens = re.findall(r"[\$a-z0-9A-Z\.=><]+", text)
            
            try:
                index = int(tokens[1])
                varName = str(tokens[2])
                conditions = int(tokens[3])
                results = int(tokens[4])
                aditional = (conditions + results) * 5
            except Exception as e:
                logit(f"received message {text} in function removeVariable, not properly formated", 2)
                message = "--message not properly formated--"
                return message

            if tokens.__len__() != 6 + aditional:
                logit(f"received message {text} in function removeVariable, not properly formated", 2)
                message = "--message not properly formated--"
                return message

            cnd = list()
            res = list()
            last = 0
            for i in range(conditions):
                a = i * 5
                leftVar = tokens[5 + a]
                leftType = tokens[6 + a]
                rightVar = tokens[7 + a]
                rightType = tokens[8 + a]
                cs = tokens[9 + a]
                last = 9 + a + 1
                s = statement(leftVar, leftType, rightVar, rightType, cs)
                cnd.append(s)

            last1 = 0
            for i in range(results):
                a = i * 5
                leftVar = tokens[last + a]
                leftType = tokens[last + 1 + a]
                rightVar = tokens[last + 2 + a]
                rightType = tokens[last + 3 + a]
                cs = tokens[last + 4 + a]
                last1 = last + 5 + a
                s = statement(leftVar, leftType, rightVar, rightType, cs)
                res.append(s)

            funName = ""
            if tokens[last1]=="None":
                funName = None
            else:
                funName = tokens[last1]

            vc = valCondition(varName, cnd, res, funName= funName)
            
            if index != None:
                if index > 0 and index < len(support.factory.getNodes()) + 1:
                    message = script.addValConditionProgram(index, vc)
                else:
                    logit(f"index {ind} received by querry, is out of limits", 2)
                    message = "--no result--"

        # 📎 provided arguments are node index and variable name
        # 📎 both arguments are forwarded to removeVariable function in script.py
        elif text.__contains__("removeVariable"):
            tokens = re.findall(r"[\$a-z0-9A-Z\.]+", text)
            if tokens.__len__() != 3:
                logit(f"received message {text} in function removeVariable, not properly formated", 2)
                message = "--message not properly formated--"
                return message
            index = int(tokens[1])
            varName = str(tokens[2])
            if index != None:
                if index > 0 and index < len(support.factory.getNodes()) + 1:
                    message = script.removeVariable(index, varName)
                else:
                    logit(f"index {ind} received by querry, is out of limits", 2)
                    message = "--no result--"

        # 📎 provided arguments are node index, variable name, boolean that defines whether variable is global or not
        # 📎 variable type and variable value
        # 📎 both arguments are forwarded to createVariable function in script.py
        elif text.__contains__("createVariable"):
            tokens = re.findall(r"[\$a-z0-9A-Z\.]+", text)
            if tokens.__len__() != 6:
                logit(f"received message {text} in function createVariable, not properly formated", 2)
                message = "--message not properly formated--"
                return message
            index = int(tokens[1])
            varName = str(tokens[2])
            globalVar = bool(tokens[3])
            varType = str(tokens[4])
            varValue = str(tokens[5])
            if index != None:
                if index > 0 and index < len(support.factory.getNodes()) + 1:
                    message = script.createVariable(index, varName, globalVar, varType, varValue)
                else:
                    logit(f"index {ind} received by querry, is out of limits", 2)
                    message = "--no result--"

        # 📎 this command requests two arguments, node index and switch name
        # 📎 both arguments are forwarded to turnSwitch function in script.py
        elif text.__contains__("turnSwitch("):
            tokens = re.findall(r"[\$a-z0-9A-Z\.]+", text)
            if tokens.__len__() != 3:
                logit(f"received message {text} in function turnSwitch, not properly formated", 2)
                message = "--message not properly formated--"
                return message
            ind = int(tokens[1])
            if ind != None:
                switchName = tokens[2]
                if ind > 0 and ind < len(support.factory.getNodes()) + 1:
                    message = script.turnSwitch(ind, switchName)
                else:
                    logit(f"index {ind} received by querry, is out of limits", 2)
                    message = "--no result--"

        # 📎 this command requests three arguments, node index, list name and index of value to be selected
        # 📎 all arguments are forwarded to changeListValue function in script.py
        elif text.__contains__("changeListValue"):
            tokens = re.findall(r"[\$a-z0-9A-Z\.]+", text)
            if tokens.__len__() != 4:
                logit(f"received message {text} in function changeListValue, not properly formated", 2)
                message = "--message not properly formated--"
                return message
            ind = int(tokens[1])
            if ind != None:
                listName = tokens[2]
                listValue = tokens[3]
                if ind > 0 and ind < len(support.factory.getNodes()) + 1:
                    message = script.changeListValue(ind, listName, listValue)
                else:
                    logit(f"index {ind} received by querry, is out of limits", 2)
                    message = "--no result--"

        # 📎 this command requests three arguments, node index and trigger name, and a new value to be set
        # 📎 all of arguments are forwarded to changeTriggerValue function in script.py
        elif text.__contains__("changeTriggerValue"):
            tokens = re.findall(r"[\$a-z0-9A-Z\.]+", text)
            if tokens.__len__() != 4:
                logit(f"received message {text} in function changeTriggerValue, not properly formated", 2)
                message = "--message not properly formated--"
                return message
            ind = int(tokens[1])
            if ind != None:
                triggerName = tokens[2]
                triggerValue = tokens[3]
                if ind > 0 and ind < len(support.factory.getNodes()) + 1:
                    message = script.changeTriggerValue(ind, triggerName, triggerValue)
                else:
                    logit(f"index {ind} received by querry, is out of limits", 2)
                    message = "--no result--"

        # 📎 gets message that contains writeVar with 3 arguments.
        # 📎 first argument is index of the node, second is variable name and third is variable value
        # 📎 all of 3 arguments are sent to function writeVar in script.py            
        elif text.__contains__("writeVar("): 
            tokens = re.findall(r"[\$a-z0-9A-Z\.]+", text)
            if tokens.__len__() != 4:
                logit(f"received message {text} in function writeVar, not properly formated", 2)
                message = "--message not properly formated--"
                return message
            ind = int(tokens[1])
            if ind != None:
                vn = tokens[2]
                vv = tokens[3]
                if ind > 0 and ind < len(support.factory.getNodes()) + 1:
                    message = script.writeVar(ind, vn, vv)
                else:
                    logit(f"index {ind} received by querry, is out of limits", 2)
                    message = "--no result--"
        elif text.__contains__("readAll("):
            message = support.factory.readAll()

        if message != "--no result--":
            message = f"--response--\n{message}\n--end response--"

    except Exception as e:
        logit(f"--onProcessAdmin-- error message:{e}", 2)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

    return message