import requests
import os

class ThreatIntelProvider:
    """
    Real-time reputation enrichment for the Agentic pipeline.
    Connects to AbuseIPDB to satisfy Enterprise enrichment requirements.
    """
    def __init__(self, abuse_key=None):
        # We use an environment variable so your API key stays safe
        self.abuse_key = abuse_key or os.getenv("ABUSEIPDB_KEY", "")

    def get_ip_reputation(self, ip):
        """
        Queries AbuseIPDB for a reputation score.
        """
        if not self.abuse_key:
            return "Reputation: UNKNOWN (API Key missing. Sandbox mode.)"

        url = 'https://api.abuseipdb.com/api/v2/check'
        params = {'ipAddress': ip, 'maxAgeInDays': '90'}
        headers = {'Accept': 'application/json', 'Key': self.abuse_key}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                score = data['data']['abuseConfidenceScore']
                country = data['data']['countryName']
                return f"Abuse Score: {score}/100 | Country: {country}"
            return f"Reputation: API Error ({response.status_code})"
        except Exception as e:
            return f"Reputation: Error ({str(e)})"

    def get_mitre_context(self, description):
        """
        Maps the alert text to a MITRE technique.
        """
        desc = description.lower()
        if "brute force" in desc or "failed login" in desc:
            return "MITRE ATT&CK: T1110 (Brute Force)"
        if "malware" in desc:
            return "MITRE ATT&CK: T1587.001 (Malware)"
        return "MITRE ATT&CK: T1059 (Command/Scripting Interpreter)"