'''
*************** Name: KS Node
*************** Part of: KS Smart Systems
*************** Author: Aleksandar Damnjanovic AKA Kind Spirit
*************** YouTube channel: Kind Spirit Technology
*************** Date: 26.11.2024.
*************** Location: Kragujevac, Serbia
'''

import re
import datetime
import time
import support
from pathlib import Path
import sys, os

class node:
    def __init__(self, nodeIndex, nodeName, unitTopic, variables, sensors, elementLists, elementTriggers,  
                elementSwitches, valConditions, serials, funNames, timeLimits, unitType, slave):
        self.__nodeIdex = nodeIndex
        self.__nodeName = nodeName
        self.__unitTopic = unitTopic
        self.__vars= variables
        self.__sens= sensors
        self.__elLists = elementLists
        self.__elTrigger = elementTriggers
        self.__elSwitch = elementSwitches
        self.__valConditions = valConditions
        self.__serials = serials
        self.__funNames= funNames
        self.__timeLims = timeLimits
        self.__unitType = unitType
        self.__slave = slave
        self.__presence = False
        self.__presenceTimeStamp = 0
        self.resetEpoh()

    def resetEpoh(self):
        self.__nodeEpoh = 24 * 60 * 60

    def getTopic(self):
        return self.__unitTopic

    def setPresenceTimeStamp(self, value):
        self.__presenceTimeStamp = value

    def getPresenceTimeStamp(self):
        return self.__presenceTimeStamp

    def getPresence(self):
        return self.__presence
    
    def setPresence(self, value):
        self.__presence = value
        if value== True:
            self.setPresenceTimeStamp(round(time.time()))

    def getType(self):
        return self.__unitType
    
    def getSlave(self):
        return self.__slave

    def getNodeEpoh(self):
        return self.__nodeEpoh

    def getGlobalVariables(self):
        return self.__globalVariables

    def getNodeName(self):
        return self.__nodeName
    
    def getNodeIndex(self):
        return self.__nodeIdex

    def getVariables(self):
        return self.__vars

    def getSensors(self):
        return self.__sens

    def getElementLists(self):
        return self.__elLists
    
    def getElementTriggers(self):
        return self.__elTrigger
    
    def getElementSwitches(self):
        return self.__elSwitch
    
    def getValueConditions(self):
        return self.__valConditions

    def getSerials(self):
        return self.__serials

    def getFunctionNames(self):
        return self.__funNames
    
    def getTimeLimits(self):
        return self.__timeLims
    
    def getGlobalPair(self, varName):
        index = None
        name = None

        res = re.findall("\\$[0-9]+\\$", varName)
        if len(res) > 0:
            res = varName.split("$")
            for i in range(0, len(res)):
                if list(res).__contains__(""):
                    res.remove("")
                if list(res).__contains__(" "):
                    res.remove(" ")
            index = int(res[0])
            name = res[1]

        return index, name

    #If returns None, it means that variable name doesn't exist
    #in better words, name is good for the taking
    def getVariableValueByName(self, name):
        ind, nm = self.getGlobalPair(name)
        
        if ind == None:
            for v in self.__vars:
                if v.getName() == name:
                    return v.getValue()
        else:
            for v in support.factory.getGlobalVars():
                if v.getNodeIndex() == ind and v.getName() == nm:
                    return v.getValue()
        return None

    def setVariableValueByName(self, name, value):

        ind, nm = self.getGlobalPair(name)

        if ind == None:
            for v in self.__vars:
                if v.getName() == name:
                    v.setValue(value)
                    break
            for v in support.factory.getGlobalVars():
                if v.getNodeIndex()== self.getNodeIndex():
                    if v.getName() == name:
                        v.setValue(value)
                        break
        else:
            name = f"${nm}"
            for v in support.factory.getGlobalVars():
                a = v.getNodeIndex()
                if v.getNodeIndex() == ind and v.getName() == name:
                    v.setValue(value)
                    break
            for n in support.factory.getNodes():
                if n.getNodeIndex() == ind:
                    for v in n.getVariables():
                        if v.getName() == name:
                            v.setValue(value)
                            break                            

    def processSwitches(self):
        if self.getNodeIndex() == 7:
            pass
        for s in self.getElementSwitches():
            val = self.getVariableValueByName(s.getValue())
            force = self.getVariableValueByName(s.getForce())
            v= None
            if force == 1:
                v = force
            else:
                v = val
            message = f"I_{self.getNodeIndex()}_C_{s.getIndex()}_{v}"
            support.factory.appendMessage(message)

    def processTriggers(self):
        for s in self.getElementTriggers():
            val = str(self.getVariableValueByName(s.getValue())).replace("\"", "")
            force = str(self.getVariableValueByName(s.getForce())).replace("\"", "")
            v= None
            if force != "":
                v = force
            else:
                v = val
            message = f"I_{self.getNodeIndex()}_T_{s.getIndex()}_{v}"
            support.factory.appendMessage(message)

    def processLists(self):

        for s in self.getElementLists():
            val = self.getVariableValueByName(s.getState())
            force = str(self.getVariableValueByName(s.getForce())).replace("\"", "")
            elements = self.getVariableValueByName(s.getListValues())
            v= None
            if force != "":
                v = int(force)
            else:
                v = val
            if v < len(elements):
                message = f"I_{self.getNodeIndex()}_T_{s.getIndex()}_{v}"
                support.factory.appendMessage(message)

    def processSensors(self):

        for s in self.getSensors():
            if s.getEpoh() != None:
                if self.__nodeEpoh > self.getVariableValueByName(s.getEpoh()):
                    self.__nodeEpoh = self.getVariableValueByName(s.getEpoh())
                message = f"I_{self.getNodeIndex()}_S_{s.getIndex()}"
                support.factory.appendMessage(message)
                break

    def processNode(self):
        self.resetEpoh()

        for v in self.__vars:
            if v.getType() == "fun":
                v.setValue(1)

        self.processTimeLimits()
        self.processValConditions()
        self.processSerial()
        self.processSwitches()
        self.processTriggers()
        self.processLists()
        self.processSensors()

    def changeSwitch(self, s):
        st = self.getVariableValueByName(s.getSwitchTime())
        ep = self.getVariableValueByName(s.getEpoh())
        a= st + ep
        b= round(time.time())
        newVal = a - b

        if a > b:
            if self.__nodeEpoh > newVal:
                self.__nodeEpoh = newVal

        if b >= a:
            self.setVariableValueByName(s.getSwitchTime(), b)
            if self.__nodeEpoh > self.getVariableValueByName(s.getEpoh()):
                self.__nodeEpoh = self.getVariableValueByName(s.getEpoh())
            i = self.getVariableValueByName(s.getLastIndex())
            l = len(self.getVariableValueByName(s.getElements()))
            if i == l - 1:
                self.setVariableValueByName(s.getLastIndex(), 0)
            else:
                self.setVariableValueByName(s.getLastIndex() ,self.getVariableValueByName(s.getLastIndex()) + 1)
            
        ind = self.getVariableValueByName(s.getLastIndex())
        working= self.getVariableValueByName(s.getElements())[ind]

        self.setVariableValueByName(working, 1)
    
    def processSerial(self):
        t = round(time.time())
        for s in self.__serials:
            if self.getVariableValueByName(s.getSwitchTime()) == 0:
                self.setVariableValueByName(s.getSwitchTime(), t)
            if s.getFunName() != None:
                if self.getVariableValueByName(s.getFunName())==1:
                    self.changeSwitch(s)
            else:
                self.changeSwitch(s)

    def processTimeLimits(self):
        for tl in self.__timeLims:
            if(self.testTime(tl)==False):
                self.setFunNameValue(tl.getFunction(), 0)

    def parseValueFromStatement(self, value, type):
        val = None
        if type== "var":
            val = self.getVariableValueByName(value)
        else:
            testFloat = re.findall("[0-9]+\\.[0-9]+", value)
            testInt = re.findall("[0-9]+", value)
            testString = re.findall("\"[\\d\\w\\s]\"", value)
            if len(testFloat)>0:
                val = float(testFloat[0])
            elif len(testInt)>0:
                val = int(testInt[0])
            elif len(testString)>0:
                val = str(testString[0])
        return val

    def processValConditions(self):
        
        for v in self.getValueConditions():
            condition = True

            if v.getFunName() != None:
                if self.getVariableValueByName(v.getFunName()) != 1:
                    continue
            
            for s in v.getConditions():
                left = self.parseValueFromStatement(s.getLeftSide(), s.getLeftType())
                right = self.parseValueFromStatement(s.getRightSide(), s.getRightType())

                if s.getCase() == "=" or s.getCase()== "==":
                    if left != right:
                        condition = False
                        break
                if s.getCase() == ">":
                    if left <= right:
                        condition = False
                        break
                if s.getCase() == "<":
                    if left >= right:
                        condition = False
                        break

            if condition == False:
                continue
            else:
                for r in v.getResult():
                    right = self.parseValueFromStatement(r.getRightSide(), r.getRightType())
                    if r.getCase() == "=" or r.getCase()== "==":
                        self.setVariableValueByName(r.getLeftSide(), right)
                    else:
                        print(f"Sintax error function {v.getName()}")

    def setFunNameValue(self, funName, newValue):
        for v in self.__vars:
            if v.getName() == funName:
                v.setValue(newValue)
                break

    def testTime(self, timeLimFun):
        s= timeLimFun.getStart()
        s= self.getVariableValueByName(s)
        e= timeLimFun.getEnd()
        e= self.getVariableValueByName(e)
        
        s= str(s).replace("\"", "")
        e= str(e).replace("\"", "")
        s = s.split(":")
        e = e.split(":") 
        
        s_hour= int(s[0])
        s_min = int(s[1]) 
        e_hour= int(e[0])
        e_min = int(e[1])

        start = datetime.datetime(2000, 1, 1, hour=s_hour, minute= s_min)
        end = datetime.datetime(2000, 1, 1, hour=e_hour, minute= e_min)
        st= start.hour *60*60 + start.minute *60
        en= end.hour *60*60 + end.minute *60
        n= datetime.datetime.now()
        nowTime= n.hour *60*60 + n.minute *60 + n.second
        condition= False
        epoh= 0
        if st<=en:
            if nowTime == en:
                epoh = 24*60*60 - nowTime + st
            elif nowTime>=st and nowTime < en:
                condition = True
                epoh = en - nowTime
            else:
                if nowTime < st:
                    epoh = st - nowTime
                if nowTime > en:
                    epoh = 24*60*60 - nowTime + st
        else:
            if nowTime == st:
                condition = True
                epoh = 24*60*60 - nowTime + en
            elif nowTime > st or nowTime < en:
                condition = True
                if nowTime > st:
                    epoh = 24*60*60 - nowTime + en
                if nowTime < en:
                    epoh = en - nowTime
            else:
                epoh= st - nowTime

        if epoh < self.__nodeEpoh:
            self.__nodeEpoh = epoh

        return condition

