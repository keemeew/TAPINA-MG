# TAPINA-MG
Distributed machine learning can suffer from network bottlenecks during gradient aggregation. Programmable data planes enable in-network aggregation to mitigate this issue, but their limited resources make widespread deployment challenging. In this work, we study the problem of placing in-network aggregation functions in multi-tenant environments to minimize network traffic. We formulate the problem as an ILP and prove its NP-hardness. To address this, we propose TAPINA-MG, a traffic-aware placement algorithm based on a two-stage many-to-one matching game. Simulation results show that TAPINA-MG achieves near-optimal performance with low complexity, achieving up to 22.5%, 38.9%, and 96.0% reduction for network traffic, maximum link utilization, and job completion time, respectively, compared to state of the art, and effectively handles dynamic situations with minimal migration delay and comparable traffic performance.

# Test for TAPINA-MG
This is a example test scenario of TAPINA-MG based on P4 software programmable switches.

## Dependencies
To run this code, basic dependencies such as p4c, BMv2, Mininet and other libraries should be installed. 
### Install dependencies
1. [p4c](https://github.com/p4lang/p4c)

   ```
   source /etc/lsb-release
   echo "deb http://download.opensuse.org/repositories/home:/p4lang/xUbuntu_${DISTRIB_RELEASE}/ /" | sudo tee /etc/apt/sources.list.d/home:p4lang.list
   curl -fsSL https://download.opensuse.org/repositories/home:p4lang/xUbuntu_${DISTRIB_RELEASE}/Release.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/home_p4lang.gpg > /dev/null
   sudo apt-get update
   sudo apt install p4lang-p4c
   ```
   
2. [BMv2](https://github.com/p4lang/behavioral-model)

   ```
   . /etc/os-release
   echo "deb http://download.opensuse.org/repositories/home:/p4lang/xUbuntu_${VERSION_ID}/ /" | sudo tee /etc/apt/sources.list.d/home:p4lang.list
   curl -fsSL "https://download.opensuse.org/repositories/home:p4lang/xUbuntu_${VERSION_ID}/Release.key" | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/home_p4lang.gpg > /dev/null
   sudo apt update
   sudo apt install p4lang-bmv2
   ```

3. [P4Utils](https://github.com/nsg-ethz/p4-utils)

   ```
   git clone https://github.com/nsg-ethz/p4-utils.git
   cd p4-utils
   sudo ./install.sh
   ```

4. [Mininet](https://github.com/mininet/mininet)

## Instructions
This repository provides an example scenario with 2-ary fat-tree topology. 

1. Download the repository to the local.
   
2. Open three terminals for running a simulation.

3. Generate rules for testing TAPINA.
   ```
   (Terminal 1) python3 ~/TAPINA/p4src/rule/rule_generator/tapina_rule_generator.py --jobs-json ~/TAPINA/p4src/rule/rule_generator/job.json
   ```

   Note that this script enables generating rules for the TAPINA switches and normal switches under various configurations.

4. Configure the network by Mininet and install the compiled program on BMv2 switches.
   ```
   (Terminal 2) sudo python3 ~/TAPINA/network.py
   ```

   Note that it pauses until we 'Enter' with a "Waiting for inserting rules..." message. This is because we need to insert rules in step 4 before running the simulation.
   
   Note that you need to modify the follows for different scenarios:
   1) P4 programs for each switch in network.py,
   2) Generating job packets in packet/tapina_send_and_receive_h*.py,
   3) Adopted rules in P4 programs (e.g., p4src/include/forwarder.p4)

5. Insert BMv2 rules.
   ```
   (Terminal 3) . ~/TAPINA/p4src/rule/rule_insert.sh
   ```

   Note that you need to modify thrift port numbers and rule paths for different sceanrios.

6. Run simulation.


   After inserting rules, type any input (e.g., Enter) to continue the simulation on Terminal 1. Then the hosts run each program automatically. 


7. See the results.


   The output logs will be stored in ~/TAPINA/results/host*.txt. 
