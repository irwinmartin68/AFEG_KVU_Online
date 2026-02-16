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
        "timestamp":datetime.now().strftime("%H:%M:%S.%f")[:-3],
        "hash":hash_entry(result)
    })
    st.session_state.ledger.append(entry)
    st.session_state.session_revenue += entry["value"]
    st.session_state.latency += entry["latency"]

def generate_audit_zip():
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as zf:
        ledger_text="\n".join([json.dumps(e) for e in st.session_state.ledger])
        zf.writestr("AFEG_AUDIT_EXPORT.txt",ledger_text)
    buf.seek(0)
    return buf

# ------------------ UI SETUP (COMMAND CENTER VISUALS) ------------------
st.set_page_config(page_title="AFEG KVU Auditor", layout="wide")

# Custom CSS for the Terminal Feed and High-Tier Metrics
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
    .stMetric {
        background-color: #111;
        border: 1px solid #333;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("AFEG KVU // National Economic Auditor")
st.caption("Live Infrastructure Telemetry Dashboard | Status: AUDIT-READY")

# Navigation
tab1, tab2, tab3, tab4 = st.tabs(["ACT 1: GATEWAY", "ACT 2: LIVE SURGE", "ACT 3: IMMUTABLE VAULT", "ACT 4: TREASURY"])

# ------------------ ACT1: QUERY (SINGLE TRANSACTION) ------------------
with tab1:
    col_a, col_b = st.columns([2,1])
    with col_a:
        st.header("Gateway Seeding")
        query = st.text_input("INPUT UK AI TELEMETRY QUERY:", placeholder="e.g. Logic-gate sync verify...")
        if st.button("EXECUTE KVU CAPTURE", use_container_width=True):
            if query:
                result = simulate_kvu(query)
                add_to_ledger(query, result)
                st.success(f"Transaction Finalized. Value Captured: £{result['value']}")
    
    with col_b:
        if st.session_state.ledger:
            st.subheader("Last Entry Hash")
            st.code(st.session_state.ledger[-1]['hash'])

# ------------------ ACT2: SIMULATION (SURGE WINDOW) ------------------
with tab2:
    st.header("Node Simulation Surge")
    
    m1, m2, m3 = st.columns(3)
    rev_ph = m1.empty()
    kvu_ph = m2.empty()
    vat_ph = m3.empty()
    
    if st.button("TRIGGER NATIONAL SURGE", use_container_width=True):
        surge_window = st.empty()
        surge_stream = []
        
        for i in range(SIMULATION_STEPS):
            demo_query = f"UK_NODE_REF_{random.randint(1000,9999)}"
            result = simulate_kvu(demo_query)
            add_to_ledger(demo_query, result)
            
            # Update Live Dashboard
            rev_ph.metric("SESSION REVENUE", f"£{st.session_state.session_revenue:,.4f}")
            kvu_ph.metric("TOTAL NORMALIZED KVU", f"{sum(e['normalized_total'] for e in st.session_state.ledger):,.2f}")
            vat_ph.metric("VAT LIABILITY (20%)", f"£{(st.session_state.session_revenue * VAT_RATE):,.4f}")
            
            # Build Terminal Log
            log_line = f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] VALIDATED | QUERY: {demo_query} | KVU: {result['normalized_total']} | £{result['value']}"
            surge_stream.insert(0, log_line)
            surge_window.markdown(f'<div class="terminal-box">{"<br>".join(surge_stream[:100])}</div>', unsafe_allow_html=True)
            
            time.sleep(0.04)
        st.toast("Node Surge Complete", icon="✅")

# ------------------ ACT 3: THE VAULT (SEARCH BACK IN) ------------------
with tab3:
    st.header("Immutable Audit Vault")
    
    search_query = st.text_input("SEARCH LEDGER (By Keyword, Timestamp, or Hash):", placeholder="Search '12:05' or 'Query_45'...")
    
    if st.session_state.ledger:
        if search_query:
            # Filters the ledger based on the search string
            filtered_data = [e for e in st.session_state.ledger if search_query.lower() in str(e).lower()]
            st.write(f"Showing {len(filtered_data)} results for: '{search_query}'")
            st.table(filtered_data)
        else:
            st.write("Full Audit History (Last 50 Entries):")
            st.table(st.session_state.ledger[-50:][::-1])
    else:
        st.info("Vault is currently empty. Run a simulation to generate records.")

# ------------------ ACT 4: TREASURY (EXPORT) ------------------
with tab4:
    st.header("Treasury Revenue Portal")
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.metric("FINAL REVENUE CAPTURE", f"£{st.session_state.session_revenue:,.4f}")
        st.write(f"Total Transactions Logged: {len(st.session_state.ledger)}")
    
    with col_t2:
        if st.session_state.ledger:
            st.download_button(
                label="DOWNLOAD IMMUTABLE AUDIT ZIP",
                data=generate_audit_zip(),
                file_name=f"AFEG_KVU_AUDIT_REPORT.zip",
                mime="application/zip",
                use_container_width=True
            )