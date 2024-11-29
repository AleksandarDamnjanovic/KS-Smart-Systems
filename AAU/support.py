'''
*************** Name: KS Node
*************** Part of: KS Smart Systems
*************** Author: Aleksandar Damnjanovic AKA Kind Spirit
*************** YouTube channel: Kind Spirit Technology
*************** Date: 26.11.2024.
*************** Location: Kragujevac, Serbia
'''

import time
import support
import threading

scriptFile = ""
backupScript = ""
test = ""
certificate = ""
serverKey = ""
serverCertificate = ""

address =       ""
port =          8883
auPort =        10001
user =          "" 
password =      ""
START =         False

factory = None
nodes = None

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
                self.__client.connect(support.address, support.port)
                done = True
            except Exception as e:
                print(f"--communication loop-- error message:{e}")

        self.__client.subscribe(self.__topic)
        print(self.__topic)
        print("listening...")
        while(True):
            self.__client.loop_start()
            time.sleep(1)
            self.__client.loop_stop()
