'''
*************** Name: KS Node
*************** Part of: KS Smart Systems
*************** Author: Aleksandar Damnjanovic AKA Kind Spirit
*************** YouTube channel: Kind Spirit Technology
*************** Date: 25.05.2026.
*************** Location: Kragujevac, Serbia
*************** Description:
                    Holds code necassery for parsing kst script into programing objects.
'''

from accessories.ks_node import node
import re
from pathlib import Path
import sys, os
import support
from accessories.script_objects import *
from accessories.ks_logger import logit

def parseNodes(factory, __nodes, __globalVars):
    p = Path(support.scriptFile)
    file = None
    
    if p.exists():
        file = open(support.scriptFile, "r")
        logit("Processing script", 0)
    else:
        logit("There is no existing kst script. Can't process with parsing!!!", 1)
        logit("AAU terminated!!!", 1)
        quit()
    
    content= file.read()
    file.close()
    x= content.split("}")

    __nodes.clear()
    __globalVars.clear()

    for unit in x:

        try:
            if not (unit.__contains__("MASTER")) or (unit.__contains__("SLAVE")):
                continue 
            start = unit.index(")")
            nameIndexType = unit[0:start]
            unitIndex = int(re.search("[0-9]+", nameIndexType)[0])
            unitNameTopic = re.findall("\"[\\d\\w\\s\\.\\,\\-\\_]+\"", nameIndexType)
            unitName = unitNameTopic[0].replace("\"", "")
            unitTopic = unitNameTopic[1].replace("\"", "")
            nameIndexType = nameIndexType[nameIndexType.index(unitName)+ len(unitName):len(nameIndexType)]
            unitType = re.search("(MASTER)|(SLAVE)", nameIndexType)[0]
            slave = None
            if unitType == "SLAVE":
                slave = int(re.search("[\\d]+", nameIndexType)[0])
        except e as Exception:
            logit("Script parsing error!!! Headers not formed properly!!!", 1)
            logit("AAU terminated!!!", 1)
            quit()

        try:
            b = str(unit).index("<variables>")
            e = str(unit).index("</variables>")
            variables = unit[b+11:e]
            variables = factory.clean(variables)
            b = str(unit).index("<sensors>")
            e = str(unit).index("</sensors>")
            sensors = unit[b+10:e]
            sensors = factory.clean(sensors)
            b = str(unit).index("<elements>")
            e = str(unit).index("</elements>")
            elements = unit[b+11:e]
            elements = factory.clean(elements)
            b = str(unit).index("<programs>")
            e = str(unit).index("</programs>")
            prog = unit[b+11:e]
            prog = factory.clean(prog)
        except e as Exception:
            logit(f"Script parsing error!!! Variables, sensors, elements or programs not splited properly in node {unitIndex}!!!", 1)
            logit("AAU terminated!!!", 1)
            quit()

        vars= list()
        sens= list()
        elLists = list()
        elTrigger = list()
        elSwitch = list()
        valConditions = list()
        serials = list()
        funNames= list()
        timeLims = list()

        for var in variables.splitlines():

            try:
                type, name, value= parseVariables(var)
                var_= variable(type, name, value)
                if type.__contains__("global"):
                    gvar= globalVariable(type, name, value, unitIndex)
                    __globalVars.append(gvar)
                vars.append(var_)
            except e as Exception:
                logit(f"Variable parsing error in node {unitIndex}!!!", 1)
                logit("AAU terminated!!!", 1)
                quit()

        for sen in sensors.splitlines():

            try:
                sens.append(parseSensor(sen))
            except e as Exception:
                logit(f"Sensor parsing error in node {unitIndex}!!!", 1)
                logit("AAU terminated!!!", 1)
                quit()
        
        for el in elements.splitlines():

            try:
                if el.startswith("list"):
                    elLists.append(parseElList(el))
                elif el.startswith("trigger"):
                    elTrigger.append(parseTriggerOrSwitch(el, type = 0))
                elif el.startswith("switch"):
                    elSwitch.append(parseTriggerOrSwitch(el, type = 1))
            except e as Exception:
                logit(f"List, trigger or switch parsing error in node {unitIndex}!!!", 1)
                logit("AAU terminated!!!", 1)
                quit()
        
        try:
            l1 = prog.split(";")
            temp= list()
            for l in l1:
                if l.startswith("\n"):
                    temp.append(l[1:len(l)])
                elif l=="":
                    pass
                else:
                    temp.append(l) 
            l1= temp
            for p in l1:
                if p.__contains__("valCondition"):
                    a = parseValCondition(p)
                    if a.getFunName() != None:
                        funNames.append(a.getFunName())
                    valConditions.append(a)
                elif p.__contains__("serial"):
                    a = parseSerial(p, vars)
                    if a.getFunName() != None:
                        funNames.append(a.getFunName())
                    serials.append(a)
                elif p.__contains__("timeLim"):
                    timeLims.append(parseTimeLims(p))
        except e as Exception:
            logit(f"Program parsing error in node {unitIndex}!!!", 1)
            logit("AAU terminated!!!", 1)
            quit()

        __nodes.append(node(unitIndex, unitName, unitTopic, vars, sens, elLists, elTrigger,
                                 elSwitch, valConditions, serials, funNames, timeLims, unitType, slave))

