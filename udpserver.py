import RDT
import sys

# Include the provided functions here: process_large_object, process_small_object, process_data
# ...
def process_large_object(data, object_id):
    filename = f"large_object_{object_id}.bin"
    with open(filename, 'wb') as file:
        file.write(data)
    print(f"Large object saved to {filename}")
    
small_objects = []
MAX_SMALL_OBJECTS = 10  # Number of small objects to accumulate before writing to file

def process_small_object(data):
    small_objects.append(data)
    if len(small_objects) == MAX_SMALL_OBJECTS:
        with open('small_objects.bin', 'ab') as file:
            for obj in small_objects:
                file.write(obj)
        print(f"{MAX_SMALL_OBJECTS} small objects saved to small_objects.bin")
        small_objects.clear()
        
        large_object_counter = 0

def process_data(data):
    global large_object_counter
    large_object_size_threshold = 100 * 1024  # 100 KB

    if len(data) > large_object_size_threshold:
        large_object_counter += 1
        process_large_object(data, large_object_counter)
    else:
        process_small_object(data)

def main():
    #server_address = ('localhost', 12345)
    server_address = ('172.17.0.2', 12345)
    rdt_instance = RDT.ReliableDataTransfer()
    rdt_instance.rdt_initialize(server_address, bind=True, simulate_unreliability=True)

    try:
        while True:
            data, client_address = rdt_instance.rdt_recv()
            print(f"Received data from {client_address}")
            process_data(data)

    except KeyboardInterrupt:
        print("Server is shutting down.")
    finally:
        rdt_instance.rdt_config(pprint=True)


main()
