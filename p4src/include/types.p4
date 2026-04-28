#ifndef _TYPES_
#define _TYPES_

#include "configuration.p4"

// Mirror types
typedef bit<3> mirror_type_t;

const mirror_type_t MIRROR_TYPE_I2E = 1;
const mirror_type_t MIRROR_TYPE_E2E = 2;

// Ethernet-specific types
typedef bit<48> mac_addr_t;
typedef bit<16> ether_type_t;

const ether_type_t ETHERTYPE_IPV4   = 16w0x0800;
const ether_type_t ETHERTYPE_ARP    = 16w0x0806;
const ether_type_t ETHERTYPE_ROCEv1 = 16w0x8915;

// IPv4-specific types;
typedef bit<32> ipv4_addr_t;
enum bit<8> ip_protocol_t {
    ICMP = 1,
    UDP  = 17
}

// ARP-specific types
enum bit<16> arp_opcode_t {
    REQUEST = 1,
    REPLY   = 2
}

// ICMP-specific types
enum bit<8> icmp_type_t {
    ECHO_REPLY   = 0,
    ECHO_REQUEST = 8
}

// UDP-specific types;
typedef bit<16> udp_port_t;

const udp_port_t UDP_PORT_ROCEV2        =   4791;
const udp_port_t UDP_PORT_SWITCHML_BASE = 0xbee0;
const udp_port_t UDP_PORT_SWITCHML_MASK = 0xfff0;

// IB/RoCE-specific types:
typedef bit<128> ib_gid_t;
typedef bit<24> sequence_number_t;
typedef bit<24> queue_pair_t;
typedef bit<32> rkey_t;
typedef bit<64> addr_t;

// UC opcodes
enum bit<8> ib_opcode_t {
    UC_SEND_FIRST                = 8w0b00100000,
    UC_SEND_MIDDLE               = 8w0b00100001,
    UC_SEND_LAST                 = 8w0b00100010,
    UC_SEND_LAST_IMMEDIATE       = 8w0b00100011,
    UC_SEND_ONLY                 = 8w0b00100100,
    UC_SEND_ONLY_IMMEDIATE       = 8w0b00100101,
    UC_RDMA_WRITE_FIRST          = 8w0b00100110,
    UC_RDMA_WRITE_MIDDLE         = 8w0b00100111,
    UC_RDMA_WRITE_LAST           = 8w0b00101000,
    UC_RDMA_WRITE_LAST_IMMEDIATE = 8w0b00101001,
    UC_RDMA_WRITE_ONLY           = 8w0b00101010,
    UC_RDMA_WRITE_ONLY_IMMEDIATE = 8w0b00101011
}

typedef bit<(max_num_queue_pairs_log2)> queue_pair_index_t; 

enum bit<2> worker_type_t {
    FORWARD_ONLY = 0,
    SWITCHML_UDP = 1, 
    ROCEv2       = 2 
}

typedef bit<16> worker_id_t; 
typedef bit<32> worker_bitmap_t;
struct worker_bitmap_pair_t {
    worker_bitmap_t first;
    worker_bitmap_t second;
}

typedef bit<8> num_workers_t;
struct num_workers_pair_t {
    num_workers_t first;
    num_workers_t second;
}

typedef bit<15> pool_index_t;
typedef bit<14> pool_index_by2_t;
typedef bit<16> worker_pool_index_t;

typedef bit<32> value_t;
struct value_pair_t {
    value_t first;
    value_t second;
}

typedef bit<16> exponent_t;
struct exponent_pair_t {
    exponent_t first;
    exponent_t second;
}

enum bit<3> packet_size_t {
    IBV_MTU_128  = 0,
    IBV_MTU_256  = 1,
    IBV_MTU_512  = 2,
    IBV_MTU_1024 = 3
}

typedef bit<16> drop_probability_t;

typedef bit<32> counter_t;

typedef bit<4> packet_type_underlying_t;
enum bit<4> packet_type_t {
    MIRROR     = 0x0,
    BROADCAST  = 0x1,
    RETRANSMIT = 0x2,
    IGNORE     = 0x3,
    CONSUME0   = 0x4,
    CONSUME1   = 0x5,
    CONSUME2   = 0x6,
    CONSUME3   = 0x7,
    HARVEST0   = 0x8,
    HARVEST1   = 0x9,
    HARVEST2   = 0xa,
    HARVEST3   = 0xb,
    HARVEST4   = 0xc,
    HARVEST5   = 0xd,
    HARVEST6   = 0xe,
    HARVEST7   = 0xf
}

struct port_metadata_t {
    drop_probability_t ingress_drop_probability;
    drop_probability_t egress_drop_probability;
}

@flexible
header switchml_md_h { 

    bit<16> mgid;

    bit<13> recirculation_type;
    bit<1> round_end_flag; 

    bit<3> packet_size;

    bit<2>  worker_type;
    bit<16> worker_id; 

    bit<16> src_port;
    bit<16> dst_port;

    bit<4> packet_type;

    bit<16> ether_type_msb;

    bit<15> pool_index;

    bit<8> first_last_flag;

    bit<32> map_result;

    bit<32> worker_bitmap_before;

    bit<32> tsi;
    bit<8> job_number;

    bit<9> ingress_port;

    bit<1> egress_drop_flag; 

    bit<8> num_workers;

    bit<16> round;
}

struct metadata_t {
    switchml_md_h switchml_md;
    worker_bitmap_t worker_bitmap;
    bit<1> pool_set;
    bool checksum_err_ipv4;
    bool update_ipv4_checksum;
    mac_addr_t switch_mac;
    ipv4_addr_t switch_ip;
    bit<1> agg_flag;
    bit<1> action_flag;
    bit<32> sign_bitmap_index;
    bit<32> sign_reg_idx;
    bit<32> sign_vector1;
    bit<32> sign_vector2;
    bit<8> switch_id;
    bit<8> addr_index;
}


#endif /* _TYPES_ */
