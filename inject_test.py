import json
import pandas as pd
import os

# CONFIG
JSON_DB = "documentaiton/active_incidents.json"

# Mock Data that looks exactly like what the AI would produce
mock_incident = {
    "id": str(pd.Timestamp.now().timestamp()),
    "timestamp": str(pd.Timestamp.now()),
    "src_ip": "103.45.12.99",
    "status": "PENDING",
    "ai_analysis": """
**Threat Intelligence Summary:**
- **Source:** 103.45.12.99
- **ISP:** China Unicom
- **Abuse Score:** 100% (Critical)
- **Reports:** 1,450+ in last 24 hours

**Assessment:**
This IP is a known scanner targeting SSH ports. It has no legitimate business justification for accessing our network.

**Recommendation:**
**BLOCK** immediately at the perimeter firewall.
    """
}

# Load existing data or create new
if os.path.exists(JSON_DB):
    with open(JSON_DB, "r") as f:
        try:
            data = json.load(f)
        except:
            data = []
else:
    data = []

# Append the new mock incident
data.append(mock_incident)

# Save back to file
with open(JSON_DB, "w") as f:
    json.dump(data, f, indent=4)

print(f"[+] Successfully injected mock incident for {mock_incident['src_ip']}")