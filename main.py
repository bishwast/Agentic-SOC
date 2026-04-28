from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from logging.handlers import RotatingFileHandler
import os
import json
import re
from datetime import datetime
from crew_logic import run_agentic_triage
from tools.response_engine import ResponseEngine

# 1. CONFIGURE ENTERPRISE LOGGING
# Using a RotatingFileHandler ensures we don't overwhelm the DGX disk space.
log_handler = RotatingFileHandler("soc_service.log", maxBytes=1000000, backupCount=3)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[log_handler, logging.StreamHandler()]
)
logger = logging.getLogger("AgenticSOC")

# 2. INITIALIZE ACTIVE DEFENSE & SIEM ENGINES
response_engine = ResponseEngine()
SPLUNK_ENABLED_TOGGLE = os.getenv("SPLUNK_ENABLED", "False").lower() == "true"

try:
    from tools.splunk_connector import SplunkHEC
    SPLUNK_ENABLED = True if SPLUNK_ENABLED_TOGGLE else False
except ImportError:
    SPLUNK_ENABLED = False

splunk = SplunkHEC(token=os.getenv("SPLUNK_HEC_TOKEN", "")) if SPLUNK_ENABLED else None

# 3. INITIALIZE ATCE APP
app = FastAPI(
    title="Agentic SOC - Autonomous Threat Containment & Enforcement (ATCE)",
    version="1.0.0",
    description="Deterministic enforcement layer for probabilistic agentic triage."
)

class AlertRequest(BaseModel):
    alert_id: str
    description: str
    source_ip: str

class UnblockRequest(BaseModel):
    source_ip: str

# 4. STATEFUL AUDIT JOURNAL (Memory Layer)
def log_decision_to_history(alert_id, ip, decision_text, action):
    history_file = "soc_history.json"
    entry = {
        "timestamp": str(datetime.now()),
        "alert_id": alert_id,
        "ip": ip,
        "decision": decision_text,
        "action_taken": action
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
    with open(history_file, "w") as f:
        json.dump(history[-50:], f, indent=4)

# 5. ATCE TRIAGE & ENFORCEMENT ENDPOINT
@app.post("/api/v1/triage")
async def triage_alert(alert: AlertRequest):
    logger.info(f"Initializing ATCE Workflow: {alert.alert_id} | Target: {alert.source_ip}")
    
    try:
        # Step A: Execute Agentic Forensic Reasoning
        # This calls your CrewAI logic (Analyst + Auditor)
        result = run_agentic_triage(alert.model_dump())
        recommendation_text = str(result)
        
        # Step B: Logic Extraction via Regex
        confidence_match = re.search(r"CONFIDENCE:\s*(\d+)", recommendation_text.upper())
        confidence_score = int(confidence_match.group(1)) if confidence_match else 0
        
        logger.info(f"DEBUG: Original Agent Score is {confidence_score}")

        # --- REFINED ATCE POLICY OVERRIDE (Policy-702) ---
        # We are expanding the search to include the CVE and making it more aggressive
        critical_indicators = ["RCE", "CRITICAL", "EXPLOIT", "CVE-2026-33827", "MALICIOUS"]
        
        # Check if the report contains the high-risk indicators
        is_critical = any(indicator in recommendation_text.upper() for indicator in critical_indicators)
        
        if is_critical:
            logger.warning(f"ATCE POLICY OVERRIDE TRIGGERED: Critical signature found in report.")
            confidence_score = 95 
        else:
            logger.info("DEBUG: No critical signatures detected. Proceeding with Agent score.")
        # --------------------------------------------------

        # Step C: Active Defense Execution
        # This triggers the iptables block if confidence >= 90
        action_executed = response_engine.execute_response(
            ip=alert.source_ip, 
            confidence=confidence_score, 
            decision_text=recommendation_text
        )

        # Step D: Update Audit Journal
        log_decision_to_history(alert.alert_id, alert.source_ip, recommendation_text, action_executed)

        # Step E: SIEM Synchronization (Optional)
        siem_sync_status = False
        if SPLUNK_ENABLED and splunk:
            siem_sync_status = splunk.log_event(
                alert_id=alert.alert_id,
                source_ip=alert.source_ip,
                recommendation=f"{recommendation_text} | Action: {action_executed}",
                audit_reason="ATCE Autonomous Execution"
            )

        return {
            "status": "success",
            "alert_id": alert.alert_id,
            "atce_confidence": confidence_score,
            "action_executed": action_executed,
            "forensic_report": recommendation_text
        }
        
    except Exception as e:
        logger.error(f"ATCE Engine Critical Failure: {str(e)}")
        raise HTTPException(status_code=500, detail="The ATCE Engine encountered a critical reasoning error.")

@app.post("/api/v1/unblock")
async def unblock_ip(request: UnblockRequest):
    """
    Administrative endpoint to manually revoke an autonomous block.
    """
    logger.info(f"Manual Revocation Request: IP {request.source_ip}")
    
    success = response_engine.unblock_ip(request.source_ip)
    
    if success:
        # Log the cleanup action to your history file for auditing
        log_decision_to_history(
            alert_id="ADMIN_REVOKE", 
            ip=request.source_ip, 
            decision_text="Manual Admin Cleanup", 
            action="UNBLOCKED"
        )
        return {
            "status": "success", 
            "ip": request.source_ip, 
            "action": "REVOKED",
            "message": "Firewall rule successfully removed."
        }
    else:
        raise HTTPException(
            status_code=404, 
            detail="Failed to remove rule. IP may not be currently blocked."
        )

@app.get("/health")
async def health():
    return {
        "status": "operational", 
        "mode": "Autonomous Enforcement (ATCE)", 
        "engine": "Llama 3.2 (DGX-Optimized)",
        "policy_version": "702.v1",
        "last_health_check": str(datetime.now())
    }

    

if __name__ == "__main__":
    import uvicorn
    # Starting the server on the DGX local loopback
    uvicorn.run(app, host="0.0.0.0", port=8000)