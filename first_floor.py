import RPi.GPIO as GPIO
import time
import threading
import socket
import json
import select

HOST = "localhost"
PORT = 10585

socketInstance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP IPV4

firstFloorData = {
    "parkingSpacesMap": [False] * 8,
    "carCount": 0,
    "isFloorFull": GPIO.LOW,
    "metadata": "firstFloor"
}

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(22, GPIO.OUT)  # ENDERECO_01
GPIO.setup(26, GPIO.OUT)  # ENDERECO_02
GPIO.setup(19, GPIO.OUT)  # ENDERECO_03
GPIO.setup(18, GPIO.IN)  # SENSOR_DE_VAGA
GPIO.setup(27, GPIO.OUT)  # SINAL_DE_LOTADO_FECHADO
GPIO.setup(23, GPIO.IN)  # SENSOR_ABERTURA_CANCELA_ENTRADA
GPIO.setup(24, GPIO.IN)  # SENSOR_FECHAMENTO_CANCELA_ENTRADA
GPIO.setup(10, GPIO.OUT)  # MOTOR_CANCELA_ENTRADA
GPIO.setup(25, GPIO.IN)  # SENSOR_ABERTURA_CANCELA_SAIDA
GPIO.setup(12, GPIO.IN)  # SENSOR_FECHAMENTO_CANCELA_SAIDA
GPIO.setup(17, GPIO.OUT)  # MOTOR_CANCELA_SAIDA


def readParkingSpaces():
    while True:
        for i in range(8):
            GPIO.output(22, i & 1)
            GPIO.output(26, (i & 2) >> 1)
            GPIO.output(19, (i & 4) >> 2)

            time.sleep(0.05)

            isParkingSpaceBusy = bool(GPIO.input(18))

            firstFloorData['parkingSpacesMap'][i] = isParkingSpaceBusy

def handleEntranceParkingBarrier():
    while True:
        time.sleep(0.05)
        SENSOR_ABERTURA_CANCELA_ENTRADA = GPIO.input(23)

        if SENSOR_ABERTURA_CANCELA_ENTRADA:
            GPIO.output(10, 1)

            while True:
                SENSOR_FECHAMENTO_CANCELA_ENTRADA = GPIO.input(24)
                if SENSOR_FECHAMENTO_CANCELA_ENTRADA:
                    GPIO.output(10, 0)

                    firstFloorData['carCount'] = firstFloorData['carCount'] + 1
                    if firstFloorData['isFloorFull'] == GPIO.LOW and firstFloorData['carCount'] == 16:
                        flipFullFloorState()
                    break


def handleExitParkingBarrier():
    while True:
        time.sleep(0.05)

        SENSOR_ABERTURA_CANCELA_SAIDA = GPIO.input(25)

        if SENSOR_ABERTURA_CANCELA_SAIDA:
            GPIO.output(17, 1)

            while True:
                SENSOR_FECHAMENTO_CANCELA_SAIDA = GPIO.input(12)
                if SENSOR_FECHAMENTO_CANCELA_SAIDA:
                    GPIO.output(17, 0)

                    firstFloorData['carCount'] = firstFloorData['carCount'] - 1

                    if firstFloorData['isFloorFull'] == GPIO.HIGH and firstFloorData['carCount'] < 16:
                        flipFullFloorState()
                    break


def handleSocketCommunication():
    while True:
        try:
            time.sleep(1)
            socketInstance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP IPV4

            socketInstance.connect((HOST, PORT))
            while True:
                try:
                    time.sleep(0.5)
                    print('sentData', firstFloorData)

                    socketInstance.send(str.encode(json.dumps(firstFloorData))) # TODO

                    ready, _, _ = select.select([socketInstance], [], [], 0.1)
                    if not ready:
                        pass
                    else:
                        data = socketInstance.recv(1024)
       
                        if not data:
                            break
                        else:
                            userManualCommands = json.loads(data.decode())
                            
                            if userManualCommands['command'] == 'first_floor_full':
                                flipFullFloorState()

                except Exception as e:
                    print('exception', e)
                    break
        except Exception as e: 
            print('exception', e)

def flipFullFloorState():
    firstFloorData['isFloorFull'] = not firstFloorData['isFloorFull']
    print('GPIO 27 SET TO', firstFloorData['isFloorFull'])
    GPIO.output(27, firstFloorData['isFloorFull'])

threading.Thread(target=readParkingSpaces).start()
threading.Thread(target=handleEntranceParkingBarrier).start()
threading.Thread(target=handleExitParkingBarrier).start()
threading.Thread(target=handleSocketCommunication).start()

