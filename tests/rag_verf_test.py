import httpx
import asyncio

API_URL = "http://127.0.0.1:8000/api/v1/triage"

async def run_rag_test():

    """Sends three different alerts to prove the AI is using the context provided in teh playbook."""

    async with httpx.AsyncClient() as client:
        # Test 1: Geolocation Playbook Trigger
        print("--- TEST 1: UNUSUAL LOGIN ---")
        alert_1 = {
            "alert_id": "RAG-LOGIN-001",
            "description": "Brute force login attempt from unusual geolocation",
            "source_ip": "45.33.22.11"
        }
        resp1 = await client.post(API_URL, json=alert_1)
        print(f"Action: {resp1.json().get('action')}\n")

        # Test 2: Malware Playbook Trigger
        print("--- TEST 2: MALWARE DETECTION ---")
        alert_2 = {
            "alert_id": "RAG-MALWARE-001",
            "description": "Malicious hash detected on endpoint workstation-04",
            "source_ip": "10.0.0.55"
        }
        resp2 = await client.post(API_URL, json=alert_2)
        print(f"Action: {resp2.json().get('action')}\n")

        # Test 3: Unknown Scenario (The Fallback)
        print("--- TEST 3: UNKNOWN ALERT ---")
        alert_3 = {
            "alert_id": "RAG-UNKNOWN-001",
            "description": "Printer out of paper",
            "source_ip": "192.168.1.100"
        }
        resp3 = await client.post(API_URL, json=alert_3)
        print(f"Action: {resp3.json().get('action')}\n")

if __name__ == "__main__":
    asyncio.run(run_rag_test())