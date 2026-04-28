#ifndef _UDP_RECEIVER_
#define _UDP_RECEIVER_

#include "configuration.p4"
#include "types.p4"
#include "headers.p4"

control UDPReceiver(
    inout header_t hdr,
    inout standard_metadata_t standard_metadata,
    inout metadata_t meta){

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action forward() {
        meta.switchml_md.packet_type = 3;
    }
    action set_bitmap(
        bit<16> mgid, 
        bit<16> worker_id,
        bit<8> num_workers, 
        bit<32> worker_bitmap, 
        bit<2> worker_type
        ) {

        meta.worker_bitmap           = worker_bitmap;
        meta.switchml_md.num_workers = num_workers;
        hdr.switchml.num_workers = (bit<32>)num_workers;

        meta.switchml_md.mgid = mgid;

        meta.switchml_md.packet_size = hdr.switchml.size;
        
        meta.switchml_md.round_end_flag = hdr.switchml.round_end_flag; 
        meta.switchml_md.round = hdr.switchml.round;

        meta.switchml_md.worker_type = worker_type;
        meta.switchml_md.worker_id = worker_id;
        hdr.ipv4.identification = worker_id;
        meta.switchml_md.dst_port = hdr.udp.src_port;
        meta.switchml_md.src_port = hdr.udp.dst_port;
        meta.switchml_md.tsi = hdr.switchml.tsi;
        meta.switchml_md.job_number = hdr.switchml.job_number;

        meta.switchml_md.pool_index = hdr.switchml.pool_index[13:0] ++ hdr.switchml.pool_index[15:15];
    }


    table receive_udp {
        key = {
            standard_metadata.ingress_port   : ternary;
            hdr.ethernet.src_addr     : ternary;
            hdr.ethernet.dst_addr     : ternary;
            hdr.ipv4.src_addr         : ternary;
            hdr.ipv4.dst_addr         : ternary;
            hdr.udp.dst_port          : ternary;
            hdr.switchml.job_number  : exact;
            meta.switch_id            : ternary;
        }

        actions = {
            drop;
            set_bitmap;
            @defaultonly forward;
        }

        const entries = {
            #include "/home/tofino/TAPINA/p4src/rule/rule_generator/rules/tapina/s1_receive_udp_entries.p4"
            #include "/home/tofino/TAPINA/p4src/rule/rule_generator/rules/tapina/s3_receive_udp_entries.p4"
            #include "/home/tofino/TAPINA/p4src/rule/rule_generator/rules/tapina/s7_receive_udp_entries.p4"
        }
        const default_action = forward;
    }

    apply {
        receive_udp.apply();
    }
}

#endif /* _UDP_RECEIVER_ */
