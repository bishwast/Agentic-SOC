import streamlit as st
import pandas as pd
import json
import os
import time

# Configuration
LOG_PATH = "/var/ossec/logs/alerts/alerts.json"
REFRESH_RATE = 2  # Seconds

st.set_page_config(layout="wide", page_title="SOC Monitor")

def parse_wazuh_logs(filepath):
    """Parses the last 50 lines of the Wazuh alert log."""
    if not os.path.exists(filepath):
        st.error(f"Log file not found: {filepath}")
        return pd.DataFrame()

    data = []
    try:
        # standard linux 'tail' simulation for efficiency
        with open(filepath, "r") as f:
            lines = f.readlines()[-50:]     # Starting 50 elements form the end of the Wazuh alert log
            
        for line in lines:
            try:
                log = json.loads(line)
                # Flattening the nested JSON structure for the dataframe
                entry = {
                    "timestamp": log.get("timestamp"),
                    "level": log.get("rule", {}).get("level"),
                    "rule_id": log.get("rule", {}).get("id"),
                    "description": log.get("rule", {}).get("description"),
                    "src_ip": log.get("data", {}).get("srcip", "-"),
                    "action": "Blocked" if "drop" in str(log) else "Monitored"
                }
                data.append(entry)
            except json.JSONDecodeError:
                continue
    except PermissionError:
        st.error("Permission denied reading log file.")
        return pd.DataFrame()

    df = pd.read_json(json.dumps(data))
    
    if not df.empty and 'timestamp' in df.columns:
        return df.sort_values(by="timestamp", ascending=False)
    return df

def main():
    st.header("Active Threat Monitor")
    
    # 1. Sidebar Configuration
    with st.sidebar:
        st.title("SOC Control Panel")
        st.markdown("---")
        # Let user choose severity threshold
        severity_threshold = st.slider(
            "Min Severity Level", 
            min_value=1, 
            max_value=15, 
            value=5  # Default to 5 to see your current logs
        )
        st.info(f"Filtering for Level {severity_threshold} and above.")

    # 2. Main Layout Containers
    metric_container = st.empty()
    table_placeholder = st.empty()

    while True:
        # Load raw data
        raw_df = parse_wazuh_logs(LOG_PATH)

        if not raw_df.empty:
            # 3. Apply Sidebar Filter Logic
            filtered_df = raw_df[raw_df['level'] >= severity_threshold]
            
            critical_alerts = raw_df[raw_df['level'] >= 10].shape[0]
            
            # 4. Update Metrics (Based on full log for context)
            with metric_container.container():
                m1, m2, m3 = st.columns(3)
                m1.metric("Global Criticals", critical_alerts)
                m2.metric("Displayed Events", len(filtered_df))
                m3.metric("System State", "ONLINE")

            # 5. Update Filtered Data Table
            with table_placeholder.container():
                st.dataframe(
                    filtered_df, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "timestamp": "Time",
                        "level": "Severity",
                        "src_ip": "Source IP",
                        "description": "Alert Description"
                    }
                )
        
        time.sleep(REFRESH_RATE)

if __name__ == "__main__":
    main()