from dotenv import load_dotenv
load_dotenv()  # Loads variables from .env
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from logging.handlers import RotatingFileHandler
import os
import json
from datetime import datetime
from crew_logic import run_agentic_triage

# 1. CONFIGURE LOGGING (Moved up to capture startup logs)
log_handler = RotatingFileHandler("soc_service.log", maxBytes=1000000, backupCount=3)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[log_handler, logging.StreamHandler()]
)
logger = logging.getLogger("AgenticSOC")

# 2. RESILIENCE CHECK: Environment-Aware SIEM Toggle
# This prevents the "Connection Refused" errors when Splunk is not present.
SPLUNK_ENABLED_TOGGLE = os.getenv("SPLUNK_ENABLED", "False").lower() == "true"

try:
    from tools.splunk_connector import SplunkHEC
    # Only enable if the file exists AND the .env toggle is explicitly True
    SPLUNK_ENABLED = True if SPLUNK_ENABLED_TOGGLE else False
except ImportError:
    SPLUNK_ENABLED = False

if SPLUNK_ENABLED:
    logger.info("SIEM Mode: Splunk Integration Active")
    splunk = SplunkHEC(token=os.getenv("SPLUNK_HEC_TOKEN", ""))
else:
    logger.info("SIEM Mode: Local-Only (Splunk Disabled)")
    splunk = None

# 3. INITIALIZE APP
app = FastAPI(title="Agentic SOC - Phase 11.5 (Hardened)")

# 4. DATA MODELS
class AlertRequest(BaseModel):
    alert_id: str
    description: str
    source_ip: str

# 5. MEMORY HELPER (Addressing Statelessness)
def log_decision_to_history(alert_id, ip, decision):
    """
    Maintains a local JSON journal of AI decisions for audit and pattern recognition.
    """
    history_file = "soc_history.json"
    entry = {
        "timestamp": str(datetime.now()),
        "alert_id": alert_id,
        "ip": ip,
        "decision": decision
    }
    
    try:
        if os.path.exists(history_file):
            with open(history_file, "r") as f:
                history = json.load(f)
        else:
            history = []
    except (json.JSONDecodeError, FileNotFoundError):
        history = []

    history.append(entry)
    
    # Maintain a rolling window of 50 events to save disk I/O on the DGX
    with open(history_file, "w") as f:
        json.dump(history[-50:], f, indent=4)

# 6. ENDPOINTS
@app.post("/api/v1/triage")
async def triage_alert(alert: AlertRequest):
    """
    Main endpoint for AI-driven triage and governance.
    """
    logger.info(f"Incoming Triage Request: {alert.alert_id} for IP {alert.source_ip}")
    
    try:
        # Step A: Run Multi-Agent Reasoning Trace
        result = run_agentic_triage(alert.dict())
        recommendation_text = str(result)
        
        # Step B: Update Local Memory (Phase 11.5 Upgrade)
        log_decision_to_history(alert.alert_id, alert.source_ip, recommendation_text)

        # Step C: Log to SIEM (If configured)
        siem_sync_status = False
        if SPLUNK_ENABLED and splunk:
            siem_sync_status = splunk.log_event(
                alert_id=alert.alert_id,
                source_ip=alert.source_ip,
                recommendation=recommendation_text,
                audit_reason="Hardened AI Triage Verified"
            )
            logger.info(f"SIEM Sync for {alert.alert_id}: {siem_sync_status}")

        return {
            "status": "success",
            "alert_id": alert.alert_id,
            "recommendation": recommendation_text,
            "siem_synced": siem_sync_status,
            "audit_logged": True
        }
        
    except Exception as e:
        logger.error(f"Triage Engine Failure: {str(e)}")
        raise HTTPException(status_code=500, detail="The Agentic Engine encountered a reasoning error.")

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "engine": "Llama 3.2 (DGX-Accelerated)", 
        "siem_enabled": SPLUNK_ENABLED,
        "memory_active": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)