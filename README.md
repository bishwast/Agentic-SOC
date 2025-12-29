# Agentic SOC: Autonomous Incident Response on NVIDIA DGX

This repository implements a fully **Autonomous Agentic SOC** (Phase 5) running on on-premise NVIDIA DGX infrastructure. The system utilizes a multi-agent AI architecture to ingest SIEM telemetry, perform threat reasoning, and execute response actions without human intervention.

## 1. Core Infrastructure

The project is hosted on-premise to ensure data sovereignty and low-latency inference.

| Component | Type | Function |
| :--- | :--- | :--- |
| **NVIDIA DGX Spark** | Hardware | High-performance AARCH64/ARM64 platform for local LLM execution. |
| **Wazuh** | SIEM/XDR | Endpoint telemetry collection and Level 10+ alert generation. |
| **Ollama** | Inference | Local engine hosting **Llama 3.2** for privacy-compliant processing. |
| **CrewAI** | Orchestration | Multi-agent role management and sequential task execution. |
| **LangChain** | Middleware | Interface between agents and local Ollama API endpoints. |

## 2. Agentic Framework & Logic

The system follows the **OODA Loop** (Observe, Orient, Decide, Act) to handle security incidents.

### Agent Roles (Defined in `agents.yaml`)
* **Triage Specialist**: Extracts security entities (Source IP, Usernames, Rule IDs) from raw JSON logs.
* **Threat Researcher**: Cross-references entities against MITRE ATT&CK patterns to identify TTPs.
* **Incident Commander**: Final decision-maker. Issues response actions (BLOCK, WATCH, IGNORE) based on threat severity.

### Technical Process Flow
1.  **Ingestion**: A Python-based `File Watcher` monitors `/var/ossec/logs/alerts/alerts.json`.
2.  **Filtering**: Pre-processing logic isolates High Severity alerts (Level ≥ 10).
3.  **Reasoning**: CrewAI orchestrates sequential hand-offs between agents.
4.  **Response**: The Commander generates a finalized JSON report containing the justification and mitigation action.

## 3. Installation & Setup

### Prerequisites
* **Architecture**: ARM64 / AARCH64 (NVIDIA DGX Spark).
* **OS**: Ubuntu 24.04 LTS.
* **Dependencies**: Ollama with Llama 3.2 installed.

### Environment Deployment
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
![Ollama Avive Status](/documentaiton/images/ollama_active.png)

Ollama List
![Ollama List](/documentaiton/images/ollama_list.png)

## 4. Usage and Validation

### Execution

The entry point must be executed via the virtual environment's binary to maintain root-level access to Wazuh logs while utilizing user-space dependencies.

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

SOC Incident Response Report is explained in detail below.

![SOC Incident Response Report](./documentaiton/active-defense.md)

### 5. Technical Achievements

- Environment Isolation: Implemented stable venv architecture to resolve circular dependency conflicts between crewai, litellm, and openai.

- Permission Bridging: Established targeted execution strategy allowing user-space Python agents to ingest root-protected SIEM logs.

- Local Inference: Achieved low-latency, privacy-preserving reasoning using on-premise GPUs via Ollama.

- Modular Orchestration: Decoupled agent logic into YAML configurations for scalable role and task management.

#### For detail documentation refer to the PDF file below.
![Detail Report](/documentaiton/reports/Agentic%20Soc%20Model%20Documentation.pdf)

#### Link to the Incident Respose Result:
![Incident Respose Result](./documentaiton/insidence_response.md)

#### Link to the Mitigation Implementation Report:
![Mitigation Implementation Report](./documentaiton/mitigation_implementaion.md)
