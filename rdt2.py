import socket
import random
import struct
import select
import hashlib
import pdb

# Constants
PAYLOAD = 1000
CPORT = 8000
SPORT = 8001
TIMEOUT = 0.05
TWAIT = 10 * TIMEOUT
TYPE_DATA = 12
TYPE_ACK = 11
MSG_FORMAT = 'B?32sH'  # Adjusted for MD5 checksum (32 bytes)
HEADER_SIZE = 38  # Adjusted for MD5 checksum size

# Global variables
peeraddr = ()
LOSS_RATE = 0.1
ERR_RATE = 0.1
data_buffer = []
send_seq_num = 0
recv_seq_num = 0
last_ack_no = None


# Function to calculate MD5 checksum
def md5_checksum(data):
    return hashlib.md5(data).hexdigest().encode()


# Functions using MD5 checksum
def udt_send(sockd, peer_addr, byte_msg):
    global LOSS_RATE, ERR_RATE
    if peer_addr == ():
        print("Socket send error: Peer address not set yet")
        return -1
    else:
        drop = random.random()
        if drop < LOSS_RATE:
            print("WARNING: Packet lost in unreliable layer")
            return len(byte_msg)

        corrupt = random.random()
        if corrupt < ERR_RATE:
            err_bytearr = bytearray(byte_msg)
            pos = random.randint(0, len(byte_msg) - 1)
            err_bytearr[pos] ^= 0xFF  # Corrupt the byte
            err_msg = bytes(err_bytearr)
            print("WARNING: Packet corrupted in unreliable layer")
            return sockd.sendto(err_msg, peer_addr)
        else:
            return sockd.sendto(byte_msg, peer_addr)


def udt_recv(sockd, length):
    (rmsg, peer) = sockd.recvfrom(length)
    return rmsg


def make_data(seq_num, data):
    global TYPE_DATA, MSG_FORMAT
    checksum = md5_checksum(data)
    msg_format = struct.Struct(MSG_FORMAT)
    init_msg = msg_format.pack(TYPE_DATA, seq_num, checksum, socket.htons(len(data))) + data
    return init_msg


def rdt_network_init(drop_rate, err_rate):
    """
    Initialize network properties for RDT.
    """
    random.seed()
    global LOSS_RATE, ERR_RATE
    LOSS_RATE = float(drop_rate)
    ERR_RATE = float(err_rate)
    print(f"Drop rate: {LOSS_RATE}, Error rate: {ERR_RATE}")


