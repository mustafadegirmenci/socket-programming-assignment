import RDT
import os
import sys

def create_object(size_in_bytes):
    """Create an object of the specified size."""
    return os.urandom(size_in_bytes)

def main():
    server_ip = '176.219.56.61'
    server_port = 12345
    server_address = (server_ip, server_port)

    rdt_instance = RDT.ReliableDataTransfer()
    rdt_instance.rdt_initialize(server_address, simulate_unreliability=True)

    try:
        for i in range(20):  # Example: 10 large and 10 small objects
            if i % 2 == 0:
                object_size = 1024 * 1024  # 1 MB for large objects
            else:
                object_size = 1024  # 1 KB for small objects

            data_object = create_object(object_size)
            print(f"Sending object {i+1} of size {object_size} bytes...")
            rdt_instance.rdt_send(data_object)

        print("All objects have been sent to the server.")

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

    finally:
        rdt_instance.rdt_config(pprint=True)

if __name__ == "__main__":
    main()
