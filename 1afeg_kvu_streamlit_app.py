import streamlit as st
import time, hashlib, json, io, zipfile, random
from datetime import datetime

# ------------------ CONFIG ------------------
KVU_VALUE = 0.001
NORMALIZATION_FACTOR = 0.01
VAT_RATE = 0.20
SIMULATION_STEPS = 50

# ------------------ SESSION STATE ------------------
for key, default in [("ledger", []), ("session_revenue", 0.0), ("latency", 0.0)]:
    if key not in st.session_state:
        st.session_state[key] = default

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
    latency=random.uniform(0.1,0.5)
    return {
        "inference":round(inference,2),
        "memory":round(memory,2),
        "reasoning":round(reasoning,2),
        "raw_total":round(raw_total,2),
        "normalized_total":round(normalized_total,4),
        "value":round(value,4),
        "vat":round(vat,4),
        "latency":round(latency,3)
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

# ------------------ UI SETUP (RESTORED WORDING) ------------------
st.set_page_config(page_title="AFEG KVU Auditor", layout="wide")

st.markdown("""
    <style>
    .terminal-box {
        background-color: #050505;
        color: #00FF41;
        padding: 20px;
        border-radius: 8px;
        border: 2px solid #1A1A1A;
        font-family: 'Courier New', Courier, monospace;
        height: 400px;
        overflow-y: scroll;
        font-size: 13px;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("AFEG KVU SYSTEM")

# Master Metrics (Top Bar)
m1, m2, m3 = st.columns(3)
m1.metric("SESSION TOTAL REVENUE", f"£{st.session_state.session_revenue:,.4f}")
m2.metric("SESSION TOTAL TAX (20%)", f"£{(st.session_state.session_revenue * VAT_RATE):,.4f}")
m3.metric("SESSION TOTAL KVU", f"{sum(e['normalized_total'] for e in st.session_state.ledger):,.2f}")

# Act Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "ACT 1: GATEWAY SEEDING", 
    "ACT 2: NATIONAL SIMULATION", 
    "ACT 3: IMMUTABLE VAULT", 
    "ACT 4: 24-HOUR ENDURANCE"
])

# ------------------ ACT 1: GATEWAY SEEDING ------------------
with tab1:
    st.header("ACT 1: GATEWAY SEEDING")
    query = st.text_input("ENTER UK AI QUERY", placeholder="e.g. Explain the trade model...")
    if st.button("SUBMIT QUERY"):
        if query:
            result = simulate_kvu(query)
            add_to_ledger(query, result)
            st.success(f"QUERY REVENUE: £{result['value']:,.4f} | TAX: £{result['vat']:,.4f}")
            st.json(result)

# ------------------ ACT 2: NATIONAL SIMULATION ------------------
with tab2:
    st.header("ACT 2: NATIONAL SIMULATION")
    if st.button("START NATIONAL SURGE"):
        surge_window = st.empty()
        surge_stream = []
        for i in range(SIMULATION_STEPS):
            demo_query = f"UK_NODE_SYNC_{random.randint(100,999)}"
            result = simulate_kvu(demo_query)
            add_to_ledger(demo_query, result)
            
            log_line = f"[{datetime.now().strftime('%H:%M:%S')}] SYNC_OK | QUERY: {demo_query} | KVU: {result['normalized_total']} | £{result['value']}"
            surge_stream.insert(0, log_line)
            surge_window.markdown(f'<div class="terminal-box">{"<br>".join(surge_stream[:100])}</div>', unsafe_allow_html=True)
            time.sleep(0.05)
            st.rerun() # Refresh metrics at top

# ------------------ ACT 3: IMMUTABLE VAULT (SEARCH) ------------------
with tab3:
    st.header("ACT 3: IMMUTABLE VAULT")
    search_query = st.text_input("SEARCH AUDIT HISTORY (Keyword or Hash)")
    if st.session_state.ledger:
        if search_query:
            filtered = [e for e in st.session_state.ledger if search_query.lower() in str(e).lower()]
            st.write(f"Showing {len(filtered)} results")
            st.table(filtered)
        else:
            st.table(st.session_state.ledger[::-1])
    
    if st.button("RESET VAULT VIEW"):
        st.rerun()

# ------------------ ACT 4: 24-HOUR ENDURANCE ------------------
with tab4:
    st.header("ACT 4: 24-HOUR ENDURANCE")
    if st.button("START 24HR CYCLE SIMULATION"):
        # Act 4 mirrors Act 2 logic but represents the long-form endurance
        endurance_window = st.empty()
        endurance_stream = []
        for i in range(SIMULATION_STEPS + 50):
            demo_query = f"ENDURANCE_LOOP_{random.randint(1000,9999)}"
            result = simulate_kvu(demo_query)
            add_to_ledger(demo_query, result)
            
            log_line = f"[{datetime.now().strftime('%H:%M:%S')}] STABLE | LOOP: {i} | KVU: {result['normalized_total']} | £{result['value']}"
            endurance_stream.insert(0, log_line)
            endurance_window.markdown(f'<div class="terminal-box">{"<br>".join(endurance_stream[:100])}</div>', unsafe_allow_html=True)
            time.sleep(0.04)
            st.rerun()