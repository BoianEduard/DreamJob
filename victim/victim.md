# JobOffer.sh
1. Simulates the macro code embedded in the malicious document as executed by the victim.
2. Downloads the malicious payload archive (job_offer.zip) from the attacker-controlled HTTP server.
3. Saves the archive to a temporary location on the victim machine.
4. Extracts the contents of the archive (which includes dbll_dropper.sh, persist_launcher.sh, rat_client.py, etc.) to a working directory.
5. Lists extracted files for verification and visibility during the demo.
6. Executes the dbll_dropper.sh script which installs the RAT, sets up persistence, and launches the RAT immediately.
7. Completes the simulated macro execution, handing control to the dropper and RAT for further actions.


# job_offer.zip

## dbll_dropper.sh
```
1. Creates a hidden directory (~/.local/.hidden) to store rat_client.py
2. Copies the RAT script to this hidden location and makes it executable.
3. Sets up persistence by adding a cron job with @reboot to automatically re-launch the RAT on system startup, simulating the behavior of LNK shortcut persistence used in the actual attack.
4. Starts the RAT immediately in the background.
```

## persist_launcher.sh
```
The original attack uses a LNK shortcut file in the Startup folder as a persistence mechanism.
persist_launcher.sh simulates this shortcut by running the RAT executable/script to replay the "shortcut launch" action on a Linux system 
```

## rat_client.py
simulates several key behaviors of a Remote Access Trojan (RAT) used in the Dream Job APT campaign
```
get_host_info()
    Collects host details to send as a beacon: hostname, current user, IP addresses, and a snapshot of running processes (top 5 lines).

run_recon()
    Runs Linux shell commands to collect network interface details and DNS configuration simulated as reconnaissance data.
    Simulates the APT’s behavior of internal network discovery.

steal_creds()
    Returns a fake static credentials string to simulate theft of user credentials (simulation of APIs to extract browser passwords, Windows credentials, etc.)

exfiltrate_directory()
    Archives and compresses the victim’s ~/important directory into a tar.gz file to simulate realistic data exfiltration.
    Reads the compressed file data for uploading to C2.

post_data(endpoint, data, files)
    Sends HTTP POST requests to the C2 endpoint.
    Supports JSON data for system beacons and file uploads for exfiltrated data or credentials.

get_task()
    Polls the C2 server for the next task to execute: "recon", "steal_creds", "exfil", "sleep", or remote shell command starting with "exec:".

run_shell_command(cmd)
    Executes arbitrary shell commands received via the C2 and returns their output for beaconing.

main()
    The main loop:
    - Sends host info beacon to C2.
    - Retrieves and executes tasks from the C2.
    - Performs reconnaissance, credentials theft simulation, exfiltration, or shell command execution accordingly.

```

# Setup
1. only need to run JobOffer.sh to start the attack
2. all dependencies from the rat_client.py must pe installed
3. create ~/important/ dir and add a secret.txt with some secret in it - the C2 server can send the exfil command to demo data exfil - will crete an archive with all content from ~/important
4. must have crontab and other os deps
