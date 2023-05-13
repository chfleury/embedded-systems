import socket
import json
import threading
import os
import time

HOST = "localhost"
PORT = 10583


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
                print('entrou')
                print('entrou2')

                data = connection.recv(64).decode()
                print('entrou3')

                dataDictionary = json.loads(data)

                print('datad', dataDictionary)
                if  dataDictionary["metadata"] == "firstFloor":
                    parkingSpacesMap['firstFloorMap'] = dataDictionary["parkingSpacesMap"]
                elif dataDictionary["metadata"] == "secondFloor":
                    parkingSpacesMap['secondFloorMap'] = dataDictionary["parkingSpacesMap"]

                print("data", json.loads(data))
                x = json.loads(data.decode())
                print(x["seco"])

                connection.sendall(str.encode(json.dumps(dataDictionary)))
            except:
                print('explodiu')
                break


def userInterface():
    while True:
        # print("Primeiro Andar:", parkingSpacesMap['firstFloorMap'])
        # print("Segundo Andar:", parkingSpacesMap['secondFloorMap'])
        # time.sleep(0.3)  # TODO
        # os.system("clear")
        pass


def sendMessage(data) -> None:
    try:
        socketInstance.send(str.encode(json.dumps(data)))  # TODO
    except:
        pass


threading.Thread(target=handleSocketCommunication).start()
threading.Thread(target=userInterface).start()
