import os
import pandas as pd
import json
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from tools.ip_intel import AbuseIPDBTool

# 1. Environment Setup
load_dotenv()
os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"
os.environ["OPENAI_MODEL_NAME"] = "llama3.2"
os.environ["OPENAI_API_KEY"] = "ollama"

# 2. Tool Initialization
reputation_tool = AbuseIPDBTool()

# 3. Agents
threat_researcher = Agent(
    role='Threat Researcher',
    goal='Enrich alerts with global threat intelligence.',
    backstory="You are an expert CTI analyst. You check the IP reputation and provide a summary.",
    tools=[reputation_tool],
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

# --- NEW: JSON LOGGING FOR DASHBOARD ---
def log_to_dashboard(result, inputs):
    json_file = "documentaiton/active_incidents.json"
    
    new_entry = {
        "id": str(pd.Timestamp.now().timestamp()),
        "timestamp": str(pd.Timestamp.now()),
        "src_ip": inputs['src_ip'],
        "status": "PENDING",
        "ai_analysis": result
    }
    
    # Read existing data
    if os.path.exists(json_file):
        with open(json_file, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
        
    data.append(new_entry)
    
    with open(json_file, "w") as f:
        json.dump(data, f, indent=4)

# 6. Proof of Work (Markdown)
def save_proof_of_work(result, inputs):
    log_file = "documentaiton/agent_decisions.md"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    timestamp = pd.Timestamp.now()
    
    with open(log_file, "a") as f:
        f.write(f"\n## Incident Report: {inputs['src_ip']}\n")
        f.write(f"- **Timestamp**: {timestamp}\n")
        f.write(f"- **Status**: PENDING HUMAN APPROVAL\n")
        f.write(f"### Agent Proposal\n")
        f.write(f"{result}\n")
        f.write("\n---\n")
    
    print(f"\n[+] Success! Proposal logged to {log_file}")
    
    # CALL THE JSON LOGGER
    log_to_dashboard(result, inputs)

if __name__ == "__main__":
    print("### SOC Crew Initializing (Passive Mode) ###")
    inputs = {'src_ip' : '1.2.3.4'}
    result = soc_crew.kickoff(inputs=inputs)
    save_proof_of_work(result, inputs)