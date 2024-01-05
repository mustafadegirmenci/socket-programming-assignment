#!/usr/bin/python3
"""File transfer client program for receiving multiple files"""

import sys
import os
import rdt2 as rdt
PAYLOAD = rdt.PAYLOAD
SERVER_IP = "localhost"
FOLDER_RELATIVE_PATH = "objects"

def receive_file(client_socket, directory):
    """
    Function to handle the reception of a single file.
    """
    # Receive file size
    file_length_data = rdt.rdt_recv(client_socket, PAYLOAD)
    if not file_length_data:
        return False
    file_length = int(file_length_data)

    # Receive file name
    filename_data = rdt.rdt_recv(client_socket, PAYLOAD)
    if not filename_data:
        return False
    filename = filename_data.decode("ascii")
    filepath = os.path.join(directory, filename)

    try:
        with open(filepath, 'wb') as fobj:
            print(f"Receiving {filename} ({file_length} bytes)")

            # Acknowledge file reception
            rdt.rdt_send(client_socket, b'OKAY')

            # File reception
            received = 0
            while received < file_length:
                data = rdt.rdt_recv(client_socket, PAYLOAD)
                if not data:
                    break
                fobj.write(data)
                received += len(data)
                print(f"---- Client progress: {received} / {file_length}")

            print(f"Completed receiving {filename}")
            return True

    except OSError as e:
        print(f"Error writing to file {filepath}: {e}")
        rdt.rdt_send(client_socket, b'ERROR')
        return False

def main():
    directory = sys.argv[2]
    os.makedirs(directory, exist_ok=True)

    rdt.rdt_network_init(sys.argv[3], sys.argv[4])

    client_socket = rdt.rdt_socket()
    if client_socket is None:
        sys.exit(0)

    if rdt.rdt_bind(client_socket, rdt.CPORT) == -1:
        sys.exit(0)

    if rdt.rdt_peer(SERVER_IP, rdt.SPORT) == -1:
        sys.exit(0)

    while True:
        if not receive_file(client_socket, directory):
            break

    rdt.rdt_close(client_socket)
