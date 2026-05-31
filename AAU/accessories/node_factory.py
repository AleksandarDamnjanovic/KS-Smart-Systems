from accessories.ks_node import node
from accessories.script_objects import *
import re
from pathlib import Path
import sys, os
import support
from accessories.script_parser import parseNodes
import time

class nodeFactory:
    def __init__(self):
        self.__nodes = list()
        self.__globalVars = list()
        self.__messages = list()
        self.restartEpoh()

    def appendToGlobalVariables(self, variable):
        self.__globalVars.append(variable)

    def removeGlobalVariable(self, index, varName):
        var = None
        for i in self.__globalVars:
            if i.getName() == varName:
                var = i
                break
        if var != None:
            support.lock.acquire()
            self.__globalVars.remove(i)
            support.lock.release()

    # 📎 default epoh is set to be 24 hours. whatever new epoh is going to be acrording to the script
    # 📎 this value is going to be shortened
    def restartEpoh(self):
        self.__factoryEpoh = 24 * 60 * 60

    # 📎 reads entire script from function readAll and then reads content of previous script and store it in
    # 📎 the backup-script file, while new content is stored into script.kst 
    def updateScript(self):
        content = self.readAll()
        f = open(support.scriptFile, "r")
        old= f.read()
        f.close()
        f = open(support.baskupScriptFile, "w")
        f.write(old)
        f.close()
        f = open(support.scriptFile, "w")
        f.write(content)
        f.close()

    # 📎 gets variable objet's value, based on node index and variable name
    def readVar(self, ind, name):
        n= self.getNodeByIndex(ind)
        val = n.getVariableValueByName(name)
        return val

    # 📎 turns variable object into textual - script representation of it for the purpose of rebuilding the script
    # 📎 returns textual - script representation of all variables in the node
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

    # 📎 from objects, returns script - textual representation of node header for the purpose of rebuilding the script
    def readHeader(self, index):
        for n in self.__nodes:
            if n.getNodeIndex() == index:
                return f"{n.getNodeIndex()}(\"{n.getNodeName()}\", \"{n.getTopic()}\", [{n.getType()}]"

    # 📎 returns all textual - script representation of all of sensors in the node
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
        
    # 📎 returns all of elements(lists, triggers and swithes) in textual - script form for the purpose of 
    # 📎 rebuilding the script
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
        
    # 📎 get number of nodes in the entire script
    def readNodeCount(self):
        return f"{str(support.factory.getNodes().__len__())}"
        
    # 📎 returns all of programs from the node in textual - script form for the purpose of reconstructing the scipt
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

    # 📎 reads entire script from the node factory
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
            logit(f"--onReadAll-- error message:{e}", 2)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            login(f"{exc_type} {fname} {exc_tb.tb_lineno}", 2)

        return content
    
    # 📎 searches for the variable based on node index, element type, element index and force
    # 📎 and gets its value
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

    # 📎 deals with presence varible per node
    def setNodePresenceByIndex(self, index, value):
        for n in self.__nodes:
            if n.getNodeIndex() == index:
                n.setPresence(value)
                return True
        return False

    # 📎 gets node object based on provided index
    def getNodeByIndex(self, index):
        for n in self.__nodes:
            if n.getNodeIndex() == index:
                return n

    # 📎 checks validity of message returned from the microcontroller
    # 📎 if message is not valid, warning is going to be sent to the user
    def processConfirmation(self, text):
        valid = False
        demandUpdate = -1
        __tokens= text.split("_")
        __tokens= list(filter(None, __tokens))

        if __tokens[0]=="I" or __tokens[0]== "Q":
            return

        __nodeIndex = int(__tokens[1])
        presence= self.setNodePresenceByIndex(__nodeIndex , True)
        n = self.getNodeByIndex(__nodeIndex)
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
            logit(f"--processing confirmation-- error message:{e}", 2)

        return valid, demandUpdate

    # 📎 lists throught epoh of all nodes and takes the shorter epoh among them
    def calculateFactoryEpoh(self):
        self.restartEpoh()
        for n in self.getNodes():
            if self.__factoryEpoh > n.getNodeEpoh():
                self.__factoryEpoh = n.getNodeEpoh()

    # 📎 returns the shorter epoh from the entire node list
    def getFactoryEpoh(self):
        return self.__factoryEpoh

   # 📎 return messages from the single node
    def getMessagesByIndex(self, index):
        messages = list()
        for m in self.getMessages():
            mm = str(m).split("_")
            mm = int(mm[1])
            if mm == index:
                messages.append(m)
        return messages

   # 📎 create entire pack of messages that are going to be sent to all of clients
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

   # 📎 remove all of messages from the list of messages
    def clearMessages(self):
        self.__messages.clear()

   # 📎 get all of messages
    def getMessages(self):
        return self.__messages
    
   # 📎 set new message pack to a message list
    def setMessages(self, messages):
        self.__messages = messages

   # 📎 add one message to the message list
    def appendMessage(self, message):
        self.__messages.append(message)

   # 📎 gets all of global variables
    def getGlobalVars(self):
        return self.__globalVars

   # 📎 formats variable line from the script into text that is easy to parse 
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

   # 📎 parse entire script and create nodes object list
    def buildNodes(self):
        parseNodes(self, self.__nodes, self.__globalVars)

   # 📎 return list of node objects
    def getNodes(self):
        return self.__nodes