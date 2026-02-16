import streamlit as st
import time, hashlib, json, io, zipfile, random
from datetime import datetime

# ------------------ CONFIG (STEP 2, 3, 4) ------------------
NORMALIZATION_FACTOR = 0.01  # Step 2
KVU_VALUE = 0.001           # Step 3 (£0.001)
VAT_RATE = 0.20              # Step 4 (20%)
SIMULATION_STEPS = 50

# ------------------ SESSION STATE (STEP 5) ------------------
if "ledger" not in st.session_state:
    st.session_state.ledger = []
if "session_revenue" not in st.session_state:
    st.session_state.session_revenue = 0.0

# ------------------ CORE ENGINE (STEPS 1-4) ------------------
def simulate_kvu(query:str):
    base = max(len(query), 10)
    
    # Step 1: Raw Total KVUs
    inference_kvu = base * random.uniform(2.3, 2.7)
    memory_kvu = base * random.uniform(1.7, 1.9)
    reasoning_kvu = base * random.uniform(2.1, 2.3)
    raw_total = inference_kvu + memory_kvu + reasoning_kvu
    
    # Step 2: Normalized KVUs
    normalized_total = raw_total * NORMALIZATION_FACTOR
    
    # Step 3: Value per KVU
    value = normalized_total * KVU_VALUE
    
    # Step 4: VAT
    vat = value * VAT_RATE
    
    return {
        "inference": round(inference_kvu, 2),
        "memory": round(memory_kvu, 2),
        "reasoning": round(reasoning_kvu, 2),
        "raw_total": round(raw_total, 2),
        "normalized_total": round(normalized_total, 4),
        "value": round(value, 4),
        "vat": round(vat, 4)
    }

def add_to_ledger(query, result):
    entry = result.copy()
    entry.update({
        "query": query,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "hash": hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()
    })
    st.session_state.ledger.append(entry)
    st.session_state.session_revenue += entry["value"]

# ------------------ UI SETUP ------------------
st.set_page_config(page_title="AFEG KVU Auditor", layout="wide")

st.markdown("""
    <style>
    .terminal-box {
        background-color: #000000;
        color: #00FF41;
        padding: 20px;
        border: 1px solid #333;
        font-family: monospace;
        height: 400px;
        overflow-y: scroll;
        white-space: pre-wrap;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("AFEG KVU SYSTEM")

# Master Metrics (Step 5)
m_cols = st.columns(3)
m_rev = m_cols[0].empty()
m_tax = m_cols[1].empty()
m_kvu = m_cols[2].empty()

# Refresh UI Totals
def refresh_metrics():
    total_kvu = sum(e['normalized_total'] for e in st.session_state.ledger)
    total_vat = sum(e['vat'] for e in st.session_state.ledger)
    m_rev.metric("SESSION TOTAL REVENUE", f"£{st.session_state.session_revenue:,.4f}")
    m_tax.metric("SESSION TOTAL TAX (20%)", f"£{total_vat:,.4f}")
    m_kvu.metric("SESSION TOTAL KVU", f"{total_kvu:,.2f}")

refresh_metrics()

tab1, tab2, tab3, tab4 = st.tabs([
    "ACT 1: GATEWAY SEEDING", 
    "ACT 2: NATIONAL SIMULATION", 
    "ACT 3: IMMUTABLE VAULT", 
    "ACT 4: 24-HOUR ENDURANCE"
])

# ACT 1
with tab1:
    st.header("ACT 1: GATEWAY SEEDING")
    query = st.text_input("ENTER UK AI QUERY")
    if st.button("SUBMIT QUERY"):
        if query:
            result = simulate_kvu(query)
            add_to_ledger(query, result)
            st.json(result)
            refresh_metrics()

# ACT 2
with tab2:
    st.header("ACT 2: NATIONAL SIMULATION")
    if st.button("START NATIONAL SURGE"):
        window = st.empty()
        logs = []
        for i in range(SIMULATION_STEPS):
            node_name = f"Node_Sync_{random.randint(100,999)}"
            res = simulate_kvu(node_name)
            add_to_ledger(node_name, res)
            refresh_metrics()
            
            line = f"[{datetime.now().strftime('%H:%M:%S')}] QUERY: {node_name} | KVU: {res['normalized_total']} | £{res['value']}"
            logs.insert(0, line)
            window.markdown(f'<div class="terminal-box">{"<br>".join(logs)}</div>', unsafe_allow_html=True)
            time.sleep(0.05)

# ACT 3
with tab3:
    st.header("ACT 3: IMMUTABLE VAULT")
    search = st.text_input("SEARCH AUDIT HISTORY (Keyword or Hash)")
    if st.session_state.ledger:
        filtered = [e for e in st.session_state.ledger if not search or search.lower() in str(e).lower()]
        st.table(filtered[::-1])
    
    if st.button("RESET VAULT VIEW"):
        st.rerun()

# ACT 4
with tab4:
    st.header("ACT 4: 24-HOUR ENDURANCE")
    if st.button("START 24HR CYCLE SIMULATION"):
        window = st.empty()
        logs = []
        for i in range(SIMULATION_STEPS):
            loop_name = f"Endurance_Loop_{i}"
            res = simulate_kvu(loop_name)
            add_to_ledger(loop_name, res)
            refresh_metrics()
            
            line = f"[{datetime.now().strftime('%H:%M:%S')}] LOOP: {i} | KVU: {res['normalized_total']} | £{res['value']}"
            logs.insert(0, line)
            window.markdown(f'<div class="terminal-box">{"<br>".join(logs)}</div>', unsafe_allow_html=True)
            time.sleep(0.05)