import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from tools.threat_intel import ThreatIntelProvider
from langchain_community.tools import DuckDuckGoSearchRun
from crewai.tools import tool

# Load the .env file into the active environment
load_dotenv()

# Initialize enrichment
intel = ThreatIntelProvider()

# --- THE NATIVE TOOL WRAPPER ---
@tool("Internet Search Tool")
def internet_search_tool(query: str) -> str:
    """Searches the internet for emerging threats, CVE details, and exploit behaviors."""
    ddg = DuckDuckGoSearchRun()
    return ddg.invoke(query)

def run_agentic_triage(alert_data):

    # Custom storage path to avoid /tmp permission issues
    os.environ["CREWAI_STORAGE_DIR"] = "./.crewai"

    # 1. Native LLM Initialization (Data Privacy/Sovereignty)
    llm = LLM(
        model="ollama/llama3.2",
        base_url="http://localhost:11434"
    )

    # 2. CLOUD AUDITOR
    cloud_gpt4 = LLM(
        model="gpt-4o", 
        api_key=os.environ.get("OPENAI_API_KEY")
    )

    # --- AGENTS ---

    # 3. Cyber Threat Intelligence Lead
    researcher = Agent(
        role='Cyber Threat Intelligence Lead',
        goal='Cross-reference alert signatures with global threat intelligence and live CVE databases.',
        backstory="""Expert at correlating raw technical signatures with global threat patterns. 
        You use live search tools to identify if an alert matches known 2025-2026 exploitation techniques.""",
        tools=[internet_search_tool],  # <-- Explicitly using the wrapped tool
        llm=cloud_gpt4,
        verbose=True
    )

    # 4. Explainability Requirements
    analyst = Agent(
        role='Senior SOC Analyst',
        goal='Analyze security alerts and provide deep forensic reasoning trace.',
        backstory= """Expert Teir-3 Analyst. You must always cite technical evidence.
                    Context: IP Reputation {ip_rep}, MITRE {mitre}""".format(
                        ip_rep = intel.get_ip_reputation(alert_data.get('source_ip')),
                        mitre = intel.get_mitre_context(alert_data.get('description'))
                    ),
        llm=llm,
        verbose=True
    )

    # 5. Security Auditor
    auditor = Agent(
        role='Security Compliance Auditor',
        goal='Assign a confidence score to the Analyst\'s recommendation.',
        backstory="""You are the final gatekeeper. 
        POLICY OVERRIDE (702): If an IP has a 99%+ reputation score and is attempting an RCE, 
        the Confidence Score MUST be 95 or higher to allow for immediate autonomous blocking.
        Do not use placeholders. Be decisive.""",
        llm=cloud_gpt4,
        verbose=True
    )

    # --- TASKS ---

    research_task = Task(
        description=f"Search for emerging threats and specific CVEs related to this signature: {alert_data.get('description')}.",
        agent=researcher,
        expected_output="""A technical intelligence summary identifying associated CVEs, 
        threat actor groups, and known malicious behaviors related to this alert."""
    )

    triage_task = Task(
        description=f"""Perform a deep analysis of alert: {alert_data.get('description')}.
                    IMPORTANT: Look for behavioral patterns. 
                    1. Is this a single event or a high-frequency burst (e.g., Brute Force)?
                    2. Does the Researcher's Intel suggest this tool (e.g., Hydra/Nmap) is being used?
                    3. Calculate the 'Aggression Score' based on the number of attempts.""",
        agent=analyst,
        expected_output="""A forensic report. YOU MUST:
        1. Replace all placeholders with actual data from {source_ip}.
        2. Confirm if the intelligence matches the AbuseIPDB score of 99%+.
        3. State clearly: 'Recommendation: IMMEDIATE BLOCK REQUIRED'."""
    )

    audit_task = Task(
        description="Verify the analyst's report against Policy-702. Calculate a Confidence Score (0-100).",
        agent=auditor,
        expected_output="""Return exactly in this format:
                        CONFIDENCE: [Score]
                        DECISION: [Action]
                        REASON: [Brief explanation]"""
    )

    # --- CREW ---
    
    crew = Crew(
        agents=[researcher, analyst, auditor], 
        tasks=[research_task, triage_task, audit_task], 
        process=Process.sequential
    )
    
    return crew.kickoff()