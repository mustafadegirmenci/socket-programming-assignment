import socket

import checksum

SERVER_IP = "localhost"
SERVER_PORT = 8000
BUFFER_SIZE = 1024
FILE_COUNT = 10


def rdt_send(message: str, address: (str, int)):
    sock.sendto(message.encode(), address)


def rdt_rcv() -> (bytes, (str, int)):  # data, (ip, port)
    received = sock.recvfrom(BUFFER_SIZE)
    return received


if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rdt_send(f"GIVE ME THE FILES", (SERVER_IP, SERVER_PORT))

    for file_index in range(FILE_COUNT):
        data, _ = rdt_rcv()

        packet_count = int(data.decode().split(":")[1])
        print(f"[INFO] {packet_count} packets are coming for file{file_index}...")

        packet_index = 0
        while packet_index < packet_count:
            data, _ = rdt_rcv()
            if checksum.validate_checksum(data):
                print(f"[INFO] Sending ACK{packet_index} for file{file_index}...")
                rdt_send(f"ACK{packet_index}", (SERVER_IP, SERVER_PORT))
                packet_index += 1
            else:
                print(f"[INFO] Sending NAK{packet_index} for file{file_index}.........")
                rdt_send(f"NAK{packet_index}", (SERVER_IP, SERVER_PORT))
        print(f"[INFO] Received file{file_index}.\n")
