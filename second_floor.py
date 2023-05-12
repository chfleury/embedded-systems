import RPi.GPIO as GPIO
import time
import threading
import socket
import json

HOST = "localhost"
PORT = 10582

socketInstance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP IPV4

GPIO.setmode(GPIO.BCM)
GPIO.setup(13, GPIO.OUT)  # ENDERECO_01
GPIO.setup(06, GPIO.OUT)  # ENDERECO_02
GPIO.setup(05, GPIO.OUT)  # ENDERECO_03
GPIO.setup(20, GPIO.IN)  # SENSOR_DE_VAGA
GPIO.setup(08, GPIO.OUT)  # SINAL_DE_LOTADO_FECHADO
GPIO.setup(16, GPIO.IN)  # SENSOR_DE_PASSAGEM_1
GPIO.setup(21, GPIO.IN)  # SENSOR_DE_PASSAGEM_2


def sendMessage(data) -> None:
    data['metadata'] = 'secondFloor'
    try:
        socketInstance.send(str.encode(json.dumps(data))) # TODO
    except:
        pass


def readParkingSpaces() -> None:
    parkingSpacesMap = [False] * 8
    while True:
        for i in range(8):
            time.sleep(0.03) # TODO VERIFY NEED OF THIS SLEEP

            GPIO.output(13, i & 1)
            GPIO.output(06, (i & 2) >> 1)
            GPIO.output(05, (i & 4) >> 2)

            time.sleep(0.03)

            isParkingSpaceBusy = bool(GPIO.input(12))

            parkingSpacesMap[i] = isParkingSpaceBusy

        print("Second Floor Parking Spaces: ", parkingSpacesMap)
       
        sendMessage({
            "parkingSpacesMap": parkingSpacesMap
        })

def handleSecondFloorEntrance() -> None:
    sensorOneTime = False
    sensorTwoTime = False

    while True:
        SENSOR_DE_PASSAGEM_1 = GPIO.input(16)
        SENSOR_DE_PASSAGEM_2 = GPIO.input(21)


        if SENSOR_DE_PASSAGEM_1:
            sensorOneTime = True

            if sensorTwoTime :
                print('saiu para o primeiro andar')
                sensorOneTime = False
                sensorTwoTime = False
            else: time.sleep(0.1)

        if SENSOR_DE_PASSAGEM_2:
            sensorTwoTime = True

            if sensorOneTime:
                print('entrou para o segundo andar')
                sensorOneTime = False
                sensorTwoTime = False
            else: time.sleep(0.1)

def handleSocketCommunication() -> None:
    while True:
        socketInstance.connect((HOST, PORT))

        while True:
            try:
                data = socketInstance.recv(64)
                print("data", json.loads(data.decode()))
            except:
                break


def main():
    threading.Thread(target=handleSocketCommunication).start()
    threading.Thread(target=readParkingSpaces).start()

main()