# Agentic-SOC: Autonomous Threat Triage on NVIDIA DGX

An autonomous Security Operations Center (SOC) pipeline that uses **Multi-Agent Orchestration (CrewAI)** and **Local LLMs (Llama 3.2 via Ollama)** to automate the Triage and Active Response phase of incident handling.

## 🚀 Key Features
- **Multi-Agent Triage:** Uses a 'Senior SOC Analyst' for initial reasoning and a 'Security Auditor' to prevent false positives.
- **On-Premise Privacy:** 100% of inference runs locally on NVIDIA DGX hardware; no data leaves the network.
- **RAG-Driven Governance:** Agents are constrained by official company playbooks (context/playbooks.txt).
- **Active Response:** Automatically enforces IP blocking and host isolation via a Python-based dispatch layer.
- **High-Concurrency Resilience:** Stress-tested to handle concurrent brute-force bursts with a custom caching/idempotency layer.

## 🛠️ Tech Stack
- **Inference:** Llama 3.2 (Ollama)
- **Framework:** CrewAI, LangChain, FastAPI
- **Security:** RAG (Retrieval-Augmented Generation)
- **Infrastructure:** NVIDIA DGX, Docker, Python 3.12

## Security Workflow Diagram

```mermaid
graph TD
    A[SIEM Alert] --> B{Cache Check}
    B -- Hit --> C[Return Stored Action]
    B -- Miss --> D[CrewAI: Specialist]
    D --> E[RAG: Playbook Context]
    E --> F[CrewAI: Auditor]
    F --> G{Keyword Check}
    G -- Match --> H[Firewall Log & Block]
    G -- No Match --> I[Manual Review Flag]
    H --> J[Return Response]
    I --> J

    classDef input fill:#1f77b4,color:#fff,stroke:#0d3b66,stroke-width:2px;
    classDef process fill:#2ca02c,color:#fff,stroke:#1b5e20,stroke-width:2px;
    classDef decision fill:#ff7f0e,color:#fff,stroke:#b45309,stroke-width:2px;
    classDef action fill:#d62728,color:#fff,stroke:#7f1d1d,stroke-width:2px;
    classDef output fill:#9467bd,color:#fff,stroke:#4c1d95,stroke-width:2px;

    class A input;
    class B,G decision;
    class C,D,E,F process;
    class H,I action;
    class J output;
```

## 📊 Performance
Validated via high-frequency stress testing (Hydra-style):
- **Initial Triage:** ~20-30s (Dual-agent reasoning).
- **Cached Response:** < 10ms (Idempotency layer).

## 📊 Performance & Validation
### High-Concurrency Stress Test
During a Hydra-style brute-force simulation, the system processed 10 concurrent multi-agent triage requests.
![Stress Test Launch](/images/stress_test_launch.png)
*Figure 1: Successful 200 OK responses with variable latency proving cache effectiveness.*

### Active Response Audit Trail
The following log shows the autonomous enforcement layer triggering firewall blocks based on AI-reasoning.
![Firewall Logs](/images/stress_test_firewallActions.png)
*Figure 2: Verified IP blocking and host isolation entries in the audit trail.*

---

## 🛡️ Agentic SOC: AI-Driven Incident Response Pipeline

## Recent Updates: Autonomous Triage API & RAG Integration
This project has been upgraded to a microservice architecture using **FastAPI**. 

* **API Gateway (`api.py`)**: Acts as a webhook receiver for Wazuh alerts. Utilizes Pydantic schemas to enforce strict JSON validation before processing.
* **RAG Context (`context/playbooks.txt`)**: Implements Retrieval-Augmented Generation (RAG). Before an LLM analyzes an alert, the system retrieves organizational Incident Response playbooks to govern the AI's decision-making process and prevent hallucinations.
* **Secure Configuration**: SIEM credentials and LLM endpoints are strictly managed via environment variables (`.env`).
* **Audit Logging (`logger_config.py`)**: All API transactions and LLM context-loads are permanently recorded to local log files for SOC compliance.

To view the interactive API documentation, run the server (`uvicorn api:app --reload`) and navigate to `http://127.0.0.1:8000/docs`.

### System Demonstration

**Interactive API Documentation (FastAPI/Swagger):**
![API Endpoint](images/fastapi_swaggerUI.png)

**Successful Triage Execution & RAG Context Injection:**
![Execution Response](images/execution_response.png)

**Audit Logging & Observability:**
![Audit Trail](images/audit_trial.png)

