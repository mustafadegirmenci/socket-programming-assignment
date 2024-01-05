
import threading
import rdt2

SERVER_HOST = "172.17.0.2"
SERVER_PORT = 8000
FOLDER_RELATIVE_PATH = "../root/objects"
BACKLOG_LIMIT = 5


def send_single_file(client_socket, client_address, file_name):
    file_path = f"{FOLDER_RELATIVE_PATH}/{file_name}"
    try:
        print(f"[INFO] Sending file: {file_name}...")
        with open(file_path, "rb") as file:
            while True:
                data = file.read(4096)
                if not data:
                    break
                rdt2.rdt_send(client_socket, data)
        rdt2.rdt_send(client_socket, b"EOF")
        print(f"[INFO] Finished sending file: {file_name}")
        print(f"[INFO] Waiting for acknowledgment...")

        ack = rdt2.rdt_recv(client_socket, 1024)
        if ack.decode() == "File received":
            print(f"[INFO] Acknowledgment for {file_name} received.\n")
        else:
            print(f"[WARNING] Acknowledgment for {file_name} not received as expected.\n")

    except FileNotFoundError:
        print(f"[ERROR] File not found: {file_path}")

    except Exception as e:
        print(f"[ERROR] Exception occurred while sending file: {file_path}")
        print(f"[ERROR] Exception details: {e}")


def handle_single_client(client_socket, client_address):
    file_count = int(rdt2.rdt_recv(client_socket, 1024).decode())
    print(f"[INFO] Client {client_address} requested {file_count} files.")

    for i in range(file_count):
        send_single_file(client_socket, client_address, f"large-{i}.obj")
        send_single_file(client_socket, client_address, f"small-{i}.obj")
    print(f"[INFO] All {file_count} files sent.")

    rdt2.rdt_close(client_socket)
    print(f"[INFO] Closed connection with {client_address}.\n")


def respond_file_requests():
    server_socket = rdt2.rdt_socket()
    if server_socket is None:
        print("[ERROR] Failed to create RDT socket")
        return

    if rdt2.rdt_bind(server_socket, SERVER_HOST, SERVER_PORT) < 0:
        print("[ERROR] Failed to bind RDT socket")
        return

    print(f"[INFO] Server listening on {SERVER_HOST}:{SERVER_PORT}\n")

    while True:
        client_socket, client_address = server_socket.accept()
        thread = threading.Thread(target=handle_single_client, args=(client_socket, client_address))
        print(f"[INFO] Incoming connection from: {client_address}\n")
        thread.start()


if __name__ == "__main__":
    rdt2.rdt_network_init(drop_rate=0.1, err_rate=0.1)  # Adjust drop_rate and err_rate as needed
    respond_file_requests()
