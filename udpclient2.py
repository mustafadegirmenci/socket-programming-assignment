import socket
import time

UDP_IP = "localhost"
UDP_PORT = 8000
BUFFER_SIZE = 1024


def send_packet(data, sequence_number):
    message = str(sequence_number) + ':' + data
    sock.sendto(message.encode(), (UDP_IP, UDP_PORT))


def receive_packet():
    data, addr = sock.recvfrom(BUFFER_SIZE)
    print(f"received packet: {data.decode()}")
    return data.decode()


if __name__ == "__main__":

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        # Sending Call 0
        send_packet("Data for Call 0", 0)
        print("Sent Call 0")
        time.sleep(2)  # Simulate delay

        # Wait for ACK0
        print("Waiting for ACK0...")
        data = receive_packet()
        sequence_number, received_data = data.split(':', 1)
        sequence_number = int(sequence_number)

        if sequence_number == 0 and received_data == "ACK0":
            print("Received ACK0")

        # Sending Call 1
        send_packet("Data for Call 1", 1)
        print("Sent Call 1")
        time.sleep(2)  # Simulate delay

        # Wait for ACK1
        print("Waiting for ACK1...")
        data = receive_packet()
        sequence_number, received_data = data.split(':', 1)
        sequence_number = int(sequence_number)

        if sequence_number == 1 and received_data == "ACK1":
            print("Received ACK1")
