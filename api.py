from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from logger_config import logger
import os
import asyncio
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse


# 1. Load secure credentials from .env & Config

load_dotenv()
AI_TIMEOUT = 10

# Global Dictionary
processed_alerts = {}

# 2. Structured logging configuration

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 3. Initialize API

app = FastAPI(title="Agentic SOC - Autonomous Triage API", version="1.0")

# 4. Data Models: Define the expected JSON payload from a SIEM

class SecurityAlert(BaseModel):
    alert_id: str
    description: str
    source_ip: str

# 5. Worker: Simulating LLM/CrewAI agent

async def call_llm_agent(alert: SecurityAlert):
    await asyncio.sleep(2)
    return "SUCCESS: Block Source IP Aat Firewall"


def load_rag_context():
    """Reads the local playbook to ground the LLM response."""
    try:
        with open("context/playbooks.txt", "r") as file:
            return file.read()
    except FileNotFoundError:
        logger.error("RAG context file not found.")
        return None
 

# 6. The Route - IDEMPOTENT

@app.post("/api/v1/triage")
async def triage_alert(alert: SecurityAlert):
    # STEP A: THE CHECK (Idempotency Logic)
    # Before we do anything, check if we already have seen this specific Alert ID

    if alert.alert_id in processed_alerts:
        logger.info(f"CACHE HIT: Alert {alert.alert_id} already processed. Retrieving saved result.")
        return {
            "status" : "success",
            "action" : processed_alerts[alert.alert_id],
            "note" : "cached_response"
        }

    logger.info(f"CACHE MISS: New Alert ID {alert.alert_id}. Starting AI Triage.")

    try:
        # STEP B: THE EXECUTION
        response = await asyncio.wait_for(call_llm_agent(alert), timeout=AI_TIMEOUT)

        if not response:
            raise ValueError("Empty response from AI")

        # STEP C: THE COMMIT - Saving to Memory
        # We will save the cache IF the AI Succeeds.
        processed_alerts[alert.alert_id] = response

        logger.info(f"SUCCESS: Result saved to cache for Alert {alert.alert_id}")
        return {"status": "success", "action": response}

    except asyncio.TimeoutError:
        logger.error(f"TIMEOUT: Alert {alert.alert_id} failed.")
        return JSONResponse(
            status_code=504,
            content={"status" : "error",
                     "reason" : "AI_TIMEOUT"
                    }
        )

    except Exception as e:
        logger.exception(f"SYSTEM FAILURE: {alert.alert_id}")
        return JSONResponse(
            status_code=500,
            content={
                "status" : "error",
                "reason" : "INTERNAL_FAILURE"
            }
        )  
    