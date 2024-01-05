import socket
import time

import checksum

SERVER_IP = "localhost"
SERVER_PORT = 8000
BUFFER_SIZE = 1024
REQUESTED_FILE_COUNT = 10


def rdt_send(message: str, address: (str, int)):
    sock.sendto(message.encode(), address)
    print(f"Sent: {message} to {address}")


def rdt_rcv() -> (bytes, (str, int)):  # data, (ip, port)
    received = sock.recvfrom(BUFFER_SIZE)
    print(f"Received: {received}")
    return received


if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for requested_file_index in range(REQUESTED_FILE_COUNT):
        rdt_send(f"GIVE ME THE FILE:{requested_file_index}", (SERVER_IP, SERVER_PORT))

        while True:
            time.sleep(1)

            data, _ = rdt_rcv()

            if checksum.validate_checksum(data):
                rdt_send(f"ACKFILE{requested_file_index}", (SERVER_IP, SERVER_PORT))
                requested_file_index += 1
                break
            else:
                rdt_send(f"NAKFILE{requested_file_index}", (SERVER_IP, SERVER_PORT))
