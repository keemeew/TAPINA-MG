#ifndef _CONFIGURATION_
#define _CONFIGURATION_

#define register_size 65536

#define num_slots 8192

#define max_num_workers 32
#define max_num_workers_log2 5 
#define forwarding_table_size 1024

#define max_num_queue_pairs_per_worker 512
#define max_num_queue_pairs_per_worker_log2 9

#define max_num_queue_pairs 512*32
#define max_num_queue_pairs_log2  max_num_queue_pairs_per_worker_log2 + max_num_workers_log2

#define TEST_OUTPUT_PORT 68


#endif /* _CONFIGURATION_ */
