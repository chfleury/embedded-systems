import threading
import socket
import json


def handleSocketCommunication():
    HOST = "localhost"
    PORT = 10582

    sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP IPV4
    sckt.connect((HOST, PORT))

    sendData = {"test": 123}
    sckt.sendall(str.encode(json.dumps(sendData)))

    while True:
        data = sckt.recv(512)
        print("data", data.decode())


threading.Thread(target=handleSocketCommunication).start()
