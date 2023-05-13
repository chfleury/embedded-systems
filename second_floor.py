import RPi.GPIO as GPIO
import time
import threading
import socket
import json

HOST = "localhost"
PORT = 10584

parkingSpacesMap = {
    "parkingSpacesMap": [False] * 8,
    "metadata": "secondFloor"
}

socketInstance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP IPV4

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(13, GPIO.OUT)  # ENDERECO_01
GPIO.setup(6, GPIO.OUT)  # ENDERECO_02
GPIO.setup(5, GPIO.OUT)  # ENDERECO_03
GPIO.setup(20, GPIO.IN)  # SENSOR_DE_VAGA
GPIO.setup(8, GPIO.OUT)  # SINAL_DE_LOTADO_FECHADO
GPIO.setup(16, GPIO.IN)  # SENSOR_DE_PASSAGEM_1
GPIO.setup(21, GPIO.IN)  # SENSOR_DE_PASSAGEM_2


def readParkingSpaces() -> None:
     while True:
        for i in range(8):
            time.sleep(0.03) # TODO VERIFY NEED OF THIS SLEEP

            GPIO.output(13, i & 1)
            GPIO.output(6, (i & 2) >> 1)
            GPIO.output(5, (i & 4) >> 2)

            time.sleep(0.03)

            isParkingSpaceBusy = bool(GPIO.input(20))

            x = bool(int(time.time()) & 1) # TODO
            parkingSpacesMap['parkingSpacesMap'][i] = isParkingSpaceBusy
 
         
 
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
                time.sleep(0.3)
            else: time.sleep(0.3) # TODO

        if SENSOR_DE_PASSAGEM_2:
            sensorTwoTime = True

            if sensorOneTime:
                print('entrou para o segundo andar')
                sensorOneTime = False
                sensorTwoTime = False
                time.sleep(0.3)
            else: time.sleep(0.3)

def handleSocketCommunication() -> None:
    while True:
        try:
            socketInstance.connect((HOST, PORT))
            # print('tentou conect')
            while True:
                try:
                    time.sleep(1) # TODO
                    socketInstance.send(str.encode(json.dumps(parkingSpacesMap))) # TODO

                    data = socketInstance.recv(512)
                    # print("data", json.loads(data.decode()))

                except:
                    # print('break')
                    break
        except:
            pass

def main():
    threading.Thread(target=handleSocketCommunication).start()
    threading.Thread(target=readParkingSpaces).start()
    threading.Thread(target=handleSecondFloorEntrance).start()
main()