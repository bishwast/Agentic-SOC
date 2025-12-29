# SOC Incident Response Report: Phase 6 (Autonomous Mitigation)

**Incident ID:** SOC-20251228-001  
**Report Status:** Final / Closed  
**Execution Mode:** Autonomous (Phase 6)  
**Infrastructure:** NVIDIA DGX Spark (ARM64)

---

## 1. Incident Summary

At the time of simulation test, the Agentic SOC system detected and autonomously mitigated a critical security threat. The system identified a brute-force attack originating from an unauthorized internal IP address and executed a kernel-level block via `iptables` without human intervention.

| Metric | Detail |
| :--- | :--- |
| **Severity Level** | 12 (Critical) |
| **Primary Threat** | SSH Brute Force / Account Takeover (ATO) |
| **Source IP** | `192.168.1.100` |
| **Target Host** | `dgx-node-01` |
| **Detection Source** | Wazuh SIEM (Rule 100002) |

---

## 2. Detection Data (Wazuh Telemetry)

The following raw telemetry was ingested by the **File Watcher** and passed to the agentic pipeline:

```json
{
  "timestamp": "2025-12-28T14:15:20.000+0000",
  "rule": {
    "level": 12,
    "description": "Unauthorized SSH login attempt - Possible Bruteforce",
    "id": "100002"
  },
  "agent": { "id": "001", "name": "dgx-node-01" },
  "data": {
    "srcip": "192.168.1.100",
    "dstuser": "root"
  },
  "full_log": "Dec 28 14:15:20 dgx-node-01 sshd[1234]: Failed password for root from 192.168.1.100"
}
```
---

## 3. Autonomous Reasoning Chain (OODA Loop)
The CrewAI orchestration layer utilized local Llama 3.2 inference via Ollama to process the incident:

### Step 1: Triage (Orientation)

    Analysis: Extracted high-risk entities: Source IP 192.168.1.100 and target user root.

    Result: Determined incident requires immediate escalation due to Level 12 severity and target account privilege level.

### Step 2: Threat Research (Decision)

    Analysis: Correlated activity with MITRE ATT&CK Technique T1110 (Brute Force).

    Discovery: Identified multiple failed authentication attempts within a 60-second window. IP address 192.168.1.100 is not present in the "Authorized Admin Subnet" whitelist.

### Step 3: Incident Commander (Action)

    Logic: Evaluated risk vs. uptime. Since the source is unauthorized and targeting a root account on the NVIDIA DGX Spark, the risk of compromise exceeds the requirement for connectivity.

    Final Decision: ACTION: BLOCK
![SOC Output](/agentic_soc/soc_output.log)

## 4. Remediation & Mitigation
The system autonomously generated and executed the following firewall rule to isolate the threat:

** Command Executed:**

    ```
    sudo iptables -A INPUT -s 192.168.1.100 -j DROP
    ```
### Verification:

- Firewall Status: Rule executed successfully.

- Traffic Analysis: Subsequent packets from 192.168.1.100 are being dropped at the kernel level.

- Persistence: Rlelogged for review by system administrators.

## 5. Technical Impact

- Downtime: 0 minutes.

- Data Breach: Prevented.

- System Integrity: Maintained.