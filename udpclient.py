import socket
import time

import checksum

SERVER_IP = "172.17.0.2"
SERVER_PORT = 8000
BUFFER_SIZE = 1024
FILE_COUNT = 10
FOLDER_RELATIVE_PATH = "ReceivedObjects"
TIMEOUT = 0.2


def rdt_send(sock, message: str, address: (str, int)):
    sock.sendto(message.encode(), address)


def rdt_rcv(sock) -> (bytes, (str, int)):  # data, (ip, port)
    received = sock.recvfrom(BUFFER_SIZE)
    return received


def receive_single_file(sock, file_name):

    prev_packet_count = 0
    while True:
        try:
            print(f"[INFO] Receiving packet count for file {file_name}.")
            packet_count_info, _ = rdt_rcv(sock)
            packet_count = int(packet_count_info.decode().split(":")[1])
            print(f"[INFO] {packet_count} packets are coming for file {file_name}...")

            prev_packet_count = packet_count
            break
        except socket.timeout:
            while True:
                try:
                    print(f"[INFO] Sending ACK{prev_packet_count - 1}")
                    rdt_send(sock, f"ACK{prev_packet_count - 1}", (SERVER_IP, SERVER_PORT))
                    print(f"[INFO] Sent ACK{prev_packet_count - 1} successfully")
                    break
                except socket.timeout:
                    print(f"[INFO] Timeout occured while sending ACK{prev_packet_count - 1}")
                    continue
            continue

    file_path = f"{FOLDER_RELATIVE_PATH}/{file_name}"

    packet_index = 0
    with open(file_path, "wb") as file:
        sock.settimeout(TIMEOUT)
        while packet_index < packet_count:
            while True:
                try:
                    checksum_and_data, _ = rdt_rcv(sock)
                    packet_valid = checksum.validate_checksum(checksum_and_data)
                    break
                except socket.timeout:
                    while True:
                        try:
                            print(f"[INFO] Sending ACK{packet_index - 1}")
                            rdt_send(sock, f"ACK{packet_index - 1}", (SERVER_IP, SERVER_PORT))
                            print(f"[INFO] Sent ACK{packet_index - 1} successfully")
                            break
                        except socket.timeout:
                            print(f"[INFO] Timeout occured while sending ACK{packet_index}")
                            continue
                    continue

            if packet_valid:
                file.write(checksum.extract_data(checksum_and_data))

                while True:
                    try:
                        print(f"[INFO] Sending ACK{packet_index}")
                        rdt_send(sock, f"ACK{packet_index}", (SERVER_IP, SERVER_PORT))
                        print(f"[INFO] Sent ACK{packet_index} successfully")
                        packet_index += 1
                        break
                    except socket.timeout:
                        print(f"[INFO] Timeout occured while sending ACK{packet_index}")
                        continue
            else:
                while True:
                    try:
                        rdt_send(sock, f"NAK{packet_index}", (SERVER_IP, SERVER_PORT))
                        break
                    except socket.timeout:
                        continue

    print(f"[INFO] Received file {file_name}.\n")


def receive_all_files():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        try:
            rdt_send(sock, f"GIVE ME THE FILES", (SERVER_IP, SERVER_PORT))
            break
        except socket.timeout:
            continue

    start_time = time.time()
    for file_index in range(FILE_COUNT):
        receive_single_file(sock, f"large-{file_index}.obj")
        receive_single_file(sock, f"small-{file_index}.obj")

    end_time = time.time()
    return end_time - start_time
