# Flask Server
1. Listens for victim beacons on /beacon and logs these to both console and a persistent beacons.log file.
2. Provides the current task to victims on /task endpoint.
3. Receives file uploads on /upload, saves exfiltrated files to a local "victim_exfil_data" directory instead of logging content. Upload actions are logged in victim.log.
4. Allows operators to set tasks via /set_task/<task> endpoint, supporting "sleep", "recon", "steal_creds", "exfil", and remote shell commands prefixed with "exec:".
5. Logs all victim interactions (beacon, task requests, uploads) with timestamps and victim identifiers in a comprehensive victim.log file for audit and reporting.

# Setup
1. install dependencies for the script + curl
2. local http server (TODO: "run python3 -m http.server 8000" from the dir containing job_offer.zip) 
