# Agentic SOC: Autonomous Incident Response on NVIDIA DGX

This repository implements an **Autonomous Agentic SOC** (Phase 5: Autonomous) running on on-premise NVIDIA DGX infrastructure. The system utilizes a multi-agent AI architecture to ingest SIEM telemetry, perform threat reasoning, and execute response actions without human intervention.

## 1. Core Infrastructure

The project is built on strictly on-premise components to ensure data privacy and high-performance inference.

| Component | Type | Function |
| :--- | :--- | :--- |
| **NVIDIA DGX** | Hardware |High-performance compute platform (AARCH64/ARM64 Architecture). |
| **Wazuh** | SIEM/XDR | Endpoint telemetry collection, rule analysis, and JSON alert generation. |
| **Ollama** | Inference | Local engine hosting **Llama 3.2** for privacy-compliant AI processing. |
| **CrewAI** | Orchestration | Manages agent roles, task delegation, and sequential process flows. |
| **LangChain** | Middleware | Handles communication protocols between agents and local LLM endpoints. |

## 2. Agentic Framework & Logic

The system operates on an **OODA Loop** (Observe, Orient, Decide, Act) logic model.

### Agent Roles 
1.  **Triage Specialist** (*Orientation*): Parses raw JSON alerts to extract security entities (Source IP, Rule ID, Usernames). Focuses solely on factual data extraction.
2.  **Threat Researcher** (*Decision*): Analyzes entities against MITRE ATT&CK patterns to distinguish between false positives and active threats.
3.  **Incident Commander** (*Action*): The final authority. Balances security requirements with business uptime to issue definitive actions (e.g., BLOCK, WATCH, IGNORE).

### Process Flow
1.  **Ingestion:** Python "File Watcher" monitors `/var/ossec/logs/alerts/alerts.json` for new events.
2.  **Filtering:** Pre-processing script filters for High Severity alerts (Level ≥ 10) to reduce noise.
3.  **Orchestration:** CrewAI instantiates agents using `agents.yaml` and `tasks.yaml` configurations.
4.  **Response:** The Incident Commander generates a final justification and action report.

## 3. Installation & Setup

### Prerequisites
* **System:** NVIDIA DGX or ARM64 Linux environment.
* **Python:** Virtual environment (`venv`) for dependency isolation.
* **Model:** Llama 3.2 pulled via Ollama.

### Deployment
```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies (Pinned versions for stability)
pip install crewai langchain_community litellm==1.80.11 openai==1.83.0

# 3. Verify Local Inference
ollama list  # Should show Llama3.2:latest
```
Ollama Avive Status
![Ollama Avive Status](/documentation/images/ollama_active.png)

Ollama List
![Ollama List](/documentaiton/images/ollama_list.png)

## 4. Usage

### Starting the SOC
Run the entry point script using the virtual environment's Python binary to bridge root permissions (required for Wazuh logs) with local dependencies.

```bash
sudo ./venv/bin/python3 main.py
```
### Validating the Pipeline (Synthetic Stress Test)

To verify the response logic without a live attacker, inject a synthetic Level 12 alert directly into the Wazuh log stream.

```bash
echo '{"timestamp":"2025-12-27T23:55:00.000+0000","rule":{"level":12,"description":"User admin logged in from unauthorized IP 192.168.10.254 - Possible Account Takeover","id":"100001"},"agent":{"id":"001","name":"dgx-node-01"},"manager":{"name":"wazuh-manager"},"id":"1735342200.12345","full_log":"Dec 27 23:55:00 dgx-node-01 sshd[1234]: Accepted password for admin from 192.168.10.254 port 54321 ssh2","decoder":{"name":"sshd"},"data":{"srcip":"192.168.10.254","dstuser":"admin"}}' | sudo tee -a /var/ossec/logs/alerts/alerts.json > /dev/null
```
# Expected Output:

- Final Report: Threat Assessment Complete. Analysis indicates potential suspicious network activity... ACTION: BLOCK .
![Final Result: ACTION: BLOCK](/documentaiton/images/final_report.png)

### 5. Technical Achievements

- Environment Isolation: Implemented stable venv architecture to resolve circular dependency conflicts between crewai, litellm, and openai.

- Permission Bridging: Established targeted execution strategy allowing user-space Python agents to ingest root-protected SIEM logs.

- Local Inference: Achieved low-latency, privacy-preserving reasoning using on-premise GPUs via Ollama.

- Modular Orchestration: Decoupled agent logic into YAML configurations for scalable role and task management.

#### For detail documentation refer to the PDF file below.
![Detail Report](/documentaiton/reports/Agentic%20Soc%20Model%20Documentation.pdf)
