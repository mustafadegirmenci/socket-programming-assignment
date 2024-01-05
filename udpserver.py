import math
import os
import socket

import checksum

SERVER_IP = "172.17.0.2"
SERVER_PORT = 8000
BUFFER_SIZE = 1024
FILE_COUNT = 10
FOLDER_RELATIVE_PATH = "../root/objects"
TIMEOUT = 0.2


def rdt_send(message: bytes, address: (str, int), with_checksum=True):
    if with_checksum:
        cs = checksum.calculate_checksum(message)
        message_with_checksum = cs + message
        sock.sendto(message_with_checksum, address)
    else:
        sock.sendto(message, address)


def rdt_rcv() -> (bytes, (str, int)):  # data, (ip, port)
    received = sock.recvfrom(BUFFER_SIZE)
    return received


def send_single_file(file_name, client_address):
    sock.settimeout(TIMEOUT)
    file_path = f"{FOLDER_RELATIVE_PATH}/{file_name}"
    with open(file_path, "rb") as file:
        print(f"[INFO] Sending file {file_name}...")

        file_size = os.stat(file_path).st_size
        print(f"[INFO] File size is: {file_size} bytes.")
        print(f"[INFO] Buffer size is: {BUFFER_SIZE} bytes.")

        packet_count = math.ceil(os.stat(file_path).st_size / (BUFFER_SIZE - checksum.CHECKSUM_LENGTH))
        print(f"[INFO] Packet count is: {packet_count}.")

        print(f"[INFO] Informing client about packet count...\n")

        while True:
            try:
                print(f"[INFO] Sending packet count for file {file_name}.")
                rdt_send(f"Packet Count:{packet_count}".encode(), client_address, with_checksum=False)
                break
            except socket.timeout:
                print(f"[INFO] Timeout occured while sending packet count for file {file_name}.")
                continue

        packet_index = 0
        while packet_index < packet_count:
            packet = file.read(BUFFER_SIZE - checksum.CHECKSUM_LENGTH)
            while True:
                try:
                    rdt_send(packet, client_address)
                    break
                except socket.timeout:
                    print(f"[INFO] Timeout occurred, while sending packet {packet_index}...")
                    continue

            while True:
                try:
                    data, client_address = sock.recvfrom(BUFFER_SIZE)
                    is_ack = data.decode() == f"ACK{packet_index}"
                    break
                except socket.timeout:
                    print(f"[INFO] Timeout occurred, while receiving ACK{packet_index}...")
                    continue

            if is_ack:
                packet_index += 1
            else:
                print(f"[INFO] Got {data} instead of ACK{packet_index}...")

        print(f"[INFO] File {file_name} sent.\n")


if __name__ == "__main__":
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((SERVER_IP, SERVER_PORT))

        print(f"[INFO] Waiting for file request...")
        data, client_address = rdt_rcv()

        for file_index in range(FILE_COUNT):
            send_single_file(f"large-{file_index}.obj", client_address)
            send_single_file(f"small-{file_index}.obj", client_address)
