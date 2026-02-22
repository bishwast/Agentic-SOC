import streamlit as st
import json
import os
from pathlib import Path
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURATION ---
BASE_DIR = Path(__file__).resolve().parent
JSON_DB = BASE_DIR / "documentation" / "active_incidents.json"

# Ensure the directory exists
os.makedirs(JSON_DB.parent, exist_ok=True)

# Page Setup
st.set_page_config(page_title="AI SOC Console", page_icon="🛡️", layout="wide")

# This forces a rerun of the entire script every 5 seconds (Only need one call)
st_autorefresh(interval=5000, key="soc_refresh")

st.title("🛡️ AI SOC Analyst Console")
st.markdown("### Autonomous Incident Response Queue")

# --- DATA LOADING ---
def load_incidents():
    if os.path.exists(JSON_DB):
        with open(JSON_DB, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def update_incident_status(incident_id, new_status):
    """Saves the analyst decision back to the JSON file."""
    all_incidents = load_incidents()
    for inc in all_incidents:
        if inc['id'] == incident_id:
            inc['status'] = new_status
            break
    
    with open(JSON_DB, "w") as f:
        json.dump(all_incidents, f, indent=4)
    st.rerun()

incidents = load_incidents()

# METRICS ROW
pending_incidents = [i for i in incidents if i['status'] == 'PENDING']
st.metric(label="Pending Incidents", value=len(pending_incidents), delta="Real-time")

st.divider()

# --- DISPLAY INCIDENTS ---
if not incidents:
    st.info("✅ No active incidents. System is clean.")
else:
    # We use a copy of incidents to iterate so the reversed index doesn't break logic
    # Showing newest first
    for incident in reversed(incidents):
        # We display different UI based on status
        status = incident.get('status', 'PENDING')
        
        if status == 'PENDING':
            with st.expander(f"🚨 ALERT: {incident['src_ip']} (Detected: {incident['timestamp']})", expanded=True):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("#### AI Investigation Report")
                    # Display the AI analysis (which now includes MITRE mapping)
                    st.markdown(incident['ai_analysis'])
                
                with col2:
                    st.markdown("#### Actions")
                    st.info("Review the AI proposal before authorizing.")
                    
                    # ACTION BUTTONS
                    if st.button(f"✅ APPROVE BLOCK: {incident['src_ip']}", key=f"approve_{incident['id']}"):
                        update_incident_status(incident['id'], "BLOCKED")
                        st.success(f"Firewall Rule Deployed for {incident['src_ip']}")
                        
                    if st.button(f"👁️ MONITOR ONLY: {incident['src_ip']}", key=f"watch_{incident['id']}"):
                        update_incident_status(incident['id'], "MONITORING")
                        st.warning(f"IP {incident['src_ip']} added to Watchlist.")
        
        elif status == "BLOCKED":
            st.error(f"🚫 IP {incident['src_ip']} was BLOCKED by Analyst at {incident['timestamp']}")
            
        elif status == "MONITORING":
            st.warning(f"👁️ IP {incident['src_ip']} is under ACTIVE MONITORING")

# SIDEBAR
st.sidebar.markdown("### System Status")
st.sidebar.success("🟢 Wazuh Bridge: ACTIVE")
st.sidebar.success("🟢 Ollama Engine: ONLINE")
st.sidebar.info("Running on NVIDIA DGX Spark")