import socket

import checksum

WAIT_FOR_CALL = 0
WAIT_FOR_ACK_OR_NAK = 1


UDP_IP = "localhost"
UDP_PORT = 8000
BUFFER_SIZE = 1024


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

    while True:
        if current_state == WAIT_FOR_CALL:
            print("Waiting for call from above...")
            data, client_address = rdt_rcv()
            rdt_send("DUMMYFILE".encode(), client_address)

        elif current_state == WAIT_FOR_ACK_OR_NAK:
            print("Waiting for ACK...")
            data, client_address = rdt_rcv()
