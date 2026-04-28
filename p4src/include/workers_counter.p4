#ifndef _WORKERS_COUNTER_
#define _WORKERS_COUNTER_

control WorkersCounter(
    in header_t hdr,
    inout standard_metadata_t standard_metadata,
    inout metadata_t meta){

    register<bit<8>>(register_size) workers_count;

    action count_workers_action() {
        workers_count.read(meta.switchml_md.first_last_flag, (bit<32>)meta.switchml_md.pool_index);
        meta.action_flag = 1;
    }

    action read_count_workers_action() {
        workers_count.read(meta.switchml_md.first_last_flag, (bit<32>)meta.switchml_md.pool_index);
    }

    table count_workers {
        key = {
            meta.switchml_md.num_workers: ternary;
            meta.switchml_md.map_result : ternary;
            meta.switchml_md.packet_type: ternary;
        }
        actions = {
            count_workers_action;
            read_count_workers_action;
            @defaultonly NoAction;
        }
        const entries = {
            (_, 0, 4) : count_workers_action();
            (_, _, 4) : read_count_workers_action();
        }
        const default_action = NoAction;
    }

    apply {
        count_workers.apply();
        if (meta.action_flag == 1) {
            if (meta.switchml_md.first_last_flag == 0) {
                workers_count.write((bit<32>)meta.switchml_md.pool_index,
                                    meta.switchml_md.num_workers - 1);
            } else {
                workers_count.write((bit<32>)meta.switchml_md.pool_index,
                                    meta.switchml_md.first_last_flag - 1);
            }
        }
    }
}

#endif /* _WORKERS_COUNTER_ */
