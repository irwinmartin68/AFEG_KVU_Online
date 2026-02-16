# AFEG KVU – Streamlit Online Auditor (Simple Version)
# Copy this into Notepad and save as: afeg_kvu_streamlit_app.py
# Run locally: streamlit run afeg_kvu_streamlit_app.py

import streamlit as st
import time
import hashlib
import json
import io
import zipfile
from datetime import datetime

# ---------------------------
# CONFIG (EASY TO EDIT)
# ---------------------------
KVU_VALUE = 0.001          # Value per KVU (£)
NORMALIZATION_FACTOR = 0.01  # Reduce inflated raw KVUs
VAT_RATE = 0.20

# ---------------------------
# SESSION STATE
# ---------------------------
if "ledger" not in st.session_state:
    st.session_state.ledger = []

if "session_revenue" not in st.session_state:
    st.session_state.session_revenue = 0.0

# ---------------------------
# CORE KVU SIMULATION
# ---------------------------
def simulate_kvu(query: str):
    """Simulates Inference, Memory, Reasoning KVUs and calculates value & VAT"""
    base = max(len(query), 10)
    inference_kvu = base * 2.5
    memory_kvu = base * 1.8
    reasoning_kvu = base * 2.2
    raw_total = inference_kvu + memory_kvu + reasoning_kvu
    normalized_total = raw_total * NORMALIZATION_FACTOR
    value = normalized_total * KVU_VALUE
    vat = value * VAT_RATE
    return {
        "inference": round(inference_kvu, 2),
        "memory": round(memory_kvu, 2),
        "reasoning": round(reasoning_kvu, 2),
        "raw_total": round(raw_total, 2),
        "normalized_total": round(normalized_total, 4),
        "value": round(value, 4),
        "vat": round(vat, 4),
    }

# ---------------------------
# IMMUTABLE AUDIT HASH
# ---------------------------
def generate_hash(entry: dict):
    entry_str = json.dumps(entry, sort_keys=True)
    return hashlib.sha256(entry_str.encode()).hexdigest()

# ---------------------------
# AUDIT VAULT ZIP EXPORT
# ---------------------------
def generate_audit_zip():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        ledger_text = "\n".join([json.dumps(e) for e in st.session_state.ledger])
        zf.writestr("AFEG_IMMUTABLE_AUDIT_LEDGER.txt", ledger_text)
    buffer.seek(0)
    return buffer

# ---------------------------
# UI – HEADER
# ---------------------------
st.set_page_config(page_title="AFEG KVU Auditor", layout="wide")
st.title("AFEG KVU – Online Economic Telemetry Auditor")
st.caption("Athena Fabric v4 Simulation | Raw vs Normalized KVU Tracking")

# ---------------------------
# ACT 1 – QUERY SUBMISSION
# ---------------------------
query = st.text_input("Enter a question to submit for KVU calculation:")

if st.button("Submit Query"):
    if query:
        results = simulate_kvu(query)
        results["timestamp"] = datetime.now().isoformat()
        results["query"] = query
        results["hash"] = generate_hash(results)
        st.session_state.ledger.append(results)
        st.session_state.session_revenue += results["value"]
        st.write("### KVU Results")
        st.json(results)

# ---------------------------
# ACT 2 – SESSION TOTALS
# ---------------------------
if st.session_state.ledger:
    st.write("### Session Totals")
    total_kvus = sum(e["normalized_total"] for e in st.session_state.ledger)
    total_value = sum(e["value"] for e in st.session_state.ledger)
    total_vat = sum(e["vat"] for e in st.session_state.ledger)
    st.write(f"Total Normalized KVUs: {round(total_kvus,4)}")
    st.write(f"Total Value (£): {round(total_value,4)}")
    st.write(f"Total VAT (£): {round(total_vat,4)}")

# ---------------------------
# ACT 3 – AUDIT LEDGER
# ---------------------------
if st.session_state.ledger:
    st.write("### Immutable Audit Ledger")
    for entry in st.session_state.ledger[-10:]:  # show last 10 entries
        st.json(entry)

# ---------------------------
# ACT 4 – TREASURY AUDIT ZIP
# ---------------------------
if st.session_state.ledger:
    st.download_button(
        label="Generate Secure Audit ZIP",
        data=generate_audit_zip(),
        file_name="AFEG_IMMUTABLE_AUDIT_LEDGER.zip",
        mime="application/zip"
    )