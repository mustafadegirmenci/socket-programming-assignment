import socket
import threading

SERVER_HOST = "172.17.0.2"
SERVER_PORT = 8000
FOLDER_RELATIVE_PATH = "../root/objects"
BUFFER_SIZE = 1024


def send_single_file(client_address, file_name, sequence_number, udp_socket):
    file_path = f"{FOLDER_RELATIVE_PATH}/{file_name}"
    try:
        print(f"[INFO] Sending file: {file_name} to {client_address}...")
        with open(file_path, "rb") as file:
            data = file.read(BUFFER_SIZE)
            while data:
                packet = f"{sequence_number:04d}".encode() + data
                udp_socket.sendto(packet, client_address)
                sequence_number += 1
                data = file.read(BUFFER_SIZE)
            udp_socket.sendto(f"{sequence_number:04d}EOF".encode(), client_address)
        print(f"[INFO] Finished sending file: {file_name} to {client_address}")

        print(f"[INFO] Waiting for acknowledgment...")
        ack_seq = int(udp_socket.recv(BUFFER_SIZE)[:4].decode())
        if ack_seq == sequence_number:
            print(f"[INFO] Acknowledgment for {file_name} received.\n")
        else:
            print(f"[WARNING] Acknowledgment for {file_name} not received as expected.\n"
                  f"Received:{ack_seq}\n"
                  f"Expected: {sequence_number}\n")

    except FileNotFoundError:
        print(f"[ERROR] File not found: {file_path}")

    except Exception as e:
        print(f"[ERROR] Exception occurred while sending file: {file_path}")
        print(f"[ERROR] Exception details: {e}")


def handle_single_client(client_address, client_request, udp_socket):
    file_count = int(client_request.decode())
    print(f"[INFO] Client {client_address} requested {file_count} files.")
    sequence_number = 1

    for i in range(file_count):
        send_single_file(client_address, f"large-{i}.obj", sequence_number, udp_socket)
        sequence_number += 1
        send_single_file(client_address, f"small-{i}.obj", sequence_number, udp_socket)
        sequence_number += 1
    print(f"[INFO] All {file_count} files sent to {client_address}.")


def respond_file_requests():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((SERVER_HOST, SERVER_PORT))
    print(f"[INFO] Server listening on {SERVER_HOST}:{SERVER_PORT}\n")

    while True:
        client_request, client_address = udp_socket.recvfrom(BUFFER_SIZE)
        print(f"[INFO] Incoming request from: {client_address}")
        thread = threading.Thread(target=handle_single_client, args=(client_address, client_request, udp_socket))
        thread.start()


if __name__ == "__main__":
    respond_file_requests()
