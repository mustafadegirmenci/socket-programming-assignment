import os
import socket
import time

SERVER_HOST = "172.17.0.2"
SERVER_PORT = 8000
FOLDER_RELATIVE_PATH = 'ReceivedObjects'
FILE_REQUEST_LIMIT = 10


def receive_single_file(server_socket, file_name):
    print(f"[INFO] Receiving file: {file_name}.")
    file_path = f"{FOLDER_RELATIVE_PATH}/{file_name}"

    try:
        with open(file_path, "wb") as file:
            while True:
                data = server_socket.recv(1024)
                if data.endswith(b"EOF"):
                    file.write(data[:-3])
                    break
                file.write(data)
        print(f"[INFO] Finished receiving file: {file_path}")
        print(f"[INFO] The server has been notified.\n")
        server_socket.send(b"File received")

    except FileNotFoundError:
        print(f"[ERROR] Could not write to file: {file_path}")

    except Exception as e:
        print(f"[ERROR] Exception occurred during file receive: {e}")


def request_files(file_count):
    start_time = time.time()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print(f"[INFO] Connected to server: {SERVER_HOST}:{SERVER_PORT}.")

    print(f"[INFO] Requesting {file_count} files from the server.\n")
    client_socket.send(str(file_count).encode())

    for i in range(file_count):
        receive_single_file(client_socket, f"large-{i}.obj")
        receive_single_file(client_socket, f"small-{i}.obj")

    print(f"[INFO] Received all {file_count} files.")
    print(f"[INFO] The server has been notified.\n")

    client_socket.sendall(b"Files received")
    client_socket.close()
    print(f"[INFO] Connection closed.")

    elapsed_time = time.time() - start_time
    return elapsed_time


def request_files_and_measure_time(requested_file_count):
    try:
        if requested_file_count > 10:
            print(f"[WARNING] Requested file count ({requested_file_count}) exceeds the limit.")
            print(f"[WARNING] Requesting {FILE_REQUEST_LIMIT} files.\n")
            requested_file_count = FILE_REQUEST_LIMIT

        if not os.path.exists(FOLDER_RELATIVE_PATH):
            print(f"[WARNING] Folder '{FOLDER_RELATIVE_PATH}' does not exist. Creating...\n")
            os.mkdir(FOLDER_RELATIVE_PATH)

        elapsed_time = request_files(requested_file_count)
        return elapsed_time

    except ValueError:
        print("[ERROR] Please provide a valid integer for file count.")
