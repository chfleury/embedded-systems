import RPi.GPIO as GPIO
import time
import threading


GPIO.setmode(GPIO.BCM)

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


# def readParkingSpaces():
#     while True:
#         for i in range(8):
#             GPIO.output(22, i & 1)
#             GPIO.output(26, (i & 2) >> 1)
#             GPIO.output(19, (i & 4) >> 2)

#             time.sleep(0.05)

#             print("-----")
#             SENSOR_DE_VAGA = GPIO.input(18)
#             print(SENSOR_DE_VAGA)
#             print("-----")


def handleParkingBarrier():
    while True:
        time.sleep(0.05)
        SENSOR_ABERTURA_CANCELA_ENTRADA = GPIO.input(23)
        print("sensor_abertura", SENSOR_ABERTURA_CANCELA_ENTRADA)
        if SENSOR_ABERTURA_CANCELA_ENTRADA:
            GPIO.output(10, 1)
            while True:
                SENSOR_FECHAMENTO_CANCELA_ENTRADA = GPIO.input(24)
                print("sensor_fechamento", SENSOR_FECHAMENTO_CANCELA_ENTRADA)
                if SENSOR_FECHAMENTO_CANCELA_ENTRADA:
                    GPIO.output(10, 0)
                    break


# threading.Thread(target=readParkingSpaces).start()
threading.Thread(target=handleParkingBarrier).start()

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(17, GPIO.IN)
# GPIO.setup(18, GPIO.OUT)
# input_value = GPIO.input(17)
# GPIO.output(18, GPIO.HIGH)
