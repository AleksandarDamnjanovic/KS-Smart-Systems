'''
*************** Name: KS Administrative Unit
*************** Part of: KS Smart Systems
*************** Author: Aleksandar Damnjanovic AKA Kind Spirit
*************** YouTube channel: Kind Spirit Technology
*************** Date: 01.06.2026.
*************** Location: Kragujevac, Serbia
*************** Description:
                    This unit comminucates with MQTT server via admin topic, what gives it right to issue commands
                    to AAU. KSAU is can also be used as midle point in between user and KS AAU
'''

import paho.mqtt.client as mqttClient
import time
import ssl
import threading
from threading import Thread, Lock
import sys, os
import traceback
import accessories.support
from accessories.help import help
from accessories.parser import parseCommand
import socket

client = None
CONN = None

# 📎 if we get some connection error, we are going to print out warning
def on_connect(client, data, flags, returnCode):
    if(returnCode!=0):
        print(f"Client connection error... return code: {returnCode}")

# 📎 MQTT function that reacts on messages sent by another party to topic that we listen
def on_message(client, data, message):
    try:
        text = message.payload.decode("utf-8")
        
        if message.topic != "admin":
            return

        if not str(text).startswith("--response--"):
            return

        temp = ""
        for line in text.splitlines():
            if line!="" and line != "--response--" and line != "--end response--":
                line = line.strip()
                if temp == "":
                    temp = line
                else:
                    temp = f"{temp}\n{line}"
        text = f"{temp}\r\n"

        if mode == "cli":
            print(text)
        elif mode == "tcp":
            accessories.support.lock.acquire()
            accessories.support.TEXT = text
            accessories.support.lock.release()
    except Exception as e:
        traceback.print_exc()
        print(f"--onMessage function-- error message:{e}")

if __name__=="__main__":

    mode = "cli"
    HOST = "127.0.0.1"
    PORT = -1

    try:
    
        if len(sys.argv) < 2:
            raise Exception("Wrong arguments. Provide argument help for explanation")
        elif sys.argv[1]== "help":
            print(accessories.help.arguments)
            quit()
        elif sys.argv[1]=="cli":
            pass
        elif sys.argv[1]=="tcp":
            PORT = int(sys.argv[2])
            mode = "tcp"
        else:
            raise Exception("Wrong arguments. Provide argument help for explanation")
    
        client = mqttClient.Client()
        client.on_connect= on_connect
        client.on_message= on_message
        context = ssl._create_unverified_context()
        context.load_verify_locations(cafile=accessories.support.certificate)
        client.tls_set_context(context)
        client.tls_insecure_set(True)
        client.username_pw_set(accessories.support.user, accessories.support.password)

        th = accessories.support.communication(accessories.support.topic, client)
        th.start()

        time.sleep(1)
        print(f"KS Administrative Unit, ready to serve...")
        while(True):
            if mode == "cli":
                command = input()
                if command == "exit":
                    print("KS Administrative Unit, terminated")
                    accessories.support.kill= True
                    th.join()
                    quit()
                elif command == "help":
                    print(help)
                else:
                    command = parseCommand(command)
                    if not command.startswith("Error"):
                        client.publish(accessories.support.topic, command)
                    else:
                        print(command)
            elif mode == "tcp":
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.bind((HOST, PORT))
                server.listen()

                while True:
                    accessories.support.lock.acquire()
                    CONN, addr = server.accept()
                    accessories.support.lock.release()
                    with CONN:
                        accessories.support.lock.acquire()
                        data = CONN.recv(4096)
                        accessories.support.lock.release()
                        command = data.decode().strip()
                        if command == "":
                            continue
                        if command == "exit":
                            response = f"KS Administrative Unit, terminated\r\n"
                            print(response)
                            accessories.support.lock.acquire()
                            CONN.sendall(response.encode())
                            accessories.support.lock.release()
                            accessories.support.kill= True
                            th.join()
                            quit()
                            sys.exit(1)
                        elif command == "help":
                            response = f"{help}\r\n"
                            accessories.support.lock.acquire()
                            CONN.sendall(response.encode())
                            accessories.support.lock.release()
                        else:
                            command = parseCommand(command)
                            if not command.startswith("Error"):
                                client.publish(accessories.support.topic, command)
                                response = ""
                                while response == "":
                                    time.sleep(0.1)
                                    accessories.support.lock.acquire()
                                    response = accessories.support.TEXT
                                    accessories.support.lock.release()
                                accessories.support.lock.acquire()
                                accessories.support.TEXT = ""
                                CONN.sendall(response.encode())
                                accessories.support.lock.release()
                            
    except Exception as e:
        print(f"KS Administrative Unit configuration error\r\n\t{e}")
        accessories.support.kill= True
        th.join()
        quit()