(1,7,3,_,1,_) : flood(3); // agg=s7
(0,7,1,_,0,11) : set_egress_port(3); // job 1, src h11, path s4->s7->s9->s5->s1, uplink
(0,7,1,_,1,11) : set_egress_port(2); // job 1, src h11, path s4->s7->s9->s5->s1, downlink
(0,7,2,_,0,7) : set_egress_port(3); // job 2, src h7, path s3->s7->s9->s5->s1, uplink
(0,7,2,_,1,7) : set_egress_port(1); // job 2, src h7, path s3->s7->s9->s5->s1, downlink
(0,7,2,_,0,11) : set_egress_port(3); // job 2, src h11, path s4->s7->s9->s5->s1, uplink
(0,7,2,_,1,11) : set_egress_port(2); // job 2, src h11, path s4->s7->s9->s5->s1, downlink
(0,7,4,_,0,1) : set_egress_port(1); // job 4, src h1, path s1->s5->s9->s7->s3, uplink
(0,7,4,_,1,1) : set_egress_port(3); // job 4, src h1, path s1->s5->s9->s7->s3, downlink
(0,7,4,_,0,5) : set_egress_port(1); // job 4, src h5, path s2->s5->s9->s7->s3, uplink
(0,7,4,_,1,5) : set_egress_port(3); // job 4, src h5, path s2->s5->s9->s7->s3, downlink
(0,7,4,_,0,11) : set_egress_port(1); // job 4, src h11, path s4->s7->s3, uplink
(0,7,4,_,1,11) : set_egress_port(2); // job 4, src h11, path s4->s7->s3, downlink