class timeLim:
    def __init__(self, function, start, end):
        self.__function = function
        self.__start = start
        self.__end = end

    def getFunction(self):
        return self.__function
    
    def getStart(self):
        return self.__start
    
    def getEnd(self):
        return self.__end

class serial():
    def __init__(self, name, elements, epoh, switchTime, lastIndex, funName= None):
        self.__name = name
        self.__elements = elements
        self.__epoh = epoh
        self.__switchTime = switchTime
        self.__lastIndex = lastIndex
        self.__funName = funName
    
    def getName(self):
        return self.__name
    
    def getElements(self):
        return self.__elements
    
    def getEpoh(self):
        return self.__epoh
    
    def getSwitchTime(self):
        return self.__switchTime
    
    def getLastIndex(self):
        return self.__lastIndex
    
    def getFunName(self):
        return self.__funName
    
    def setLastIndex(self, index):
        self.__lastIndex = index

    def setSwitchTime(self, t):
        self.__switchTime = t

class valCondition():
    def __init__(self, name, conditions, result, funName= None):
        self.__name = name
        self.__conditions = conditions
        self.__result = result
        self.__funName = funName
    
    def getName(self):
        return self.__name
    
    def getConditions(self):
        return self.__conditions
    
    def getResult(self):
        return self.__result
    
    def getFunName(self):
        return self.__funName

