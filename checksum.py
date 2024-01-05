import hashlib

CHECKSUM_LENGTH = 32


def calculate_checksum(data: bytes) -> bytes:
    hash_function = hashlib.sha256()
    hash_function.update(data)
    cs = hash_function.digest()
    return cs


def validate_checksum(checksum_and_data: bytes) -> bool:
    checksum = checksum_and_data[:CHECKSUM_LENGTH]
    message = checksum_and_data[CHECKSUM_LENGTH:]

    expected_checksum = calculate_checksum(message)

    print(f"\nEXPECTED CS: \n{len(expected_checksum)}, {expected_checksum}")
    print(f"RECEIVED CS: \n{len(checksum)}, {checksum}\n")

    return checksum == expected_checksum
