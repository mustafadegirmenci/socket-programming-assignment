import socket

import checksum

WAIT_FOR_CALL = 0
WAIT_FOR_ACK_OR_NAK = 1

UDP_IP = "localhost"
UDP_PORT = 8000
BUFFER_SIZE = 1024
MAX_REQUESTED_FILE_COUNT = 10


def rdt_send(message: bytes, address: (str, int)):
    cs = checksum.calculate_checksum(message)
    message_with_checksum = cs + message

    sock.sendto(message_with_checksum, address)
    print(f"Sent: {message_with_checksum} to {address}")


def rdt_rcv() -> (bytes, (str, int)):  # data, (ip, port)
    received = sock.recvfrom(BUFFER_SIZE)
    print(f"Received: {received}")
    return received


if __name__ == "__main__":
    current_state = WAIT_FOR_CALL
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    requested_file_index = 0

    while True:
        if current_state == WAIT_FOR_CALL:
            print(f"\nWaiting for file request...")
            data, client_address = rdt_rcv()

            requested_file_index = data.decode().split(":")[1]
            if requested_file_index == MAX_REQUESTED_FILE_COUNT:
                continue

            rdt_send(f"DUMMYFILE{requested_file_index}".encode(), client_address)
            current_state = WAIT_FOR_ACK_OR_NAK

        elif current_state == WAIT_FOR_ACK_OR_NAK:
            print(f"\nWaiting for ACKFILE{requested_file_index}...")
            data, client_address = rdt_rcv()

            if data.decode() == f"ACKFILE{requested_file_index}":
                current_state = WAIT_FOR_CALL
            else:
                print(f"Sending again...")
                rdt_send(f"DUMMYFILE{requested_file_index}".encode(), client_address)