def parseVariables(line):
    varType= None
    varName= None
    varVal= None
    line = line.replace("=", " ")
    tokens = line.split(" ")
    counter = 0

    for i in tokens:
        if i == "":
            counter += 1

    for i in range(0, counter):
        tokens.remove("")

    varType= tokens[0]
    offset = 0

    if str(varType).__contains__("global"):
        offset = 1
        varType = f"{tokens[0]} {tokens[1]}"

    varName= tokens[1 + offset]

    if varType != "array" and varType!= "global array":
        varVal= tokens[2 + offset]
    else:
        ind1 = line.index("[")
        ind2 = line.index("]")
        varVal = line[ind1:ind2+1]

    if varType=="string" or varType=="global string":
        if varVal.__contains__("\""):
            varVal= varVal.replace("\"","")
    
    return varType, varName, varVal 

def parseSensor(text):
    name = re.search("\"[a-zA-Z0-9\\s\\.\\,]+\"", text)[0]
    name= name.replace("\"","")
    idx1 = str(text).index(",")
    idx2 = str(text).index(",", idx1+1)
    index= text[idx1:idx2]
    for i in range(0, len(index)):
        index = index.replace(",","")
        index = index.replace(" ", "")
        if not index.__contains__(" ") and not index.__contains__(","):
            break
    index= int(index)
    idx1= idx2 + 1
    idx2 = str(text).index(",", idx1)
    epoh= text[idx1:idx2]
    for i in range(0, len(epoh)):
        epoh = epoh.replace(",","")
        epoh = epoh.replace(" ", "")
        if not epoh.__contains__(" ") and not epoh.__contains__(","):
            break
    idx1= idx2 + 1
    idx2 = str(text).index(")", idx1)
    result= text[idx1:idx2]
    for i in range(0, len(result)):
        result = result.replace(",","")
        result = result.replace(" ", "")
        result = result.replace(" ", "")
        if not result.__contains__(" ") and not result.__contains__(",") and not result.__contains__(")"):
            break
        
    return sensor(name, index, epoh, result)  

def parseElList(text):
    if not str(text).startswith("list"):
        return
    idx1 = str(text).index("\"") + 1
    idx2 = str(text).index("\"", idx1)
    name= text[idx1:idx2]   
    idx1 = str(text).index("," , idx2 + 1)
    idx2 = str(text).index(",", idx1 + 1)
    index= text[idx1:idx2]
    for i in range(0, len(index)):
        index = index.replace(",","")
        index = index.replace(" ", "")
        if not index.__contains__(" ") and not index.__contains__(","):
            break
    index = int(index)
    text = text[idx1 :len(text)]
     
    variables = re.findall("\\$[a-zA-Z0-9\\_]+", text)
    listValues = variables[0]
    listNames = variables[1]
    state = variables[2]
    force = variables[3]

    return elList(name, index, listValues, listNames, state, force)    

def parseTriggerOrSwitch(text, type= 0):
    ln= str(text).__len__()
    start = str(text).find("\"")
    end = str(text).find("\"", start + 1, ln)
    name = str(text)[start+1:end]
    start = str(text).find(",", end + 1, ln)
    end = str(text).find(",", start + 1, ln)
    index = str(text)[start+1:end]
    index = str(index).replace(" ", "")
    index = int(index)
    variables = re.findall("\\$[\\w]+[\\d]*", text)
    value = variables[0]
    force = variables[1]

    if type==0:
        return trigger(name, index, value, force)
    else:
        return switch(name, index, value, force) 

