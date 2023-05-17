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

ENDERECO_01_GPIO = 22
ENDERECO_02_GPIO = 26
ENDERECO_03_GPIO = 19
SENSOR_DE_VAGA_GPIO = 18
SINAL_DE_LOTADO_FECHADO_GPIO = 27
SENSOR_ABERTURA_CANCELA_ENTRADA_GPIO = 23
SENSOR_FECHAMENTO_CANCELA_ENTRADA_GPIO = 24
MOTOR_CANCELA_ENTRADA_GPIO = 10
SENSOR_ABERTURA_CANCELA_SAIDA_GPIO = 25
SENSOR_FECHAMENTO_CANCELA_SAIDA_GPIO = 12
MOTOR_CANCELA_SAIDA_GPIO = 17

GPIO.setup(ENDERECO_01_GPIO, GPIO.OUT)  # ENDERECO_01
GPIO.setup(ENDERECO_02_GPIO, GPIO.OUT)  # ENDERECO_02
GPIO.setup(ENDERECO_03_GPIO, GPIO.OUT)  # ENDERECO_03
GPIO.setup(SENSOR_DE_VAGA_GPIO, GPIO.IN)  # SENSOR_DE_VAGA
GPIO.setup(SINAL_DE_LOTADO_FECHADO_GPIO, GPIO.OUT)  # SINAL_DE_LOTADO_FECHADO
GPIO.setup(SENSOR_ABERTURA_CANCELA_ENTRADA_GPIO, GPIO.IN)  # SENSOR_ABERTURA_CANCELA_ENTRADA
GPIO.setup(SENSOR_FECHAMENTO_CANCELA_ENTRADA_GPIO, GPIO.IN)  # SENSOR_FECHAMENTO_CANCELA_ENTRADA
GPIO.setup(MOTOR_CANCELA_ENTRADA_GPIO, GPIO.OUT)  # MOTOR_CANCELA_ENTRADA
GPIO.setup(SENSOR_ABERTURA_CANCELA_SAIDA_GPIO, GPIO.IN)  # SENSOR_ABERTURA_CANCELA_SAIDA
GPIO.setup(SENSOR_FECHAMENTO_CANCELA_SAIDA_GPIO, GPIO.IN)  # SENSOR_FECHAMENTO_CANCELA_SAIDA
GPIO.setup(MOTOR_CANCELA_SAIDA_GPIO, GPIO.OUT)  # MOTOR_CANCELA_SAIDA


def readParkingSpaces():
    while True:
        for i in range(8):
            GPIO.output(ENDERECO_01_GPIO, i & 1)
            GPIO.output(ENDERECO_02_GPIO, (i & 2) >> 1)
            GPIO.output(ENDERECO_03_GPIO, (i & 4) >> 2)

            time.sleep(0.05)

            isParkingSpaceBusy = bool(GPIO.input(SENSOR_DE_VAGA_GPIO))

            firstFloorData['parkingSpacesMap'][i] = isParkingSpaceBusy

def handleEntranceParkingBarrier():
    while True:
        time.sleep(0.05)
        SENSOR_ABERTURA_CANCELA_ENTRADA = GPIO.input(SENSOR_ABERTURA_CANCELA_ENTRADA_GPIO)

        if SENSOR_ABERTURA_CANCELA_ENTRADA:
            GPIO.output(MOTOR_CANCELA_ENTRADA_GPIO, 1)

            while True:
                SENSOR_FECHAMENTO_CANCELA_ENTRADA = GPIO.input(SENSOR_FECHAMENTO_CANCELA_ENTRADA_GPIO)
                if SENSOR_FECHAMENTO_CANCELA_ENTRADA:
                    GPIO.output(MOTOR_CANCELA_ENTRADA_GPIO, 0)

                    firstFloorData['carCount'] = firstFloorData['carCount'] + 1
                    if firstFloorData['isFloorFull'] == GPIO.LOW and firstFloorData['carCount'] == 16:
                        flipFullFloorState()
                    break


def handleExitParkingBarrier():
    while True:
        time.sleep(0.05)

        SENSOR_ABERTURA_CANCELA_SAIDA = GPIO.input(SENSOR_ABERTURA_CANCELA_SAIDA_GPIO)

        if SENSOR_ABERTURA_CANCELA_SAIDA:
            GPIO.output(MOTOR_CANCELA_SAIDA_GPIO, 1)


            while bool(GPIO.input(SENSOR_ABERTURA_CANCELA_SAIDA_GPIO)):
                    pass
            while True:
                SENSOR_FECHAMENTO_CANCELA_SAIDA = GPIO.input(SENSOR_FECHAMENTO_CANCELA_SAIDA_GPIO)
                if SENSOR_FECHAMENTO_CANCELA_SAIDA:
                    time.sleep(0.35)

                    GPIO.output(MOTOR_CANCELA_SAIDA_GPIO, 0)

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
    print('GPIO SINAL_DE_LOTADO_FECHADO_GPIO SET TO', firstFloorData['isFloorFull'])
    GPIO.output(SINAL_DE_LOTADO_FECHADO_GPIO, firstFloorData['isFloorFull'])

threading.Thread(target=readParkingSpaces).start()
threading.Thread(target=handleEntranceParkingBarrier).start()
threading.Thread(target=handleExitParkingBarrier).start()
threading.Thread(target=handleSocketCommunication).start()

