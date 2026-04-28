import subprocess
import requests
import json
import time
import re  

# --- CONFIGURATION VARIABLES ---
CONTAINER_NAME = "victim_ssh"
API_URL = "http://127.0.0.1:8000/api/v1/triage"
ATTACK_SIGNATURES = [
    "Failed password", 
    "Invalid user", 
    "Connection closed by authenticating user",
    "admin_RCE_EXPLOIT_CVE-2026-33827"
]
# -------------------------------

def stream_telemetry():
    print(f"🛡️  Agentic SOC Bridge (Python Edition) is LIVE.")
    print(f"📡 Monitoring stream: {CONTAINER_NAME} --> {API_URL}")
    print("-" * 50)

    process = subprocess.Popen(
        ["docker", "logs", "-f", CONTAINER_NAME],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    for line in iter(process.stdout.readline, ""):
        line = line.strip()
        
        if "ls.io-init" in line:
            continue

        if any(sig in line for sig in ATTACK_SIGNATURES):
            alert_id = f"ALT-{int(time.time())}"
            print(f"🚨 ATTACK DETECTED: {line}")
            
            # --- THE FIX: DYNAMIC IP EXTRACTION ---
            # Search the log line for an IPv4 address
            ip_match = re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', line)
            actual_ip = ip_match.group(0) if ip_match else "127.0.0.1"
            # --------------------------------------
            
            payload = {
                "alert_id": alert_id,
                "source_ip": actual_ip, # <-- Now using the real IP!
                "description": f"SSH Brute Force Signature Found: {line}"
            }

            try:
                response = requests.post(API_URL, json=payload, timeout=5)
                if response.status_code == 200:
                    print(f"✅ Telemetry pushed successfully. Target IP: {actual_ip}")
                else:
                    print(f"⚠️  API returned error {response.status_code}: {response.text}")
            except requests.exceptions.ConnectionError:
                print("❌ FAILED: Could not connect to SOC API. Is uvicorn running?")

if __name__ == "__main__":
    try:
        stream_telemetry()
    except KeyboardInterrupt:
        print("\n🛑 Bridge stopped by user.")