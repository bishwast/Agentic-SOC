from wazuh_client import WazuhClient
import os

# Assuming you are using an LLM API like OpenAI or Groq
# pip install openai
from openai import OpenAI

client_ai = OpenAI(api_key=os.getenv("LLM_API_KEY"))
wazuh = WazuhClient()

def analyze_alerts():
    alerts = wazuh.get_recent_alerts(limit=1)
    if not alerts:
        print("No critical alerts found.")
        return

    for alert in alerts:
        description = alert.get('rule', {}).get('description')
        full_log = alert.get('full_log')
        
        prompt = f"""
        You are a Senior SOC Analyst. Analyze the following alert:
        Alert: {description}
        Raw Log: {full_log}
        
        Task: Provide a 2-sentence summary and a 'True' or 'False' Positive rating.
        """
        
        response = client_ai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        print(f"AI ANALYSIS: {response.choices[0].message.content}")

if __name__ == "__main__":
    analyze_alerts()