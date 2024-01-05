import socket
import time

import checksum

SERVER_IP = "172.17.0.2"
SERVER_PORT = 8000
BUFFER_SIZE = 1024
FILE_COUNT = 10
FOLDER_RELATIVE_PATH = "ReceivedObjects"
TIMEOUT = 0.5


def rdt_send(sock, message: str, address: (str, int)):
    sock.sendto(message.encode(), address)


def rdt_rcv(sock) -> (bytes, (str, int)):  # data, (ip, port)
    received = sock.recvfrom(BUFFER_SIZE)
    return received


def receive_single_file(sock, file_name):
    checksum_and_data, _ = rdt_rcv(sock)

    packet_count = int(checksum_and_data.decode().split(":")[1])
    print(f"[INFO] {packet_count} packets are coming for file {file_name}...")
    file_path = f"{FOLDER_RELATIVE_PATH}/{file_name}"

    packet_index = 0
    with open(file_path, "wb") as file:
        while packet_index < packet_count:
            print("[INFO] Waiting for next packet...")
            sock.settimeout(TIMEOUT)
            try:
                checksum_and_data, _ = rdt_rcv(sock)
                if checksum.validate_checksum(checksum_and_data):
                    file.write(checksum.extract_data(checksum_and_data))
                    print(f"[INFO] Sending ACK{packet_index} for file {file_name}...")
                    rdt_send(sock, f"ACK{packet_index}", (SERVER_IP, SERVER_PORT))
                    packet_index += 1
                else:
                    print(f"[INFO] Sending NAK{packet_index} for file {file_name}.........")
                    rdt_send(sock, f"NAK{packet_index}", (SERVER_IP, SERVER_PORT))
            except socket.timeout:
                print(f"[INFO] Packet not received within {TIMEOUT} seconds. Resending the ACK.")
                rdt_send(sock, f"ACK{packet_index}", (SERVER_IP, SERVER_PORT))

    print(f"[INFO] Received file {file_name}.\n")


def receive_all_files():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rdt_send(sock, f"GIVE ME THE FILES", (SERVER_IP, SERVER_PORT))

    start_time = time.time()
    for file_index in range(FILE_COUNT):
        receive_single_file(sock, f"large-{file_index}.obj")
        receive_single_file(sock, f"small-{file_index}.obj")

    end_time = time.time()
    return end_time - start_time