def rdt_socket():
    """
    Create an RDT socket.

    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return sock
    except socket.error as err_msg:
        print("Socket creation error: ", err_msg)
        return None


def rdt_bind(sockd, port):

    #Bind the RDT socket to a specified port.


    try:
        sockd.bind(("", port))
        return 0
    except socket.error as err_msg:
        print("Socket bind error: ", err_msg)
        return -1


def rdt_peer(peer_ip, port):

    global peeraddr
    peeraddr = (peer_ip, port)


def unpack_helper(msg):
    global MSG_FORMAT
    size = struct.calcsize(MSG_FORMAT)
    (msg_type, seq_num, recv_checksum, payload_len), payload = struct.unpack(MSG_FORMAT, msg[:size]), msg[size:]
    return (msg_type, seq_num, recv_checksum, socket.ntohs(payload_len)), payload


def is_corrupt(recv_pkt):
    global MSG_FORMAT
    (msg_type, seq_num, recv_checksum, payload_len), payload = unpack_helper(recv_pkt)
    calc_checksum = md5_checksum(payload)
    return recv_checksum != calc_checksum


# Adjusted functions for MD5 checksum
def make_ack(seq_num):
    global TYPE_ACK, MSG_FORMAT
    msg_format = struct.Struct(MSG_FORMAT)
    checksum = md5_checksum(b'')  # MD5 checksum for empty payload
    return msg_format.pack(TYPE_ACK, seq_num, checksum, socket.htons(0)) + b''


def cut_msg(byte_msg):
    global PAYLOAD
    # Truncate the message if it exceeds the PAYLOAD size
    return byte_msg[:PAYLOAD] if len(byte_msg) > PAYLOAD else byte_msg


def has_seq(recv_msg, seq_num):
    """Check if the received packet has the expected sequence number."""
    (msg_type, recv_seq_num, _, _), _ = unpack_helper(recv_msg)
    return recv_seq_num == seq_num


def is_data(recv_pkt, seq_num):
    """Check if the received packet is DATA [seq_num]."""
    (pkt_type, pkt_seq, _, _), _ = unpack_helper(recv_pkt)
    return pkt_type == TYPE_DATA and pkt_seq == seq_num


def rdt_send(sockd, byte_msg):
    global PAYLOAD, peeraddr, data_buffer, HEADER_SIZE, send_seq_num, last_ack_no

    # Ensure data not longer than max PAYLOAD
    msg = cut_msg(byte_msg)

    # Make data packet with MD5 checksum
    snd_pkt = make_data(send_seq_num, msg)

    # Attempt to send the packet
    try:
        sent_len = udt_send(sockd, peeraddr, snd_pkt)
    except socket.error as err_msg:
        print("Socket send error: ", err_msg)
        return -1
    print(f"Sent message with sequence number {send_seq_num}, size {sent_len}")

    # Setting up for receiving ACK
    r_sock_list = [sockd]
    recv_expected = False

    while not recv_expected:
        # Wait for ACK or timeout
        r, _, _ = select.select(r_sock_list, [], [], TIMEOUT)
        if r:  # ACK (or DATA) came
            for sock in r:
                # Receive ACK (or DATA)
                try:
                    recv_msg = udt_recv(sock, PAYLOAD + HEADER_SIZE)

                except socket.error as err_msg:
                    print("Socket receive error: ", err_msg)
                    return -1

                # Check if received packet is corrupted or not what we expect
                if is_corrupt(recv_msg) or not is_ack(recv_msg, send_seq_num):

                    print(f"Received corrupted or unexpected packet. Waiting for ACK {send_seq_num}")
                else:
                    print(f"Received expected ACK {send_seq_num}")
                    recv_expected = True
                    send_seq_num ^= 1  # Flip sequence number
        else:  # Timeout occurred
            print("Timeout! Resending the packet.")
            try:
                udt_send(sockd, peeraddr, snd_pkt)
            except socket.error as err_msg:
                print("Socket send error on retry: ", err_msg)
                return -1

    # Subtracting HEADER_SIZE as we're returning the size of data sent
    return sent_len - HEADER_SIZE


def rdt_recv(sockd, length):
    """Wait for a message from the remote peer.

    Input arguments:
    - sockd: The RDT socket object.
    - length: The size of the message to be received.

    Returns:
    - The received bytes message object on success, b'' on error.
    """
    global peeraddr, data_buffer, recv_seq_num, HEADER_SIZE, last_ack_no

    while True:
        # Try to receive packet
        try:
            recv_pkt = udt_recv(sockd, length + HEADER_SIZE)
        except socket.error as err_msg:
            print("Socket receive error: ", err_msg)
            return b''

        # Check if the packet is corrupted or has the wrong sequence number
        if is_corrupt(recv_pkt) or not has_seq(recv_pkt, recv_seq_num):
            if is_corrupt(recv_pkt):
                print("rdt_recv(): Received a corrupted packet.")
            else:
                print(f"rdt_recv(): Received packet with unexpected sequence number. Expected: {recv_seq_num}")

            # Send ACK for the last correctly received packet if available
            if last_ack_no is not None:
                ack_pkt = make_ack(last_ack_no)
                try:
                    udt_send(sockd, peeraddr, ack_pkt)
                except socket.error as err_msg:
                    print("Error sending ACK: ", err_msg)
        else:
            # Correct packet received
            _, payload = unpack_helper(recv_pkt)
            print(f"rdt_recv(): Correct packet received with sequence number {recv_seq_num}.")

            # Send ACK for the received packet
            try:
                ack_pkt = make_ack(recv_seq_num)
                udt_send(sockd, peeraddr, ack_pkt)
            except socket.error as err_msg:
                print("Error sending ACK: ", err_msg)
                return b''

            # Update the sequence number and return payload
            last_ack_no = recv_seq_num
            recv_seq_num ^= 1  # Toggle sequence number for next expected packet
            return payload


def is_ack(recv_pkt, seq_num):
    global TYPE_ACK

    # Dissect the received packet using unpack_helper
    (msg_type, recv_seq_num, _, _), _ = unpack_helper(recv_pkt)

    # Check if the packet type is ACK and the sequence number matches
    return msg_type == TYPE_ACK and recv_seq_num == seq_num


def rdt_close(sockd):
    """
    Close the RDT socket after ensuring no pending acknowledgments.

    Args:
    sockd (socket.socket): The RDT socket object.

    Returns:
    None
    """
    global last_ack_no, peeraddr, PAYLOAD, HEADER_SIZE, TWAIT

    r_sock_list = [sockd]
    ok_to_close = False

    while not ok_to_close:
        try:
            r, _, _ = select.select(r_sock_list, [], [], TWAIT)
            if r:  # Incoming activity within TWAIT time
                recv_pkt = udt_recv(sockd, PAYLOAD + HEADER_SIZE)
                if recv_pkt and not is_corrupt(recv_pkt) and is_data(recv_pkt, last_ack_no):
                    # Acknowledge the DATA packet
                    ack_pkt = make_ack(last_ack_no)
                    udt_send(sockd, peeraddr, ack_pkt)
                    print(f"rdt_close(): Sent last ACK[{last_ack_no}]")
            else:  # No activity within TWAIT time
                ok_to_close = True
        except socket.error as err_msg:
            print("rdt_close(): Error during socket operation: ", err_msg)
            break

    # Close the socket
    try:
        sockd.close()
    except socket.error as err_msg:
        print("Socket close error: ", err_msg)
