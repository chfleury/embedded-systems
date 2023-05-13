import RPi.GPIO as GPIO
import time
import threading
import socket
import json

HOST = "localhost"
PORT = 10582

socketInstance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP IPV4

parkingSpacesMap = {
    "parkingSpacesMap": [False] * 8,
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

            parkingSpacesMap['parkingSpacesMap'][i] = isParkingSpaceBusy

        print("First Floor Parking Spaces: ", parkingSpacesMap['parkingSpacesMap'])


def handleEntranceParkingBarrier():
    while True:
        time.sleep(0.05) # TODO
        SENSOR_ABERTURA_CANCELA_ENTRADA = GPIO.input(23)

        if SENSOR_ABERTURA_CANCELA_ENTRADA:
            GPIO.output(10, 1)

            while True:
                SENSOR_FECHAMENTO_CANCELA_ENTRADA = GPIO.input(24)
                if SENSOR_FECHAMENTO_CANCELA_ENTRADA:
                    GPIO.output(10, 0)
                    break


def handleExitParkingBarrier():
    while True:
        SENSOR_ABERTURA_CANCELA_SAIDA = GPIO.input(25)

        if SENSOR_ABERTURA_CANCELA_SAIDA:
            GPIO.output(17, 1)

            while True:
                SENSOR_FECHAMENTO_CANCELA_SAIDA = GPIO.input(12)
                if SENSOR_FECHAMENTO_CANCELA_SAIDA:
                    GPIO.output(17, 0)
                    break
        time.sleep(0.05) # TODO


def handleSocketCommunication():
    while True:
        try:
            socketInstance.connect((HOST, PORT))
            while True:
                try:
                    time.sleep(0.1) # TODO
                    socketInstance.send(str.encode(json.dumps(parkingSpacesMap))) # TODO

                    data = socketInstance.recv(512).decode()
                    print('data', data)
                    userManualCommands = json.loads(data)

                    print('usermanualcommands', userManualCommands)

                    if userManualCommands['command'] == 'first_floor_full':
                        setFullFloorLedOn()

                except:
                    # print('break')
                    break
        except:
            pass

def setFullFloorLedOn():
    print('entrou aqui pra setar')
    GPIO.output(27, 1)

threading.Thread(target=readParkingSpaces).start()
threading.Thread(target=handleEntranceParkingBarrier).start()
threading.Thread(target=handleExitParkingBarrier).start()
threading.Thread(target=handleSocketCommunication).start()

