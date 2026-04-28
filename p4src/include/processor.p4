#ifndef _PROCESSOR_
#define _PROCESSOR_

#include "types.p4"
#include "headers.p4"

// Sum calculator
// Each control handles two values
control Processor(
    in value_t value0,
    out value_t value0_out,
    inout switchml_md_h switchml_md) {

    register<bit<32>>(register_size) values;
    register<bit<32>>(register_size) values1;

    action read0_action() {
        values.read(value0_out, (bit<32>)switchml_md.pool_index);

    }

    action write_read0_action() {
        values.write((bit<32>)switchml_md.pool_index, value0);
        value0_out = value0;
    }

    action sum_read0_action() {
        bit<32>read_value;
        values.read(read_value, (bit<32>)switchml_md.pool_index);
        value0_out = read_value + value0;
        values.write((bit<32>)switchml_md.pool_index, value0_out);
    }

    table sum {
        key = {
            switchml_md.worker_bitmap_before : ternary;
            switchml_md.map_result : ternary;
            switchml_md.packet_type: ternary;
        }
        actions = {
            write_read0_action;
            sum_read0_action;
            read0_action;
            NoAction;
        }
        
        const entries = {
            (32w0,    _, 4) : write_read0_action();

            (   _, 32w0, 4) : sum_read0_action();

            (   _,    _, 4) : read0_action();

            (   _,    _, 0xf) : read0_action(); 
        }
        const default_action = NoAction;
    }

    apply {
        sum.apply();
    }
}

#endif /* _PROCESSOR_ */
