import os

import time
import rdt2

SERVER_HOST = '172.17.0.2'
SERVER_PORT = 8000
FOLDER_RELATIVE_PATH = 'ReceivedObjects'
FILE_REQUEST_LIMIT = 10


def receive_single_file(server_socket, file_name):
    print(f"[INFO] Receiving file: {file_name}.")
    file_path = f"{FOLDER_RELATIVE_PATH}/{file_name}"

    try:
        with open(file_path, "wb") as file:
            while True:
                data = rdt2.rdt_recv(server_socket, 1024)
                if data.endswith(b"EOF"):
                    file.write(data[:-3])
                    break
                file.write(data)
        print(f"[INFO] Finished receiving file: {file_path}")
        print(f"[INFO] The server has been notified.\n")
        rdt2.rdt_send(server_socket, b"File received")

    except FileNotFoundError:
        print(f"[ERROR] Could not write to file: {file_path}")

    except Exception as e:
        print(f"[ERROR] Exception occurred during file receive: {e}")


def request_files(file_count):
    start_time = time.time()

    client_socket = rdt2.rdt_socket()
    if client_socket is None:
        print("[ERROR] Failed to create RDT socket")
        return

    rdt2.rdt_peer(SERVER_HOST, SERVER_PORT)

    print(f"[INFO] Requesting {file_count} files from the server.\n")
    rdt2.rdt_send(client_socket, str(file_count).encode())

    for i in range(file_count):
        receive_single_file(client_socket, f"large-{i}.obj")
        receive_single_file(client_socket, f"small-{i}.obj")

    print(f"[INFO] Received all {file_count} files.")
    print(f"[INFO] The server has been notified.\n")

    rdt2.rdt_send(client_socket, b"Files received")
    rdt2.rdt_close(client_socket)
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


if __name__ == "__main__":
    # Adjust the number of files you want to request here
    time_taken = request_files_and_measure_time(5)
    print(f"Total time taken: {time_taken:.2f} seconds")
