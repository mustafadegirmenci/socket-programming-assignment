import socket

SERVER_ADDR = "172.17.0.2"
SERVER_PORT = 8000  # socket server port number

client_socket = socket.socket()  # instantiate
client_socket.connect((SERVER_ADDR, SERVER_PORT))  # connect to the server

message = input(" -> ")  # take input

while message.lower().strip() != 'bye':
    client_socket.send(message.encode())  # send message
    data = client_socket.recv(1024).decode()  # receive response

    print('Received from server: ' + data)  # show in terminal

    message = input(" -> ")  # again take input

client_socket.close()  # close the connection