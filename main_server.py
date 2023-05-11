import socket

HOST = "localhost"
PORT = 10581

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP IPV4
socket.bind((HOST, PORT))
socket.listen()
print("Waiting for client...")
connection, address = socket.accept()

while True:
    data = connection.recv(512)
    print("data", data)
    connection.sendall(data)
