import json
import os
from datetime import datetime

# Path to your Wazuh alerts file
LOG_PATH = "/var/ossec/logs/alerts/alerts.json"

# A test IP address that you want the agent to "block"
TEST_IP = "192.168.1.100"

def inject_test_alert():
    """
    Creates a synthetic Level 10 alert and appends it to the Wazuh log.
    """
    
    alert = {
        "timestamp": datetime.now().isoformat(),
        "rule": {
            "level": 10,
            "description": "SSH brute force attack detected - Multiple failed logins",
            "id": "5712"
        },
        "agent": {"id": "001", "name": "spark-7a18"},
        "data": {
            "srcip": TEST_IP,
            "destport": "22",
            "protocol": "tcp"
        },
        "full_log": f"Failed password for root from {TEST_IP} port 49152 ssh2",
        "location": "/var/log/auth.log"
    }

    try:
        with open(LOG_PATH, 'a') as f:
            f.write(json.dumps(alert) + '\n')
        print(f"[+] Successfully injected Level 10 alert for IP: {TEST_IP}")
    except PermissionError:
        print(f"[-] Permission Denied. Run with sudo: 'sudo python3 simulate_alert.py'")
    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    inject_test_alert()