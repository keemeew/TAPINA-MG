/*
  SwitchML-only variant derived from the uploaded SAINA program.
  SAINA-specific convergence detection and adaptive-k logic removed.
*/

#include <core.p4>
#include <v1model.p4>

#include "include/configuration.p4"
#include "include/types.p4"
#include "include/headers.p4"
#include "include/parsers.p4"
#include "include/forwarder.p4"
#include "include/udp_receiver.p4"
#include "include/udp_sender.p4"
#include "include/workers_counter.p4"
#include "include/processor.p4"
#include "include/next_step_selector.p4"

control MyIngress(
    inout header_t hdr,
    inout metadata_t meta,
    inout standard_metadata_t standard_metadata) {

    action set_switch_id(bit<8> switch_id){
        meta.switch_id = switch_id;
    }

    table tb_set_switch_id {
        key = {
            hdr.ipv4.version : exact;
        }
        actions = {
            set_switch_id;
            NoAction();
        }
        default_action = NoAction();
        size = 1;
    }
    
    register<bit<32>>(num_slots) worker_bitmap;
    register<bit<32>>(num_slots) worker_bitmap1;

    action reconstruct_worker_bitmap_from_worker_id(worker_bitmap_t bitmap) {
        meta.worker_bitmap = bitmap;
    }

    table reconstruct_worker_bitmap {
        key = {
            meta.switchml_md.worker_id : ternary;
        }
        actions = {
            reconstruct_worker_bitmap_from_worker_id;
        }
        const entries = {
            0  &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 0);
            1  &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 1);
            2  &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 2);
            3  &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 3);
            4  &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 4);
            5  &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 5);
            6  &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 6);
            7  &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 7);
            8  &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 8);
            9  &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 9);
            10 &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 10);
            11 &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 11);
            12 &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 12);
            13 &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 13);
            14 &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 14);
            15 &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 15);
            16 &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 16);
            17 &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 17);
            18 &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 18);
            19 &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 19);
            20 &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 20);
            21 &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 21);
            22 &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 22);
            23 &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 23);
            24 &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 24);
            25 &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 25);
            26 &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 26);
            27 &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 27);
            28 &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 28);
            29 &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 29);
            30 &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 30);
            31 &&& 0x1f : reconstruct_worker_bitmap_from_worker_id(1 << 31);
        }
    }

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action check_worker_bitmap_action() {
        meta.switchml_md.map_result = meta.switchml_md.worker_bitmap_before & meta.worker_bitmap;
    }

    action update_worker_bitmap_set0_action() {
        bit<32> read_value;
        worker_bitmap.read(read_value, (bit<32>)meta.switchml_md.pool_index[14:1]);
        meta.switchml_md.worker_bitmap_before = read_value;
        read_value = read_value | meta.worker_bitmap;
        worker_bitmap.write((bit<32>)meta.switchml_md.pool_index[14:1], read_value);

        bit<32> read_value1;
        worker_bitmap1.read(read_value1 , (bit<32>)meta.switchml_md.pool_index[14:1]);
        read_value1 = read_value1 & (~meta.worker_bitmap);
        worker_bitmap1.write((bit<32>)meta.switchml_md.pool_index[14:1], read_value1);

        check_worker_bitmap_action();
    }

    action update_worker_bitmap_set1_action() {
        bit<32> read_value1;
        worker_bitmap1.read(read_value1, (bit<32>)meta.switchml_md.pool_index[14:1]);
        meta.switchml_md.worker_bitmap_before = read_value1;
        read_value1 = read_value1 | meta.worker_bitmap;
        worker_bitmap1.write((bit<32>)meta.switchml_md.pool_index[14:1], read_value1);

        bit<32> read_value;
        worker_bitmap.read(read_value, (bit<32>)meta.switchml_md.pool_index[14:1]);
        read_value = read_value & (~meta.worker_bitmap);
        worker_bitmap.write((bit<32>)meta.switchml_md.pool_index[14:1], read_value);

        check_worker_bitmap_action();
    }

    table update_and_check_worker_bitmap {
        key = {
            meta.switchml_md.pool_index : ternary;
            meta.switchml_md.packet_type : ternary;
        }
        actions = {
            update_worker_bitmap_set0_action;
            update_worker_bitmap_set1_action;
            drop;
            NoAction;
        }
        const entries = {
            (15w0 &&& 15w1, 4) : update_worker_bitmap_set0_action();
            (15w1 &&& 15w1, 4) : update_worker_bitmap_set1_action();
        }
        const default_action = NoAction;
    }

    Forwarder() forwarder;
    UDPReceiver() udp_receiver;
    WorkersCounter() workers_counter;
    NextStepSelector() next_step_selector;

    Processor() value00;
    Processor() value01;
    Processor() value02;
    Processor() value03;
    Processor() value04;
    Processor() value05;
    Processor() value06;
    Processor() value07;
    Processor() value08;
    Processor() value09;
    Processor() value10;
    Processor() value11;
    Processor() value12;
    Processor() value13;
    Processor() value14;
    Processor() value15;
    Processor() value16;
    Processor() value17;
    Processor() value18;
    Processor() value19;
    Processor() value20;
    Processor() value21;
    Processor() value22;
    Processor() value23;
    Processor() value24;
    Processor() value25;
    Processor() value26;
    Processor() value27;
    Processor() value28;
    Processor() value29;
    Processor() value30;
    Processor() value31;

    apply {
        tb_set_switch_id.apply();
        if (meta.switchml_md.packet_type == 4) {
            udp_receiver.apply(hdr, standard_metadata, meta);
            meta.switchml_md.ingress_port = standard_metadata.ingress_port;
        } else if (meta.switchml_md.packet_type == 5 ||
                meta.switchml_md.packet_type == 6 ||
                meta.switchml_md.packet_type == 7) {
            
            reconstruct_worker_bitmap.apply();
        }

        if (meta.switchml_md.packet_type == 4 &&
            meta.switchml_md.worker_type == 1 
            ) {
            
            update_and_check_worker_bitmap.apply();

            workers_counter.apply(hdr, standard_metadata, meta);
        }

        if (meta.switchml_md.packet_type >= 4 && meta.switchml_md.worker_type == 1) {

            value00.apply(hdr.d0.d00, hdr.d0.d00, meta.switchml_md);
            value01.apply(hdr.d0.d01, hdr.d0.d01, meta.switchml_md);
            value02.apply(hdr.d0.d02, hdr.d0.d02, meta.switchml_md);
            value03.apply(hdr.d0.d03, hdr.d0.d03, meta.switchml_md);
            value04.apply(hdr.d0.d04, hdr.d0.d04, meta.switchml_md);
            value05.apply(hdr.d0.d05, hdr.d0.d05, meta.switchml_md);
            value06.apply(hdr.d0.d06, hdr.d0.d06, meta.switchml_md);
            value07.apply(hdr.d0.d07, hdr.d0.d07, meta.switchml_md);
            value08.apply(hdr.d0.d08, hdr.d0.d08, meta.switchml_md);
            value09.apply(hdr.d0.d09, hdr.d0.d09, meta.switchml_md);
            value10.apply(hdr.d0.d10, hdr.d0.d10, meta.switchml_md);
            value11.apply(hdr.d0.d11, hdr.d0.d11, meta.switchml_md);
            value12.apply(hdr.d0.d12, hdr.d0.d12, meta.switchml_md);
            value13.apply(hdr.d0.d13, hdr.d0.d13, meta.switchml_md);
            value14.apply(hdr.d0.d14, hdr.d0.d14, meta.switchml_md);
            value15.apply(hdr.d0.d15, hdr.d0.d15, meta.switchml_md);
            value16.apply(hdr.d0.d16, hdr.d0.d16, meta.switchml_md);
            value17.apply(hdr.d0.d17, hdr.d0.d17, meta.switchml_md);
            value18.apply(hdr.d0.d18, hdr.d0.d18, meta.switchml_md);
            value19.apply(hdr.d0.d19, hdr.d0.d19, meta.switchml_md);
            value20.apply(hdr.d0.d20, hdr.d0.d20, meta.switchml_md);
            value21.apply(hdr.d0.d21, hdr.d0.d21, meta.switchml_md);
            value22.apply(hdr.d0.d22, hdr.d0.d22, meta.switchml_md);
            value23.apply(hdr.d0.d23, hdr.d0.d23, meta.switchml_md);
            value24.apply(hdr.d0.d24, hdr.d0.d24, meta.switchml_md);
            value25.apply(hdr.d0.d25, hdr.d0.d25, meta.switchml_md);
            value26.apply(hdr.d0.d26, hdr.d0.d26, meta.switchml_md);
            value27.apply(hdr.d0.d27, hdr.d0.d27, meta.switchml_md);
            value28.apply(hdr.d0.d28, hdr.d0.d28, meta.switchml_md);
            value29.apply(hdr.d0.d29, hdr.d0.d29, meta.switchml_md);
            value30.apply(hdr.d0.d30, hdr.d0.d30, meta.switchml_md);
            value31.apply(hdr.d0.d31, hdr.d0.d31, meta.switchml_md);

            next_step_selector.apply(hdr, standard_metadata, meta);
        } else{
            forwarder.apply(hdr, standard_metadata, meta);
        }
    } 
}

