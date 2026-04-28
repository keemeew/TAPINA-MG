#ifndef _NEXT_STEP_SELECTOR_
#define _NEXT_STEP_SELECTOR_

#include "configuration.p4"
#include "types.p4"
#include "headers.p4"

control NextStepSelector(
    inout header_t hdr,
    inout standard_metadata_t standard_metadata,
    inout metadata_t meta){

    action finish_consume() {
        mark_to_drop(standard_metadata);
    }

    action broadcast() {
        hdr.ethernet.src_addr = hdr.ethernet.dst_addr;
        standard_metadata.egress_spec = TEST_OUTPUT_PORT;
        hdr.switchml.packet_type = 1;
    }

    action retransmit() {
        standard_metadata.egress_spec = TEST_OUTPUT_PORT;
        meta.switchml_md.packet_type = 2;
        hdr.switchml.packet_type = (bit<8>)meta.switchml_md.packet_type;
    }

    action drop() {
        mark_to_drop(standard_metadata);
        hdr.switchml.packet_type = 3;
    }

    table next_step {
        key = {
            meta.switchml_md.packet_type : ternary;
            meta.switchml_md.first_last_flag : ternary; 
            meta.switchml_md.map_result : ternary;
        }
        actions = {
            finish_consume;
            broadcast;
            retransmit;
            drop;
        }

        const entries = {
            (4, 1, 0) : broadcast();

            (4, _, 0) : finish_consume();

            (4, 0, _) : retransmit();

            (4, _, _) : drop();
        }

        const default_action = drop();
    }

    apply {
        next_step.apply();
    }
}

#endif /* _NEXT_STEP_SELECTOR_ */
