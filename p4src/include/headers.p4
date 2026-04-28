#ifndef _HEADERS_
#define _HEADERS_

#include "types.p4"

header ethernet_h {
    mac_addr_t dst_addr;
    mac_addr_t src_addr;
    bit<16>    ether_type;
}

header ipv4_h {
    bit<4>        version;
    bit<4>        ihl;
    bit<8>        diffserv;
    bit<16>       total_len;
    bit<16>       identification;
    bit<3>        flags;
    bit<13>       frag_offset;
    bit<8>        ttl;
    ip_protocol_t protocol;
    bit<16>       hdr_checksum;
    ipv4_addr_t   src_addr;
    ipv4_addr_t   dst_addr;
}

header icmp_h {
    icmp_type_t msg_type;
    bit<8>      msg_code;
    bit<16>     checksum;
}

header arp_h {
    bit<16>       hw_type;
    ether_type_t  proto_type;
    bit<8>        hw_addr_len;
    bit<8>        proto_addr_len;
    arp_opcode_t  opcode;
}

header arp_ipv4_h {
    mac_addr_t   src_hw_addr;
    ipv4_addr_t  src_proto_addr;
    mac_addr_t   dst_hw_addr;
    ipv4_addr_t  dst_proto_addr;
}

header udp_h {
    bit<16> src_port;
    bit<16> dst_port;
    bit<16> length;
    bit<16> checksum;
}

header switchml_h {
    bit<4> msg_type;
    bit<1> round_end_flag;  
    bit<3> size;
    bit<8> job_number; 
    bit<32> tsi;   
    bit<16> pool_index;
    bit<8> packet_type;
    bit<16> round;
    bit<8> switch_id;
    bit<32> num_workers;
}


header data_h {
    value_t d00;
    value_t d01;
    value_t d02;
    value_t d03;
    value_t d04;
    value_t d05;
    value_t d06;
    value_t d07;
    value_t d08;
    value_t d09;
    value_t d10;
    value_t d11;
    value_t d12;
    value_t d13;
    value_t d14;
    value_t d15;
    value_t d16;
    value_t d17;
    value_t d18;
    value_t d19;
    value_t d20;
    value_t d21;
    value_t d22;
    value_t d23;
    value_t d24;
    value_t d25;
    value_t d26;
    value_t d27;
    value_t d28;
    value_t d29;
    value_t d30;
    value_t d31;
}

struct header_t {
    ethernet_h     ethernet; // 14
    ipv4_h         ipv4; // 20
    udp_h          udp; // 8
    switchml_h     switchml; // 16
    data_h         d0;  // 128
}

#endif /* _HEADERS_ */
