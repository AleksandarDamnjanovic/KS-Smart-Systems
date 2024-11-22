import paho.mqtt.client as mqttClient
import time
import ssl
import threading
from threading import Thread
import support
import script
import re
import sys, os

script.buildAll()
script.refresh()

def rerun():
    
    while support.START == True:
        time.sleep(0.1)

    support.START = True
    support.factory.clearMessages()
    script.refresh()
    support.factory.packMessages()
    support.factory.calculateFactoryEpoh()
    epoh = support.factory.getFactoryEpoh()
    sendMessages()
    
    support.START = False
    print(f"epoh until next rerun: {epoh}")

    return epoh
        
def on_connect(client, data, flags, returnCode):
    if(returnCode==0):
        print("connected...")
    else:
        print(f"Connection error... return code: {returnCode}")

def on_message(client, data, message):
    try:
        text = message.payload.decode("utf-8")

        if str(text).__contains__("--no response--") or str(text).startswith("--response--"):
            return
        
        if message.topic== "admin":
            mess= processAdmin(text)
            if mess != "":
                while support.START == True:
                    time.sleep(0.2)
                client= clients.__getitem__(0)
                client.publish("admin", mess)
        else:
            if text.__contains__("\r"):
                text= str(text).replace("\r", " ")

            if text.__contains__("\n"):
                text= str(text).replace("\n", " ")

            if text.__contains__("  "):
                text= str(text).replace("  ", " ")

            if text.__contains__(" "):
                __lines= text.split(" ")
                __lines= list(filter(None, __lines))
                __tokens= text.split("_")
                __tokens= list(filter(None, __tokens))

                if __tokens[0]=="I" or __tokens[0]== "Q":
                    return

                __result = False
                for l in __lines:
                    valid, demand = support.factory.processConfirmation(l)
                    if valid == False:
                        __result= False
                if __result == False and demand != -1:
                    print(f"update called by sensor on node: {demand}")
                    rerun()

    except Exception as e:
        print(f"--onMessage function-- error message:{e}")


clients = list()
num = len(support.nodes) + 1
for i in range(0, num):
    client = mqttClient.Client()
    client.on_connect= on_connect
    client.on_message= on_message
    context = ssl._create_unverified_context()
    context.load_verify_locations(cafile=support.certificate)
    client.tls_set_context(context)
    client.tls_insecure_set(True)
    client.username_pw_set(support.user, support.password)
    clients.append(client)

def sendMessages():
    for n in support.nodes:
        ind = n.getNodeIndex()
        message = support.factory.getMessagesByIndex(ind)
        if len(message)>0:
            message = message[0]
        client= clients.__getitem__(ind)
        try:
            client.publish(n.getTopic(), message)
        except Exception as e:
            print(f"--sendMessage function-- error message:{e}")

class running(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            if support.START == False:
                epoh= rerun()
                time.sleep(epoh)
            else:
                time.sleep(0.1)

for i in range(0, num):
    th = None
    if i == 0:
        th = support.communication("admin", clients.__getitem__(i))
    else:
        th = support.communication(support.factory.getNodeByIndex(i).getTopic(), clients.__getitem__(i))
    if th != None:
        th.start()

time.sleep(2)
run = running()
run.start()

def processAdmin(text):
    message = ""

    try:
        rnbi = re.findall("readNodeByIndex\\([\\d]+\\)", text)
        rvbni = re.findall("readVariablesByNodeIndex\\([\\d]+\\)", text)

        if text.__contains__("readHeader("):
            ind = re.findall("[\\d]+", text)
            if ind != None:
                ind = int(ind[0])
                if ind > 0 and ind < len(support.factory.getNodes()) + 1:
                    message = support.factory.readHeader(ind)
                else:
                    print(f"index {ind} received by querry, is out of limits")
                    message = "--no result--"
        elif text.__contains__("readVariables("):
            ind = re.findall("[\\d]+", text)
            if ind != None:
                ind = int(ind[0])
                if ind > 0 and ind < len(support.factory.getNodes()) + 1:
                    message = support.factory.readVariables(ind)
                else:
                    print(f"index {ind} received by querry, is out of limits")
                    message = "--no result--"
        elif text.__contains__("readSensors("):
            ind = re.findall("[\\d]+", text)
            if ind != None:
                ind = int(ind[0])
                if ind > 0 and ind < len(support.factory.getNodes()) + 1:
                    message = support.factory.readSensors(ind)
                else:
                    print(f"index {ind} received by querry, is out of limits")
                    message = "--no result--"
        elif text.__contains__("readElements("):
            ind = re.findall("[\\d]+", text)
            if ind != None:
                ind = int(ind[0])
                if ind > 0 and ind < len(support.factory.getNodes()) + 1:
                    message = support.factory.readElements(ind)
                else:
                    print(f"index {ind} received by querry, is out of limits")
                    message = "--no result--"
        elif text.__contains__("readPrograms("):
            ind = re.findall("[\\d]+", text)
            if ind != None:
                ind = int(ind[0])
                if ind > 0 and ind < len(support.factory.getNodes()) + 1:
                    message = support.factory.readPrograms(ind)
                else:
                    print(f"index {ind} received by querry, is out of limits")
                    message = "--no result--"
        elif text.__contains__("readNodeCount("):
            message = support.factory.readNodeCount()
        elif text.__contains__("readVar("): 
            ind = int(re.findall("[\\d]+", text)[0])
            if ind != None:
                name = re.findall("\\$[a-zA-Z0-9]+", text)[0]
                if ind > 0 and ind < len(support.factory.getNodes()) + 1:
                    message = support.factory.readVar(ind, name)
                else:
                    print(f"index {ind} received by querry, is out of limits")
                    message = "--no result--"
        elif text.__contains__("writeNode("): 
            ind = int(re.findall("[\\d]+", text)[0])
            if ind != None:
                start = text.index("writeNode(") + 10
                text = text[start: str(text).__len__()]
                if ind > 0 and ind < len(support.factory.getNodes()) + 1:
                    message = script.writeNode(ind, text)
                else:
                    print(f"index {ind} received by querry, is out of limits")
                    message = "--no result--"
        elif text.__contains__("turnSwitch("): 
            ind = int(re.findall("[\\d]+", text)[0])
            if ind != None:
                start = text.index("turnSwitch(") + 9
                text = text[start: str(text).__len__()]
                if ind > 0 and ind < len(support.factory.getNodes()) + 1:
                    message = script.turnSwitch(ind, text)
                else:
                    print(f"index {ind} received by querry, is out of limits")
                    message = "--no result--"
        elif text.__contains__("pressButton("): 
            ind = int(re.findall("[\\d]+", text)[0])
            if ind != None:
                start = text.index("pressButton(") + 12
                text = text[start: str(text).__len__()]
                if ind > 0 and ind < len(support.factory.getNodes()) + 1:
                    message = script.turnSwitch(ind, text)
                else:
                    print(f"index {ind} received by querry, is out of limits")
                    message = "--no result--"
        elif text.__contains__("writeVar("): 
            ind = int(re.findall("[\\d]+", text)[0])
            if ind != None:
                start = text.index("writeVar(") + 9
                text = text[start: str(text).__len__()]
                if ind > 0 and ind < len(support.factory.getNodes()) + 1:
                    message = script.writeVar(ind, text)
                else:
                    print(f"index {ind} received by querry, is out of limits")
                    message = "--no result--"
        elif text.__contains__("readAll("):
            message = support.factory.readAll()

        if message != "--no result--":
            message = f"--response--\n{message}\n--end response--"

    except Exception as e:
        print(f"--onProcessAdmin-- error message:{e}")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

    return message