import socket
import json
import threading
import os
import time

HOST = "localhost"
PORT = 10582

firstFloorMap = [False] * 8
secondFloorMap = [False] * 8

socketInstance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP IPV4
socketInstance.bind((HOST, PORT))
socketInstance.listen()


def handleSocketCommunication():
    while True:
        print("Waiting for client...")
        connection, address = socketInstance.accept()

        while True:
            try:
                data = connection.recv(64).decode()

                dataDictionary = json.loads(data)

                if dataDictionary["metadata"] == "secondFloor":
                    secondFloorMap = dataDictionary["parkingSpacesMap"]
                elif dataDictionary["metadata"] == "firstFloor":
                    firstFloorMap = dataDictionary["parkingSpacesMap"]

                print("data", json.loads(data))
                x = json.loads(data.decode())
                print(x["test"])

                connection.sendall(data)
            except:
                break


def userInterface():
    print("Primeiro Andar:", firstFloorMap)
    print("Segundo Andar:", secondFloorMap)
    time.sleep(0.3)  # TODO
    os.system("clear")


def sendMessage(data) -> None:
    try:
        socketInstance.send(str.encode(json.dumps(data)))  # TODO
    except:
        pass


threading.Thread(target=handleSocketCommunication).start()
threading.Thread(target=userInterface).start()
