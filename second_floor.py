import RPi.GPIO as GPIO
import time
import threading


GPIO.setmode(GPIO.BCM)

GPIO.setup(21, GPIO.OUT)  # ENDERECO_01
GPIO.setup(20, GPIO.OUT)  # ENDERECO_02
GPIO.setup(16, GPIO.OUT)  # ENDERECO_03
GPIO.setup(12, GPIO.IN)  # SENSOR_DE_VAGA
GPIO.setup(23, GPIO.OUT)  # SINAL_DE_LOTADO_FECHADO
GPIO.setup(25, GPIO.IN)  # SENSOR_DE_PASSAGEM_1
GPIO.setup(24, GPIO.OUT)  # SENSOR_DE_PASSAGEM_2


def readParkingSpaces():
    parkingSpacesMap = [False] * 8
    isFloorFull = True
    while True:
        for i in range(8):
            time.sleep(0.03)

            GPIO.output(21, i & 1)
            GPIO.output(20, (i & 2) >> 1)
            GPIO.output(16, (i & 4) >> 2)

            time.sleep(0.03)

            isParkingSpaceBusy = bool(GPIO.input(12))

            isFloorFull = isFloorFull and isParkingSpaceBusy

            parkingSpacesMap[i] = isParkingSpaceBusy

        print(isFloorFull)

        print("First Floor Parking Spaces: ", parkingSpacesMap)


threading.Thread(target=readParkingSpaces).start()

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(17, GPIO.IN)
# GPIO.setup(18, GPIO.OUT)
# input_value = GPIO.input(17)
# GPIO.output(18, GPIO.HIGH)
