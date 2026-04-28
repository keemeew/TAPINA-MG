import argparse
from p4utils.mininetlib.network_API import NetworkAPI
from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.link import TCLink
from multiprocessing import Process
from time import sleep
import subprocess


def open_new_terminal(command):
    subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', command])

# # Run command on Mininet node
def run_command_on_host(host_node, command):
    result = host_node.cmd(command)
    # print(f"Command result on {host_node.name}:\n{result}")

# Configure Network
def config_network():
    global p4_tapina,p4_forwarding_2,p4_forwarding_4,p4_forwarding_5,p4_forwarding_6,p4_forwarding_7,p4_forwarding_8,p4_forwarding_9,p4_forwarding_10
    net = NetworkAPI()

    # If want to use Mininet CLI, modify to True
    net.cli_enabled = False
    
    # Link option
    linkops = dict(bw=1000, loss=0, use_htb=True)
    
    # Network general options
    net.setLogLevel('info')

    # Network definition
    net.addP4Switch('s1')
    net.addP4Switch('s2')
    net.addP4Switch('s3')
    net.addP4Switch('s4')
    net.addP4Switch('s5')
    net.addP4Switch('s6')
    net.addP4Switch('s7')
    net.addP4Switch('s8')
    net.addP4Switch('s9')
    net.addP4Switch('s10')

    net.setP4Source("s1",p4_tapina)
    net.setP4Source("s2",p4_forwarding_2)
    net.setP4Source("s3",p4_tapina)
    net.setP4Source("s4",p4_forwarding_4)
    net.setP4Source("s5",p4_forwarding_5)
    net.setP4Source("s6",p4_forwarding_6)
    net.setP4Source("s7",p4_tapina)
    net.setP4Source("s8",p4_forwarding_8)
    net.setP4Source("s9",p4_forwarding_9)
    net.setP4Source("s10",p4_forwarding_10)

    # net.setP4SourceAll(p4)

    net.addHost('h1')
    net.addHost('h2')
    net.addHost('h3')
    net.addHost('h4')
    net.addHost('h5')
    net.addHost('h6')
    net.addHost('h7')
    net.addHost('h8')
    net.addHost('h9')
    net.addHost('h10')
    net.addHost('h11')
    net.addHost('h12')

    net.addLink('h1', 's1',**linkops) 
    net.addLink('h2', 's1',**linkops) 
    net.addLink('h3', 's1',**linkops) 
    net.addLink('h4', 's2',**linkops)
    net.addLink('h5', 's2',**linkops)
    net.addLink('h6', 's2',**linkops)
    net.addLink('h7', 's3',**linkops)
    net.addLink('h8', 's3',**linkops)
    net.addLink('h9', 's3',**linkops)
    net.addLink('h10', 's4',**linkops)
    net.addLink('h11', 's4',**linkops)
    net.addLink('h12', 's4',**linkops)
    
    net.addLink('s1', 's5',addr1="00:00:00:00:01:05",addr2="00:00:00:00:05:01",**linkops)
    net.addLink('s1', 's6',addr1="00:00:00:00:01:06",addr2="00:00:00:00:06:01",**linkops)
    
    net.addLink('s2', 's5',addr1="00:00:00:00:02:05",addr2="00:00:00:00:05:02",**linkops)
    net.addLink('s2', 's6',addr1="00:00:00:00:02:06",addr2="00:00:00:00:06:02",**linkops)

    net.addLink('s3', 's7',addr1="00:00:00:00:03:07",addr2="00:00:00:00:07:03",**linkops)
    net.addLink('s3', 's8',addr1="00:00:00:00:03:08",addr2="00:00:00:00:08:03",**linkops)

    net.addLink('s4', 's7',addr1="00:00:00:00:04:07",addr2="00:00:00:00:07:04",**linkops)
    net.addLink('s4', 's8',addr1="00:00:00:00:04:08",addr2="00:00:00:00:08:04",**linkops)
    
    net.addLink('s5', 's9',addr1="00:00:00:00:05:09",addr2="00:00:00:00:09:05",**linkops)
    net.addLink('s5', 's10',addr1="00:00:00:00:05:0a",addr2="00:00:00:00:0a:05",**linkops)
    
    net.addLink('s6', 's9',addr1="00:00:00:00:06:09",addr2="00:00:00:00:09:06",**linkops)
    net.addLink('s6', 's10',addr1="00:00:00:00:06:0a",addr2="00:00:00:00:0a:06",**linkops)

    net.addLink('s7', 's9',addr1="00:00:00:00:07:09",addr2="00:00:00:00:09:07",**linkops)
    net.addLink('s7', 's10',addr1="00:00:00:00:07:0a",addr2="00:00:00:00:0a:07",**linkops)

    net.addLink('s8', 's9',addr1="00:00:00:00:08:09",addr2="00:00:00:00:09:08",**linkops)
    net.addLink('s8', 's10',addr1="00:00:00:00:08:0a",addr2="00:00:00:00:0a:08",**linkops)

    # Assignment strategy
    net.mixed()

    # Nodes general options: Log, Pcap ,,,
    # net.enableCpuPortAll()
    # net.enablePcapDumpAll()
    # net.enableLogAll()

    return net

