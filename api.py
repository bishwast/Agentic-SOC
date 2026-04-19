import os
import json
import asyncio
import logging
import ollama
import subprocess

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from logger_config import logger
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse



# 1. Setup and Persistence
load_dotenv()
STATE_FILE = "triage_state.json"
AI_TIMEOUT = 10

def load_persistence():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

# Only Once from the Disk Initialize the Memory
processed_alerts = load_persistence()
        

# 2. Structured logging configuration
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 3. API and Models
app = FastAPI(title="Agentic SOC - Autonomous Triage API")

# 4. Data Models: Define the expected JSON payload from a SIEM
class SecurityAlert(BaseModel):
    alert_id: str
    description: str
    source_ip: str

# Simulating LLM/CrewAI agent
async def call_llm_agent(alert: SecurityAlert, context: str):
    """
    PHASE 7: Real LLM Integration via Ollama on NVIDIA DGX.
    This replaces the 'Simulated' if/else logic with neural reasoning.
    """
    try:
        # We tell the AI exactly how to behave
        system_instruction = f"""
        You are an Autonomous SOC Analyst. 
        Your task is to triage security alerts using ONLY the provided playbooks.
        
        RULES:
        1. If a playbook matches, state the ACTION clearly.
        2. If no playbook matches, respond: 'ACTION: Manual Triage Required'.
        3. Be concise. One sentence only.

        OFFICIAL PLAYBOOKS:
        {context}
        """

        user_input = f"ALERT ID: {alert.alert_id} | DESCRIPTION: {alert.description} | SOURCE: {alert.source_ip}"

        # Using the model you already have: llama3.2
        response = await asyncio.to_thread(
            ollama.chat,
            model='llama3.2', 
            messages=[
                {'role': 'system', 'content': system_instruction},
                {'role': 'user', 'content': user_input},
            ]
        )

        # Extract the text response from the Ollama object
        return response['message']['content'].strip()

    except Exception as e:
        logger.error(f"Ollama Neural Error: {e}")
        return "ACTION: Neural Engine Failure (Fallback to Manual)"


def load_rag_context():
    """Reads the local playbook to ground the LLM response."""
    try:
        with open("context/playbooks.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        logger.warning("RAG context file missing. AI will rely on general knowledge.")
        return "No specific playbook available."
 
# 5. The Response Manager

async def execute_active_response(alert_id: str, ai_action: str, ip:str):
    """The Dispatcher: Translates AI Texts into System-Level actions."""
    
    action_log = "firewall_actions.log"
    ai_action_lower = ai_action.lower()

    try:
        # STEP A: IP Blocking (Simulation/Local Firewall)
        if "block" in ai_action_lower or "mfa" in ai_action_lower:
            command = f"BLOCKING IP: {ip} for Alert {alert_id}"
            logger.info(f"[*] ACTIVE RESPONSE: {command}")

            with open(action_log, "a") as f:
                f.write(f"[{alert_id}] {command} - Reason: {ai_action}\n")
            return "SUCCESS: Firewall Rule Applied"
        elif "isolate" in ai_action_lower:
            command = f"ISOLATING HOST:{ip}"
            logger.warning(f"[!] CRITICAL RESPONSE: {command}")

            with open(action_log, "a") as f:
                f.write(f"[{alert_id}] {command} - Reason: {ai_action}\n")
            return "SUCCESS: Host Isolated from Segment"

        # FALLBACK: When no high-confidence action detected
        else:
            logger.info(f"[!] RESPONSE: No automated action taken for Alert {alert_id}. Pending Manual Review.")
            return "PENDING: Manual Review Required"
    except Exception as e:
        logger.error(f"Active Response Failed: {e}")
        return "FAILURE: Response Execution Error"

# 6. The Route - IDEMPOTENT

@app.post("/api/v1/triage")
async def triage_alert(alert: SecurityAlert):

    # STEP A: THE CHECK (Idempotency Logic) - Before we do anything, check if we already have seen this specific Alert ID
    if alert.alert_id in processed_alerts:
        logger.info(f"CACHE HIT: Alert {alert.alert_id} already processed. Retrieving saved result.")
        return {
            "status" : "success",
            "action" : processed_alerts[alert.alert_id],
            "note" : "cached_response"
        }

    logger.info(f"CACHE MISS: New Alert ID {alert.alert_id}. Starting AI Triage.")

    try:

        # STEP A. RETRIEVE and GENERATE (Ollama Call)
        playbook_content =  load_rag_context()
        ai_response = await asyncio.wait_for(
            call_llm_agent(alert, playbook_content), 
            timeout=AI_TIMEOUT)

        # STEP B. EXECUTE: The New Active Response Phase
        execution_status = await execute_active_response(
            alert.alert_id,
            ai_response,
            alert.source_ip
        )

        # STEP C: THE COMMIT - Save to RAM and Disk.
        processed_alerts[alert.alert_id] = ai_response
        # Update the permanent record (Persistence)
        with open(STATE_FILE, "w") as f:
            json.dump(processed_alerts, f, indent=4)

        logger.info(f"SUCCESS: Result saved to cache for Alert {alert.alert_id}")

        # STEP D: RETURN (Include all execution status for the SIEM)
        return {"status": "success", 
                "action": ai_response,
                "response_execution": execution_status
                }

    except asyncio.TimeoutError:
        logger.error(f"TIMEOUT: Alert {alert.alert_id} failed.")
        return JSONResponse(
            status_code=504,
            content={"status" : "error",
                     "reason" : "AI_TIMEOUT"
                    }
        )
    
    except Exception as e:
        logger.exception(f"SYSTEM FAILURE: Alert {alert.alert_id} encountered an error.")
        return JSONResponse(
            status_code=500,
            content={
                "status" : "error",
                "reason" : "INTERNAL_FAILURE"
            }
        )  
    