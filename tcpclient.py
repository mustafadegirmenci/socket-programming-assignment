import os
import socket

SERVER_HOST = '172.17.0.2'
SERVER_PORT = 8000
FILE_COUNT = 10
FOLDER_RELATIVE_PATH = 'ReceivedObjects'


def receive_single_file(server_socket, file_name):
    print(f"[INFO] Receiving file: {file_name}.")
    file_path = f'{FOLDER_RELATIVE_PATH}/{file_name}'

    try:
        with open(file_path, 'wb') as file:
            while True:
                data = server_socket.recv(1024)
                if data.endswith(b"EOF"):
                    file.write(data[:-3])
                    break
                file.write(data)
        print(f"[INFO] Finished receiving file: {file_path}\n")

    except FileNotFoundError:
        print(f"[ERROR] Could not write to file: {file_path}")

    except Exception as e:
        print(f"[ERROR] Exception occurred during file receive: {e}")


def request_files():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print(f"[INFO] Connected to server: {SERVER_HOST}:{SERVER_PORT}.")

    for i in range(FILE_COUNT):
        large_file_name = f'large-{i}.obj'
        receive_single_file(client_socket, large_file_name)

        small_file_path = f'small-{i}.obj'
        receive_single_file(client_socket, small_file_path)
        print(f"[INFO] Received small file: {small_file_path}.")

    client_socket.close()
    print(f"[INFO] Connection closed.")


if __name__ == "__main__":
    if not os.path.exists(FOLDER_RELATIVE_PATH):
        print(f"[WARNING] Folder '{FOLDER_RELATIVE_PATH}' does not exist. Creating...\n")
        os.mkdir(FOLDER_RELATIVE_PATH)

    request_files()
    print(f"[INFO] Requesting files from the server.")
