import os
import socket
from RDT import ReliableDataTransfer

SERVER_HOST = '172.17.0.2'
SERVER_PORT = 8000
FOLDER_RELATIVE_PATH = 'ReceivedObjects'
FILE_REQUEST_LIMIT = 10

def receive_file(rdt, file_name):
    print(f"[INFO] Receiving file: {file_name}.")
    file_path = os.path.join(FOLDER_RELATIVE_PATH, file_name)

    try:
        with open(file_path, "wb") as file:
            while True:
                data = rdt.rdt_recv()
                if data.endswith(b"EOF"):
                    file.write(data[:-3])
                    break
                file.write(data)
        print(f"[INFO] Finished receiving file: {file_path}")
        rdt.rdt_send(b"File received")

    except FileNotFoundError:
        print(f"[ERROR] Could not write to file: {file_path}")

    except Exception as e:
        print(f"[ERROR] Exception occurred during file receive: {e}")

def request_files(file_count):
    rdt = ReliableDataTransfer()
    rdt.rdt_initialize((SERVER_HOST, SERVER_PORT), bind=False)

    print(f"[INFO] Connected to server: {SERVER_HOST}:{SERVER_PORT}.")

    for i in range(file_count):
        rdt.rdt_send(f"large-{i}.obj".encode())
        receive_file(rdt, f"large-{i}.obj")
        rdt.rdt_send(f"small-{i}.obj".encode())
        receive_file(rdt, f"small-{i}.obj")

    print(f"[INFO] Received all {file_count} files.")
    rdt.rdt_send(b"Files received")
    rdt.socket.close()
    print(f"[INFO] Connection closed.")

if __name__ == "__main__":
    if not os.path.exists(FOLDER_RELATIVE_PATH):
        os.makedirs(FOLDER_RELATIVE_PATH)
    request_files(FILE_REQUEST_LIMIT)
