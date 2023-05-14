# import RPi.GPIO as GPIO
import time
import threading
import socket
import json
import select

HOST = "localhost"
PORT = 10585


socketInstance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP IPV4

parkingSpacesMap = {
    "parkingSpacesMap": [False] * 8,
    "metadata": "secondFloor"
}


# GPIO.setmode(GPIO.BCM)
# GPIO.setwarnings(False)
# GPIO.setup(13, GPIO.OUT)  # ENDERECO_01
# GPIO.setup(6, GPIO.OUT)  # ENDERECO_02
# GPIO.setup(5, GPIO.OUT)  # ENDERECO_03
# GPIO.setup(20, GPIO.IN)  # SENSOR_DE_VAGA
# GPIO.setup(8, GPIO.OUT)  # SINAL_DE_LOTADO_FECHADO
# GPIO.setup(16, GPIO.IN)  # SENSOR_DE_PASSAGEM_1
# GPIO.setup(21, GPIO.IN)  # SENSOR_DE_PASSAGEM_2


def readParkingSpaces():
     while True:
        for i in range(8):

            # GPIO.output(13, i & 1)
            # GPIO.output(6, (i & 2) >> 1)
            # GPIO.output(5, (i & 4) >> 2)

            time.sleep(0.05)

            isParkingSpaceBusy = False

            if i == 2:
                isParkingSpaceBusy = True


            # isParkingSpaceBusy = bool(GPIO.input(20))

            parkingSpacesMap['parkingSpacesMap'][i] = isParkingSpaceBusy
 

# def handleSecondFloorEntrance():
#     sensorOneTime = None
#     sensorTwoTime = None

#     while True:
#         SENSOR_DE_PASSAGEM_1 = bool(GPIO.input(16))
#         SENSOR_DE_PASSAGEM_2 = bool(GPIO.input(21))
#         if sensorOneTime is not None and sensorTwoTime is not None:

#             print(sensorOneTime, sensorTwoTime)

#         if SENSOR_DE_PASSAGEM_1 and sensorOneTime is None:
#             sensorOneTime = time.time()
#             while bool(GPIO.input(16)):
#                 pass
#             # time.sleep(0.3)

#         if SENSOR_DE_PASSAGEM_2 and sensorTwoTime is None:
#             sensorTwoTime = time.time()
#             while bool(GPIO.input(21)):
#                 pass

#         if sensorOneTime is not None and sensorTwoTime is not None:
#             deltaTime = sensorTwoTime - sensorOneTime

#             if deltaTime > 0:
#                  print('entrou para o segundo andar!')
#                  print(time.time())
#             else: 
#                 print('saiu para o primeiro andar2!')
#                 print(time.time())
#             sensorOneTime = None
#             sensorTwoTime = None
#             time.sleep(0.4)

#             continue
#         time.sleep(0.25)



def handleSocketCommunication():
    while True:
        try:
            socketInstance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP IPV4

            socketInstance.connect((HOST, PORT))
            # print('tentou conect')
            while True:
                try:
                    time.sleep(1) # TODO

                    print('sentData', parkingSpacesMap)
                    socketInstance.send(str.encode(json.dumps(parkingSpacesMap))) # TODO

                    ready, _, _ = select.select([socketInstance], [], [], 0.1)
                    if not ready:
                        print('not ready')
                        pass
                    else:
                        print('ready')

                        data = socketInstance.recv(1024)
       
                        print('chegou aqui')
                        if not data:
                            print('not data')
                            break
                        else:
                            userManualCommands = json.loads(data.decode())
                            print('data', userManualCommands)
                            print(userManualCommands['command'], 'second_floor_full')

                            if userManualCommands['command'] == 'second_floor_full':
                                setFullFloorLedOn()

                            print("Received message from server:",data)

                except Exception as e: 
                    print('execpt handleSocketCommunication inside', e)
                    break
        except Exception as e: 
            print('execpt handleSocketCommunication outside', e)



def setFullFloorLedOn():
    print('led on')
    # GPIO.output(8, 1)
    pass

threading.Thread(target=handleSocketCommunication).start()
threading.Thread(target=readParkingSpaces).start()
# threading.Thread(target=handleSecondFloorEntrance).start()
 