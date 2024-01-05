#!/usr/bin/python3
"""File transfer server program for sending multiple files"""

import sys
import os
import pdb

import rdt2 as rdt
PAYLOAD=rdt.PAYLOAD
DROP_RATE = 0.1
ERROR_RATE=0.1
FOLDER_RELATIVE_PATH = "objects"
CLIENT_IP="localhost"

def send_file(filepath, server_socket):
    """
    Function to handle the sending of a single file.
    """
    try:
        with open(filepath, 'rb') as file:
            file_length = os.path.getsize(filepath)
            filename = os.path.basename(filepath)
            pdb.set_trace()
            print(f"[INFO]Sending {filename} ({file_length} bytes)")

            # Sending file size and file name
            rdt.rdt_send(server_socket, str(file_length).encode("ascii"))
            rdt.rdt_send(server_socket, filename.encode("ascii"))

            # Wait for client response
            response = rdt.rdt_recv(server_socket, PAYLOAD)
            if response == b'':
                return
            elif response == b'ERROR':
                print("[INFO]Client error in file reception.")
                return

            # File transfer
            sent = 0
            while sent < file_length:
                data = file.read(PAYLOAD)
                if not data:
                    break
                pdb.set_trace()
                sent += rdt.rdt_send(server_socket, data)
                print(f"[INFO]Server progress: {sent} / {file_length}")

            print(f"[INFO]Completed sending {filename}")

    except OSError as e:
        print(f"[INFO]Error opening file {filepath}: {e}")

def main():


    # Check the number of input arguments


    directory = FOLDER_RELATIVE_PATH
    if not os.path.isdir(directory):
        print(f"Directory {directory} does not exist.")
        return -1

    rdt.rdt_network_init(DROP_RATE, ERROR_RATE)

    server_socket = rdt.rdt_socket()
    if server_socket is None:
        sys.exit(0)

    if rdt.rdt_bind(server_socket, rdt.SPORT) == -1:
        print("[INFO]Cannot bin server socket")
        sys.exit(0)

    if rdt.rdt_peer(CLIENT_IP, rdt.CPORT) == -1:
        print("[INFO]Cannot connect client socket")
        sys.exit(0)

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            send_file(filepath, server_socket)

    rdt.rdt_close(server_socket)
    print("Server program terminated")

if __name__ == "__main__":
    main()
