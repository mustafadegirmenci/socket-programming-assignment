import socket

import checksum

WAIT_FOR_CALL = 0
WAIT_FOR_ACK_OR_NAK = 1

UDP_IP = "localhost"
UDP_PORT = 8000
BUFFER_SIZE = 1024
FILE_COUNT = 10


def rdt_send(message: bytes, address: (str, int), with_checksum = True):
    if with_checksum:
        cs = checksum.calculate_checksum(message)
        message_with_checksum = cs + message
        sock.sendto(message_with_checksum, address)
    else:
        sock.sendto(message, address)


def rdt_rcv() -> (bytes, (str, int)):  # data, (ip, port)
    received = sock.recvfrom(BUFFER_SIZE)
    return received


if __name__ == "__main__":
    current_state = WAIT_FOR_CALL
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    print(f"[INFO] Waiting for file request...")
    data, client_address = rdt_rcv()

    for file_index in range(FILE_COUNT):
        print(f"[INFO] Sending file {file_index}...")
        packet_count = 3

        print(f"[INFO] Informing client about packet count...")
        rdt_send(f"Packet Count:{packet_count}".encode(), client_address, with_checksum=False)

        packet_index = 0
        while packet_index < packet_count:
            rdt_send(f"file{file_index} - packet{packet_index}".encode(), client_address)

            print(f"[INFO] Waiting for ACK{packet_index}...")
            data, client_address = rdt_rcv()

            if data.decode() == f"ACK{packet_index}":
                print(f"[INFO] Got ACK{packet_index}...")
                packet_index += 1
                continue

            print(f"[INFO] Sending again...")
        print(f"[INFO] File {file_index} sent.\n")
