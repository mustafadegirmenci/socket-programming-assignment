import socket
import threading

SERVER_HOST = '172.17.0.2'
SERVER_PORT = 8000
FILE_COUNT = 10
FOLDER_RELATIVE_PATH = '../root/objects'
BACKLOG_LIMIT = 5


def send_single_file(client_socket, file_name):
    file_path = f'{FOLDER_RELATIVE_PATH}/{file_name}'
    try:
        print(f"[INFO] Sending file: {file_name}...")
        with open(file_path, 'rb') as file:
            for data in file:
                client_socket.sendall(data)
        client_socket.sendall(b"EOF")
        print(f"[INFO] Finished sending file: {file_path}\n")

    except FileNotFoundError:
        print(f"[ERROR] File not found: {file_path}")

    except Exception as e:
        print(f"[ERROR] Exception occurred while sending file: {file_path}")
        print(f"[ERROR] Exception details: {e}")


def handle_single_client(client_socket, client_address):
    for i in range(FILE_COUNT):
        send_single_file(client_socket, f'large-{i}.obj')
        send_single_file(client_socket, f'small-{i}.obj')

    print(f"[INFO] All files sent.")

    client_socket.close()
    print(f"[INFO] Closed connection with {client_address}.\n")


def respond_file_requests():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(BACKLOG_LIMIT)
    print(f"[INFO] Server listening on {SERVER_HOST}:{SERVER_PORT}\n")

    while True:
        client_socket, client_address = server_socket.accept()
        thread = threading.Thread(target=handle_single_client, args=(client_socket, client_address))
        print(f"[INFO] Incoming connection from: {client_address}\n")
        thread.start()


if __name__ == "__main__":
    respond_file_requests()
