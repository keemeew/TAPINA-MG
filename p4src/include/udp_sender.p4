#ifndef _UDP_SENDER_
#define _UDP_SENDER_

control UDPSender(
    inout header_t hdr,
    inout standard_metadata_t standard_metadata,
    inout metadata_t meta
    ) {

    action set_dst_addr(
        mac_addr_t eth_src_addr,
        mac_addr_t eth_dst_addr,
        ipv4_addr_t ip_dst_addr) {

        hdr.switchml.msg_type = 1;
        
        hdr.ethernet.src_addr = eth_src_addr;
        hdr.ethernet.dst_addr = eth_dst_addr;
        hdr.ipv4.dst_addr = ip_dst_addr;
        hdr.ipv4.src_addr = ip_dst_addr;

        hdr.switchml.switch_id = (bit<8>) meta.switch_id;

    }

    table dst_addr {
        key = {
            hdr.switchml.job_number : exact;
            hdr.ipv4.identification : exact; 
            meta.switchml_md.worker_type: exact; 
            hdr.switchml.packet_type : ternary;
        actions = {
            set_dst_addr;
        }
        const entries = {
            #include "/home/tofino/TAPINA/p4src/rule/rule_generator/rules/tapina/s1_dst_addr_entries.p4"
            #include "/home/tofino/TAPINA/p4src/rule/rule_generator/rules/tapina/s3_dst_addr_entries.p4"
            #include "/home/tofino/TAPINA/p4src/rule/rule_generator/rules/tapina/s7_dst_addr_entries.p4"
        }
    }

    action set_adder(bit<48> eth_src_addr, bit<48> eth_dst_addr){
        hdr.ethernet.src_addr = eth_src_addr;
        hdr.ethernet.dst_addr = eth_dst_addr;
    }

    table tb_set_ethernet_address{
        key = {
            meta.switchml_md.worker_type: exact; 
            meta.switch_id: ternary;
            hdr.switchml.job_number: ternary;
            hdr.switchml.packet_type : exact;
            hdr.switchml.msg_type : exact;
            hdr.ipv4.identification: exact;
        }
        actions = {
            set_adder;
        }
        const entries = {
            #include "/home/tofino/TAPINA/p4src/rule/rule_generator/rules/tapina/s1_tb_set_ethernet_address_entries.p4"
            #include "/home/tofino/TAPINA/p4src/rule/rule_generator/rules/tapina/s3_tb_set_ethernet_address_entries.p4"
            #include "/home/tofino/TAPINA/p4src/rule/rule_generator/rules/tapina/s7_tb_set_ethernet_address_entries.p4"
        }
    }

    apply {
        dst_addr.apply();
        tb_set_ethernet_address.apply();
    }
}

#endif /* _UDP_SENDER_ */
