import errno
import os
import random
import signal
import socket
import threading
import time
from struct import pack, unpack
from typing import List, Tuple
import hashlib
from dataclasses import dataclass


class UDT_Struct_Counter_FSM:
    def __init__(self):
        self.sent_count = 0
        self.delay_count=0
        self.lost_count=0
        self.corrupt_checksum_count=0
        self.duplicate_count=0
        self.nocorrupt_count =0
        self.received_count=0
        
class RDT_Struct_Counter_FSM:
    def __init__(self):
        self.sent_count = 0
        self.timeout_count=0
        self.ack_count=0
        self.duplicate_ack_count=0
        self.corrupt_before_transmit=0
        self.corrupt_checksum_count=0
        self.unexpected_conditions_sending_part=0
        self.unexpected_conditions_receiving_part=0
        self.received_count=0
        self.duplicate_count=0
        self.nocorrupt_count =0
        
        
    

MAX_DATA_SIZE = 2 ** 15
DELAY_RATE = 0.0
LOSS_RATE = 0.01
CORRUPTION_RATE = 0.001
DUPLICATION_RATE = 0.0001

"""__rdt_stats = {
    'sent': 0,
    'timeout': 0,
    'ack': 0,
    'duplicated_ack': 0,
    'send_corrupt': 0,
    'send_unknown': 0,
    'received': 0,
    'corrupt': 0,
    'duplicated': 0,
    'unknown': 0,
    'safe': 0
}

__udt_stats = {
    'sent': 0,
    'delayed': 0,
    'lost': 0,
    'corrupt': 0,
    'duplicated': 0,
    'safe': 0,
    'received': 0
}"""

RDT_VALUES_FSM = RDT_Struct_Counter_FSM()
UDT_VALUES_FSM = UDT_Struct_Counter_FSM()

class PacketHandler:
    def make_packet(self,data: bytes, seq_num=0b1111, ack=False) -> bytes:
        flags = pack('!B', (seq_num << 4) + ack)
        checksum = self.calculate_md5_checksum(flags + data)
        return checksum + flags + data
    
    def extract_packet(self,pkt: bytes):
        checksum = pkt[:16]
        flags = pkt[16:17]
        data = pkt[17:]
        return List[checksum, data, flags]

    def is_corrupt( self,pkt: bytes) -> bool:
        received_checksum, data, flags = self.extract_packet(pkt)
        calculated_checksum = self.calculate_md5_checksum(flags + data)
        return received_checksum != calculated_checksum

    @staticmethod
    def calculate_md5_checksum(data: bytes) -> bytes:
        md5 = hashlib.md5()
        md5.update(data)
        return md5.digest()



