'''
*************** Name: KS Node
*************** Part of: KS Smart Systems
*************** Author: Aleksandar Damnjanovic AKA Kind Spirit
*************** YouTube channel: Kind Spirit Technology
*************** Date: 26.11.2024.
*************** Location: Kragujevac, Serbia
*************** Description:
                    This is the main part of the project. This file should be executed in order for program to work.
'''

import paho.mqtt.client as mqttClient
from accessories.admin import processAdmin
import time
import ssl
import threading
from threading import Thread
import support
import script
import sys, os
from accessories.ks_logger import logit
import traceback

# 📎 function that does all the work
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
    logit(f"epoh until next rerun: {epoh}", 0)

    return epoh
        
# 📎 if we get some connection error, we are going to log warning
def on_connect(client, data, flags, returnCode):
    if(returnCode!=0):
        logit(f"Client connection error... return code: {returnCode}", 2)

# 📎 MQTT function that reacts on messages sent by another party to topic that we listen
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
                        break
                if __result == False and demand != -1:
                    logit(f"update called by sensor on node: {demand}", 0)
                    rerun()

    except Exception as e:
        traceback.print_exc()
        logit(f"--onMessage function-- error message:{e}", 2)

# 📎 this function sens messages from all nodes to coresponding MQTT topics
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
            logit(f"--sendMessage function-- error message:{e}", 2)

# 📎 the main purpose of this theread is to run indefinitelly and to call function rerun periodically.
# 📎 function rerun is what actually does all the work
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

  # 📎 entry point
if __name__ == "__main__":
    script.buildAll()
    script.refresh()

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