class statement:
    def __init__(self, leftSide, leftType, rightSide, rightType, case):
        self.__leftSide = leftSide
        self.__leftType = leftType
        self.__rightSide = rightSide
        self.__rightType = rightType
        self.__case = case
    
    def getLeftSide(self):
        return self.__leftSide
    
    def getLeftType(self):
        return self.__leftType
    
    def getRightSide(self):
        return self.__rightSide
    
    def getRightType(self):
        return self.__rightType
    
    def getCase(self):
        return self.__case

class trigger:
    def __init__(self, name, index, value, force):
        self.__name = name
        self.__index = index
        self.__value = value
        self.__force = force

    def getName(self):
        return self.__name
    
    def getIndex(self):
        return self.__index
    
    def getValue(self):
        return self.__value
    
    def getForce(self):
        return self.__force
    
class switch:
    def __init__(self, name, index, value, force):
        self.__name = name
        self.__index = index
        self.__value = value
        self.__force = force

    def getName(self):
        return self.__name
    
    def getIndex(self):
        return self.__index
    
    def getValue(self):
        return self.__value

    def getForce(self):
        return self.__force

class elList:
    def __init__(self, name, index, listValues, listNames, state, force):
        self.__name = name
        self.__index = index
        self.__listValues = listValues
        if listNames == "NULL":
            self.__listNames = None
        else:
            self.__listNames = listNames
        self.__state = state
        self.__force = force

    def getName(self):
        return self.__name
    
    def getIndex(self):
        return self.__index
    
    def getListValues(self):
        return self.__listValues
    
    def getListNames(self):
        return self.__listNames
    
    def getState(self):
        return self.__state
    
    def getForce(self):
        return self.__force

