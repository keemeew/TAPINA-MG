(1,3,4,_,1,_) : flood(4); // agg=s3
(1,3,5,_,1,_) : flood(5); // agg=s3
(0,3,1,_,0,8) : set_egress_port(5); // job 1, src h8, path s3->s8->s10->s6->s1, uplink
(0,3,1,_,1,8) : set_egress_port(2); // job 1, src h8, path s3->s8->s10->s6->s1, downlink
(0,3,2,_,0,7) : set_egress_port(4); // job 2, src h7, path s3->s7->s9->s5->s1, uplink
(0,3,2,_,1,7) : set_egress_port(1); // job 2, src h7, path s3->s7->s9->s5->s1, downlink
(0,3,3,_,0,9) : set_egress_port(4); // job 3, src h9, path s3->s7, uplink
(0,3,3,_,1,9) : set_egress_port(3); // job 3, src h9, path s3->s7, downlink
