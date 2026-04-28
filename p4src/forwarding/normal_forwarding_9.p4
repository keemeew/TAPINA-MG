/* -*- P4_16 -*- */

#include <core.p4>
#include <v1model.p4>

typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

header ethernet_t {
		macAddr_t dstAddr;
		macAddr_t srcAddr;
		bit<16>   etherType;
}

header ipv4_t {
		bit<4>    version;
		bit<4>    ihl;
		bit<8>    dscp;
		bit<16>   totalLen;
		bit<16>   identification;
		bit<3>    flags;
		bit<13>   fragOffset;
		bit<8>    ttl;
		bit<8>    protocol;
		bit<16>   hdrChecksum;
		ip4Addr_t srcAddr;
		ip4Addr_t dstAddr;
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
    bit<8> last_packet_flag;
}

struct header_t {
    ethernet_t     ethernet; // 14
    ipv4_t         ipv4; // 20
    udp_h          udp; // 8
    switchml_h     switchml; // 16
}

struct metadata {}

parser MyParser(packet_in pkt,
                out header_t hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {
		state start {
			transition parse_ethernet;
		}

		state parse_ethernet {
			pkt.extract(hdr.ethernet);
			transition parse_ipv4;
		}

		state parse_ipv4 {
			pkt.extract(hdr.ipv4);
			transition parse_udp;
		}

		state parse_udp {
			pkt.extract(hdr.udp);
			transition  parse_switchml;
		}

		state parse_switchml {
			pkt.extract(hdr.switchml);
			transition accept;
		}
}

control MyDeparser(packet_out packet, 
                   in header_t hdr) {
		apply {
				packet.emit(hdr);
		}
}

control MyVerifyChecksum(inout header_t hdr, inout metadata meta) {
		apply {  }
}

control MyIngress(inout header_t hdr,
				  inout metadata meta,
				  inout standard_metadata_t standard_metadata) {

	action set_egress_port(bit<9> egress_spec, bit<48> dst_mac, bit<48> src_mac) {
		standard_metadata.egress_spec = egress_spec;
		hdr.ethernet.srcAddr = src_mac;
		hdr.ethernet.dstAddr = dst_mac;
		hdr.ipv4.ttl=hdr.ipv4.ttl-1;
	}

	table tb_forward {
		key = {
			hdr.ethernet.srcAddr : ternary;
			hdr.switchml.job_number : exact;
			hdr.switchml.msg_type : exact;
			hdr.ipv4.srcAddr: exact;
		}
		actions = {
			set_egress_port;
			NoAction;
		}
		const entries = {
			#include "/home/tofino/TAPINA/p4src/rule/rule_generator/rules/normal/s9_tb_forward_entries.p4"
		}
		const default_action = NoAction();
	}

	apply {
		tb_forward.apply();				
	}
}

control MyEgress(inout header_t hdr,
			 	 inout metadata meta,
			 	 inout standard_metadata_t standard_metadata) {
	
	apply {}
}

control MyComputeChecksum(inout header_t hdr, inout metadata meta) {
		apply {}
}

V1Switch(
		MyParser(),
		MyVerifyChecksum(),
		MyIngress(),
		MyEgress(),
		MyComputeChecksum(),
		MyDeparser()
) main;
