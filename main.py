import os
import pandas as pd
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

# 6. Proof of Work (The "Digital Paper Trail")
def save_proof_of_work(result, inputs):
    log_file = "validation_pow/agent_decisions.md"
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

if __name__ == "__main__":
    print("### SOC Crew Initializing (Passive Mode) ###")
    inputs = {'src_ip' : '1.2.3.4'}
    result = soc_crew.kickoff(inputs=inputs)
    
    print("\n\n########################")
    print("## PROPOSAL GENERATED ##")
    print("########################\n")
    print(result)
    
    save_proof_of_work(result, inputs)