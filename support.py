import time
import support
import threading

scriptFile = "/home/kst/Automatizacija/script/script.kst"
backupScript = "/home/kst/Automatizacija/script/backup.kst"
test = "/home/kst/Automatizacija/script/example.kst"
certificate = "/home/kst/Automatizacija/security/ca.crt"
serverKey = "/home/kst/Automatizacija/security/broker.key"
serverCertificate = "/home/kst/Automatizacija/security/broker.crt"

address =       "192.168.0.201"
port =          8883
auPort =        10001
user =          "AAU" 
password =      "00007070"
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