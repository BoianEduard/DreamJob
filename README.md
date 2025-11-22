# DreamJob

## Environment
This demo simulates the "Dream Job" APT attack using two main containers connected in a network topology:
- **Attacker Container**
  - Runs:
    - HTTP server hosting `job_offer.zip` archive (simulated OneDrive/Dropbox).
    - Flask-based Command & Control (C2) server for RAT communication and tasking.
  - Logs all victim beacons, tasks, and uploaded files for analysis.

- **Victim Container**
  - Runs:
    - `JobOffer.sh`: simulates the malicious macro execution in the attack document.
    - Extracts and runs dropped scripts including:
      - `dbll_dropper.sh`: simulates DLL dropper, installs RAT, sets persistence.
      - `persist_launcher.sh`: simulates Windows LNK shortcut persistence.
      - `rat_client.py`: a Python RAT simulating communication with C2 and performing tasks.

- **Network**
  - Docker or Mininet handles connectivity between attacker and victim containers on a virtual network.
  - Attacker accessible to victim for HTTP downloads and RAT C2 communications.

---

## Files on Each Machine
### Attacker
**job_offer.zip** - Archive containing payload scripts for victim download.  
**c2_server.py** - Flask C2 server script 
**HTTP server** - serve `job_offer.zip` 

### Victim
**JobOffer.sh** - Simulates macro; downloads and runs dropper and RAT.

---

## Attack Flow for Demo

1. **Macro Simulation (`JobOffer.sh`)**  
   - Victim executes `JobOffer.sh` simulating user opening malicious document.
   - Downloads the payload archive from attacker HTTP server.
   - Extracts payload scripts and executes the dropper.

2. **Dropping and Persisting (`dbll_dropper.sh`)**  
   - Dropper copies RAT to hidden directory ~/.local/.hidden
   - Sets persistence via cron job (`@reboot`), simulating Windows LNK shortcut in Startup.
   - Launches RAT immediately to start operation.

3. **RAT Execution (`rat_client.py`)**  
   - Sends system info beacon to C2.
   - Polls C2 for tasks: reconnaissance, credential theft, data exfiltration, or shell command execution.
   - Uploads command output or exfiltrated data to attacker server.

4. **Command & Control**  
   - Operator sets tasks via C2 HTTP `/set_task/` endpoint.
   - ex: "curl http://127.0.0.1:8080/set_task/exec:whoami" (on the attacker)
   - C2 server logs all victim interactions in files' and saves exfiltrated files locally.

5. **Logging and Analysis**  
   - Beacons, uploads, and victim actions persist in logs for post-demo audit.
   - Demo reflects realistic attack stages and tools from the Dream Job campaign.

---

