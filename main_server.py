import socket
import json
import threading
import os
import time

HOST = "localhost"
PORT = 10585


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


        clients = []
        while len(clients) < 2:
            print('len', len(clients))
            connection, _ = socketInstance.accept()
            clients.append(connection)

        print('passou aqui')
        while True:
            try:
                for client in clients:
                    time.sleep(0.1) # TODO
                    print('chegou 0')

                    data = client.recv(1024).decode()
                    print('chegou 10')

                    print('data decoe', data)
                    dataDictionary = json.loads(data)
                    print('chegou 20')

                    print(dataDictionary)


                    if  dataDictionary["metadata"] == "firstFloor":

                        parkingSpacesMap['firstFloorMap'] = dataDictionary["parkingSpacesMap"]
                    
                    if dataDictionary["metadata"] == "secondFloor":
                        print('aAAAAAAAAAAAAA')
                        parkingSpacesMap['secondFloorMap'] = dataDictionary["parkingSpacesMap"]

                    print('parkinAqui', parkingSpacesMap)

                    if userManualCommands["command"] is not None:
                        client.send(str.encode(json.dumps(userManualCommands)))
                userManualCommands["command"] = None

            except Exception as e: 
                print(e)
                break



def userInput():
    try:
        while True:
            print('asdsadsassa')
            x = int(input())

            if x == 1:
                print('entrou aqui')
                userManualCommands['command'] = 'first_floor_full'
            elif x == 2:
                userManualCommands['command'] = 'second_floor_full'
    except: pass

def userInterface():
    while True:
        print("Total de carros TODO")
        print("Primeiro Andar:", parkingSpacesMap['firstFloorMap'])
        print("Segundo Andar:", parkingSpacesMap['secondFloorMap'])
        print(parkingSpacesMap)
        print("Comandos disponiveis ('1' ou '2')")
        print("'1' - Liga/Desliga sinal de lotado do estacionamento.")
        print("'2' - Liga/Desliga sinal de lotado do segundo andar.")
        time.sleep(1)  # TODO
        os.system("clear")
        pass




threading.Thread(target=handleSocketCommunication).start()
threading.Thread(target=userInterface).start()
threading.Thread(target=userInput).start()
