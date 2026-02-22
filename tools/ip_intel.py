import os
import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from dotenv import load_dotenv

load_dotenv()

class IPCheckInput(BaseModel):
    """Input schema for checking an IP address."""

    # Defined a required string field with validation and documentation metadata using Pydantic.
    ip_address: str = Field (..., description="The IPv4 address to check for reputation.")

class AbuseIPDBTool(BaseTool):
    """Registers an AbuseIPDB IP reputation checker as a callable tool for CrewAI agents."""

    name : str = "abuse_ipdb_check"
    description : str = "Checks AbuseIPDB for an IP's reputation score and report counts. Essential for validating threats."
    
    # Uses Pydantic for: Type checking, Required fields and validation
    args_schema: Type[BaseModel] = IPCheckInput

    def _run(self, ip_address: str) -> str:
        """
        Securely calls the AbuseIPDB API, checks an IP’s reputation, 
        and returns a clean summary for a CrewAI agent to use.
        Falls back to a simulated malicious profile if the API fails.
        """

        api_key = os.getenv("ABUSEIPDB_API_KEY")
        url = 'https://api.abuseipdb.com/api/v2/check'
        params = { 
            'ipAddress' : ip_address, 
            'maxAgeInDays' : '90'
            }
        headers = { 
            'Accept' : 'application/json', 
            'Key' : api_key
            }

        try:
            if not api_key:
                raise ValueError("ABUSEIPDB_API_KEY is missing from the .env file.")

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()     # Forces an exception for 401, 403, 404, 500 errors.

            data = response.json()['data']
            return f"IP: {ip_address} | Score: {data['abuseConfidenceScore']}% | Total Reports: {data['totalReports']}"

        except Exception as e:
            # Permanent fallback to ensure the agent continues the OODA loop
            return f"API Connection Error: {str(e)} | FLLBACK MOCK DATA - IP: {ip_address} | Score: 85% | Total Reports: 150 | Treat as malicious."
        
