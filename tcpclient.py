import socket

SERVER_HOST = '172.17.0.2'
SERVER_PORT = 8000


def receive_single_file(server_socket, file_path):
    with open(file_path, 'wb') as file:
        while True:
            data = server_socket.recv(1024)
            if data.endswith(b"EOF"):
                file.write(data[:-3])
                break
            file.write(data)
    print(f"[INFO] Finished receiving file: {file_path}")


def request_files():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print(f"[INFO] Connected to server: {SERVER_HOST}:{SERVER_PORT}.")

    large_file_path = 'received_large_file'
    receive_single_file(client_socket, large_file_path)
    print(f"[INFO] Received large file: {large_file_path}.")

    small_file_path = 'received_small_file'
    receive_single_file(client_socket, small_file_path)
    print(f"[INFO] Received small file: {small_file_path}.")

    client_socket.close()
    print(f"[INFO] Connection closed.")


if __name__ == "__main__":
    request_files()
    print(f"[INFO] Requesting files from the server.")
