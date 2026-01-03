import time
import json
import os
import sys
from main import soc_crew, save_proof_of_work

# CONFIGURATION
# Point to the REAL Wazuh Alert Log
LOG_FILE_PATH = "/var/ossec/logs/alerts/alerts.json"
SEVERITY_THRESHOLD = 5  # Lowered to 5 for testing (as SSH failures are usually Level 5-7)

def follow(file):
    """Generator function that yields new lines in a file (like tail -f)."""
    file.seek(0, 2)  # Go to the end of the file
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

def process_alert(json_line):
    try:
        data = json.loads(json_line)
        
        # Extract Key Fields
        rule_level = data.get('rule', {}).get('level', 0)
        rule_desc = data.get('rule', {}).get('description', 'Unknown Alert')
        src_ip = data.get('data', {}).get('srcip')
        
        # FILTER: Only trigger if it's an external IP (ignore internal/localhost if needed)
        # For this test, we ALLOW everything to ensure the demo works.
        if rule_level >= SEVERITY_THRESHOLD and src_ip:
            print(f"\n[!] ALERT DETECTED (Level {rule_level})")
            print(f"    Rule: {rule_desc}")
            print(f"    Attacker IP: {src_ip}")
            
            # Anti-Spam: Don't trigger on the same IP twice in 1 minute (Optional logic)
            print(">>> Triggering AI SOC Crew...")
            inputs = {'src_ip': src_ip}
            result = soc_crew.kickoff(inputs=inputs)
            save_proof_of_work(result, inputs)
            print(">>> Investigation Complete. Listening for new threats...\n")
            
    except json.JSONDecodeError:
        pass
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Check for Root (Required to read Wazuh logs)
    if os.geteuid() != 0:
        print("[!] PERMISSION ERROR: This script must be run as root/sudo to read Wazuh logs.")
        print("    Try: sudo env \"PATH=$PATH\" python3 wazuh_bridge.py")
        sys.exit(1)

    print(f"### AI SOC BRIDGE ACTIVE (REAL MODE) ###")
    print(f"[*] Monitoring: {LOG_FILE_PATH}")
    
    if not os.path.exists(LOG_FILE_PATH):
        print(f"[!] Error: Wazuh logs not found at {LOG_FILE_PATH}")
        sys.exit(1)

    try:
        with open(LOG_FILE_PATH, 'r') as log_file:
            for line in follow(log_file):
                process_alert(line)
    except KeyboardInterrupt:
        print("\n[!] Stopped.")