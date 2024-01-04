import socket


def receive_file(server_socket, file_path):
    with open(file_path, 'wb') as file:
        while True:
            data = server_socket.recv(1024)
            if data.endswith(b"EOF"):
                file.write(data[:-3])
                break
            file.write(data)


def tcp_client(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    print(f"Connected to server {host}:{port}")

    large_file = 'received_large_file'
    receive_file(client_socket, large_file)

    small_file = 'received_small_file'
    receive_file(client_socket, small_file)

    client_socket.close()


if __name__ == "__main__":
    HOST = '172.17.0.2'
    PORT = 8000
    tcp_client(HOST, PORT)
