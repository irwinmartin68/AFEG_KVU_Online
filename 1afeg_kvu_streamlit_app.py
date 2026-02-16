import streamlit as st
import time, hashlib, json, random
from datetime import datetime

# ------------------ NATIONAL SCALE CONFIG (LOCKED) ------------------
# Based on 1.5 Billion Queries/Day @ 650 KVU Avg
KVU_VALUE = 0.001
VAT_RATE = 0.20
NATIONAL_DAILY_KVU = 975_000_000_000 
NATIONAL_DAILY_VAT = 195_000_000
SIM_STEPS = 100 
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

# ------------------ THE ORIGINAL CALIBRATED EQUATION ------------------
def simulate_kvu(query:str, scale_factor=1.0):
    base = (400 + (len(query) * 10)) * scale_factor
    q_low = query.lower()
    
    # Tiered Logic Calibration
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
st.set_page_config(page_title="AFEG National Auditor", layout="wide")

# Sidebar Controls
st.sidebar.title("AFEG KVU CONTROLS")
view_mode = st.sidebar.radio("CATEGORY FOCUS", ["ALL", "INFERENCE", "REASONING", "MEMORY"])
text_size = st.sidebar.slider("TEXT SIZE", 10, 30, 14)

st.markdown(f"""
    <style>
    .terminal-box {{
        background-color: #000000;
        color: #00FF41;
        padding: 20px;
        border: 1px solid #333;
        font-family: monospace;
        height: 450px;
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
    m_rev.metric("SESSION TOTAL REVENUE", f"£{st.session_state.session_revenue:,.2f}")
    m_tax.metric("SESSION TOTAL TAX (20%)", f"£{total_vat:,.2f}")
    m_kvu.metric("SESSION TOTAL KVU", f"{total_kvu:,.0f}")

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
        r1c1, r1c2, r1c3 = st.columns(3)
        r1c1.metric("INFERENCE" + (" (FOCUS)" if view_mode=="INFERENCE" else ""), f"{res['inference']:,}")
        r1c2.metric("REASONING" + (" (FOCUS)" if view_mode=="REASONING" else ""), f"{res['reasoning']:,}")
        r1c3.metric("MEMORY" + (" (FOCUS)" if view_mode=="MEMORY" else ""), f"{res['memory']:,}")
        
        r2c1, r2c2, r2c3 = st.columns(3)
        r2c1.metric("REVENUE CAPTURED", f"£{res['value']:,.4f}")
        r2c2.metric("VAT CAPTURED", f"£{res['vat']:,.4f}")
        r2c3.metric("ACT SUBTOTAL", f"£{st.session_state.act1_subtotal:,.4f}")

# ------------------ ACT 2: NATIONAL SIMULATION (975B SURGE) ------------------
with tab2:
    st.header("ACT 2: NATIONAL SIMULATION (975B KVU)")
    
    # Grid Matrix for Surge
    s1, s2, s3 = st.columns(3)
    sinf, sres, smem = s1.empty(), s2.empty(), s3.empty()
    s4, s5, s6 = st.columns(3)
    srev, svat, stot = s4.empty(), s5.empty(), s6.empty()

    if st.button("START NATIONAL SURGE"):
        window = st.empty()
        logs = []
        batch_size = NATIONAL_DAILY_KVU / SIM_STEPS
        
        for i in range(SIM_STEPS):
            node_id = f"UK_NODE_REF_{random.randint(1000,9999)}"
            # Scaled for National Load
            res = simulate_kvu(node_id, scale_factor=(batch_size/650)) 
            add_to_ledger(node_id, res)
            refresh_master_metrics()
            
            # Live Update 6-Grid Matrix
            sinf.metric("INFERENCE", f"{res['inference']:,.0f}")
            sres.metric("REASONING", f"{res['reasoning']:,.0f}")
            smem.metric("MEMORY", f"{res['memory']:,.0f}")
            srev.metric("REVENUE CAPTURED", f"£{res['value']:,.2f}")
            svat.metric("VAT CAPTURED", f"£{res['vat']:,.2f}")
            stot.metric("UNIT TOTAL (RAW)", f"{res['raw_total']:,.0f}")
            
            line = f"[{datetime.now().strftime('%H:%M:%S')}] SYNC_OK | {node_id} | KVU_BATCH: {res['raw_total']:,.0f} | £{res['value']:,.2f}"
            logs.insert(0, line)
            window.markdown(f'<div class="terminal-box">{"<br>".join(logs[:50])}</div>', unsafe_allow_html=True)
            time.sleep(0.05)

# ------------------ ACT 3: IMMUTABLE VAULT ------------------
with tab3:
    st.header("ACT 3: IMMUTABLE VAULT")
    search = st.text_input("SEARCH AUDIT HISTORY")
    if st.session_state.ledger:
        filtered = [e for e in st.session_state.ledger if not search or search.lower() in str(e).lower()]
        st.table(filtered[::-1])

# ------------------ ACT 4: 24-HOUR ENDURANCE ------------------
with tab4:
    st.header("ACT 4: 24-HOUR ENDURANCE")
    if st.button("START ENDURANCE CYCLE"):
        window = st.empty()
        logs = []
        for i in range(ENDURANCE_STEPS):
            res = simulate_kvu(f"Loop_{i}")
            add_to_ledger(f"Loop_{i}", res)
            refresh_master_metrics()
            line = f"[{datetime.now().strftime('%H:%M:%S')}] STABLE | KVU: {res['raw_total']:,} | £{res['value']:.4f}"
            logs.insert(0, line)
            window.markdown(f'<div class="terminal-box">{"<br>".join(logs[:50])}</div>', unsafe_allow_html=True)
            time.sleep(0.02)