def parseValCondition(text):    
    fn = re.search( "=[\\s]*valCondition", text)
    
    if fn != None:
        fn= True    
    funName= None
    
    if fn==True:
        funName = re.search( "\\$[a-zA-Z0-9]+", text)
        if funName != None:
            funName = funName[0]    
    
    index= text.index("valCondition(") + 13 
    text = text[index:len(text)]
    
    if text.startswith("\n"):
        text = text[1:len(text)]
    
    if text.endswith("\n"):
        text = text[0: len(text) - 1]
    
    ind1 = text.index("\"")
    ind2 = text.index("\"", ind1 + 1)
    name = text[ind1 + 1: ind2]
    text = text[ind2: len(text)]
    ind1 = text.index(",")
    ind2 = text.index(",", ind1 + 1)
    parsing = text[ind1: ind2]
    parsing = parsing.splitlines()
    conditions = list()
    parseStatements(parsing, conditions)
    ind1 = ind2 + 1
    ind2 = len(text)
    parsing = text[ind1: ind2]
    parsing = parsing.splitlines()
    results = list()
    parseStatements(parsing, results)
    
    return valCondition(name, conditions, results , funName)    

def parseStatements(parsing, conditions):
    for l in parsing:
        condition = re.search("\\$[a-zA-Z0-9]+[\\s]*[=><]+[\\s]*(\\$[a-zA-Z0-9]+|[0-9\\.]+|[\"a-zA-Z0-9]+)", l)
        if condition != None:
            condition = condition[0]
            cs = re.search("[<>=]+", condition)[0]
            id = condition.index(cs)
            left = condition[0:id]
            if left.__contains__(" "):
                left = left.replace(" ", "")
            leftType = "var"
            if not left.startswith("$"):
                leftType = "value"
            right = condition[id+ len(cs):len(condition)]
            if right.__contains__(" "):
                right = right.replace(" ", "")
            rightType = "var"
            if not right.startswith("$"):
                rightType = "value"
            conditions.append(statement(left, leftType, right, rightType, cs))  

def parseSerial(text, vars):
    fn = re.search( "=[\\s]*serial", text)
    if fn != None:
        fn= True    
    funName= None

    if fn==True:
        funName = re.search( "\\$[a-zA-Z0-9]+", text)
        if funName != None:
            funName = funName[0]    
    
    index= text.index("serial(") + 7    
    text = text[index:len(text)]
    
    if text.startswith("\n"):
        text = text[1:len(text)]
    
    if text.endswith("\n"):
        text = text[0: len(text) - 1]
    
    ind1 = text.index(",")
    ind2 = 0
    value = text[0: ind1]
    name = None
    
    if value.__contains__("\""):
        name = re.search("\"[a-zA-Z0-9\\s]+\"", value)
        if name != None:
            name = name[0].replace("\"", "")
    else:
        name = re.search("\\$[a-zA-Z0-9]+", value)
        if name != None:
            name = name[0]
    
    ind1 = text.index(name) + len(name)
    text = text[ind1: len(text)]
    switches = re.search("\\$[a-zA-Z0-9\\_\\-]+", text)
    
    if switches != None:
        switches = switches[0]
    
    ind1 = text.index(switches) + len(switches)
    text = text[ind1: len(text)]
    swe = re.search("([\\d]+)|(\\$[a-zA-Z0-9]+)", text)
    
    if swe != None:
        swe = swe[0]    
    
    ind1 = text.index(swe) + len(swe)
    text = text[ind1: len(text)]    
    stime = re.search("([\\d]+)|(\\$[a-zA-Z0-9]+)", text)
    
    if stime != None:
        stime = stime[0]    
    
    ind1 = text.index(stime) + len(stime)
    text = text[ind1: len(text)]    
    lastIndex = re.search("([\\d]+)|(\\$[a-zA-Z0-9]+)", text)
    
    if lastIndex != None:
        lastIndex = lastIndex[0]    
    
    return serial(name, switches, swe, stime, lastIndex, funName)  

def parseTimeLims(text):
    text = text[8:len(text)]
    fun = re.search("\\$[a-zA-Z0-9]+", text)
    
    if fun != None:
        fun = fun[0]    
    
    text = text[len(fun):len(text)]
    startEnd = re.findall("(\\$[\\w\\d]+)", text)
    start = None
    end = None

    if startEnd != None:
        start = startEnd[0]
        end = startEnd[1]
    
    return timeLim(fun, start, end)