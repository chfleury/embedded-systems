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
                conn, addr = socketInstance.accept()
                socketsList.append(conn)
                print(f"New connection from {addr}")
            # incoming data from an existing connection
            else:
                try:
                    time.sleep(0.1) # TODO

                    print('comando', userManualCommands["command"])
                    print(len(read_sockets), len(socketsList))

                    for connection in socketsList:
                        if connection != socketInstance and userManualCommands["command"] is not None:
                            print('entrou no send')
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
                        # print(f"Received data from {sock.getpeername()}: {data.decode()}")
                    else:
                        # connection closed
                        sock.close()
                        if sock in socketsList:
                            socketsList.remove(sock)
                except:
                    # connection closed or error
                    sock.close()
                    if sock in socketsList:
                        socketsList.remove(sock)
        



def userInput():
    while True:
        try:
            # print('asdsadsassa')
            x = int(input())

            if x == 1:
                # print('entrou aqui')
                userManualCommands['command'] = 'first_floor_full'
            elif x == 2:
                userManualCommands['command'] = 'second_floor_full'
        except: pass

def userInterface():
    while True:

        os.system("clear") # TODO

        print("Total de carros no estacionamento:", parkingSpaceData['totalCarCount'])
        print("Número de carros no Primeiro Andar:", int(parkingSpaceData["totalCarCount"]) - int(parkingSpaceData["secondFloorCarCount"]))
        print("Número de carros no Segundo Andar:", parkingSpaceData["secondFloorCarCount"])
        print("Vagas disponíveis no Primeiro Andar:", parkingSpaceData['firstFloorMap'])
        print("Vagas disponíveis no Segundo Andar:", parkingSpaceData['secondFloorMap'])
        print("Total de dinheiro gerado pelo estacionamento: R$" + str(parkingSpaceData['totalRevenue']))
        print(parkingSpaceData)
        print("Comandos disponiveis ('1' ou '2')")
        print("'1' - Liga/Desliga sinal de lotado do estacionamento.")
        print("'2' - Liga/Desliga sinal de lotado do segundo andar.")

        time.sleep(1)  # TODO
        pass


def calculateRevenue():
    while True:
        parkingSpaceData['totalRevenue'] = parkingSpaceData['totalRevenue'] + (int(parkingSpaceData["totalCarCount"]) * 0.15)
        time.sleep(60)

threading.Thread(target=handleSocketCommunication).start()
# threading.Thread(target=userInterface).start()
threading.Thread(target=userInput).start()
threading.Thread(target=calculateRevenue).start()
