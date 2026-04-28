from scapy.all import sendp, sniff, bind_layers, sendpfast
from scapy.all import Packet
from scapy.all import Ether, IP, UDP
from scapy.all import BitField, ByteField, SignedIntField
import os
import time
import argparse
import sys
import threading

class Logger:
    def __init__(self, filename="output.txt"):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

parser = argparse.ArgumentParser(description='parser')

parser.add_argument('--packet_number', required=True, type=int, default=100, help='')

class TAPINA_hdr(Packet):
    """ TAPINA Header """
    name = "TAPINA"
    fields_desc = [

        BitField('msg_type', 0, 4),
        BitField('round_end_flag', 0, 1),
        BitField('packet_size_t', 0, 3),
        BitField('job_number', 0,8),
        BitField('packet_id', 0, 32),
        BitField('pool_index', 0, 16),
        BitField('packet_type', 0, 8),
        BitField('round', 0,16),
        BitField('switch_id', 0, 8),
        BitField('num_workers', 0, 32),
    ]

class DATA(Packet):
    """ data Header. """
    name = "data"
    fields_desc = [
        BitField('d00', 0,32),
        BitField('d01', 1,32),
        BitField('d02', 2,32),
        BitField('d03', 3,32),
        BitField('d04', 4,32),
        BitField('d05', 5,32),
        BitField('d06', 6,32),
        BitField('d07', 7,32),
        BitField('d08', 8,32),
        BitField('d09', 9,32),
        BitField('d10', 10,32),
        BitField('d11', 11,32),
        BitField('d12', 12,32),
        BitField('d13', 13,32),
        BitField('d14', 14,32),
        BitField('d15', 15,32),
        BitField('d16', 16,32),
        BitField('d17', 17,32),
        BitField('d18', 18,32),
        BitField('d19', 19,32),
        BitField('d20', 20,32),
        BitField('d21', 21,32),
        BitField('d22', 22,32),
        BitField('d23', 23,32),
        BitField('d24', 24,32),
        BitField('d25', 25,32),
        BitField('d26', 26,32),
        BitField('d27', 27,32),
        BitField('d28', 28,32),
        BitField('d29', 29,32),
        BitField('d30', 30,32),
        BitField('d31', 31,32)
    ]

def receive_packet():
    global iface
    bind_layers(Ether, IP)
    bind_layers(IP, UDP)
    bind_layers(UDP, TAPINA_hdr)
    bind_layers(TAPINA_hdr, DATA)
    print("sniffing on %s" % iface)
    sniff(iface = iface, prn = lambda x: handle_pkt(x))

def handle_pkt(pkt):
    global init_time, logging_file, args, last_packet_flag, cnt
    cnt += 1
    if TAPINA_hdr in pkt:
        if pkt[TAPINA_hdr].packet_type == 3:
            seq_num = pkt[TAPINA_hdr].job_number
            num_workers = pkt[TAPINA_hdr].num_workers
            switch_id = pkt[TAPINA_hdr].switch_id

            print(f"Job ID: {seq_num} | Aggregated swtich : {switch_id} | The number of workers for Job {seq_num}: {num_workers}")
            sys.stdout.flush()
            if seq_num == args.packet_number:
                last_packet_flag = 1

def generate_packets(num_packets, job_id, src_mac, dst_mac, src_ip):
    global args
    pkts = []
    for i in range (1,num_packets+1):
        if i % 2 == 0:
            pre_pkt = Ether(src=src_mac, dst=dst_mac, type = 0x0800) / IP(ihl = 5, proto = 17, src=src_ip) / UDP(sport=40000, dport = 48864)
            pkt = pre_pkt / TAPINA_hdr(msg_type= 0, round_end_flag= 0, packet_size_t=0 , job_number=job_id, packet_id=i,pool_index= 2000*job_id+32768+i, packet_type=4, round= 0, switch_id= 0) / DATA()
            pkts.append(pkt)
        else:
            pre_pkt = Ether(src=src_mac, dst=dst_mac, type = 0x0800) / IP(ihl = 5, proto = 17, src=src_ip) / UDP(sport=40000, dport = 48864)
            pkt = pre_pkt / TAPINA_hdr(msg_type= 0, round_end_flag= 0, packet_size_t=0 , job_number=job_id, packet_id=i,pool_index= 2000*job_id+i, packet_type=4, round= 0, switch_id= 0) / DATA()
            pkts.append(pkt)
    return pkts

def send_packet1():
    global iface, pkts1, pkts2, pkts3, pkts4, pkts5, num_packets, send_flag
    while True:
        if send_flag is True:
            for i in range(0, num_packets):
                sendp(pkts1[i], iface=iface, verbose=False)
            break

def send_packet2():
    global iface, pkts1, pkts2, pkts3, pkts4, pkts5, num_packets, send_flag
    while True:
        if send_flag is True:
            for i in range(0, num_packets):
                sendp(pkts2[i], iface=iface, verbose=False)
            break

def send_packet3():
    global iface, pkts1, pkts2, pkts3, pkts4, pkts5, num_packets, send_flag
    while True:
        if send_flag is True:
            for i in range(0, num_packets):
                sendp(pkts3[i], iface=iface, verbose=False)
            break

def send_packet4():
    global iface, pkts1, pkts2, pkts3, pkts4, pkts5, num_packets, send_flag
    while True:
        if send_flag is True:
            for i in range(0, num_packets):
                sendp(pkts4[i], iface=iface, verbose=False)
            break

def send_packet5():
    global iface, pkts1, pkts2, pkts3, pkts4, pkts5, num_packets, send_flag
    while True:
        if send_flag is True:
            for i in range(0, num_packets):
                sendp(pkts5[i], iface=iface, verbose=False)
            break

def send_and_receive():
    global iface, args, last_packet_flag, logging_file, num_packets, pkts1, pkts2, pkts3, pkts4, pkts5, send_flag, last_packet_flag

    init_time = time.time()
    pkts1 = []
    pkts2 = []
    pkts3 = []
    pkts4 = []
    pkts5 = []

    receive_thread = threading.Thread(target=receive_packet, args=())
    receive_thread.daemon = True    
    receive_thread.start()

    send3_thread = threading.Thread(target=send_packet3, args=())
    send3_thread.daemon = True    
    send3_thread.start()

    num_packets = args.packet_number
    # generate_packets(num_packets, job_id, src_mac, dst_mac, src_ip)
    pkts3 = generate_packets(num_packets, 3, "00:00:0a:00:01:03", "00:01:0a:00:01:03", "10.0.1.3")  ## need to modify for each host

    while time.time() - init_time < 10:
        time.sleep(0.1)

    send_flag= True

    while time.time() - init_time < 60:
        time.sleep(0.1)
    
    time.sleep(10)
    
    sys.exit()

if __name__ == '__main__':
    global iface, args, init_time, send_flag, last_packet_flag, cnt

    sys.stdout = Logger("/home/tofino/TAPINA/results/h3.txt")

    send_flag = False
    last_packet_flag = 0
    cnt = 0

    init_time = time.time()

    args = parser.parse_args()
    iface = "h3-eth0" ## need to modify for each host

    send_and_receive()
