#!/usr/bin/env python3

from mininet.net import Mininet
from mininet.node import Controller
from mininet.log import setLogLevel, info
import subprocess
import time
import os

def run(cmd, check=False):
    """Run command quietly"""
    return subprocess.run(cmd, capture_output=True, text=True, check=check)

def setup_container(name, image, bridge, ip):
    """Create container and connect to network"""
    # Remove old container
    run(['docker', 'rm', '-f', name])
    
    # Create container
    result = run([
        'docker', 'run', '-dit', '--name', name,
        '--privileged', '--cap-add=NET_ADMIN',
        '--network=none', image
    ], check=True)
    
    # Get PID
    pid = run(['docker', 'inspect', '-f', '{{.State.Pid}}', name], check=True)
    pid = int(pid.stdout.strip())
    
    # Create network connection
    veth_h = f'vh-{name[-3:]}'
    veth_c = f'vc-{name[-3:]}'
    
    run(['ip', 'link', 'add', veth_h, 'type', 'veth', 'peer', 'name', veth_c])
    run(['ip', 'link', 'set', veth_c, 'netns', str(pid)])
    run(['ovs-vsctl', 'add-port', bridge, veth_h])
    run(['ip', 'link', 'set', veth_h, 'up'])
    
    # Configure container interface
    ns = ['nsenter', '-t', str(pid), '-n']
    run(ns + ['ip', 'link', 'set', veth_c, 'name', 'eth0'])
    run(ns + ['ip', 'addr', 'add', f'{ip}/24', 'dev', 'eth0'])
    run(ns + ['ip', 'link', 'set', 'eth0', 'up'])
    run(ns + ['ip', 'link', 'set', 'lo', 'up'])
    
    info(f'  ✓ {name}: {ip}\n')

def main():
    if os.geteuid() != 0:
        print("ERROR: Run as root (sudo python3 topology.py)")
        return
    
    setLogLevel('info')
    
    info('\n' + '='*60 + '\n')
    info('  LAZARUS APT - Operation Dream Job Demo\n')
    info('='*60 + '\n\n')
    
    # Create Mininet network
    info('Starting network...\n')
    net = Mininet(controller=Controller, build=False)
    net.addController('c0')
    s1 = net.addSwitch('s1')
    net.build()
    net.start()
    
    # Setup containers
    info('Creating containers...\n')
    setup_container('mn-attacker', 'lazarus-attacker:latest', s1.name, '10.0.0.1')
    setup_container('mn-victim', 'lazarus-victim:latest', s1.name, '10.0.0.10')
    
    time.sleep(2)
    
    # Start attacker services
    info('Starting services...\n')
    run(['docker', 'exec', '-d', 'mn-attacker', 
         'bash', '-c', 'cd /payloads && python3 -m http.server 8000'])
    run(['docker', 'exec', '-d', 'mn-attacker',
         'bash', '-c', 'cd /attacker && python3 c2_server.py'])
    info('  ✓ HTTP server: port 8000\n')
    info('  ✓ C2 server: port 8080\n')
    
    # Print usage
    info('\n' + '='*60 + '\n')
    info('  READY\n')
    info('='*60 + '\n')
    info('  Attacker: 10.0.0.1 | Victim: 10.0.0.10\n\n')
    info('  Commands:\n')
    info('    docker exec -it mn-victim bash\n')
    info('    docker exec -it mn-attacker bash\n')
    info('    docker exec mn-victim /home/victim/scripts/JobOffer.sh\n')
    info('\n  Press Ctrl+C to stop\n')
    info('='*60 + '\n\n')
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        info('\nStopping...\n')
    finally:
        net.stop()
        run(['docker', 'rm', '-f', 'mn-attacker', 'mn-victim'])

if __name__ == '__main__':
    main()