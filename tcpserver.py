import socket
import threading

SERVER_HOST = '172.17.0.2'
SERVER_PORT = 8000
BACKLOG_LIMIT = 5


def send_single_file(client_socket, file_path):
    with open(file_path, 'rb') as file:
        for data in file:
            client_socket.sendall(data)
    client_socket.sendall(b"EOF")
    print(f"[INFO] Finished sending file: {file_path}")


def handle_single_client(client_socket, addr):
    file_to_send = '../root/objects/large-0.obj'
    send_single_file(client_socket, file_to_send)
    print(f"[INFO] Sending large file: {file_to_send}")

    file_to_send = '../root/objects/small-0.obj'
    send_single_file(client_socket, file_to_send)
    print(f"[INFO] Sending small file: {file_to_send}")

    client_socket.close()
    print(f"[INFO] Connection closed for {addr}")


def respond_file_requests():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(BACKLOG_LIMIT)
    print(f"[INFO] Server listening on {SERVER_HOST}:{SERVER_PORT}.")

    while True:
        client_socket, client_address = server_socket.accept()
        thread = threading.Thread(target=handle_single_client, args=(client_socket, client_address))
        print(f"[INFO] Client connected. {client_address}")
        thread.start()


if __name__ == "__main__":
    respond_file_requests()
    print(f"[INFO] Server started.")
