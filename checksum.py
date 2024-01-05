import hashlib
import random

CHECKSUM_LENGTH = 32


def calculate_checksum(data: bytes) -> bytes:
    hash_function = hashlib.sha256()
    hash_function.update(data)
    return hash_function.digest()


def validate_checksum(checksum_and_data: bytes) -> bool:
    checksum = checksum_and_data[:CHECKSUM_LENGTH]
    message = checksum_and_data[CHECKSUM_LENGTH:]

    expected_checksum = calculate_checksum(message)

    return checksum == expected_checksum


def extract_data(checksum_and_data: bytes) -> bytes:
    message = checksum_and_data[CHECKSUM_LENGTH:]

    return message
