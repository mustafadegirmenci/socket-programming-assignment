import socket
import time

import checksum

SERVER_IP = "localhost"
SERVER_PORT = 8000
BUFFER_SIZE = 1024


def rdt_send(message: str, address: (str, int)):
    sock.sendto(message.encode(), address)
    print(f"Sent: {message} to {address}")


def rdt_rcv() -> (bytes, (str, int)):  # data, (ip, port)
    received = sock.recvfrom(BUFFER_SIZE)
    print(f"Received: {received}")
    return received


if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        rdt_send("GIVE ME A DUMMYFILE", (SERVER_IP, SERVER_PORT))
        time.sleep(2)

        data, _ = rdt_rcv()

        if checksum.validate_checksum(data):
            rdt_send("ACK", (SERVER_IP, SERVER_PORT))
        else:
            rdt_send("NAK", (SERVER_IP, SERVER_PORT))
