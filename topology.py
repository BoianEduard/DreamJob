#!/usr/bin/env python3
"""
Lazarus Dream Job Attack - Mininet + Docker Topology
Minimal working demo
"""

from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import subprocess
import time
import sys
import os

def cleanup_containers():
    """Clean up any existing containers"""
    info('*** Cleaning up old containers\n')
    subprocess.run(['docker', 'rm', '-f', 'mn-attacker', 'mn-victim'], 
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def create_docker_container(name, image, ip):
    """Create and start a Docker container"""
    info(f'*** Starting Docker container: {name}\n')
    
    cmd = [
        'docker', 'run',
        '-dit',
        '--name', name,
        '--hostname', name,
        '--privileged',
        '--cap-add=NET_ADMIN',
        '--network=none',  # We'll connect via Mininet
        image
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        container_id = result.stdout.strip()
        
        # Get container PID
        pid_cmd = ['docker', 'inspect', '-f', '{{.State.Pid}}', container_id]
        pid_result = subprocess.run(pid_cmd, capture_output=True, text=True, check=True)
        pid = int(pid_result.stdout.strip())
        
        info(f'    Container {name} started (PID: {pid})\n')
        return container_id, pid
        
    except subprocess.CalledProcessError as e:
        info(f'    ERROR: {e.stderr}\n')
        return None, None

def connect_container_to_bridge(container_name, pid, bridge, ip):
    """Connect Docker container to Mininet OVS bridge"""
    
    # Create veth pair
    veth_host = f'veth-{container_name[3:9]}'  # Short name to avoid length issues
    veth_container = f'ceth-{container_name[3:9]}'
    
    subprocess.run(['ip', 'link', 'add', veth_host, 'type', 'veth', 
                   'peer', 'name', veth_container], check=True)
    
    # Move container end to container namespace
    subprocess.run(['ip', 'link', 'set', veth_container, 'netns', str(pid)], check=True)
    
    # Attach host end to OVS bridge (not Linux bridge!)
    subprocess.run(['ovs-vsctl', 'add-port', bridge, veth_host], check=True)
    subprocess.run(['ip', 'link', 'set', veth_host, 'up'], check=True)
    
    # Configure container interface
    subprocess.run(['nsenter', '-t', str(pid), '-n', 
                   'ip', 'link', 'set', veth_container, 'name', 'eth0'], check=True)
    subprocess.run(['nsenter', '-t', str(pid), '-n',
                   'ip', 'addr', 'add', f'{ip}/24', 'dev', 'eth0'], check=True)
    subprocess.run(['nsenter', '-t', str(pid), '-n',
                   'ip', 'link', 'set', 'eth0', 'up'], check=True)
    subprocess.run(['nsenter', '-t', str(pid), '-n',
                   'ip', 'link', 'set', 'lo', 'up'], check=True)  # Enable loopback
    
    info(f'    {container_name} connected to OVS bridge with IP {ip}\n')

def start_attacker_services(container_name):
    """Start HTTP and C2 servers on attacker"""
    info('*** Starting attacker services\n')
    
    # Start HTTP file server
    subprocess.run([
        'docker', 'exec', '-d', container_name,
        'bash', '-c', 'cd /payloads && python3 -m http.server 8000'
    ])
    info('    HTTP server started on port 8000\n')
    
    # Start C2 server
    subprocess.run([
        'docker', 'exec', '-d', container_name,
        'bash', '-c', 'cd /attacker && python3 c2_server.py'
    ])
    info('    C2 server started on port 8080\n')

def main():
    """Main function"""
    
    if os.geteuid() != 0:
        print("\n❌ ERROR: Must run as root!")
        print("   Use: sudo python3 topology.py\n")
        sys.exit(1)
    
    setLogLevel('info')
    
    info('\n')
    info('='*70 + '\n')
    info('  LAZARUS APT - Operation Dream Job\n')
    info('  Mininet + Docker Demo\n')
    info('='*70 + '\n\n')
    
    # Cleanup
    cleanup_containers()
    
    # Create Mininet network
    info('*** Creating Mininet network\n')
    net = Mininet(controller=Controller, link=TCLink, build=False)
    
    info('*** Adding controller\n')
    c0 = net.addController('c0')
    
    info('*** Adding switch\n')
    s1 = net.addSwitch('s1')
    
    info('*** Building network\n')
    net.build()
    net.start()
    
    # Get bridge name
    bridge = s1.name
    
    # Create Docker containers
    info('*** Creating Docker containers\n')
    
    attacker_id, attacker_pid = create_docker_container(
        'mn-attacker', 
        'lazarus-attacker:latest',
        '10.0.0.1'
    )
    
    victim_id, victim_pid = create_docker_container(
        'mn-victim',
        'lazarus-victim:latest',
        '10.0.0.10'
    )
    
    if not attacker_id or not victim_id:
        info('*** ERROR: Failed to create containers\n')
        net.stop()
        sys.exit(1)
    
    time.sleep(2)
    
    # Connect containers to Mininet bridge
    info('*** Connecting containers to network\n')
    connect_container_to_bridge('mn-attacker', attacker_pid, bridge, '10.0.0.1')
    connect_container_to_bridge('mn-victim', victim_pid, bridge, '10.0.0.10')
    
    time.sleep(2)
    
    # Test connectivity
    info('\n*** Testing connectivity\n')
    result = subprocess.run([
        'docker', 'exec', 'mn-victim',
        'ping', '-c', '2', '10.0.0.1'
    ], capture_output=True)
    
    if b'2 received' in result.stdout:
        info('    ✓ Victim can reach Attacker\n')
    else:
        info('    ✗ Connectivity test failed\n')
    
    # Start attacker services
    time.sleep(1)
    start_attacker_services('mn-attacker')
    
    # Print info
    info('\n')
    info('='*70 + '\n')
    info('  NETWORK READY\n')
    info('='*70 + '\n')
    info('  Topology:\n')
    info('    Attacker: 10.0.0.1  (HTTP:8000, C2:8080)\n')
    info('    Victim:   10.0.0.10\n')
    info('\n')
    info('  Useful commands:\n')
    info('    # Access attacker shell:\n')
    info('    docker exec -it mn-attacker bash\n')
    info('\n')
    info('    # Access victim shell:\n')
    info('    docker exec -it mn-victim bash\n')
    info('\n')
    info('    # Start attack on victim:\n')
    info('    docker exec -it mn-victim /home/victim/scripts/JobOffer.sh\n')
    info('\n')
    info('    # Set C2 task (from attacker):\n')
    info('    docker exec mn-attacker curl http://10.0.0.1:8080/set_task/recon\n')
    info('\n')
    info('    # Watch C2 logs:\n')
    info('    docker exec mn-attacker tail -f /attacker/beacons.log\n')
    info('\n')
    info('  Press Ctrl+D to stop the demo\n')
    info('='*70 + '\n\n')
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        info('\n*** Stopping network\n')
    
    finally:
        # Cleanup
        net.stop()
        cleanup_containers()
        info('*** Done\n')

if __name__ == '__main__':
    main()