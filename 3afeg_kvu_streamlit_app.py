import streamlit as st
import hashlib
import json
import random
import time
from datetime import datetime

# -------------------------------
# CORE ENGINE (FORMERLY BACKEND)
# -------------------------------
def simulate_kvu(query: str, mode: str):
    base = 400 + (len(query) * 10)
    q_low = query.lower()
    
    # Intent Detection Logic
    if any(w in q_low for w in ["why", "how", "explain"]):
        inf, res, mem = base * 0.8, base * 1.2, base * 0.1
        label = "Deep Reasoning"
    else:
        inf, res, mem = base * 1.0, base * 0.1, base * 0.2
        label = "Standard Inference"

    # Mode multiplier
    if mode == "Surge Simulation":
        multiplier = random.uniform(3, 6)
    elif mode == "24 Hour Real-Time Mode":
        multiplier = random.uniform(1, 2)
    else:
        multiplier = 1

    total = (inf + res + mem) * multiplier
    return round(total, 4), round(inf * multiplier, 4), round(res * multiplier, 4), round(mem * multiplier, 4), label

# -------------------------------
# UI CONFIG & STATE
# -------------------------------
st.set_page_config(page_title="AFEG KVU Telemetry Dashboard", layout="wide")

if "ledger" not in st.session_state: st.session_state.ledger = []
if "total_kvu" not in st.session_state: st.session_state.total_kvu = 0.0

# SIDEBAR CONTROLS
st.sidebar.title("AFEG v7 Control Panel")
mode = st.sidebar.radio("Simulation Mode", ["Normal", "Surge Simulation", "24 Hour Real-Time Mode"])
text_size = st.sidebar.slider("Text Size (px)", 12, 32, 18)

# DYNAMIC STYLING
st.markdown(f"""<style>
    html, body, [class*="st-"] {{ font-size: {text_size}px !important; }}
    .audit-card {{ background-color: rgba(0, 255, 65, 0.05); border: 1px solid #00FF41; padding: 20px; border-radius: 10px; }}
</style>""", unsafe_allow_html=True)

# -------------------------------
# DASHBOARD UI
# -------------------------------
st.title("AFEG v7 // Unified Governance & Telemetry")
st.caption(f"Status: Operational | Mode: {mode}")

m1, m2, m3 = st.columns(3)
m1.metric("GROSS REVENUE", f"£{st.session_state.total_kvu * 0.001:,.2f}")
m2.metric("VAT CAPTURE (20%)", f"£{(st.session_state.total_kvu * 0.001 * 0.2):,.2f}")
m3.metric("VALIDATED KVUs", f"{st.session_state.total_kvu:,.0f}")

tabs = st.tabs(["ACT 1: GATEWAY", "ACT 2: SURGE", "ACT 3: LEDGER"])

with tabs[0]:
    st.subheader("ACT 1: LIVE GOVERNANCE AUDIT")
    user_query = st.text_input("Enter query to audit (e.g., 'How do I audit AI'):")
    
    if st.button("RUN AUDIT") and user_query:
        # Run Local Simulation Engine
        kvu_total_val, inf, res, mem, label = simulate_kvu(user_query, mode)
        
        # Commit to State Ledger
        entry = {
            "query": user_query,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "total_kvu": kvu_total_val,
            "inference": inf,
            "reasoning": res,
            "memory": mem,
            "label": label,
            "hash": hashlib.sha256(f"{user_query}{kvu_total_val}".encode()).hexdigest()[:16]
        }
        
        st.session_state.ledger.append(entry)
        st.session_state.total_kvu += kvu_total_val
        
        # Display Audit Card
        st.markdown(f"""<div class="audit-card">
            <b>INTENT ANALYSIS:</b> {label}<br>
            <b>SHA-256 HASH:</b> <code>{entry['hash']}</code>
        </div>""", unsafe_allow_html=True)
        
        st.rerun()

with tabs[1]:
    st.subheader("ACT 2: NATIONAL SURGE SIMULATION")
    if st.button("EXECUTE 60s SURGE"):
        prog = st.progress(0)
        for i in range(30):
            # Batch simulate 100 queries at once
            batch_val = random.uniform(5000, 15000)
            st.session_state.total_kvu += batch_val
            prog.progress((i + 1) / 30)
            time.sleep(2)
        st.rerun()

with tabs[2]:
    st.subheader("ACT 3: LEDGER VAULT (AUDIT TICKETS)")
    if st.session_state.ledger:
        st.dataframe(st.session_state.ledger, width=1200)
        if st.button("CLEAR LEDGER"):
            st.session_state.ledger = []
            st.session_state.total_kvu = 0.0
            st.rerun()