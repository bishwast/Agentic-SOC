import yaml
from crewai import Agent, Task, Crew, Process, LLM

class AgenticSocCrew:
    """
    Orchestrates the Agentic SOC team using the Llama 3.2.
    """
    def __init__(self):
        # Loading the instruction manuals - YAML
        self.agents_config = self._load_yaml('config/agents.yaml')
        self.tasks_config = self._load_yaml('config/tasks.yaml')

        # Connect to local Ollama - Llama 3.2
        self.local_llm = LLM(
            model="ollama/llama3.2",
            base_url="http://localhost:11434"
        )
    
    def _load_yaml(self, path):
        """
        Safely opens a YAML file, reads it, converts it into Python data, and returns it.
        """
        with open (path , 'r') as f:
            return yaml.safe_load(f)
    
    def build_crew(self, raw_alert_data):
        """
        Creates a team of AI agents, gives them tasks, and connects everything 
        so the work happens in order.
        """
        # Using YAML configs to define Agents
        triage_specialist = Agent(
            config=self.agents_config['triage_specialist'],
            llm=self.local_llm,
            verbose=True
        )

        commander = Agent(
            config=self.agents_config['incident_commander'],
            llm=self.local_llm,
            verbose=True
        )

        # Using YAML configs to define Tasks
        # In tasks.yaml the {raw_alert} will be replaced by the actual data here.
        triage_task= Task(
            config=self.tasks_config['triage_task'],
            agent=triage_specialist,
            context_variables={'raw_alert': raw_alert_data}
        )

        decision_task = Task(
            config=self.tasks_config['response_decision_task'],
            agent=commander
        )

        # Crew Assemble
        return Crew(
            agents=[triage_specialist, commander],
            tasks=[triage_task, decision_task],
            process=Process.sequential, 
            verbose=True
        )

