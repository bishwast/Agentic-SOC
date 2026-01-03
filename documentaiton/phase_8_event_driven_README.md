# Phase 8: Event-Driven SOAR Integration

### **Overview**
This phase transforms the project from a passive tool into an **Active Security Sentinel**. By implementing an event-driven "Bridge," the system now monitors the **Wazuh SIEM** in real-time. When high-severity threats are detected, the system autonomously triggers the AI Agents to investigate, eliminating the need for manual human initiation.

### **Architecture**
The "Nervous System" of the SOC consists of a Python-based Log Watcher that connects the **Sensor Layer** (Wazuh) to the **Logic Layer** (Llama 3.2 AI).

| Component | Technology | Function |
| :--- | :--- | :--- |
| **Sensor** | Wazuh Manager | Detects raw threats (e.g., SSH Brute Force). |
| **Bridge** | Python (Watchdog) | Tails `alerts.json`, filters for Severity 5+, and extracts Attacker IP. |
| **Responder** | CrewAI + Ollama | Receives the IP, performs enrichment, and logs a governance RFC. |

### **Adversary Emulation (Testing)**
To validate the pipeline, we utilized **Atomic Red Team** principles (Technique T1110) to simulate a realistic attack.

* **Attack Tool:** Hydra (Thc-Hydra)
* **Attack Vector:** SSH Brute Force against Localhost
* **MITRE ATT&CK:** [T1110.001 - Password Guessing](https://attack.mitre.org/techniques/T1110/001/)

### **Proof of Concept**
The system successfully detected a live brute force attack and triggered the AI response within seconds.

![Automated Detection and Response](../documentaiton/images/phase8_bridge_success.png)
*(Note: Replace with your actual screenshot)*

### **How to Run**
1.  **Start the Bridge (Root required for Log Access):**
    ```bash
    sudo ./venv/bin/python3 wazuh_bridge.py
    ```
2.  **Simulate Attack:**
    ```bash
    hydra -l root -p badpass 127.0.0.1 ssh
    ```