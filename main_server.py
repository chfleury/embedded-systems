import socket
import json
import threading
import os
import time

HOST = "localhost"
PORT = 10582


parkingSpacesMap = {
    "firstFloorMap": [False] * 8,
    "secondFloorMap": [False] * 8
}

userManualCommands = {
    "command": None
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

                print(dataDictionary)
                if  dataDictionary["metadata"] == "firstFloor":
                    parkingSpacesMap['firstFloorMap'] = dataDictionary["parkingSpacesMap"]
                elif dataDictionary["metadata"] == "secondFloor":
                    parkingSpacesMap['secondFloorMap'] = dataDictionary["parkingSpacesMap"]

                if userManualCommands["command"] is not None:
                    print('chegou aqui')
                    connection.sendall(str.encode(json.dumps(userManualCommands)))
                    print('foi de base')
                    userManualCommands["command"] = None

            except Exception as e: 
                print(e)
                break



def userInput():
    while True:
        x = int(input())

        if x == 1:
            print('entrou aqui')
            userManualCommands['command'] = 'first_floor_full'
        elif x == 2:
            userManualCommands['command'] = 'secons_floor_full'


def userInterface():
    while True:
        print("Total de carros")
        print("Primeiro Andar:", parkingSpacesMap['firstFloorMap'])
        print("Segundo Andar:", parkingSpacesMap['secondFloorMap'])
        print("Comandos disponiveis ('1' ou '2')")
        print("'1' - Liga sinal de lotado do estacionamento.")
        print("'2' - Liga sinal de lotado do segundo andar.")
        time.sleep(1)  # TODO
        os.system("clear")
        pass




threading.Thread(target=handleSocketCommunication).start()
# threading.Thread(target=userInterface).start()
threading.Thread(target=userInput).start()
