import streamlit as st
import time
import random
import hashlib
import json
import io
import zipfile
from datetime import datetime

# -----------------------------
# SESSION STATE INITIALIZATION
# -----------------------------
if "start_time" not in st.session_state:
    st.session_state.start_time = datetime.now()
if "kvu_total" not in st.session_state:
    st.session_state.kvu_total = 0.0
if "events_logged" not in st.session_state:
    st.session_state.events_logged = 0
if "ledger_compliant" not in st.session_state:
    st.session_state.ledger_compliant = []
if "ledger_intercepted" not in st.session_state:
    st.session_state.ledger_intercepted = []
if "kvu_history" not in st.session_state:
    st.session_state.kvu_history = []

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="AFEG Governance & KVU Audit System", layout="wide")

st.title("AFEG KVU – Governance, Telemetry & Audit Export Prototype")
st.caption("Semantic Firewall + Economic Telemetry + Regulator Audit Trail")

# -----------------------------
# SIDEBAR CONTROLS
# -----------------------------
st.sidebar.header("System Controls")

mode = st.sidebar.radio(
    "Operating Mode",
    ["Normal", "Surge Simulation", "24 Hour Real-Time Mode"]
)

# -----------------------------
# UPTIME TRACKER
# -----------------------------
uptime = datetime.now() - st.session_state.start_time
st.sidebar.metric("System Uptime", str(uptime).split(".")[0])

# -----------------------------
# GOVERNANCE LOGIC
# -----------------------------
RISK_KEYWORDS = ["hack", "bypass", "exploit", "illegal", "attack", "leak"]
PII_KEYWORDS = ["password", "ssn", "credit card", "private data"]

def input_scan(query):
    q = query.lower()
    if any(word in q for word in RISK_KEYWORDS):
        return "BLOCKED_INPUT"
    return "SAFE"

def output_scan(response):
    r = response.lower()
    if any(word in r for word in PII_KEYWORDS):
        return "INTERCEPTED_OUTPUT"
    return "COMPLIANT"

def generate_kvu(mode):
    base = random.uniform(0.1, 0.3)
    multiplier = 5 if mode == "Surge Simulation" else (2 if mode == "24 Hour Real-Time Mode" else 1)
    return round(base * multiplier, 4)

# -----------------------------
# GOVERNANCE GATEWAY
# -----------------------------
st.subheader("AFEG Governance Gateway")
user_query = st.text_input("Enter Query for Governance Audit")

if st.button("Run Full Governance Audit") and user_query:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query_hash = hashlib.sha256(user_query.encode()).hexdigest()

    # PASS 1: INPUT SCAN
    input_status = input_scan(user_query)

    if input_status == "BLOCKED_INPUT":
        st.warning("⚠️ Input Blocked by Semantic Firewall (User-Origin Risk)")
        entry = {
            "timestamp": timestamp, "query": user_query, "status": "BLOCKED_INPUT",
            "kvu": 0.0, "hash": query_hash, "action": "NULLIFIED"
        }
        st.session_state.ledger_intercepted.append(entry)
    else:
        # Simulated AI Processing
        ai_response = f"Processed compliant response for: {user_query}"
        kvu = generate_kvu(mode)
        
        # PASS 2: OUTPUT SCAN
        output_status = output_scan(ai_response)
        st.session_state.events_logged += 1
        st.session_state.kvu_total += kvu

        if output_status == "INTERCEPTED_OUTPUT":
            st.error("🚫 Output Intercepted by Governance Filter (System Risk)")
            entry = {
                "timestamp": timestamp, "query": user_query, "status": "INTERCEPTED_OUTPUT",
                "kvu": kvu, "hash": query_hash, "action": "GOVERNED"
            }
            st.session_state.ledger_intercepted.append(entry)
            st.markdown(f"<div style='color:grey;'>Governed Response (Greyed): {ai_response}</div>", unsafe_allow_html=True)
        else:
            st.success("✅ Output Passed Governance Scan (Compliant Event)")
            entry = {
                "timestamp": timestamp, "query": user_query, "status": "COMPLIANT",
                "kvu": kvu, "hash": query_hash, "action": "DELIVERED"
            }
            st.session_state.ledger_compliant.append(entry)
            st.write(f"AI Response: {ai_response}")

# -----------------------------
# TELEMETRY & CHARTS
# -----------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Total KVU (Economic Telemetry)", f"{st.session_state.kvu_total:.4f}")
col2.metric("AI Events Logged", st.session_state.events_logged)
col3.metric("Governance Intercepts", len(st.session_state.ledger_intercepted))

st.session_state.kvu_history.append(st.session_state.kvu_total)
st.session_state.kvu_history = st.session_state.kvu_history[-100:]
st.subheader("Live KVU Telemetry (Real-Time System Activity)")
st.line_chart(st.session_state.kvu_history)

# -----------------------------
# DUAL LEDGER VAULT
# -----------------------------
st.subheader("Ledger Vault – Tamper Traceable Audit Logs")
tab1, tab2 = st.tabs(["🟢 Compliant Ledger", "🔴 Governance Intercepts"])
with tab1:
    st.dataframe(st.session_state.ledger_compliant, use_container_width=True)
with tab2:
    st.dataframe(st.session_state.ledger_intercepted, use_container_width=True)

# -----------------------------
# REGULATOR AUDIT EXPORT
# -----------------------------
st.subheader("Regulator Audit Export Portal")
if st.button("Generate Full Audit ZIP"):
    audit_bundle = {
        "metadata": {"export_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "total_kvu": st.session_state.kvu_total},
        "compliant": st.session_state.ledger_compliant,
        "intercepted": st.session_state.ledger_intercepted
    }
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("AFEG_AUDIT_FULL.json", json.dumps(audit_bundle, indent=4))
        zf.writestr("COMPLIANT_LEDGER.json", json.dumps(st.session_state.ledger_compliant, indent=4))
        zf.writestr("INTERCEPTED_LEDGER.json", json.dumps(st.session_state.ledger_intercepted, indent=4))
    
    st.download_button("Download Regulator Audit ZIP", data=zip_buffer.getvalue(), file_name="AFEG_Regulator_Audit.zip", mime="application/zip")

st.caption(f"Live System Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")