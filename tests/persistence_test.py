import httpx
import time
import json
import asyncio

API_URL = "http://127.0.0.1:8000/api/v1/triage"

async def run_comprehensive_test():
    async with httpx.AsyncClient() as client:
        # Test Case 1: The Initial Triage (The "Cache Miss")
        alert_a = {
            "alert_id": "SOC-2026-X1",
            "description": "Suspicious Login from Unusual Country",
            "source_ip": "192.168.1.50"
        }
        
        print("--- STAGE 1: INITIAL TRIAGE ---")
        start = time.time()
        resp1 = await client.post(API_URL, json=alert_a)
        duration1 = time.time() - start
        print(f"Status: {resp1.status_code} | Time: {duration1:.2f}s")
        print(f"Result: {resp1.json()}\n")

        # Test Case 2: Immediate Duplicate (The "Memory Hit")
        print("--- STAGE 2: MEMORY CACHE HIT ---")
        start = time.time()
        resp2 = await client.post(API_URL, json=alert_a)
        duration2 = time.time() - start
        print(f"Status: {resp2.status_code} | Time: {duration2:.4f}s")
        print(f"Note: {resp2.json().get('note', 'N/A')}")
        print("Efficiency: Should be nearly instant (< 0.01s)\n")

        print("--- STAGE 3: VERIFYING DISK PERSISTENCE ---")
        print("Check your project folder. Do you see 'triage_state.json'?")
        with open("triage_state.json", "r") as f:
            disk_data = json.load(f)
            if "SOC-2026-X1" in disk_data:
                print("✅ SUCCESS: Alert ID found in persistent storage.")
            else:
                print("❌ FAILURE: Alert ID not found on disk.")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())