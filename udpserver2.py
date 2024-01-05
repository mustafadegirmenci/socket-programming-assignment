import socket
import threading

SERVER_HOST = "172.17.0.2"
SERVER_PORT = 8000
FOLDER_RELATIVE_PATH = "../root/objects"
BUFFER_SIZE = 4096


def send_single_file(client_address, file_name, udp_socket):
    file_path = f"{FOLDER_RELATIVE_PATH}/{file_name}"
    try:
        print(f"[INFO] Sending file: {file_name} to {client_address}...")
        with open(file_path, "rb") as file:
            data = file.read(BUFFER_SIZE)
            while data:
                udp_socket.sendto(data, client_address)
                data = file.read(BUFFER_SIZE)
        udp_socket.sendto(b"EOF", client_address)
        print(f"[INFO] Finished sending file: {file_name} to {client_address}")
        print(f"[INFO] Waiting for acknowledgment...")

        ack = udp_socket.recv(1024)
        if ack.decode() == "ACK":
            print(f"[INFO] Acknowledgment for {file_name} received.\n")
        else:
            print(f"[WARNING] Acknowledgment for {file_name} not received as expected.\n")

    except FileNotFoundError:
        print(f"[ERROR] File not found: {file_path}")

    except Exception as e:
        print(f"[ERROR] Exception occurred while sending file: {file_path}")
        print(f"[ERROR] Exception details: {e}")


def handle_single_client(client_address, client_request, udp_socket):
    file_count = int(client_request.decode())
    print(f"[INFO] Client {client_address} requested {file_count} files.")

    for i in range(file_count):
        send_single_file(client_address, f"large-{i}.obj", udp_socket)
        send_single_file(client_address, f"small-{i}.obj", udp_socket)
    print(f"[INFO] All {file_count} files sent to {client_address}.")


def respond_file_requests():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((SERVER_HOST, SERVER_PORT))
    print(f"[INFO] Server listening on {SERVER_HOST}:{SERVER_PORT}\n")

    while True:
        client_request, client_address = udp_socket.recvfrom(BUFFER_SIZE)
        print(f"[INFO] Incoming request from: {client_address}")
        handle_single_client(client_address, client_request, udp_socket)


if __name__ == "__main__":
    respond_file_requests()
