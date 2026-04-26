import requests
import json
import urllib3

# This line stops Python from complaining about "Self-Signed Certificates" 
# which are very common in home labs or private enterprise networks.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SplunkHEC:
    """
    Splunk HTTP Event Collector (HEC) Connector.
    Used for sending AI Triage results back to a centralized Enterprise SIEM.
    """
    def __init__(self, token="", host="localhost", port=8088):
        self.token = token
        self.url = f"https://{host}:{port}/services/collector/event"
        self.headers = {
            "Authorization": f"Splunk {self.token}",
            "Content-Type": "application/json"
        }

    def log_event(self, alert_id, source_ip, recommendation, audit_reason):
        """
        Forwards a structured JSON payload to Splunk.
        This creates the 'Audit Trail' needed for security governance.
        """
        payload = {
            "sourcetype": "agentic_soc_audit",
            "event": {
                "alert_id": alert_id,
                "source_ip": source_ip,
                "recommendation": recommendation,
                "audit_reason": audit_reason,
                "engine": "Llama-3.2-Agentic-SOC",
                "hardware": "NVIDIA-DGX-ARM64"
            }
        }
        try:
            # We use verify=False because local Splunk installs often use HTTPS 
            # without a formal certificate.
            response = requests.post(
                self.url, 
                headers=self.headers, 
                data=json.dumps(payload), 
                verify=False, 
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"[!] Splunk Connector Error: {e}")
            return False