import time
import json
import subprocess
import re
import sys

# CONFIGURATION
LOG_FILE = "/var/ossec/logs/alerts/alerts.json"
TARGET_AGENT_ID = "001"  # The ID of your Honeypot Agent
ACTIVE_RESPONSE_CMD = "ai-firewall-block600" # Must match <name> in ossec.conf

# ---------------------------------------------------------
# FUNCTION: Trigger the Active Response (The "Muscle")
# ---------------------------------------------------------
def trigger_active_response(agent_id, ip_to_block, rule_id):
    """
    Executes the Wazuh Active Response command to block the IP.
    """
    print(f"\n[!] ⚡ AI DECISION: High Confidence Threat Detected (Rule {rule_id})")
    print(f"    Target IP: {ip_to_block}")
    print(f"    Action: INITIATING ACTIVE DEFENSE...")

    try:
        # Construct the command to tell Wazuh to block the IP
        cmd = [
            "/var/ossec/bin/agent_control",
            "-u", agent_id,
            "-f", ACTIVE_RESPONSE_CMD,
            "-b", ip_to_block
        ]

        # Run the command and capture output
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"[+] ✅ SUCCESS: Block command sent to Agent {agent_id}.")
            print(f"    Wazuh Output: {result.stdout.strip()}")
        else:
            print(f"[-] ❌ FAILURE: Could not trigger Active Response.")
            print(f"    Error: {result.stderr.strip()}")

    except Exception as e:
        print(f"[-] CRITICAL ERROR executing response: {str(e)}")

# ---------------------------------------------------------
# FUNCTION: Simulate AI Analysis (The "Brain")
# ---------------------------------------------------------
def analyze_alert(alert_json):
    """
    Placeholder for your LLM Logic. 
    In a full production version, this would send the 'alert_json' to Ollama/OpenAI.
    """
    rule_desc = alert_json.get('rule', {}).get('description', 'Unknown Alert')
    print(f"\n{'='*60}")
    print(f"[*] ALERT ANALYZED: {rule_desc}")
    print(f"{'-'*20} AI ANALYSIS {'-'*20}")
    print(f"Based on the pattern of 'Invalid User' login attempts, this indicates")
    print(f"an automated brute-force attack. The source IP is aggressively probing")
    print(f"non-existent accounts.")
    print(f"RECOMMENDATION: Immediate blocking of the source IP.")
    print(f"{'='*60}")

# ---------------------------------------------------------
# MAIN EXECUTION LOOP
# ---------------------------------------------------------
def main():
    print(f"[*] AI SOC Analyst Started...")
    print(f"[*] Monitoring Log: {LOG_FILE}")
    print(f"[*] Active Response Target: Agent {TARGET_AGENT_ID}")
    
    # Open the log file and go to the end (tail mode)
    try:
        f = open(LOG_FILE, 'r')
        f.seek(0, 2) # Move to end of file
    except FileNotFoundError:
        print(f"Error: Could not find {LOG_FILE}. Are you running as sudo?")
        sys.exit(1)

    while True:
        line = f.readline()
        if not line:
            time.sleep(1) # Wait for new logs
            continue

        try:
            # Parse the JSON log line
            data = json.loads(line)
            
            # Extract Key Fields
            rule_id = data.get('rule', {}).get('id')
            src_ip = data.get('data', {}).get('srcip')
            
            # -------------------------------------------------
            # LOGIC: Check for Brute Force Rules (5710, 5716)
            # -------------------------------------------------
            if rule_id in ["5710", "5716", "5712", "5503"]:
                if src_ip:
                    # 1. Analyze (Print the AI text)
                    analyze_alert(data)
                    
                    # 2. Respond (Pull the trigger)
                    trigger_active_response(TARGET_AGENT_ID, src_ip, rule_id)
                else:
                    print("[-] Alert detected, but no Source IP found in log.")

        except json.JSONDecodeError:
            continue # Skip broken lines
        except Exception as e:
            print(f"[-] Error processing log line: {e}")

if __name__ == "__main__":
    main()