class sensor:
    def __init__(self, name, index, epoh, readings):
        self.__name = name
        self.__index = index
        if epoh == "NULL":
            self.__epoh = None
        else:
            self.__epoh = epoh
        self.__readings = readings

    def getName(self):
        return self.__name
    
    def getIndex(self):
        return self.__index
    
    def getEpoh(self):
        return self.__epoh
    
    def getReadings(self):
        return self.__readings

class variable:
    def __init__(self, type, name, value):
        self.__type = type
        self.__name = name
        self.setValue(value)

    def getType(self):
        return self.__type
    
    def getName(self):
        return self.__name
    
    def getValue(self):
        return self.__value
    
    def setValue(self, value):
        if(self.__type.__contains__("int")):
            self.__value = int(value)
        elif(self.__type.__contains__("float")):
            self.__value = float(value)
        elif(self.__type.__contains__("string")):
            self.__value = value
        elif(self.__type.__contains__("array")):
            v = list()
            e= re.findall("[a-zA-Z0-9\\$\\_\\-\\%\"]+", value)
            if e[0].__contains__("-"):
                n = re.findall("[\\d]+", e[0])
                n = int(n[1])
                nn = list()
                for i in range(0, n+1):
                    nn.append(i)
                self.__value = nn
            else:
                for ee in e:
                    if str(ee).__contains__("\""):
                        ee = str(ee).replace("\"", "")
                    v.append(ee)
                self.__value = v
        elif(self.__type.__contains__("fun")):
            self.__value = int(value)

