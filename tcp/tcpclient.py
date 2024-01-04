import socket


# Get the IP address of the current Docker container's interface
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to a remote server (Google's DNS) to retrieve the IP address
        s.connect(('8.8.8.8', 80))
        ip_address = s.getsockname()[0]
    except socket.error:
        ip_address = 'localhost'  # Default to localhost if unable to get the IP address
    finally:
        s.close()
    return ip_address


HOST = get_ip_address()
PORT = 8000  # socket server port number

print(HOST)

client_socket = socket.socket()  # instantiate
client_socket.connect((HOST, PORT))  # connect to the server

message = input(" -> ")  # take input

while message.lower().strip() != 'bye':
    client_socket.send(message.encode())  # send message
    data = client_socket.recv(1024).decode()  # receive response

    print('Received from server: ' + data)  # show in terminal

    message = input(" -> ")  # again take input

client_socket.close()  # close the connection
