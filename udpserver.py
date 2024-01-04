
from RDT import *

SERVER_HOST = "172.17.0.2"
SERVER_PORT = 8000
FOLDER_RELATIVE_PATH = "../root/objects"

def send_file_via_udp(rdt, client_address, file_name):
    file_path = os.path.join(FOLDER_RELATIVE_PATH, file_name)
    try:
        with open(file_path, "rb") as file:
            while True:
                data = file.read(4096)
                if not data:
                    break
                rdt.rdt_send(data, client_address)
            rdt.rdt_send(b"EOF", client_address)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {file_path}")
    except Exception as e:
        print(f"[ERROR] {e}")

def main():
    rdt = ReliableDataTransfer()
    rdt.rdt_initialize((SERVER_HOST, SERVER_PORT), bind=True)

    while True:
        data, client_address = rdt.rdt_recv()
        if data:
            file_name = data.decode()
            send_file_via_udp(rdt, client_address, file_name)



if __name__ == "__main__":
    main()
