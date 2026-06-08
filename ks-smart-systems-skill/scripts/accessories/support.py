'''
*************** Name: KS Administrative Unit
*************** Part of: KS Smart Systems
*************** Author: Aleksandar Damnjanovic AKA Kind Spirit
*************** YouTube channel: Kind Spirit Technology
*************** Date: 01.06.2026.
*************** Location: Kragujevac, Serbia
'''

import time
import accessories.support
import threading
import os

localDir = os.getcwd()

lock = threading.Lock()

certificate = f"{localDir}/certs/ca.crt"
serverKey = f"{localDir}/certs/broker.key"
serverCertificate = f"{localDir}/certs/broker.crt"

address =       "192.168.0.24"
port =          8883
user =          "admin" 
password =      "00004444"
kill =          False
topic =         "admin"

TEXT = ""

class communication(threading.Thread):
    def __init__(self, topic, client):
        super().__init__()
        self.__topic = topic
        self.__client = client
    
    def run(self):
        done= False
        while(not done):
            print(f"Trying to connect to topic {self.__topic}")
            time.sleep(0.5)
            try:
                self.__client.connect(address, port)
                done = True
            except Exception as e:
                print(f"--communication loop-- error message:{e}")

        self.__client.subscribe(self.__topic)
        print(f"{self.__topic} ... connected")
        while(not kill):
            self.__client.loop_start()
            if kill:
                self.__client.disconnect()
                break
            time.sleep(1)
            self.__client.loop_stop()
