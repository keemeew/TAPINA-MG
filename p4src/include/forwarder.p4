#ifndef _FORWARDER_
#define _FORWARDER_

#include "configuration.p4"
#include "types.p4"
#include "headers.p4"

control Forwarder(
    in header_t hdr,
    inout standard_metadata_t standard_metadata,
    inout metadata_t meta){

    action set_egress_port(bit<9> egress_port) {
        standard_metadata.egress_spec = egress_port;
    }

    action flood(bit<16> flood_mgid) {
        standard_metadata.mcast_grp = flood_mgid;
       
    }

    table forward {
        key = {
            meta.switchml_md.worker_type: exact;
            meta.switch_id: ternary;
            hdr.switchml.job_number: ternary;
            hdr.switchml.packet_type : ternary;
            hdr.switchml.msg_type : exact;
            hdr.ipv4.identification : ternary;
        }
        actions = {
            set_egress_port;
            flood;
        }
        const entries = {
            #include "/home/tofino/TAPINA/p4src/rule/rule_generator/rules/tapina/s1_forward_entries.p4"
            #include "/home/tofino/TAPINA/p4src/rule/rule_generator/rules/tapina/s3_forward_entries.p4"
            #include "/home/tofino/TAPINA/p4src/rule/rule_generator/rules/tapina/s7_forward_entries.p4"
        }
    }
    apply {
        forward.apply();
    }
}

#endif /* _FORWARDER_ */
