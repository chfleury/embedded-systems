import socket
import json
import threading
import os
import time
import select

HOST = "localhost"
PORT = 10585


parkingSpaceData = {
    "firstFloorMap": [False] * 8,
    "secondFloorMap": [False] * 8,
    "totalCarCount": 0,
    "totalRevenue": 0.0,
    "secondFloorCarCount": 0 
}

userManualCommands = {
    "command": None
}

socketInstance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP IPV4
socketInstance.bind((HOST, PORT))
socketInstance.listen()
socketsList = [socketInstance] 



def handleSocketCommunication():
    while True:
        read_sockets, _, _ = select.select(socketsList, [], [])

        for sock in read_sockets:
            if sock == socketInstance:
                conn, _ = socketInstance.accept()
                socketsList.append(conn)
            else:
                try:
                    time.sleep(0.1)

                    for connection in socketsList:
                        if connection != socketInstance and userManualCommands["command"] is not None:
                            connection.send(str.encode(json.dumps(userManualCommands)))
                    
                    userManualCommands["command"] = None

                    data = sock.recv(1024)
                    if data:
                        dataDictionary = json.loads(data.decode())

                        if  dataDictionary["metadata"] == "firstFloor":
                            parkingSpaceData['firstFloorMap'] = dataDictionary["parkingSpacesMap"]
                            parkingSpaceData["totalCarCount"] = dataDictionary['carCount']
                        if dataDictionary["metadata"] == "secondFloor":
                            parkingSpaceData['secondFloorMap'] = dataDictionary["parkingSpacesMap"]
                            parkingSpaceData['secondFloorCarCount'] = dataDictionary['carCount']
                    else:
                        sock.close()
                        if sock in socketsList:
                            socketsList.remove(sock)
                except:
                    sock.close()
                    if sock in socketsList:
                        socketsList.remove(sock)
        



def userInput():
    while True:
        try:
            x = int(input())

            if x == 1:
                userManualCommands['command'] = 'first_floor_full'
            elif x == 2:
                userManualCommands['command'] = 'second_floor_full'
        except: pass

def userInterface():
    while True:
        os.system("clear")

        print("Total de carros no estacionamento:", parkingSpaceData['totalCarCount'])
        print("Número de carros no Primeiro Andar:", int(parkingSpaceData["totalCarCount"]) - int(parkingSpaceData["secondFloorCarCount"]))
        print("Número de carros no Segundo Andar:", parkingSpaceData["secondFloorCarCount"])
        print("Vagas Ocupadas no Primeiro Andar:", parkingSpaceData['firstFloorMap'])
        print("Vagas Ocupadas no Segundo Andar:", parkingSpaceData['secondFloorMap'])
        print("Total de dinheiro gerado pelo estacionamento: R$" + str(parkingSpaceData['totalRevenue']))
        print("Comandos disponiveis ('1' ou '2')")
        print("'1' - Liga/Desliga sinal de lotado do estacionamento.")
        print("'2' - Liga/Desliga sinal de lotado do segundo andar.")

        time.sleep(0.5)


def calculateRevenue():
    while True:
        parkingSpaceData['totalRevenue'] = parkingSpaceData['totalRevenue'] + (int(parkingSpaceData["totalCarCount"]) * 0.15)
        time.sleep(60)

threading.Thread(target=handleSocketCommunication).start()
threading.Thread(target=userInterface).start()
threading.Thread(target=userInput).start()
threading.Thread(target=calculateRevenue).start()
