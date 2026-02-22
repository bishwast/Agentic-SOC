import os
import requests
import urllib3
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Suppress SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WazuhClient:
    def __init__(self):
        self.host = os.getenv("WAZUH_HOST", "localhost")
        self.api_port = os.getenv("WAZUH_API_PORT", "55000")
        self.indexer_port = os.getenv("WAZUH_INDEXER_PORT", "9200")
        self.api_user = os.getenv("WAZUH_API_USER")
        self.api_pass = os.getenv("WAZUH_API_PASSWORD")
        self.indexer_user = os.getenv("WAZUH_INDEXER_USER")
        self.indexer_pass = os.getenv("WAZUH_INDEXER_PASSWORD")
        self.token = None

    def login(self):
        """Authenticates with the Wazuh API to get a JWT."""
        url = f"https://{self.host}:{self.api_port}/security/user/authenticate"
        try:
            # Authenticate using the 'wazuh' user
            response = requests.post(url, auth=(self.api_user, self.api_pass), verify=False)
            response.raise_for_status()
            self.token = response.json().get('data', {}).get('token')
            return True
        except Exception as e:
            print(f"API Login Failed: {e}")
            return False

    def get_manager_status(self):
        """Checks the status of the Wazuh Manager services."""
        if not self.token and not self.login():
            return None
        
        url = f"https://{self.host}:{self.api_port}/manager/status"
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(url, headers=headers, verify=False)
        return response.json()
    
    def get_recent_alerts(self, limit=3):
        """Fetches the latest high-level alerts from the Indexer."""
        # We use the admin user for the Indexer (9200)
        url = f"https://{self.host}:{self.indexer_port}/wazuh-alerts-*/_search"
        
        # Query for alerts with level 10 or higher (Critical)
        query = {
            "size": limit,
            "sort": [{"timestamp": {"order": "desc"}}],
            "query": {"range": {"rule.level": {"gte": 10}}}
        }
        
        try:
            response = requests.get(
                url, 
                auth=(self.indexer_user, self.indexer_pass), 
                json=query, 
                verify=False
            )
            response.raise_for_status()
            hits = response.json().get('hits', {}).get('hits', [])
            return [hit['_source'] for hit in hits]
        except Exception as e:
            print(f"Error fetching alerts: {e}")
            return []

if __name__ == "__main__":
    client = WazuhClient()
    status = client.get_manager_status()
    print(json.dumps(status, indent=4))