def main():
    global p4_tapina,p4_forwarding_2,p4_forwarding_4,p4_forwarding_5,p4_forwarding_6,p4_forwarding_7,p4_forwarding_8,p4_forwarding_9,p4_forwarding_10
    # args = get_args()
    p4_tapina = "/home/tofino/TAPINA/p4src/tapina.p4"
    p4_forwarding_1 = "/home/tofino/TAPINA/p4src/forwarding/normal_forwarding_1.p4"
    p4_forwarding_2 = "/home/tofino/TAPINA/p4src/forwarding/normal_forwarding_2.p4"
    p4_forwarding_4 = "/home/tofino/TAPINA/p4src/forwarding/normal_forwarding_4.p4"
    p4_forwarding_5 = "/home/tofino/TAPINA/p4src/forwarding/normal_forwarding_5.p4"
    p4_forwarding_6 = "/home/tofino/TAPINA/p4src/forwarding/normal_forwarding_6.p4"
    p4_forwarding_7 = "/home/tofino/TAPINA/p4src/forwarding/normal_forwarding_7.p4"
    p4_forwarding_8 = "/home/tofino/TAPINA/p4src/forwarding/normal_forwarding_8.p4"
    p4_forwarding_9 = "/home/tofino/TAPINA/p4src/forwarding/normal_forwarding_9.p4"
    p4_forwarding_10 = "/home/tofino/TAPINA/p4src/forwarding/normal_forwarding_10.p4"


    # # # Execute command on Mininet nodes simultaneously
    commands = []
    processes = []
    for i in range(0,12):
        command = f'python3 /home/tofino/TAPINA/packet/tapina_send_and_receive_h{i+1}.py --packet_number 10'
        commands.append(command)
    print(commands)

    net = config_network()
    net.startNetwork()

    print("If you want to process, please press Enter key.")
    input()
  

    process1 = Process(target=run_command_on_host, args=(net.net.get('h1'), commands[0]))
    process1.start()
    processes.append(process1)

    process2 = Process(target=run_command_on_host, args=(net.net.get('h2'), commands[1]))
    process2.start()    
    processes.append(process2)

    process3 = Process(target=run_command_on_host, args=(net.net.get('h3'), commands[2]))
    process3.start()
    processes.append(process3)

    process4 = Process(target=run_command_on_host, args=(net.net.get('h4'), commands[3]))
    process4.start()
    processes.append(process4)

    process5 = Process(target=run_command_on_host, args=(net.net.get('h5'), commands[4]))
    process5.start()
    processes.append(process5)

    process6 = Process(target=run_command_on_host, args=(net.net.get('h6'), commands[5]))
    process6.start()    
    processes.append(process6)

    process7 = Process(target=run_command_on_host, args=(net.net.get('h7'), commands[6]))
    process7.start()
    processes.append(process7)

    process8 = Process(target=run_command_on_host, args=(net.net.get('h8'), commands[7]))
    process8.start()
    processes.append(process8)

    process9 = Process(target=run_command_on_host, args=(net.net.get('h9'), commands[8]))
    process9.start()
    processes.append(process9)

    process10 = Process(target=run_command_on_host, args=(net.net.get('h10'), commands[9]))
    process10.start()    
    processes.append(process10)

    process11 = Process(target=run_command_on_host, args=(net.net.get('h11'), commands[10]))
    process11.start()
    processes.append(process11)

    process12 = Process(target=run_command_on_host, args=(net.net.get('h12'), commands[11]))
    process12.start()
    processes.append(process12)


    for process in processes :
        process.join()

    sleep(30)
    print("Done")
    
    # # # Turn off the Mininet
    net.stopNetwork()


if __name__ == '__main__':
    main()
