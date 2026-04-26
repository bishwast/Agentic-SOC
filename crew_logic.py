from crewai import Agent, Task, Crew, Process, LLM
from tools.threat_intel import ThreatIntelProvider
import os

# Initialize enrichment
intel = ThreatIntelProvider()

def run_agentic_triage(alert_data):

    # Custom storage path to avoid /tmp permission issues
    os.environ["CREWAI_STORAGE_DIR"] = "./.crewai"

    # 1. Native LLM Initialization
    llm = LLM(
        model="ollama/llama3.2",
        base_url="http://localhost:11434"
    )

    # 2. Explainability Requirements

    analyst = Agent(
        role='Senior SOC Analyst',
        goal='Analyze security alerts and provide deep forensic reasoning trace.',
        backstory= """Expert Teir-3 Analyst. You must always cite technical evidence.
                    Contrxt: IP Reputation {ip_rep}, MITRE {mitre}""".format(
                        ip_rep = intel.get_ip_reputation(alert_data.get('source_ip')),
                        mitre = intel.get_mitre_context(alert_data.get('description'))
                    ),
        llm=llm,
        verbose=True
    )

    # 3. Security Auditor - with Governance (Confidence Scoring)

    auditor = Agent(
        role='Security Compliance Auditor',
        goal='Assign a confidence score to the Analyst\'s recommendation.',
        backstory="""You are the final gatekeeper. 
        POLICY OVERRIDE (702): If an IP has a 99%+ reputation score and is attempting an RCE, 
        the Confidence Score MUST be 95 or higher to allow for immediate autonomous blocking.
        Do not use placeholders. Be decisive.""",
        llm=llm,
        verbose=True
    )

    # 4. TASK: The Reasoning Trace (Addressing LLM02)

    triage_task = Task(
        description=f"Perform a deep analysis of alert: {alert_data.get('description')}",
        agent=analyst,
        expected_output="""A forensic report. YOU MUST:
        1. Replace all placeholders with actual data from {source_ip}.
        2. Confirm the AbuseIPDB score of 99%+ is evidence of malicious intent.
        3. State clearly: 'Recommendation: IMMEDIATE BLOCK REQUIRED'."""
    )

    # 5. TASK: The Governance Audit (Addressing LLM08)
    audit_task = Task(
        description="Verify the analyst's report. Calculate a Confidence Score (0-100).",
        agent=auditor,
        expected_output="""Return exactly in this format:
                        CONFIDENCE: [Score]
                        DECISION: [Action]
                        REASON: [Brief explanation]"""
    )

    crew = Crew(
        agents=[analyst, auditor], 
        tasks=[triage_task, audit_task], 
        process=Process.sequential
        )
    
    return crew.kickoff()