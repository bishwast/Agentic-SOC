import time
import json
import os
import sys
from main import soc_crew, save_proof_of_work

# CONFIGURATION
LOG_FILE_PATH = "/var/ossec/logs/alerts/alerts.json"
SEVERITY_THRESHOLD = 5 

def follow(file):
    """Generator function that yields new lines in a file (like tail -f)."""
    file.seek(0, 2)  # Go to the end of the file
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

def send_to_wazuh_manager(src_ip, decision):
    """Writes a custom log entry that Wazuh Manager will ingest."""
    wazuh_intel_log = "/var/ossec/logs/active-responses.log" # Standard path for custom events
    
    log_entry = {
        "integration": "agentic_soc",
        "attacker_ip": src_ip,
        "ai_decision": str(decision), # Ensure decision is stringified
        "alert_level": 12,
        "description": f"AI SOC confirmed threat from {src_ip}. Mitigation proposed."
    }
    
    try:
        with open(wazuh_intel_log, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        print(f"[+] SIEM INTEGRATION: AI verdict for {src_ip} forwarded to Wazuh.")
    except Exception as e:
        print(f"[!] SIEM ERROR: Failed to write to {wazuh_intel_log}: {e}")

def process_alert(json_line):
    try:
        data = json.loads(json_line)
        
        # Extract Key Fields
        rule_level = data.get('rule', {}).get('level', 0)
        rule_desc = data.get('rule', {}).get('description', 'Unknown Alert')
        src_ip = data.get('data', {}).get('srcip')
        
        if rule_level >= SEVERITY_THRESHOLD and src_ip:
            print(f"\n[!] ALERT DETECTED (Level {rule_level})")
            print(f"    Rule: {rule_desc}")
            print(f"    Attacker IP: {src_ip}")
            
            print(">>> Triggering AI SOC Crew...")
            inputs = {'src_ip': src_ip}
            
            # Run the AI Investigation
            result = soc_crew.kickoff(inputs=inputs)
            
            # 1. Save locally for the Streamlit Dashboard
            save_proof_of_work(result, inputs)
            
            # 2. Forward the decision back to Wazuh SIEM
            send_to_wazuh_manager(src_ip, result)
            
            print(">>> Investigation Complete. Listening for new threats...\n")
            
    except json.JSONDecodeError:
        pass
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Check for Root (Required to read/write Wazuh logs)
    if os.geteuid() != 0:
        print("[!] PERMISSION ERROR: This script must be run as root/sudo.")
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