control MyEgress(
    inout header_t hdr,
    inout metadata_t meta,
    inout standard_metadata_t standard_metadata) {

    register<bit<32>>(100) worker_counter;
    register<bit<32>>(100) Job1; 
    register<bit<32>>(100) Job2; 
    register<bit<32>>(100) Job3; 
    register<bit<32>>(100) Job4; 
    register<bit<32>>(100) Job5; 
    register<bit<32>>(100) Job6; 
    register<bit<32>>(100) Job7; 
    register<bit<32>>(100) Job8; 
    register<bit<32>>(100) Job9;
    register<bit<32>>(100) Job10; 
    register<bit<32>>(100) Job11; 
    register<bit<32>>(100) Job12; 
    register<bit<32>>(100) Job13; 
    register<bit<32>>(100) Job14; 
    register<bit<32>>(100) Job15; 
    register<bit<32>>(100) Job16; 
    register<bit<32>>(100) Job17; 
    register<bit<32>>(100) Job18; 
    register<bit<32>>(100) Job19;
    register<bit<32>>(100) Job20;

    action worker_count(){
        hdr.switchml.packet_type = 3;
        bit<32> read_value_cnt;
        bit<32> write_value_cnt;
        worker_counter.read(read_value_cnt, (bit<32>) hdr.switchml.job_number);
        write_value_cnt = read_value_cnt + 1;
        meta.addr_index = (bit<8>) read_value_cnt;

        if (meta.addr_index == (bit<8>) hdr.switchml.num_workers) {
            meta.addr_index = 0;
            write_value_cnt = 0;
        }
        worker_counter.write((bit<32>) hdr.switchml.job_number, write_value_cnt );
    }

    action read_worker_job1(){
        bit<32> read_value_job1;
        Job1.read(read_value_job1, (bit<32>)meta.addr_index);
        meta.switchml_md.worker_id = (bit<16>) read_value_job1;
        hdr.ipv4.identification = meta.switchml_md.worker_id;
    }
    action read_worker_job2(){
        bit<32> read_value_job2;
        Job2.read(read_value_job2, (bit<32>)meta.addr_index);
        meta.switchml_md.worker_id = (bit<16>) read_value_job2;
        hdr.ipv4.identification = meta.switchml_md.worker_id;
    }
    action read_worker_job3(){
        bit<32> read_value_job3;
        Job3.read(read_value_job3, (bit<32>)meta.addr_index);
        meta.switchml_md.worker_id = (bit<16>) read_value_job3;
        hdr.ipv4.identification = meta.switchml_md.worker_id;
    }
    action read_worker_job4(){
        bit<32> read_value_job4;
        Job4.read(read_value_job4, (bit<32>)meta.addr_index);
        meta.switchml_md.worker_id = (bit<16>) read_value_job4;
        hdr.ipv4.identification = meta.switchml_md.worker_id;
    }
    action read_worker_job5(){
        bit<32> read_value_job5;
        Job5.read(read_value_job5, (bit<32>)meta.addr_index);
        meta.switchml_md.worker_id = (bit<16>) read_value_job5;
        hdr.ipv4.identification = meta.switchml_md.worker_id;
    }
    
    action do_recirculation(){
        recirculate_preserving_field_list(0);
    }

    table tb_worker_count{
        key = {
            hdr.switchml.msg_type : exact;
            hdr.switchml.job_number : exact;
        }
        actions = {
            worker_count;
        }
    }

    table tb_set_worker_id{
        key = {
            hdr.switchml.msg_type : exact;
            hdr.switchml.job_number : exact;
        }
        actions = {
            read_worker_job1;
            read_worker_job2;
            read_worker_job3;
            read_worker_job4;
            read_worker_job5;
        }
    }

    UDPSender() udp_sender;

    apply {
        if(standard_metadata.egress_port == 68){
            do_recirculation();
        }
        else{
            tb_worker_count.apply();
            tb_set_worker_id.apply();
        }

        udp_sender.apply(hdr, standard_metadata, meta);
    }
}

control MyDeparser(packet_out pkt, in header_t hdr) {
    apply {
        pkt.emit(hdr);
    }
}

control MyVerifyChecksum(inout header_t hdr, inout metadata_t meta) {
    apply { }
}

V1Switch(
    MyParser(),
    MyVerifyChecksum(),
    MyIngress(),
    MyEgress(),
    MyComputeChecksum(),
    MyDeparser()
) main;
