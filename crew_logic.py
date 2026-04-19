from crewai import Agent, Task, Crew, Process, LLM

# Use the 'openai/' prefix to use the native driver
local_llm = LLM(
    model="openai/llama3.2",
    base_url="http://localhost:11434/v1", # The /v1 is required for the OpenAI tunnel
    api_key="ollama" # Placeholder for the mandatory field
)

def run_soc_crew(alert_description, playbook_context):
    triage_specialist = Agent(
        role='Senior SOC Analyst',
        goal='Triage security alerts using local playbooks.',
        backstory='Expert in threat intelligence.',
        llm=local_llm, 
        verbose=True
    )

    security_auditor = Agent(
        role='Security Auditor',
        goal='Verify actions for safety and accuracy.',
        backstory='Ensures zero false positives.',
        llm=local_llm,
        verbose=True
    )

    # (Rest of the tasks and crew remains the same)
    triage_task = Task(
        description=f"Analyze alert: {alert_description}. Context: {playbook_context}",
        expected_output="A single action recommendation (e.g., 'BLOCK IP').",
        agent=triage_specialist
    )

    audit_task = Task(
        description="Verify the action. Return only the final verified action string.",
        expected_output="A verified action string.",
        agent=security_auditor
    )

    soc_crew = Crew(
        agents=[triage_specialist, security_auditor],
        tasks=[triage_task, audit_task],
        process=Process.sequential
    )

    return soc_crew.kickoff()