class globalVariable(variable):
    def __init__(self, type, name, value, nodeIndex):
        super().__init__(type, name, value)
        self.__nodeIndex = nodeIndex

    def getNodeIndex(self):
        return self.__nodeIndex

class nodeFactory:
    def __init__(self):
        self.__nodes = list()
        self.__globalVars = list()
        self.__messages = list()
        self.restartEpoh()

    def restartEpoh(self):
        self.__factoryEpoh = 24 * 60 * 60

    def updateScript(self):
        content = self.readAll()
        f = open(support.scriptFile, "w")
        f.write(content)
        f.close()

    def readVar(self, ind, name):
        n= self.getNodeByIndex(ind)
        val = n.getVariableValueByName(name)
        return val

    def readVariables(self, index):
        n = self.getNodeByIndex(index)
        varText= ""
        for v in n.getVariables():
                v1 = v.getValue()
                if v1 == "":
                    v1="\"\""
                if v.getType() == "string" or v.getType() == "global string":
                    if v1.__contains__("\"") != True:
                        v1 = f"\"{v1}\""
                elif v.getType() == "array" or v.getType() == "global array":
                    v2 = "["

                    test = False
                    try:
                        v11 = int(v1[0])
                        test= True
                    except Exception as e:
                        pass

                    if test and len(v1)>10:
                        v2 = f"{v2}{v1[0]}-{v1[len(v1)-1]}"
                    else:
                        for i in range(0, len(v1)):
                            v11 = v1[i]
                            if v11.startswith("$"):
                                pass
                            else:
                                test = False
                                try:
                                    v11 = int(v1[i])
                                    test= True
                                except Exception as e:
                                    pass
                                if test != True:
                                    v11 = f"\"{v1[i]}\""
                            v2 = f"{v2}{v11}"
                            if i != len(v1) - 1:
                                v2 = f"{v2}, "
                    v2 = f"{v2}]"
                    v1 = v2
                varText = f"{varText}\t\t{v.getType()} {v.getName()} = {v1}\n" 
        return f"{varText}"

    def readHeader(self, index):
        for n in self.__nodes:
            if n.getNodeIndex() == index:
                return f"{n.getNodeIndex()}(\"{n.getNodeName()}\", \"{n.getTopic()}\", [{n.getType()}]"

    def readSensors(self, index):
        for n in self.__nodes:
            if n.getNodeIndex() != index:
                continue
            varText = ""
            for s in n.getSensors():
                ep = s.getEpoh()
                if ep == None:
                    ep = "NULL"
                varText = f"{varText}\t\tsensor(\"{s.getName()}\", {s.getIndex()}, {ep}, {s.getReadings()});\n"
            return f"{varText}"
        
    def readElements(self, index):
        for n in self.__nodes:
            if n.getNodeIndex() != index:
                continue
            varText = ""

            for l in n.getElementLists():
                varText = f"{varText}\t\tlist(\"{l.getName()}\", {l.getIndex()}, {l.getListValues()}, {l.getListNames()}, {l.getState()}, {l.getForce()});\n"
            
            for l in n.getElementTriggers():
                varText = f"{varText}\t\ttrigger(\"{l.getName()}\", {l.getIndex()}, {l.getValue()}, {l.getForce()});\n"
            
            for l in n.getElementSwitches():
                varText = f"{varText}\t\tswitch(\"{l.getName()}\", {l.getIndex()}, {l.getValue()}, {l.getForce()});\n"
        
            return f"{varText}"
        
    def readNodeCount(self):
        return f"{str(support.factory.getNodes().__len__())}"
        
    def readPrograms(self, index):
        for n in self.__nodes:
            if n.getNodeIndex() != index:
                continue
            text = ""
            varText = ""
            for v in n.getValueConditions():
                if v.getFunName()!= None:
                    varText= f"\t\t{v.getFunName()} = valCondition(\n\t\t\t\"{v.getName()}\",\n"
                else:
                    varText= f"\t\tvalCondition(\n\t\t\t\"{v.getName()}\",\n"
                for i in range(0, len(v.getConditions())):
                    con = v.getConditions()[i]
                    varText = f"{varText}\t\t\t{con.getLeftSide()} {con.getCase()} {con.getRightSide()}"
                    if i == len(v.getConditions()) - 1:
                        varText = f"{varText},\n"
                    elif i < len(v.getConditions()) - 1:
                        varText = f"{varText}\n"
                for i in range(0, len(v.getResult())):
                    con = v.getResult()[i]
                    varText = f"{varText}\t\t\t{con.getLeftSide()} {con.getCase()} {con.getRightSide()}"
                    if i == len(v.getResult()) - 1:
                        varText = f"{varText});\n"
                    elif i < len(v.getResult()) - 1:
                        varText = f"{varText}\n"
                text = f"{text}{varText}"
                varText = ""
            varText = ""
            for v in n.getSerials():
                if v.getFunName()!= None:
                    varText= f"\t\t{v.getFunName()} = serial(\"{v.getName()}\", "
                else:
                    varText= f"\t\tserial(\"{v.getName()}\", "
                varText = f"{varText}{v.getElements()}, {v.getEpoh()}, {v.getSwitchTime()}, {v.getLastIndex()});"
                text = f"{text}{varText}\n"
                varText= ""
            varText = ""
            for v in n.getTimeLimits():
                varText= f"\t\ttimeLim({v.getFunction()}, {v.getStart()}, {v.getEnd()});\n"
                text = f"{text}{varText}"
                varText= ""

            return f"{text}"

    def readAll(self):
        content = ""
        try:
            for n in range(1, self.__nodes.__len__()+1):
                text= self.readHeader(n)
                text = text + "){\n\t<variables>\n"
                varText = ""
                varText = self.readVariables(n)
                text = f"{text}{varText}\t</variables>\n\n\t<sensors>\n"
                varText = ""
                varText = self.readSensors(n)
                text = f"{text}{varText}\t</sensors>\n\n\t<elements>\n"
                varText = ""
                varText = self.readElements(n)
                text = f"{text}{varText}\t</elements>\n\n\t<programs>\n"
                varText = ""
                varText = self.readPrograms(n)
                text = f"{text}\t</programs>\n"
                text = text + "}\n"

                content = f"{content}{text}\n"
                text= ""
        except Exception as e:
            print(f"--onReadAll-- error message:{e}")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

        return content
    
    def getVariableByReference(self, nodeIndex, elType, elIndex, force= False):
        n = self.getNodeByIndex(nodeIndex)
        v = None
        v1 = None
        if elType == "C":
            vg = n.getElementSwitches()
            for vv in vg:
                if vv.getIndex() == elIndex:
                    if force==False:
                        v = vv.getValue()
                    else:
                        v = vv.getForce()
                    break
        elif elType == "T":
            vg= n.getElementTriggers()
            for vv in vg:
                if vv.getIndex() == elIndex:
                    if force==False:
                        v = vv.getValue()
                    else:
                        v = vv.getForce()
                    break
            if v == None:
                vg= n.getElementLists()
                for vv in vg:
                    if vv.getIndex() == elIndex:
                        if force==False:
                            v1= vv.getState()
                        else:
                            v1 = vv.getForce()
                        break
                v= v1
        elif elType == "S" or elType == "R":
            vg= n.getSensors()
            for vv in vg:
                if vv.getIndex() == elIndex:
                    v = vv.getReadings()
                    break
        return v

    def setNodePresenceByIndex(self, index, value):
        for n in self.__nodes:
            if n.getNodeIndex() == index:
                n.setPresence(value)
                return True
        return False

    def getNodeByIndex(self, index):
        for n in self.__nodes:
            if n.getNodeIndex() == index:
                return n

    def processConfirmation(self, text):
        valid = False
        demandUpdate = -1
        __tokens= text.split("_")
        __tokens= list(filter(None, __tokens))

        if __tokens[0]=="I" or __tokens[0]== "Q":
            return

        __nodeIndex = int(__tokens[1])
        presence= self.setNodePresenceByIndex(__nodeIndex , True)
        n= self.getNodeByIndex(__nodeIndex)
        if n != None:
            n.setPresenceTimeStamp(round(time.time()))

        try:
            if __tokens[0] == "Ci" or __tokens[0] == "Cr":

                value = self.getVariableByReference(__nodeIndex, __tokens[2], int(__tokens[3]))
                varName = value
                value = n.getVariableValueByName(value)
                force = None
                if __tokens[0] == "Ci":
                    force = self.getVariableByReference(__nodeIndex, __tokens[2], int(__tokens[3]), True)
                    force = n.getVariableValueByName(force)
                
                conf = None
                if __tokens[2] == "C":
                    conf = int(__tokens[4])
                elif __tokens[2] == "T":
                    conf = __tokens[4]
                elif __tokens[2] == "S" or __tokens[2] == "R":
                    conf = float(__tokens[4])    

                if __tokens[0] == "Ci":
                    if __tokens[2]== "C":
                        if force == 1 and conf == 1:
                            valid = True
                        elif force == 0 and value == conf:
                            valid = True
                    elif __tokens[2] == "T":
                        if str(force) != "" and str(conf) == str(force):
                            valid = True
                        elif str(force) == "" and str(value) == str(conf):
                            valid = True
                elif __tokens[0] == "Cr":
                    previous = n.getVariableValueByName(varName)
                    if conf == previous:
                        valid = True
                    else:
                        n.setVariableValueByName(varName, conf)
                        valid = False
                        demandUpdate = __nodeIndex
            elif __tokens[0] == "Cq":
                valid = True
                demandUpdate = __nodeIndex
        except Exception as e:
            print(f"--processing confirmation-- error message:{e}")

        return valid, demandUpdate

    def calculateFactoryEpoh(self):
        self.restartEpoh()
        for n in self.getNodes():
            if self.__factoryEpoh > n.getNodeEpoh():
                self.__factoryEpoh = n.getNodeEpoh()

    def getFactoryEpoh(self):
        return self.__factoryEpoh

    def getMessagesByIndex(self, index):
        messages = list()
        for m in self.getMessages():
            mm = str(m).split("_")
            mm = int(mm[1])
            if mm == index:
                messages.append(m)
        return messages

    def packMessages(self):
        temp = list()
        for n in self.getNodes():
            ind = n.getNodeIndex()
            message = ""
            messages = self.getMessagesByIndex(ind)
            delim = ""
            for m in messages:
                message = f"{message}{delim}{m}"
                if delim == "":
                    delim = " "
            temp.append(message)
        self.__messages = temp

    def clearMessages(self):
        self.__messages.clear()

    def getMessages(self):
        return self.__messages
    
    def setMessages(self, messages):
        self.__messages = messages

    def appendMessage(self, message):
        self.__messages.append(message)

    def getGlobalVars(self):
        return self.__globalVars

    def clean(self, text):
        temp= ""
        lines= text.splitlines()
        for line in lines:  
            if line.strip():
                line = " ".join(line.split())
                if temp != "":
                    temp = temp + "\n" + line
                else:
                    temp = line

        return temp     

    def parseVariables(self, line):
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

    def parseSensor(self, text):
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

    def parseElList(self, text):
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

    def parseTriggerOrSwitch(self, text, type= 0):
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

    def parseValCondition(self, text):    

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
        self.parseStatements(parsing, conditions)
        ind1 = ind2 + 1
        ind2 = len(text)
        parsing = text[ind1: ind2]
        parsing = parsing.splitlines()
        results = list()
        self.parseStatements(parsing, results)
        return valCondition(name, conditions, results , funName)    

    def parseStatements(self, parsing, conditions):
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

    def parseSerial(self, text, vars):
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

    def parseTimeLims(self, text):
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

    def buildNodes(self):

        p = Path(support.scriptFile)
        backup = Path(support.backupScript)
        
        file = None
        if p.exists():
            file = open(support.scriptFile, "r")
            print("--processing existing script--")
        elif backup.exists():
            file = open(support.backupScript, "r")
            print("--main script doesn't exist-- proceeding with reading of backup script")
        else:
            print("--error reading script-- there is no existing script")

        content= file.read()
        file.close()
        x= content.split("}")

        self.__nodes.clear()
        self.__globalVars.clear()
        for unit in x:
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

            b = str(unit).index("<variables>")
            e = str(unit).index("</variables>")

            variables = unit[b+11:e]
            variables = self.clean(variables)

            b = str(unit).index("<sensors>")
            e = str(unit).index("</sensors>")

            sensors = unit[b+10:e]
            sensors = self.clean(sensors)

            b = str(unit).index("<elements>")
            e = str(unit).index("</elements>")

            elements = unit[b+11:e]
            elements = self.clean(elements)

            b = str(unit).index("<programs>")
            e = str(unit).index("</programs>")

            prog = unit[b+11:e]
            prog = self.clean(prog)

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
                type, name, value= self.parseVariables(var)
                var_= variable(type, name, value)
                if type.__contains__("global"):
                    gvar= globalVariable(type, name, value, unitIndex)
                    self.__globalVars.append(gvar)
                vars.append(var_)

            for sen in sensors.splitlines():
                sens.append(self.parseSensor(sen))

            for el in elements.splitlines():
                if el.startswith("list"):
                    elLists.append(self.parseElList(el))
                elif el.startswith("trigger"):
                    elTrigger.append(self.parseTriggerOrSwitch(el, type = 0))
                elif el.startswith("switch"):
                    elSwitch.append(self.parseTriggerOrSwitch(el, type = 1))

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
                    a = self.parseValCondition(p)
                    if a.getFunName() != None:
                        funNames.append(a.getFunName())
                    valConditions.append(a)
                elif p.__contains__("serial"):
                    a = self.parseSerial(p, vars)
                    if a.getFunName() != None:
                        funNames.append(a.getFunName())
                    serials.append(a)
                elif p.__contains__("timeLim"):
                    timeLims.append(self.parseTimeLims(p))
            self.__nodes.append(node(unitIndex, unitName, unitTopic, vars, sens, elLists, elTrigger,
                                     elSwitch, valConditions, serials, funNames, timeLims, unitType, slave))
    def getNodes(self):
        return self.__nodes

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

