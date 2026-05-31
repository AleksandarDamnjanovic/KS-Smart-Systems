import re

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