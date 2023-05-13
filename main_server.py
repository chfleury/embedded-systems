import socket
import json
import threading
import os
import time

HOST = "localhost"
PORT = 10584


parkingSpacesMap = {
    "firstFloorMap": [False] * 8,
    "secondFloorMap": [False] * 8
}

socketInstance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP IPV4
socketInstance.bind((HOST, PORT))
socketInstance.listen()


def handleSocketCommunication():
    while True:
        print("Waiting for client...")

        connection, address = socketInstance.accept()

        while True:
            try:
                time.sleep(1) # TODO

                data = connection.recv(512).decode()

                dataDictionary = json.loads(data)

                if  dataDictionary["metadata"] == "firstFloor":
                    parkingSpacesMap['firstFloorMap'] = dataDictionary["parkingSpacesMap"]
                elif dataDictionary["metadata"] == "secondFloor":
                    parkingSpacesMap['secondFloorMap'] = dataDictionary["parkingSpacesMap"]

                connection.sendall(str.encode(json.dumps(dataDictionary)))
            except Exception as e: 
                print(e)

                break


def userInterface():
    while True:
        print("Primeiro Andar:", parkingSpacesMap['firstFloorMap'])
        print("Segundo Andar:", parkingSpacesMap['secondFloorMap'])
        time.sleep(0.3)  # TODO
        os.system("clear")
        pass

threading.Thread(target=handleSocketCommunication).start()
threading.Thread(target=userInterface).start()
