import json
import time
import os
import sys
from crew import AgenticSocCrew

def watch_wazuh_logs(file_path):
    """
    Monitors the Wazuh alerts.json file for new security events. 
    This script is a nonstop security watcher that calls an AI team 
    whenever a dangerous alert appears.
    """
    # Initializing the Agentic Team from the crew.py logic
    try:
        soc_team = AgenticSocCrew()
    except Exception as e:
        print(f"[-] Failed to initialize SOC Crew: {e}")
        sys.exit(1)

    print(f"[*] Starting Agentic SOC.... Monitoring: {file_path}")

    # Only process new alerts - open the file and move the pointer to the end.
    with open(file_path, 'r') as f: 
        """
        Start watching from now, not the past.
        Jump to the end of the file -> Ignore old alerts -> Only read new ones
        """
        f.seek(0, os.SEEK_END)

        while True:
            # REad one line from the file
            line = f.readline()

            if not line:        #If no new alert
                time.sleep(1)   # Wait a second
                continue        # Go back to the top of the loop
        
            try:
                alert_data = json.loads(line)
                # Filter: Only trigger AI reasoning fo high-level alerts - level 10+
                rule_level = alert_data.get('rule', {}).get('level', 0)

                # Trigger logic for high-severity alerts
                if rule_level >= 10:
                    print(f"\n[!] High Severity Alert (Level {rule_level}) Detected")

                    # Build and run the Agentic Crew with the current alert line as input
                    soc_crew = soc_team.build_crew(raw_alert_data=line)

                    # Start the agentic workflow
                    print("[*] Dispatching Agentic Crew for response...")
                    result = soc_crew.kickoff()

                    print("\n--- AGENTIC RESPONSE REPORT ---")
                    print(result)
                    print("--------------------------------\n")

            except json.JSONDecodeError:
                continue
            except Exception as e:
                    print(f"[!] Error: {e}")

if __name__ == "__main__":
     LOG_PATH = "/var/ossec/logs/alerts/alerts.json"

     if os.path.exists(LOG_PATH):
        try:
            # Check for read permissions
            if os.access(LOG_PATH, os.R_OK):
                watch_wazuh_logs(LOG_PATH)
            else:
                print(f"Permission Error: User cannot read {LOG_PATH}.")
                print("Run: 'sudo chmod +r /var/ossec/logs/alerts/alerts.json'")
        except KeyboardInterrupt:
            print("\n[*] Shutting down Agentic SOC watcher.")
     else:
         print(f"Critical Error: {LOG_PATH} not found. Ensure Wazuh is installed and running.")