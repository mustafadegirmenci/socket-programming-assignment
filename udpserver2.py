import socket

WAIT_FOR_CALL_0 = 0
WAIT_FOR_ACK_0 = 1
WAIT_FOR_CALL_1 = 2
WAIT_FOR_ACK_1 = 3


UDP_IP = "localhost"
UDP_PORT = 8000
BUFFER_SIZE = 1024


if __name__ == "__main__":
    current_state = WAIT_FOR_CALL_0
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        if current_state == WAIT_FOR_CALL_0:
            print("Waiting for Call 0 from above...")
            data, client_address = sock.recvfrom(BUFFER_SIZE)
            sequence_number, received_data = data.decode().split(':', 1)
            sequence_number = int(sequence_number)

            if sequence_number == 0:
                print("Received Call 0:", received_data)
                sock.sendto((str(sequence_number) + ':' + "ACK0").encode(), client_address)
                current_state = WAIT_FOR_ACK_0

        elif current_state == WAIT_FOR_ACK_0:
            print("Waiting for ACK0...")
            data, client_address = sock.recvfrom(BUFFER_SIZE)
            sequence_number, received_data = data.decode().split(':', 1)
            sequence_number = int(sequence_number)

            if sequence_number == 0 and received_data == "ACK0":
                print("Received ACK0")
                current_state = WAIT_FOR_CALL_1

        elif current_state == WAIT_FOR_CALL_1:
            print("Waiting for Call 1 from above...")
            data, client_address = sock.recvfrom(BUFFER_SIZE)
            sequence_number, received_data = data.decode().split(':', 1)
            sequence_number = int(sequence_number)

            if sequence_number == 1:
                print("Received Call 1:", received_data)
                sock.sendto((str(sequence_number) + ':' + "ACK1").encode(), client_address)
                current_state = WAIT_FOR_ACK_1

        elif current_state == WAIT_FOR_ACK_1:
            print("Waiting for ACK1...")
            data, client_address = sock.recvfrom(BUFFER_SIZE)
            sequence_number, received_data = data.decode().split(':', 1)
            sequence_number = int(sequence_number)

            if sequence_number == 1 and received_data == "ACK1":
                print("Received ACK1")
                current_state = WAIT_FOR_CALL_0
