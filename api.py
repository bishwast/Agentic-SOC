from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from logger_config import logger
import os
from dotenv import load_dotenv

# Load secure credentials from .env
load_dotenv()

app = FastAPI(title="Agentic SOC - Autonomous Triage API", version="1.0")

# Define the expected JSON payload from a SIEM
class SecurityAlert(BaseModel):
    alert_id: str
    description: str
    source_ip: str

def load_rag_context():
    """Reads the local playbook to ground the LLM response."""
    try:
        with open("context/playbooks.txt", "r") as file:
            return file.read()
    except FileNotFoundError:
        logger.error("RAG context file not found.")
        return None
 
@app.post("/api/v1/triage")
async def trigger_ai_triage(alert: SecurityAlert):
    logger.info(f"Incoming alert: [{alert.alert_id}] from IP: {alert.source_ip}")
    
    playbook_context = load_rag_context()
    if not playbook_context:
        raise HTTPException(status_code=500, detail="Internal System Error: Missing IR Playbooks")
    
    logger.info("Loaded RAG playbooks successfully.")
    
    # Construct the RAG prompt
    prompt = f"Context: {playbook_context}\n\nTask: Analyze this alert and recommend an action: {alert.description}"
    
    # TODO: Future CrewAI/Ollama execution goes here.
    # Simulated response for interview demonstration:
    simulated_ai_response = f"Action Required: Based on IR directives, investigate IP {alert.source_ip}."
    
    logger.info(f"Triage completed successfully for alert {alert.alert_id}.")
    
    return {
        "status": "success", 
        "alert_processed": alert.alert_id,
        "ai_analysis": simulated_ai_response,
        "prompt_constructed": prompt
    }