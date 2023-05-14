import RPi.GPIO as GPIO
import time
import threading
import socket
import json
import select

HOST = "localhost"
PORT = 10585



socketInstance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP IPV4

secondFloorData = {
    "parkingSpacesMap": [False] * 8,
    "carCount": 0,
    "isFloorFull": GPIO.LOW,
    "metadata": "secondFloor"
}


ENDERECO_01_GPIO = 13
ENDERECO_02_GPIO = 6
ENDERECO_03_GPIO = 5
SENSOR_DE_VAGA_GPIO = 20
SINAL_DE_LOTADO_FECHADO_GPIO = 8
SENSOR_DE_PASSAGEM_1_GPIO = 16
SENSOR_DE_PASSAGEM_2_GPIO = 21

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(ENDERECO_01_GPIO, GPIO.OUT)  # ENDERECO_01
GPIO.setup(ENDERECO_02_GPIO, GPIO.OUT)  # ENDERECO_02
GPIO.setup(ENDERECO_03_GPIO, GPIO.OUT)  # ENDERECO_03
GPIO.setup(SENSOR_DE_VAGA_GPIO, GPIO.IN)  # SENSOR_DE_VAGA
GPIO.setup(SINAL_DE_LOTADO_FECHADO_GPIO, GPIO.OUT)  # SINAL_DE_LOTADO_FECHADO
GPIO.setup(SENSOR_DE_PASSAGEM_1_GPIO, GPIO.IN)  # SENSOR_DE_PASSAGEM_1
GPIO.setup(SENSOR_DE_PASSAGEM_2_GPIO, GPIO.IN)  # SENSOR_DE_PASSAGEM_2


def readParkingSpaces():
     while True:
        for i in range(8):

            GPIO.output(ENDERECO_01_GPIO, i & 1)
            GPIO.output(ENDERECO_02_GPIO, (i & 2) >> 1)
            GPIO.output(ENDERECO_03_GPIO, (i & 4) >> 2)

            time.sleep(0.05)

            isParkingSpaceBusy = bool(GPIO.input(SENSOR_DE_VAGA_GPIO))

            secondFloorData['parkingSpacesMap'][i] = isParkingSpaceBusy
 

def handleSecondFloorEntrance():
    sensorOneTime = None
    sensorTwoTime = None

    while True:
        try:
            SENSOR_DE_PASSAGEM_1 = bool(GPIO.input(SENSOR_DE_PASSAGEM_1_GPIO))
            SENSOR_DE_PASSAGEM_2 = bool(GPIO.input(SENSOR_DE_PASSAGEM_2_GPIO))
            if sensorOneTime is not None and sensorTwoTime is not None:

                print(sensorOneTime, sensorTwoTime)

            if SENSOR_DE_PASSAGEM_1 and sensorOneTime is None:
                sensorOneTime = time.time()
                while bool(GPIO.input(SENSOR_DE_PASSAGEM_1_GPIO)):
                    pass

            if SENSOR_DE_PASSAGEM_2 and sensorTwoTime is None:
                sensorTwoTime = time.time()
                while bool(GPIO.input(SENSOR_DE_PASSAGEM_2_GPIO)):
                    pass

            if sensorOneTime is not None and sensorTwoTime is not None:
                deltaTime = sensorTwoTime - sensorOneTime

                if deltaTime > 0:
                    print('entrou para o segundo andar!1')

                    secondFloorData['carCount'] = secondFloorData['carCount'] + 1
                    if secondFloorData['isFloorFull'] == GPIO.LOW and secondFloorData['carCount'] >= 8:
                        flipFullFloorState()

                    print('entrou para o segundo andar!')
                    print(time.time())
                else: 
                    print('saiu para o primeiro andar!')

                    secondFloorData['carCount'] = secondFloorData['carCount'] - 1
                    if secondFloorData['isFloorFull'] == GPIO.HIGH:
                        flipFullFloorState()
                    print('saiu para o primeiro andar2!')
                    print(time.time())
                sensorOneTime = None
                sensorTwoTime = None
                time.sleep(0.4)

                continue
            time.sleep(0.25)
        except Exception as e:
            pass

def handleSocketCommunication():
    while True:
        try:
            time.sleep(1)

            socketInstance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP IPV4

            socketInstance.connect((HOST, PORT))
            while True:
                try:
                    time.sleep(0.5) # TODO

                    print('sentData', secondFloorData)
                    socketInstance.send(str.encode(json.dumps(secondFloorData))) # TODO

                    ready, _, _ = select.select([socketInstance], [], [], 0.1)
                    if not ready:
                        pass
                    else:
                        data = socketInstance.recv(1024)
       
                        if not data:
                            break
                        else:
                            userManualCommands = json.loads(data.decode())
                            print(userManualCommands['command'], 'second_floor_full')

                            if userManualCommands['command'] == 'second_floor_full':
                                flipFullFloorState()

                except Exception as e: 
                    print('exception', e)
                    break
        except Exception as e: 
            print('exception', e)



 
def flipFullFloorState():
    secondFloorData['isFloorFull'] = not secondFloorData['isFloorFull']
    print('GPIO SINAL_DE_LOTADO_FECHADO_GPIO SET TO', secondFloorData['isFloorFull'])
    GPIO.output(SINAL_DE_LOTADO_FECHADO_GPIO, secondFloorData['isFloorFull'])

threading.Thread(target=handleSocketCommunication).start()
threading.Thread(target=readParkingSpaces).start()
threading.Thread(target=handleSecondFloorEntrance).start()
 