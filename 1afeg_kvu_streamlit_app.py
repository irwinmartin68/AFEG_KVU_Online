import streamlit as st
import time, hashlib, json, io, zipfile, random
from datetime import datetime

# ------------------ CONFIG ------------------
KVU_VALUE = 0.001
NORMALIZATION_FACTOR = 0.01
VAT_RATE = 0.20
SIMULATION_STEPS = 50

# ------------------ SESSION STATE ------------------
if "ledger" not in st.session_state:
    st.session_state.ledger = []
if "session_revenue" not in st.session_state:
    st.session_state.session_revenue = 0.0

# ------------------ KVU SIMULATION ------------------
def simulate_kvu(query:str):
    base = max(len(query),10)
    inference = base * random.uniform(2.3,2.7)
    memory = base * random.uniform(1.7,1.9)
    reasoning = base * random.uniform(2.1,2.3)
    raw_total = inference+memory+reasoning
    normalized_total = raw_total*NORMALIZATION_FACTOR
    value = normalized_total*KVU_VALUE
    vat = value*VAT_RATE
    return {
        "inference":round(inference,2),
        "memory":round(memory,2),
        "reasoning":round(reasoning,2),
        "raw_total":round(raw_total,2),
        "normalized_total":round(normalized_total,4),
        "value":round(value,4),
        "vat":round(vat,4)
    }

# ------------------ LEDGER & HASH ------------------
def hash_entry(entry:dict):
    return hashlib.sha256(json.dumps(entry,sort_keys=True).encode()).hexdigest()

def add_to_ledger(query,result):
    entry = result.copy()
    entry.update({
        "query":query,
        "timestamp":datetime.now().strftime("%H:%M:%S"),
        "hash":hash_entry(result)
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

# Master Metrics (Linked to dynamic placeholders during simulation)
m_cols = st.columns(3)
m_rev = m_cols[0].empty()
m_tax = m_cols[1].empty()
m_kvu = m_cols[2].empty()

# Initial display
m_rev.metric("SESSION TOTAL REVENUE", f"£{st.session_state.session_revenue:,.4f}")
m_tax.metric("SESSION TOTAL TAX (20%)", f"£{(st.session_state.session_revenue * VAT_RATE):,.4f}")
m_kvu.metric("SESSION TOTAL KVU", f"{sum(e['normalized_total'] for e in st.session_state.ledger):,.2f}")

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
            # Update main metrics immediately
            m_rev.metric("SESSION TOTAL REVENUE", f"£{st.session_state.session_revenue:,.4f}")
            m_tax.metric("SESSION TOTAL TAX (20%)", f"£{(st.session_state.session_revenue * VAT_RATE):,.4f}")
            m_kvu.metric("SESSION TOTAL KVU", f"{sum(e['normalized_total'] for e in st.session_state.ledger):,.2f}")

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
            
            # Update main metrics live
            m_rev.metric("SESSION TOTAL REVENUE", f"£{st.session_state.session_revenue:,.4f}")
            m_tax.metric("SESSION TOTAL TAX (20%)", f"£{(st.session_state.session_revenue * VAT_RATE):,.4f}")
            m_kvu.metric("SESSION TOTAL KVU", f"{sum(e['normalized_total'] for e in st.session_state.ledger):,.2f}")
            
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
            
            # Update main metrics live
            m_rev.metric("SESSION TOTAL REVENUE", f"£{st.session_state.session_revenue:,.4f}")
            m_tax.metric("SESSION TOTAL TAX (20%)", f"£{(st.session_state.session_revenue * VAT_RATE):,.4f}")
            m_kvu.metric("SESSION TOTAL KVU", f"{sum(e['normalized_total'] for e in st.session_state.ledger):,.2f}")
            
            line = f"[{datetime.now().strftime('%H:%M:%S')}] LOOP: {i} | KVU: {res['normalized_total']} | £{res['value']}"
            logs.insert(0, line)
            window.markdown(f'<div class="terminal-box">{"<br>".join(logs)}</div>', unsafe_allow_html=True)
            time.sleep(0.05)