import re
import support
import datetime
import time
from accessories.ks_logger import logit

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

   # 📎 return epoh to the original value(24 hours)
    def resetEpoh(self):
        self.__nodeEpoh = 24 * 60 * 60

   # 📎 returns MQTT topic for the node
    def getTopic(self):
        return self.__unitTopic

   # 📎 sets presence time stamp(time in the moment of execution)
    def setPresenceTimeStamp(self, value):
        self.__presenceTimeStamp = value

   # 📎 gets presence time stamp
    def getPresenceTimeStamp(self):
        return self.__presenceTimeStamp

   # 📎 presence is variable that defines wetheather presence time stamp is going to be taken ********
    def getPresence(self):
        return self.__presence
    
    def setPresence(self, value):
        self.__presence = value
        if value== True:
            self.setPresenceTimeStamp(round(time.time()))
    # ************************************************************************************************
    
    # 📎 getters and setters for the main object variables *******************************************
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

    def getVariable(self, varName):
        for i in self.__vars:
            if(i.getName()==varName):
                return i

    def appendVariableToTheNode(self, variable):
        self.__vars.append(variable)

    def removeVariableByName(self, varName):
        var = None
        for i in self.__vars:
            if i.getName() == varName:
                var = i
                break
        if var != None:
            support.lock.acquire()
            self.__vars.remove(i)
            support.lock.release()
            return True
        else:
            return False

    def getSensors(self):
        return self.__sens

    def getSensorByName(self, sensorName):
        for i in self.__sens:
            if i.getName() == sensorName:
                return i

    def getElementLists(self):
        return self.__elLists

    def getListByName(self, listName):
        for i in self.__elLists:
            if i.getName() == listName:
                return i
    
    def getElementTriggers(self):
        return self.__elTrigger

    def getTriggerByName(self, triggerName):
        for i in self.__elTrigger:
            if i.getName()== triggerName:
                return i
    
    def getElementSwitches(self):
        return self.__elSwitch

    def getSwitchByName(self, switchName):
        for i in self.__elSwitch:
            if i.getName() == switchName:
                return i
    
    def getValueConditions(self):
        return self.__valConditions

    def addValueCondition(self, vc):
        self.__valConditions.append(vc)

    def removeValueCondition(self, name):
        var = None
        for i in self.__valConditions:
            if i.getName() == name:
                var = i
                break
        if var != None:
            support.lock.acquire()
            self.__valConditions.remove(i)
            support.lock.release()
            return True
        else:
            return False

    def getSerials(self):
        return self.__serials

    def removeSerialProgram(self, name):
        var = None
        for i in self.__serials:
            if i.getName() == name:
                var = i
                break
        if var != None:
            support.lock.acquire()
            self.__serials.remove(i)
            support.lock.release()
            return True
        else:
            return False

    def addSerialProgram(self, s):
        try:
            support.lock.acquire()
            self.__serials.append(s)
            support.lock.release()
            return True
        except Exception as e:
            logit("Problem, appending serial program to node {getNodeIndex()}")
            return False

    def getFunctionNames(self):
        return self.__funNames

    def removeFunctionNames(self, name):
        var = None
        for i in self.__funNames:
            if i.getName() == name:
                var = i
                break
        if var != None:
            support.lock.acquire()
            self.__funNames.remove(i)
            support.lock.release()
            return True
        else:
            return False

    def addFunctionName(self, name):
        self.__funNames.append(name)
    
    def getTimeLimits(self):
        return self.__timeLims

    def addTimeLimit(self, tl):
        try:
            support.lock.acquire()
            self.__timeLims.append(tl)
            support.lock.release()
            return True
        except Exception as e:
            logit(f"timeLim program unable to add to the list\r\n\t{e}", 2)
            return False

    def removeTimeLimit(self, funName):
        try:
            p = None
            for i in self.__timeLims:
                if i.getFunction() == funName:
                    p = i
                    break
            if p==None:
                raise Exception(f"there is no {funName} in the list of timeLim programs")
            else:
                support.lock.acquire()
                self.__timeLims.remove(p)
                support.lock.release()
                return True
        except Exception as e:
            logit(f"unable to remove time lim program from the list\r\n\t{e}", 2)
            return False   
    # **************************************************************************************************

    # 📎 returns global index and variable name for global variable
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

    # 📎 gets value of variable by provided variable name
    # 📎 If returns None, it means that variable name doesn't exist
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

   # 📎 sets value for variable with the given name
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

   # 📎 processes messages for switches
    def processSwitches(self):
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

   # 📎 processes messages for triggers
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

   # 📎 processes messages for lists
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

   # 📎 processes messages for sensors
    def processSensors(self):
        for s in self.getSensors():
            if s.getEpoh() != None:
                if self.__nodeEpoh > self.getVariableValueByName(s.getEpoh()):
                    self.__nodeEpoh = self.getVariableValueByName(s.getEpoh())
                message = f"I_{self.getNodeIndex()}_S_{s.getIndex()}"
                support.factory.appendMessage(message)
                break

   # 📎 processes messages for entire node
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

    # 📎 function for processing program for serial swithcing and function change switch that actually checks 
    # 📎 conditions necessary for next switch to be turned on ***********************************************
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
    # **********************************************************************************************************

    # 📎 three function that deal with val condition program
    # 📎 first is getting values from provided variables, second is actually processing the program and third
    # 📎 is setting a new value for fun variable ***************************************************************
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
    # **************************************************************************************************************

    # 📎 two functions that deal with time limit programs. process time limits checks conditions in every time limit 
    # 📎 program, and function time test processes actual time limitation ******************************************
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

    def processTimeLimits(self):
        for tl in self.__timeLims:
            if(self.testTime(tl)==False):
                self.setFunNameValue(tl.getFunction(), 0)
# ******************************************************************************************************************