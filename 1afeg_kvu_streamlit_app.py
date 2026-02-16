import streamlit as st
import time, hashlib, json, io, zipfile, random
from datetime import datetime

# ------------------ CONFIG (LOCKED) ------------------
KVU_VALUE = 0.001
VAT_RATE = 0.20
SIMULATION_STEPS = 50
ENDURANCE_STEPS = 150 # Increased for Act 4

# ------------------ SESSION STATE ------------------
if "ledger" not in st.session_state:
    st.session_state.ledger = []
if "session_revenue" not in st.session_state:
    st.session_state.session_revenue = 0.0

# ------------------ THE ORIGINAL EQUATION ------------------
def simulate_kvu(query:str):
    base = 400 + (len(query) * 10)
    q_low = query.lower()
    
    if any(w in q_low for w in ["why", "how", "explain"]):
        inf, res, mem = base * 0.8, base * 1.2, base * 0.1
    elif any(w in q_low for w in ["what", "who", "where", "when"]):
        inf, res, mem = base * 0.5, base * 0.1, base * 1.5
    else:
        inf, res, mem = base * 1.0, base * 0.1, base * 0.2
        
    raw_total = inf + res + mem
    value = raw_total * KVU_VALUE
    vat = value * VAT_RATE
    
    return {
        "inference": round(inf, 2),
        "reasoning": round(res, 2),
        "memory": round(mem, 2),
        "raw_total": round(raw_total, 2),
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

m_cols = st.columns(3)
m_rev = m_cols[0].empty()
m_tax = m_cols[1].empty()
m_kvu = m_cols[2].empty()

def refresh_metrics():
    total_kvu = sum(e['raw_total'] for e in st.session_state.ledger)
    total_vat = st.session_state.session_revenue * VAT_RATE
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

with tab1:
    st.header("ACT 1: GATEWAY SEEDING")
    query = st.text_input("ENTER UK AI QUERY")
    if st.button("SUBMIT QUERY"):
        if query:
            result = simulate_kvu(query)
            add_to_ledger(query, result)
            st.json(result)
            refresh_metrics()

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
            line = f"[{datetime.now().strftime('%H:%M:%S')}] QUERY: {node_name} | KVU: {res['raw_total']} | £{res['value']}"
            logs.insert(0, line)
            window.markdown(f'<div class="terminal-box">{"<br>".join(logs)}</div>', unsafe_allow_html=True)
            time.sleep(0.05)

with tab3:
    st.header("ACT 3: IMMUTABLE VAULT")
    search = st.text_input("SEARCH AUDIT HISTORY (Keyword or Hash)")
    if st.session_state.ledger:
        filtered = [e for e in st.session_state.ledger if not search or search.lower() in str(e).lower()]
        st.table(filtered[::-1])
    if st.button("RESET VAULT VIEW"):
        st.rerun()

with tab4:
    st.header("ACT 4: 24-HOUR ENDURANCE")
    if st.button("START 24HR CYCLE SIMULATION"):
        window = st.empty()
        logs = []
        for i in range(ENDURANCE_STEPS):
            loop_name = f"Endurance_Loop_{i}"
            res = simulate_kvu(loop_name)
            add_to_ledger(loop_name, res)
            refresh_metrics()
            line = f"[{datetime.now().strftime('%H:%M:%S')}] STABLE | LOOP: {i} | KVU: {res['raw_total']} | £{res['value']}"
            logs.insert(0, line)
            window.markdown(f'<div class="terminal-box">{"<br>".join(logs)}</div>', unsafe_allow_html=True)
            time.sleep(0.02) # Faster surge for endurance