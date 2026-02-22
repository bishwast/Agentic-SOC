import os
import pandas as pd
import json
from pathlib import Path
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM  # FIXED: Added missing comma
from tools.ip_intel import AbuseIPDBTool

# --- PATH CONFIGURATION ---
# This finds the directory where the script is currently running
BASE_DIR = Path(__file__).resolve().parent
JSON_DB = BASE_DIR / "documentation" / "active_incidents.json"
MD_LOG = BASE_DIR / "documentation" / "agent_decisions.md"

# 1. Environment Setup
load_dotenv()

# Explicitly define the local Ollama LLM
local_llm = LLM(
    model="ollama/llama3.2",
    base_url="http://localhost:11434"
)

# 2. Tool Initialization
reputation_tool = AbuseIPDBTool()

# 3. Agents
# Update the Threat Researcher Agent in main.py
threat_researcher = Agent(
    role='Threat Researcher',
    goal='Enrich alerts with global threat intelligence and MITRE mapping.',
    backstory=(
        "You are an expert CTI analyst. You check IP reputation and "
        "always map findings to the MITRE ATT&CK framework. Your analysis "
        "must include the specific Technique ID (e.g., T1110 for Brute Force) "
        "and a brief explanation of the tactical goal."
    ),
    tools=[reputation_tool],
    llm=local_llm,
    verbose=True,
    allow_delegation=False,
)

incident_commander = Agent(
    role='Incident Commander',
    goal='Propose mitigation actions for the SOC team.',
    backstory=(
        "You are the Incident Commander. You review threat reports and propose a "
        "response (BLOCK or WATCH). You do not execute the block yourself; "
        "instead, you log a formal request for the security engineer to approve."
    ),
    llm=local_llm,
    verbose=True,
    allow_delegation=False,
)

# 4. Tasks
research_task = Task(
    description="Analyze the source IP {src_ip} using global threat intelligence.",
    expected_output="A summary of the IP reputation score and history.",
    agent=threat_researcher
)

mitigation_task = Task(
    description=(
        "Review the research findings for {src_ip}.\n"
        "1. Determine if the IP is a high risk.\n"
        "2. Generate a formal 'Request for Change' (RFC) to BLOCK or WATCH the IP.\n"
        "3. Your final answer must be the content of this request."
    ),
    expected_output="A formal mitigation proposal.",
    agent=incident_commander
)

# 5. Team Orchestration
soc_crew = Crew(
    agents=[threat_researcher, incident_commander],
    tasks=[research_task, mitigation_task],
    process=Process.sequential,
    verbose=True
)

# --- JSON LOGGING FOR DASHBOARD ---
def log_to_dashboard(result, inputs):
    # Ensure the directory exists
    os.makedirs(JSON_DB.parent, exist_ok=True)
    
    new_entry = {
        "id": str(pd.Timestamp.now().timestamp()),
        "timestamp": str(pd.Timestamp.now()),
        "src_ip": inputs['src_ip'],
        "status": "PENDING",
        "ai_analysis": str(result)
    }
    
    data = []
    # Read existing data using the correct variable name
    if JSON_DB.exists():
        with open(JSON_DB, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
        
    data.append(new_entry)
    
    with open(JSON_DB, "w") as f:
        json.dump(data, f, indent=4)

# 6. Proof of Work (Markdown)
def save_proof_of_work(result, inputs):
    os.makedirs(MD_LOG.parent, exist_ok=True)
    
    timestamp = pd.Timestamp.now()
    
    with open(MD_LOG, "a") as f:
        f.write(f"\n## Incident Report: {inputs['src_ip']}\n")
        f.write(f"- **Timestamp**: {timestamp}\n")
        f.write(f"- **Status**: PENDING HUMAN APPROVAL\n")
        f.write(f"### Agent Proposal\n")
        f.write(f"{result}\n")
        f.write("\n---\n")
    
    print(f"\n[+] Success! Proposal logged to {MD_LOG}")
    
    # CALL THE JSON LOGGER
    log_to_dashboard(result, inputs)

    # Prepare data for the professional report and call it
    incident_data = {
        'src_ip': inputs['src_ip'],
        'ai_analysis': str(result)
    }
    generate_soc_report(incident_data)

def generate_soc_report(incident_data):
    """Formats raw AI output into a professional PIR (Post-Incident Report)."""
    report = f"""# SOC INCIDENT REPORT: {incident_data['src_ip']}
**Date:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
**Severity:** HIGH
**Status:** MITIGATED (Simulation)

## 1. Executive Summary
On {pd.Timestamp.now().date()}, an automated brute-force attack was detected. The Agentic SOC system identified the threat and initiated an AI-driven investigation.

## 2. AI Analysis & Investigation Results
{incident_data['ai_analysis']}

## 3. Proposed Remediation
The Incident Commander recommends a BLOCK on the source IP at the network perimeter.
"""
    with open(f"documentation/REPORT_{incident_data['src_ip']}.md", "w") as f:
        f.write(report)
    print(f"[+] Professional Report Generated: documentation/REPORT_{incident_data['src_ip']}.md")

if __name__ == "__main__":
    print("### SOC Crew Initializing (Passive Mode) ###")
    inputs = {'src_ip' : '1.2.3.4'}
    result = soc_crew.kickoff(inputs=inputs)
    save_proof_of_work(result, inputs)