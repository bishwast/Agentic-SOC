from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from logger_config import logger
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse


# 1. Load secure credentials from .env & Config

load_dotenv()
AI_TIMEOUT = 10

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
 

# 6. The Route

@app.post("/api/v1/triage")
async def triage_alert(alert: SecurityAlert):
    # LOG START: Every request is logged for auditing.
    logger.info(f"START: Triage alert for Alert ID: {alert.alert_id}")

    try:
        # TIMEOUT LOGIC: Wrap the AI Call in a timer
        response = await asyncio.wait_for(
            call_llm_agent(alert), 
            timeout=AI_TIMEOUT
            )

        if not response:
            raise ValueError("LLM returned an empty response")
            
        logger.info(f"SUCCESS: AI Completed Triage for alert: {alert.alert_id}")

        return {
            "status": "success", 
            "action": response
            }

    except asyncio.TimeoutException:
        logger.error(f"TIMEOUT: AI took longer than {AI_TIMEOUT} to respond for Alert ID {alert.alert_id}")

        return JSONResponse(
            status_code=504,            # Gateway Timeout status code
            content={
                "status": "degraded",
                "action": "MANUAL_REVIEW_REQUIRED", 
                "reason": "AI_TIMEOUT"
                }
        )
    
    except Exception as e:
        # LOG FAILURE: 'logger.exception' records the full crash report internally.
        logger.exception(f"CRITICAL FAILURE: Unexpected error on Alert {alert.alert_id}")

        # GENERIC MESSAGE: To the user to keep the system secure - considering failure state
        return JSONResponse(
            status_code=500,            # Internal Server Error status code
            content={
                "status": "error", 
                "action": "ESCALATE_TO_HUMAN", 
                "reason": "INTERNAL_SYSTEM_FAILURE"
                }
        )