class ReliableDataTransfer:
    socket: socket.socket
    bound = False
    simulate_experiment = False
    init = False
    send_part_seq_num = 0
    recv_part_seq_num = 0
    estimated_rtt = 1.0
    dev_rtt = 0
    packet_handler = PacketHandler()


    def rdt_initialize(self,address: tuple[str, int], bind=False, simulate_unreliability=False) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if bind:
            self.socket.bind(address)
            self.bound = True
        else:
            self.socket.connect(address)

        self.simulate_unreliability = simulate_unreliability
        self.init = True


    def rdt_send(self,data: bytes, address: tuple[str, int] = None) -> int:
        if not self.init:
            raise OSError(errno.EDESTADDRREQ, os.strerror(errno.EDESTADDRREQ) + ':  rdt not initialized')
        if self.bound and address is None:
            raise OSError(errno.EDESTADDRREQ, os.strerror(errno.EDESTADDRREQ))
        elif len(data) > MAX_DATA_SIZE:
            raise OSError(errno.EMSGSIZE, os.strerror(errno.EMSGSIZE))

        sndpkt = self.packet_handler.make_packet(data, self.send_part_seq_num)

        timeout_interval = max(1e-3, self.estimated_rtt + 4 * self.dev_rtt)
        has_timeout = False

        while True:
            size = self.udt_send(sndpkt, address)
            start = time.perf_counter_ns()

            RDT_VALUES_FSM.sent_count+=1

            try:
                self.start_timer(timeout_interval)

                while True:
                    recv_pkt, _ = self.udt_recv(self)
                    end = time.perf_counter_ns()

                    _, flags = self.packet_handler.extract_packet(recv_pkt)

                    if not self.packet_handler.is_corrupt(recv_pkt):
                        if self.is_ack(flags, self.send_part_seq_num):
                            break
                        elif self.is_ack(flags, self.send_part_seq_num ^ 1):
                            RDT_VALUES_FSM.duplicate_ack_count += 1
                        else:  # shouldn't happen
                            RDT_VALUES_FSM.unexpected_conditions_sending_part+= 1
                    else:
                        RDT_VALUES_FSM.corrupt_before_transmit += 1

                self.stop_timer()
            except TimeoutError:
                RDT_VALUES_FSM.timeout_count += 1

                timeout_interval *= 2
                has_timeout = True
            else:
                RDT_VALUES_FSM.ack_count += 1

                self.send_part_seq_num ^= 1

                if not has_timeout:
                    sample_rtt = (end - start) / 1e9
                    self.dev_rtt = 0.75 * self.dev_rtt + 0.25 * abs(self.estimated_rtt - sample_rtt)
                    self.estimated_rtt = 0.875 * self.estimated_rtt + 0.125 * sample_rtt

                return size
            finally:
                self.stop_timer()
                
    def has_seq(self,flags: int, seq_num: int) -> bool:
        return (flags >> 4) == seq_num

    def rdt_recv(self) :
        if not self.init:
            raise OSError(errno.EDESTADDRREQ, os.strerror(errno.EDESTADDRREQ) + ': Call rdt_init')

        while True:
            recv_pkt, address = self.udt_recv()
            RDT_VALUES_FSM.received_count += 1

            if not self.packet_handler.is_corrupt(recv_pkt):
                data, flags =self.packet_handler.extract_packet(recv_pkt)

                if self.has_seq(flags, self.recv_seq_num):
                    RDT_VALUES_FSM.nocorrupt_count += 1

                    send_pkt = self.packet_handler.make_packet(ack=True, seq_num=self.recv_seq_num)
                    self.udt_send(send_pkt, address)

                    self.recv_seq_num ^= 1

                    if self.bound:
                        return data, address
                    else:
                        return data
                elif self.has_seq(flags, self.recv_seq_num ^ 1):
                    RDT_VALUES_FSM.duplicate_count += 1
                else:  # shouldn't happen
                    RDT_VALUES_FSM.unexpected_conditions_sending_part += 1
            else:
                RDT_VALUES_FSM.corrupt_checksum_count += 1

            send_pkt =self.packet_handler.make_packet(ack=True, seq_num=self.recv_seq_num ^ 1)
            self.udt_send(send_pkt, address)

    def handle_error(self,error_code, message):
        raise OSError(error_code, os.strerror(error_code) + ': ' + message)


    def extract(self,pkt: bytes):
        checksum, flags = unpack('!HB', pkt[:3])
        data = pkt[3:]
        return List[data, flags]


    def is_ack(self,flags: int, seq_num: int) -> bool:
        return bool(flags & 0x01) and self.has_seq(flags, seq_num)


    
    def start_timer(self,timeout):
        signal.signal(signal.SIGALRM, lambda _, __: (_ for _ in ()).throw(TimeoutError()))
        signal.setitimer(signal.ITIMER_REAL, timeout)


    def stop_timer(self):
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, signal.SIG_IGN)


    def rdt_config(self,pprint=False):
        if not pprint:
            return {
                'rdt': RDT_VALUES_FSM,
                'udt': UDT_VALUES_FSM
            }

        recv_p = (100 / RDT_VALUES_FSM.received_count) if RDT_VALUES_FSM.received_count > 0 else 0
        sent_p = (100 / RDT_VALUES_FSM.sent_count) if RDT_VALUES_FSM.sent_count > 0 else 0

        print('\nRDT values:')
        print(f"* Received {RDT_VALUES_FSM.received_count} packets")

        if RDT_VALUES_FSM.received_count > 0:
            print(f"  {RDT_VALUES_FSM.nocorrupt_count} ({RDT_VALUES_FSM.nocorrupt_count * recv_p}%) no corrupted packets")
            print(f"  {RDT_VALUES_FSM.corrupt_checksum_count} ({RDT_VALUES_FSM.corrupt_checksum_count * recv_p}%) corrupt with checksum error packets")
            print(f"  {RDT_VALUES_FSM.duplicate_count} ({RDT_VALUES_FSM.duplicate_ack_count* recv_p}%) duplicated packets")
            print(f"  {RDT_VALUES_FSM.unexpected_conditions_receiving_part} ({RDT_VALUES_FSM.unexpected_conditions_receiving_part * recv_p}%) unknown packets")

        print(f"* Sent {RDT_VALUES_FSM.sent_count} packets")

        if RDT_VALUES_FSM.sent_count > 0:
            print(f"  {RDT_VALUES_FSM.ack_count} ({RDT_VALUES_FSM.ack_count * sent_p}%) ACK packets received")
            print(f"  {RDT_VALUES_FSM.duplicate_ack_count} ({RDT_VALUES_FSM.duplicate_ack_count* sent_p}%) duplicated ACK packets received")
            print(f"  {RDT_VALUES_FSM.corrupt_before_transmit} ({RDT_VALUES_FSM.corrupt_before_transmit * sent_p}%) corrupt packets received")
            print(f"  {RDT_VALUES_FSM.unexpected_conditions_sending_part} ({RDT_VALUES_FSM.unexpected_conditions_sending_part * sent_p}%) unknown packets sended")
            print(f"  {RDT_VALUES_FSM.timeout_count} timeout events")

        udt_p = (100 /UDT_VALUES_FSM.sent_count) if UDT_VALUES_FSM.sent_count > 0 else 0

        print('\nUDT values')
        print(f"******* Received {UDT_VALUES_FSM.received_count} packets ******")
        print(f"*******Sent {UDT_VALUES_FSM.sent_count} packets ******")

        if self.simulate_experiment and UDT_VALUES_FSM.sent_count > 0:
            print(f"  {UDT_VALUES_FSM.nocorrupt_count} ({UDT_VALUES_FSM.nocorrupt_count * udt_p}%) safe packets")
            print(f"  {UDT_VALUES_FSM.delay_count} ({UDT_VALUES_FSM.delay_count * udt_p}%) delayed packets")
            print(f"  {UDT_VALUES_FSM.lost_count} ({UDT_VALUES_FSM.lost_count * udt_p}%) lost packets")
            print(f"  {UDT_VALUES_FSM.corrupt_checksum_count} ({UDT_VALUES_FSM.corrupt_checksum_count * udt_p}%) corrupt packets")
            print(f"  {UDT_VALUES_FSM.duplicate_count} ({UDT_VALUES_FSM.duplicate_count * udt_p}%) duplicated packets")


    def udt_send(self,pkt: bytes, address: tuple[str, int] = None, *, _is_recursion=False) -> int:
        UDT_VALUES_FSM.sent_count += 1 if not _is_recursion else 0

        if self.simulate_experiment and not _is_recursion:
            if random.random() < DELAY_RATE:
                UDT_VALUES_FSM.delay_count += 1

                threading.Timer(1e-3, lambda: self.udt_send(pkt, address, _is_recursion=True)).start()

                return len(pkt)
            elif random.random() < LOSS_RATE:
                UDT_VALUES_FSM.lost_count += 1

                return len(pkt)
            elif random.random() < CORRUPTION_RATE:
                UDT_VALUES_FSM.corrupt_checksum_count += 1

                mask = 0x00

                for bit in random.sample(range(8), random.randint(1, 2)):
                    mask |= (1 << bit)

                pkt = bytearray(pkt)
                pkt[random.randrange(len(pkt))] ^= mask
                pkt = bytes(pkt)
            elif random.random() < DUPLICATION_RATE:
                UDT_VALUES_FSM.duplicate_count += 1

                self.udt_send(pkt, address, _is_recursion=True)
            else:
                UDT_VALUES_FSM.nocorrupt_count += 1

        if address is not None:
            return self.socket.sendto(pkt, address)
        else:
            return self.socket.send(pkt)


    def udt_recv(self) :
        data, address = self.socket.recvfrom(MAX_DATA_SIZE)

        UDT_VALUES_FSM.received_count+=1

        return Tuple[ data, address]


__all__ = ['rdt_init', 'rdt_send', 'rdt_recv', 'rdt_stats']