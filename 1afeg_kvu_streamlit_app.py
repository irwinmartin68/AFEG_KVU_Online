# AFEG KVU – Full Streamlit Online Auditor
# Copy this into Notepad and save as: 1afeg_kvu_app.py
# Run locally: streamlit run 1afeg_kvu_app.py

import streamlit as st
import time
import hashlib
import json
import io
import zipfile
from datetime import datetime
import random

# ---------------------------
# CONFIG
# ---------------------------
KVU_VALUE = 0.001
NORMALIZATION_FACTOR = 0.01
VAT_RATE = 0.20
SIMULATION_STEPS = 50  # For demo purposes, replace with larger numbers for full sim

# ---------------------------
# SESSION STATE
# ---------------------------
if "ledger" not in st.session_state:
    st.session_state.ledger = []

if "session_revenue" not in st.session_state:
    st.session_state.session_revenue = 0.0

if "latency" not in st.session_state:
    st.session_state.latency = 0.0

if "view" not in st.session_state:
    st.session_state.view = "All"

# ---------------------------
# CORE KVU SIMULATION
# ---------------------------
def simulate_kvu(query: str):
    base = max(len(query), 10)
    inference_kvu = base * random.uniform(2.3, 2.7)
    memory_kvu = base * random.uniform(1.7, 1.9)
    reasoning_kvu = base * random.uniform(2.1, 2.3)
    raw_total = inference_kvu + memory_kvu + reasoning_kvu
    normalized_total = raw_total * NORMALIZATION_FACTOR
    value = normalized_total * KVU_VALUE
    vat = value * VAT_RATE
    latency = random.uniform(0.1, 0.5)  # seconds
    return {
        "inference": round(inference_kvu, 2),
        "memory": round(memory_kvu, 2),
        "reasoning": round(reasoning_kvu, 2),
        "raw_total": round(raw_total, 2),
        "normalized_total": round(normalized_total, 4),
        "value": round(value, 4),
        "vat": round(vat, 4),
        "latency": round(latency, 3),
    }

# ---------------------------
# HASH + LEDGER
# ---------------------------
def generate_hash(entry: dict):
    entry_str = json.dumps(entry, sort_keys=True)
    return hashlib.sha256(entry_str.encode()).hexdigest()

def add_to_ledger(query, result):
    entry = result.copy()
    entry["query"] = query
    entry["timestamp"] = datetime.now().isoformat()
    entry["hash"] = generate_hash(entry)
    st.session_state.ledger.append(entry)
    st.session_state.session_revenue += entry["value"]
    st.session_state.latency += entry["latency"]

def generate_audit_zip():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        ledger_text = "\n".join([json.dumps(e) for e in st.session_state.ledger])
        zf.writestr("AFEG_IMMUTABLE_AUDIT_LEDGER.txt", ledger_text)
    buffer.seek(0)
    return buffer

# ---------------------------
# UI SETUP
# ---------------------------
st.set_page_config(page_title="AFEG KVU Auditor", layout="wide")
st.title("AFEG KVU – Full Online Simulation")
st.caption("Athena Fabric v4 Simulation | Live KVU Tracking")

# Sidebar controls
st.sidebar.title("Controls")
view_option = st.sidebar.radio("View Metrics", ["All", "Inference", "Memory", "Reasoning"])
st.session_state.view = view_option
text_size = st.sidebar.slider("Text Size", 12, 24, 16)

# ---------------------------
# ACT 1 – QUERY SUBMISSION
# ---------------------------
query = st.text_input("Enter a question to submit for KVU calculation:")

if st.button("Submit Query"):
    if query:
        result = simulate_kvu(query)
        add_to_ledger(query, result)
        st.success("Query submitted successfully!")
        st.json(result)

# ---------------------------
# ACT 2 – SIMULATION DEMO
# ---------------------------
if st.button("Run Demo Simulation"):
    progress_bar = st.progress(0)
    for i in range(SIMULATION_STEPS):
        demo_query = f"Demo Query {i+1}"
        result = simulate_kvu(demo_query)
        add_to_ledger(demo_query, result)
        progress_bar.progress((i+1)/SIMULATION_STEPS)
        time.sleep(0.05)  # demo speed
    st.success(f"Simulation complete ({SIMULATION_STEPS} steps)")

# ---------------------------
# ACT 3 – SESSION TOTALS
# ---------------------------
if st.session_state.ledger:
    st.subheader("Session Totals")
    total_inference = sum(e["inference"] for e in st.session_state.ledger)
    total_memory = sum(e["memory"] for e in st.session_state.ledger)
    total_reasoning = sum(e["reasoning"] for e in st.session_state.ledger)
    total_kvus = sum(e["normalized_total"] for e in st.session_state.ledger)
    total_value = sum(e["value"] for e in st.session_state.ledger)
    total_vat = sum(e["vat"] for e in st.session_state.ledger)
    total_latency = sum(e["latency"] for e in st.session_state.ledger)

    if st.session_state.view == "All" or st.session_state.view == "Inference":
        st.write(f"<p style='font-size:{text_size}px'>Total Inference KVU: {round(total_inference,2)}</p>", unsafe_allow_html=True)
    if st.session_state.view == "All" or st.session_state.view == "Memory":
        st.write(f"<p style='font-size:{text_size}px'>Total Memory KVU: {round(total_memory,2)}</p>", unsafe_allow_html=True)
    if st.session_state.view == "All" or st.session_state.view == "Reasoning":
        st.write(f"<p style='font-size:{text_size}px'>Total Reasoning KVU: {round(total_reasoning,2)}</p>", unsafe_allow_html=True)

    st.write(f"<p style='font-size:{text_size}px'>Total Normalized KVUs: {round(total_kvus,4)}</p>", unsafe_allow_html=True)
    st.write(f"<p style='font-size:{text_size}px'>Total Value (£): {round(total_value,4)}</p>", unsafe_allow_html=True)
    st.write(f"<p style='font-size:{text_size}px'>Total VAT (£): {round(total_vat,4)}</p>", unsafe_allow_html=True)
    st.write(f"<p style='font-size:{text_size}px'>Total Latency (s): {round(total_latency,3)}</p>", unsafe_allow_html=True)

# ---------------------------
# ACT 4 – AUDIT LEDGER
# ---------------------------
if st.session_state.ledger:
    st.subheader("Immutable Audit Ledger (Last 10 entries)")
    for entry in st.session_state.ledger[-10:]:
        st.json(entry)

# ---------------------------
# ACT 5 – TREASURY ZIP
# ---------------------------
if st.session_state.ledger:
    st.download_button(
        label="Generate Secure Audit ZIP",
        data=generate_audit_zip(),
        file_name="AFEG_IMMUTABLE_AUDIT_LEDGER.zip",
        mime="application/zip"
    )