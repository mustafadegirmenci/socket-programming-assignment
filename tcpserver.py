import socket


def send_file(client_socket, file_path):
    with open(file_path, 'rb') as file:
        for data in file:
            client_socket.sendall(data)
    client_socket.sendall(b"EOF")


def tcp_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection established from {addr}")

        file_to_send = '../root/objects/large-0.obj'
        print(f"Sending file: {file_to_send}")
        send_file(client_socket, file_to_send)

        file_to_send = '../root/objects/small-0.obj'
        print(f"Sending file: {file_to_send}")
        send_file(client_socket, file_to_send)

        client_socket.close()


if __name__ == "__main__":
    HOST = '172.17.0.2'
    PORT = 8000
    tcp_server(HOST, PORT)