def buildAll():
    support.factory = None
    support.nodes = None
    support.factory = nodeFactory()
    support.factory.buildNodes()
    support.nodes = support.factory.getNodes()

def refresh():
    for node in support.nodes:
        for s in node.getSerials():
            v = node.getVariableValueByName(s.getElements())
            for i in v:
                node.setVariableValueByName(i, 0)

    for node in support.nodes:
        node.processNode()

def turnSwitch(index, text):
    varName = str(text).split(",")
    varName= varName[1].replace(")", "")
    if varName.__contains__(" "):
        varName = varName. replace(" ", "")
    n = support.factory.getNodeByIndex(int(index))
    val = n.getVariableValueByName(varName)
    if val == "1" or val == 1:
        n.setVariableValueByName(varName, 0)
    else:
        n.setVariableValueByName(varName, 1)
    return "UPDATED"

def writeVar(index, text):
    if text.__contains__(")"):
        text = text.replace(")", "")
    parameters = str(text).split(",")
    varName = parameters[1]
    varValue = parameters[2]

    if(str(varName).__contains__(" ")):
        varName = varName.replace(" ", "")

    if(str(varValue).__contains__(" ")):
        varValue = varValue.replace(" ", "")
    
    n = support.factory.getNodeByIndex(int(index))
    n.setVariableValueByName(varName, varValue)
    val = n.getVariableValueByName(varName)
    if str(val) == str(varValue):
        return "UPDATED"
    else:
        return "ERROR"
