(1,1,1,_,1,_) : flood(1); // agg=s1
(1,1,2,_,1,_) : flood(2); // agg=s1
(0,1,3,_,0,2) : set_egress_port(5); // job 3, src h2, path s1->s6->s10->s7, uplink
(0,1,3,_,1,2) : set_egress_port(2); // job 3, src h2, path s1->s6->s10->s7, downlink
(0,1,3,_,0,3) : set_egress_port(4); // job 3, src h3, path s1->s5->s9->s7, uplink
(0,1,3,_,1,3) : set_egress_port(3); // job 3, src h3, path s1->s5->s9->s7, downlink
(0,1,4,_,0,1) : set_egress_port(4); // job 4, src h1, path s1->s5->s9->s7->s3, uplink
(0,1,4,_,1,1) : set_egress_port(1); // job 4, src h1, path s1->s5->s9->s7->s3, downlink
(0,1,4,_,0,2) : set_egress_port(5); // job 4, src h2, path s1->s6->s10->s8->s3, uplink
(0,1,4,_,1,2) : set_egress_port(2); // job 4, src h2, path s1->s6->s10->s8->s3, downlink
(0,1,5,_,0,2) : set_egress_port(5); // job 5, src h2, path s1->s6->s10->s8->s3, uplink
(0,1,5,_,1,2) : set_egress_port(2); // job 5, src h2, path s1->s6->s10->s8->s3, downlink
