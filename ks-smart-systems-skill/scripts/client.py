import socket
import sys

HOST = "127.0.0.1"
PORT = int(sys.argv[1])
message = ""
l = len(sys.argv)
for i in range(2, l):
    if(message==""):
        message = sys.argv[i]
    else:
        message= f"{message} {sys.argv[i]}"

if not message:
    print("Not enough arguments")
    sys.exit(1)

try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    client.sendall(message.encode())
    response = client.recv(4096).decode()
    print(response.strip())
except ConnectionRefusedError:
    print("ERROR: Cannot connect to server.")
except Exception as e:
    print(f"ERROR: {e}")
finally:
    client.close()