# Phase 9: The Analyst Console (Human-in-the-Loop)

### **Overview**
While Phase 8 automated the detection and analysis, Phase 9 introduces the **Governance Layer**. In a high-stakes SOC environment, AI should not autonomously block IPs without oversight. This phase implements a **Streamlit Dashboard** that serves as the "Single Pane of Glass" for the security analyst.

### **Architecture**
The system uses a decoupled architecture where the Backend (AI Agents) and Frontend (Dashboard) communicate via a structured JSON database.

| Component | Tech Stack | Role |
| :--- | :--- | :--- |
| **Backend** | Python + CrewAI | Writes investigation results to `active_incidents.json`. |
| **Frontend** | Streamlit | Reads JSON in real-time and renders the UI. |
| **Logic** | Pandas | Manages timestamps and incident state (Pending/Resolved). |

### **Features**
* **Real-Time Alerting:** Auto-refreshes to show new threats as they are detected by Wazuh.
* **Decision Support:** Displays the AI's full reasoning (Threat Intel + Assessment) before asking for a decision.
* **One-Click Response:** Simulates the execution of Firewall Rules via "Approve Block" buttons.

### **Proof of Work**
![Analyst Dashboard](../documentaiton/images/phase9_dashboard_success.png)
