import socket
import json

HOST = "localhost"
PORT = 10582

sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP IPV4
sckt.bind((HOST, PORT))
sckt.listen()
print("Waiting for client...")
connection, address = sckt.accept()

while True:
    data = connection.recv(512)
    print("data", json.loads(data.decode()))
    x = json.loads(data.decode())
    print(x["test"])
    connection.sendall(data)
