import streamlit as st
import time, hashlib, json, io, zipfile, random
from datetime import datetime

# ------------------ CONFIG ------------------
KVU_VALUE = 0.001
VAT_RATE = 0.20
SIMULATION_STEPS = 50
ENDURANCE_STEPS = 150 

# ------------------ SESSION STATE ------------------
if "ledger" not in st.session_state:
    st.session_state.ledger = []
if "session_revenue" not in st.session_state:
    st.session_state.session_revenue = 0.0
if "act1_subtotal" not in st.session_state:
    st.session_state.act1_subtotal = 0.0
if "current_result" not in st.session_state:
    st.session_state.current_result = None

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

def add_to_ledger(query, result, is_act1=False):
    entry = result.copy()
    entry.update({
        "query": query,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "hash": hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()
    })
    st.session_state.ledger.append(entry)
    st.session_state.session_revenue += entry["value"]
    if is_act1:
        st.session_state.act1_subtotal += entry["value"]
    st.session_state.current_result = entry

# ------------------ UI SETUP ------------------
st.set_page_config(page_title="AFEG KVU Auditor", layout="wide")

st.sidebar.title("AFEG KVU CONTROLS")
text_size = st.sidebar.slider("TEXT SIZE", 10, 30, 14)

st.markdown(f"""
    <style>
    .terminal-box {{
        background-color: #000000;
        color: #00FF41;
        padding: 20px;
        border: 1px solid #333;
        font-family: monospace;
        height: 400px;
        overflow-y: scroll;
        white-space: pre-wrap;
        font-size: {text_size}px;
    }}
    </style>
    """, unsafe_allow_html=True)

st.title("AFEG KVU SYSTEM")

# Master Metrics (Top Bar)
m_cols = st.columns(3)
m_rev = m_cols[0].empty()
m_tax = m_cols[1].empty()
m_kvu = m_cols[2].empty()

def refresh_master_metrics():
    total_kvu = sum(e['raw_total'] for e in st.session_state.ledger)
    total_vat = st.session_state.session_revenue * VAT_RATE
    m_rev.metric("SESSION TOTAL REVENUE", f"£{st.session_state.session_revenue:,.4f}")
    m_tax.metric("SESSION TOTAL TAX (20%)", f"£{total_vat:,.4f}")
    m_kvu.metric("SESSION TOTAL KVU", f"{total_kvu:,.2f}")

refresh_master_metrics()

tab1, tab2, tab3, tab4 = st.tabs([
    "ACT 1: GATEWAY SEEDING", 
    "ACT 2: NATIONAL SIMULATION", 
    "ACT 3: IMMUTABLE VAULT", 
    "ACT 4: 24-HOUR ENDURANCE"
])

# ------------------ ACT 1: GATEWAY SEEDING ------------------
with tab1:
    st.header("ACT 1: GATEWAY SEEDING")
    query = st.text_input("ENTER UK AI QUERY")
    
    if st.button("SUBMIT QUERY"):
        if query:
            result = simulate_kvu(query)
            add_to_ledger(query, result, is_act1=True)
            refresh_master_metrics()

    if st.session_state.current_result:
        res = st.session_state.current_result
        st.markdown("---")
        
        # THE UPDATED 6-GRID MATRIX
        # Row 1: KVU Categories
        r1_c1, r1_c2, r1_c3 = st.columns(3)
        r1_c1.metric("INFERENCE", f"{res['inference']:,}")
        r1_c2.metric("REASONING", f"{res['reasoning']:,}")
        r1_c3.metric("MEMORY", f"{res['memory']:,}")
        
        # Row 2: Financials & Totals
        r2_c1, r2_c2, r2_c3 = st.columns(3)
        r2_c1.metric("REVENUE CAPTURED", f"£{res['value']:,.4f}")
        r2_c2.metric("VAT CAPTURED", f"£{res['vat']:,.4f}")
        r2_c3.metric("ACT SUBTOTAL", f"£{st.session_state.act1_subtotal:,.4f}")
        
        # Supporting unit total row
        st.write(f"**UNIT TOTAL (RAW):** {res['raw_total']:,} KVUs")
        st.markdown("---")

# ------------------ ACT 2: NATIONAL SIMULATION ------------------
with tab2:
    st.header("ACT 2: NATIONAL SIMULATION")
    if st.button("START NATIONAL SURGE"):
        window = st.empty()
        logs = []
        for i in range(SIMULATION_STEPS):
            node_name = f"Node_Sync_{random.randint(100,999)}"
            res = simulate_kvu(node_name)
            add_to_ledger(node_name, res)
            refresh_master_metrics()
            line = f"[{datetime.now().strftime('%H:%M:%S')}] QUERY: {node_name} | KVU: {res['raw_total']} | £{res['value']}"
            logs.insert(0, line)
            window.markdown(f'<div class="terminal-box">{"<br>".join(logs)}</div>', unsafe_allow_html=True)
            time.sleep(0.05)

# ------------------ ACT 3: IMMUTABLE VAULT ------------------
with tab3:
    st.header("ACT 3: IMMUTABLE VAULT")
    search = st.text_input("SEARCH AUDIT HISTORY (Keyword or Hash)")
    if st.session_state.ledger:
        filtered = [e for e in st.session_state.ledger if not search or search.lower() in str(e).lower()]
        st.table(filtered[::-1])
    if st.button("RESET VAULT VIEW"):
        st.rerun()

# ------------------ ACT 4: 24-HOUR ENDURANCE ------------------
with tab4:
    st.header("ACT 4: 24-HOUR ENDURANCE")
    if st.button("START 24HR CYCLE SIMULATION"):
        window = st.empty()
        logs = []
        for i in range(ENDURANCE_STEPS):
            loop_name = f"Endurance_Loop_{i}"
            res = simulate_kvu(loop_name)
            add_to_ledger(loop_name, res)
            refresh_master_metrics()
            line = f"[{datetime.now().strftime('%H:%M:%S')}] STABLE | LOOP: {i} | KVU: {res['raw_total']} | £{res['value']}"
            logs.insert(0, line)
            window.markdown(f'<div class="terminal-box">{"<br>".join(logs)}</div>', unsafe_allow_html=True)
            time.sleep(0.02)