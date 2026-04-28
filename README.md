# TAPINA
Distributed machine learning is an effective method to alleviate the intensive computation costs of training; however, it suffers from network bottlenecks while collecting local results. The recent advent of programmable data planes has opened a new avenue, in-network aggregation, which executes gradient aggregations in the middle of the network, resolving network bottlenecks, and further accelerates distributed machine learning. However, due to resource-constrained features of current programmable data planes, deploying in-network aggregation functionalities throughout the network would impose an unacceptable burden, posing a need for sophisticated deployment. In this paper, a problem of deploying in-network aggregation functionalities is studied to minimize the total network traffic in multi-tenant distributed machine learning. We formulate the problem as an integer linear programming (ILP) problem and prove its NP-hardness. Since finding the optimal solution using the brute-force method is extremely complicated, we propose a traffic-aware in-network aggregation placement algorithm based on a two-stage many-to-one matching game (denoted TAPINA-MG). The simulation results demonstrate that TAPINA-MG shows near-optimal performance with low complexity, achieving up to 22.5% traffic reduction compared to the state-of-the-art algorithm. 

# Test for TAPINA
This is a toy example of TAPINA based on the P4 language.

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

## BMv2 Instructions
This repository provides an example scenario with 2-ary fat-tree topology. 

1. Download the repository to the local.
   
2. Open three terminals for running a simulation.

3. Generate rules for testing TAPINA.
   ```
   (Terminal 1) python3 ~/TAPINA/p4src/rule/rule_generator/tapina_rule_generator.py --jobs-json ~/TAPINA/p4src/rule/rule_generator/job.json
   ```

   Note that this script enables generating rules for the TAPINA switches and normal switches under various configurations.

4. Configure the network and install the FAT-INT program on BMv2 switches.
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
