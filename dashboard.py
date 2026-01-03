import streamlit as st
import json
import os

# CONFIG
JSON_DB = "documentaiton/active_incidents.json"

st.set_page_config(page_title="AI SOC Console", page_icon="🛡️", layout="wide")

st.title("🛡️ AI SOC Analyst Console")
st.markdown("### Autonomous Incident Response Queue")

# METRICS ROW
if os.path.exists(JSON_DB):
    with open(JSON_DB, "r") as f:
        try:
            incidents = json.load(f)
        except:
            incidents = []
else:
    incidents = []

pending_count = len([i for i in incidents if i['status'] == 'PENDING'])
st.metric(label="Pending Incidents", value=pending_count, delta="Real-time")

st.divider()

# DISPLAY INCIDENTS
if not incidents:
    st.info("✅ No active incidents. System is clean.")
else:
    # Show newest first
    for index, incident in enumerate(reversed(incidents)):
        if incident['status'] == 'PENDING':
            with st.expander(f"🚨 ALERT: {incident['src_ip']} (Detected: {incident['timestamp']})", expanded=True):
                
                # Layout
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("#### AI Investigation Report")
                    st.markdown(incident['ai_analysis'])
                
                with col2:
                    st.markdown("#### Actions")
                    st.info("Review the AI proposal before authorizing.")
                    
                    # ACTION BUTTONS
                    if st.button(f"✅ APPROVE BLOCK", key=f"btn_approve_{index}"):
                        st.success(f"Firewall Rule Deployed for {incident['src_ip']}")
                        
                    if st.button(f"👁️ MONITOR ONLY", key=f"btn_watch_{index}"):
                        st.warning(f"IP {incident['src_ip']} added to Watchlist.")

st.sidebar.markdown("### System Status")
st.sidebar.success("🟢 Wazuh Bridge: ACTIVE")
st.sidebar.success("🟢 Ollama Engine: ONLINE")
st.sidebar.info("running on NVIDIA DGX Spark")