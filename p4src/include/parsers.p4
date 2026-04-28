#ifndef _PARSERS_
#define _PARSERS_

#include "types.p4"
#include "headers.p4"

parser MyParser(packet_in pkt,
                out header_t hdr,
		        inout metadata_t meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        pkt.extract(hdr.ethernet);
        transition select(hdr.ethernet.ether_type) {
            ETHERTYPE_IPV4 : parse_ipv4;
            default : accept_regular;
        }
    }

    state parse_ipv4 {
        pkt.extract(hdr.ipv4);
        transition select(hdr.ipv4.ihl, hdr.ipv4.frag_offset, hdr.ipv4.protocol) {
            (5, 0, ip_protocol_t.UDP)  : parse_udp;
            default                    : accept_regular;
        }
    }

    state parse_udp {
        pkt.extract(hdr.udp);
        transition select(hdr.udp.dst_port) {
            UDP_PORT_SWITCHML_BASE &&& UDP_PORT_SWITCHML_MASK : parse_switchml;
            default                                           : accept_regular;
        }
    }

    state parse_switchml {
        pkt.extract(hdr.switchml);
        transition select(hdr.switchml.packet_type){
            4: parse_values;
            1: parse_recirculate;
            3: parse_forwarding;
            default : parse_recirculate;
        }
    }

    state parse_values {
        pkt.extract(hdr.d0);
        meta.switchml_md.setValid();
        meta.switchml_md.packet_type = 4;
        transition accept;
    }

    state parse_recirculate {
        pkt.extract(hdr.d0);
        meta.switchml_md.setValid();
        meta.switchml_md.worker_type = 1;
        transition accept;
    }

    state parse_forwarding {
        pkt.extract(hdr.d0);
        meta.switchml_md.setValid();
        transition accept;
    }


    state accept_regular {
        meta.switchml_md.setValid();
        meta.switchml_md.packet_type = 3;
        transition accept;
    }
}

control MyComputeChecksum(inout header_t  hdr, inout metadata_t meta) {
     apply {
    }
}

#endif /* _PARSERS_ */