Built on NVIDIA DGX Spark | Llama 3.2 | Wazuh SIEM | CrewAI
### 🚀 The Mission

Modern Security Operations Centers (SOCs) are overwhelmed by "alert fatigue." This project demonstrates a SOAR (Security Orchestration, Automation, and Response) pipeline that reduces the Mean Time to Detect (MTTD) and Respond (MTTR) by automating the initial investigation phase of a cyberattack.

Instead of a human analyst manually checking IP reputations and writing reports, this system uses Local Agentic AI to perform deep forensics in under 30 seconds.

---
### 🏗️ Architecture & OODA Loop

The project follows the military OODA Loop (Observe, Orient, Decide, Act) to handle threats:

1. Observe: A Wazuh Agent on an Azure Cloud Honeypot detects an SSH Brute Force attack (MITRE T1110).

2. Orient: A custom Python Bridge on the NVIDIA DGX ingests the raw telemetry via a secure Tailscale tunnel.

3. Decide: CrewAI Agents (running Llama 3.2 locally via Ollama) perform:

    Threat Research: Automated IP reputation checks via AbuseIPDB.

    MITRE Mapping: Contextualizing the attack within the MITRE ATT&CK framework.

    Incident Command: Proposing a "Block" or "Watch" mitigation strategy.

4. Act:

    Human-in-the-Loop: Decisions are sent to a Streamlit Dashboard for human authorization.

    Professional Reporting: Automatically generates a Markdown-based Post-Incident Report (PIR).

    SIEM Feedback: Forwards the AI verdict back to the Wazuh Manager as a High-Severity alert.
---
### 📊 Project Highlights

- Infrastructure: Deployed on enterprise-grade NVIDIA DGX hardware for high-speed local LLM inference.

- Intelligence: Leverages Llama 3.2 to ensure data privacy (no security logs ever leave the local environment).

- Compliance: All findings are mapped to MITRE ATT&CK IDs to ensure industry-standard documentation.

- Interface: Custom Streamlit dashboard provides a real-time "Single Pane of Glass" for security analysts.
---
### 📁 Evidence of Work

The system produces professional, executive-ready reports for every incident.
See: documentation/REPORT_100.109.254.30.md

    Sample Report Output:

        Severity: HIGH

        Attack Vector: T1110 - Brute Force (SSH)

        AI Analysis: "The source IP has a high abuse score on AbuseIPDB. Recommending immediate firewall block..."
---
### 🛠️ Tech Stack

- SIEM: Wazuh

- AI Framework: CrewAI, Ollama (Llama 3.2)

- Dashboard: Streamlit

- Infrastructure: Ubuntu (NVIDIA DGX), Azure (Honeypot), Tailscale (Networking)

- Language: Python
---
## 📸 Visual Proof of Concept

### Real-Time Analyst Console
![Streamlit Dashboard](./images/dashboard_screenshot.png)
*Figure 1: The custom Streamlit interface showing AI-generated forensics and the "Approve Block" action button.*

### SIEM Integration (Wazuh)
![Wazuh Alerts](./images/wazuh_alerts.png)
*Figure 2: Custom Level 12 alerts appearing in the Wazuh SIEM after the AI Agent completes its investigation.*
---
🛠️ Engineering Optimizations

    Log Management: Implemented RotatingFileHandler to manage high-volume telemetry logs on ARM64 architecture, preventing disk exhaustion during sustained brute-force attacks.

    Git Efficiency: Configured advanced history filtering to maintain a lean repository while preserving critical project documentation.

---

### 🚀 Getting Started
1. Hardware & Environment Prerequisites

    Compute: Designed for ARM64 architecture (tested on NVIDIA DGX).

    OS: Ubuntu 22.04+.

    Connectivity: Tailscale for secure tunneling between the cloud honeypot and local lab.

2. Installation

    ```
    # Clone the repository
    git clone https://github.com/bishwast/Agentic-SOC.git
    cd Agentic-SOC

    # Set up the virtual environment
    python3 -m venv venv
    source venv/bin/activate

    # Install dependencies
    pip install -r requirements.txt
    ```
3. SIEM & AI Configuration

- Wazuh: Ensure your Wazuh Manager is active and receiving alerts from your Azure Honeypot.

- Ollama: Install Ollama and pull the Llama 3.2 model:
    ```ollama pull llama3.2```
- API Keys: Configure your .env file with your AbuseIPDB and Wazuh credentials.

4. Execution

Run the main orchestrator to start the OODA loop:
    ```python main.py```
