import asyncio
import httpx
import time

API_URL = "http://127.0.0.1:8000/api/v1/triage"

async def send_alert(client, i):
    # Mixing unique IDs and duplicate IDs to test the cache
    alert_id = f"STRESS-BF-{i % 5}" # This will create 5 unique alerts across 20 requests
    payload = {
        "alert_id": alert_id,
        "description": "High-frequency Hydra brute force attempt detected on port 22.",
        "source_ip": f"192.168.1.{100 + i}"
    }
    try:
        start = time.perf_counter()
        resp = await client.post(API_URL, json=payload, timeout=120.0)
        end = time.perf_counter()
        print(f"[{i}] ID: {alert_id} | Status: {resp.status_code} | Time: {end-start:.2f}s")
    except Exception as e:
        print(f"[{i}] Failed: {e}")

async def run_stress():
    async with httpx.AsyncClient() as client:
        # Fire 10 alerts at once
        tasks = [send_alert(client, i) for i in range(10)]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    print("[!] LAUNCHING HYDRA BURST STRESS TEST...")
    start_time = time.perf_counter()
    asyncio.run(run_stress())
    print(f"[*] TEST COMPLETE in {time.perf_counter() - start_time:.2f}s")