import streamlit as st
import hashlib, json, random, time, io
import pandas as pd
import numpy as np
from datetime import datetime

# -----------------------------
# CORE LOGIC (KITCHEN LOGIC)
# -----------------------------
def calculate_complexity_kvu(query, mode):
    base = 400.0
    q = query.lower()
    if any(w in q for w in ["why", "how", "explain", "audit"]):
        inf, res, mem = base * 0.8, base * 2.5, base * 0.5
        label, heat = "Deep Reasoning", "high"
    elif any(w in q for w in ["what", "who", "where", "list"]):
        inf, res, mem = base * 1.2, base * 0.4, base * 0.3
        label, heat = "Standard Inference", "low"
    else:
        inf, res, mem = base, base * 0.2, base * 0.1
        label, heat = "Basic System", "low"
    
    multiplier = 2.5 if mode == "Demo Simulation" else 1.0
    return round(inf * multiplier, 2), round(res * multiplier, 2), round(mem * multiplier, 2), label, heat

# -----------------------------
# UI SETUP & TERMINAL STYLING
# -----------------------------
st.set_page_config(page_title="AFEG v7 Gateway", layout="wide")

if "total_kvu" not in st.session_state: st.session_state.total_kvu = 0.0
if "ledger" not in st.session_state: st.session_state.ledger = []
if "cat_metrics" not in st.session_state: st.session_state.cat_metrics = {"inf": 0.0, "res": 0.0, "mem": 0.0}

# SIDEBAR CONTROLS
st.sidebar.title("UI CONTROLS")
text_size = st.sidebar.slider("Global Text Scaling (px)", 12, 36, 18)
st.sidebar.divider()
st.sidebar.title("COMPUTE GRID COUNTERS")
s_inf = st.sidebar.empty()
s_res = st.sidebar.empty()
s_mem = st.sidebar.empty()

# DYNAMIC CSS (SCALING + TERMINAL LOOK)
st.markdown(f"""
<style>
    html, body, [class*="st-"] {{
        font-size: {text_size}px !important;
    }}
    /* Terminal styling for black-screen/green-text windows */
    [data-testid="stMetricValue"] {{ font-size: {text_size + 10}px !important; }}
    
    .stDataFrame div[data-testid="stTable"] {{
        background-color: #000000 !important;
        color: #00FF41 !important;
        font-family: 'Courier New', Courier, monospace !important;
    }}
    .heat-high {{ background-color: rgba(255, 69, 0, 0.1); border: 2px solid #FF4500; padding: 20px; border-radius: 10px; animation: pulse 2s infinite; }}
    .heat-low {{ background-color: rgba(0, 255, 65, 0.05); border: 2px solid #00FF41; padding: 20px; border-radius: 10px; }}
    @keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(255, 69, 0, 0.4); }} 70% {{ box-shadow: 0 0 0 10px rgba(255, 69, 0, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(255, 69, 0, 0); }} }}
</style>
""", unsafe_allow_html=True)

def update_all_metrics():
    gross_placeholder.metric("GROSS REVENUE", f"£{st.session_state.total_kvu * 0.001:,.2f}")
    vat_placeholder.metric("VAT CAPTURE", f"£{(st.session_state.total_kvu * 0.001 * 0.2):,.2f}")
    kvu_placeholder.metric("VALIDATED KVUs", f"{st.session_state.total_kvu:,.0f}")
    s_inf.metric("Inference Engine", f"{st.session_state.cat_metrics['inf']:,.1f}")
    s_res.metric("Reasoning Layer", f"{st.session_state.cat_metrics['res']:,.1f}")
    s_mem.metric("Memory Vault", f"{st.session_state.cat_metrics['mem']:,.1f}")

# -----------------------------
# MAIN DASHBOARD
# -----------------------------
st.title("AFEG v7 // National Command Center")
h1, h2, h3 = st.columns(3)
gross_placeholder, vat_placeholder, kvu_placeholder = h1.empty(), h2.empty(), h3.empty()

update_all_metrics()

tabs = st.tabs(["ACT 1: GATEWAY", "ACT 2: SURGE", "ACT 3: LEDGER VAULT", "ACT 4: 24HR FISCAL SIM"])

# --- ACT 1: GATEWAY ---
with tabs[0]:
    st.subheader("AFEG KVU GOVERNANCE AUDIT TELEMETRY")
    gate_mode = st.radio("Gateway State:", ["Live Enforcement", "Demo Simulation"], horizontal=True)
    user_query = st.text_input("Enter Audit Query:", key="gate_input")
    
    if st.button("SUBMIT QUERY") and user_query:
        inf, res, mem, label, heat = calculate_complexity_kvu(user_query, gate_mode)
        st.session_state.total_kvu += (inf + res + mem)
        st.session_state.cat_metrics['inf'] += inf
        st.session_state.cat_metrics['res'] += res
        st.session_state.cat_metrics['mem'] += mem
        
        entry = {"Time": datetime.now().strftime("%H:%M:%S"), "Origin": "Live", "Query": user_query, "KVU": (inf+res+mem), "Type": label, "Hash": hashlib.sha256(user_query.encode()).hexdigest()[:12]}
        st.session_state.ledger.insert(0, entry)
        update_all_metrics()
        st.markdown(f'<div class="heat-{heat}"><b>{label} detected.</b> Audit Hash: <code>{entry["Hash"]}</code></div>', unsafe_allow_html=True)

# --- ACT 2: SURGE (BLACK/GREEN TERMINAL) ---
with tabs[1]:
    st.subheader("ACT 2: NATIONAL SURGE SIMULATION")
    if st.button("EXECUTE 60s SURGE"):
        prog = st.progress(0)
        surge_log = st.empty()
        current_surge = []
        for i in range(30):
            b_inf, b_res, b_mem = random.uniform(5000, 10000), random.uniform(8000, 15000), random.uniform(1000, 3000)
            st.session_state.total_kvu += (b_inf + b_res + b_mem)
            st.session_state.cat_metrics['inf'] += b_inf; st.session_state.cat_metrics['res'] += b_res; st.session_state.cat_metrics['mem'] += b_mem
            
            ent = {"Time": datetime.now().strftime("%H:%M:%S"), "Origin": "Surge", "Batch": f"Cluster #{i+1}", "KVU": round(b_inf+b_res+b_mem, 2), "Hash": hashlib.md5(str(i).encode()).hexdigest()[:8]}
            st.session_state.ledger.insert(0, ent)
            current_surge.insert(0, ent)
            update_all_metrics()
            prog.progress((i + 1) / 30)
            surge_log.dataframe(current_surge, use_container_width=True, height=400)
            time.sleep(0.5)

# --- ACT 3: SEARCHABLE LEDGER VAULT ---
with tabs[2]:
    st.subheader("ACT 3: SEARCHABLE LEDGER VAULT")
    if st.session_state.ledger:
        st.data_editor(pd.DataFrame(st.session_state.ledger), use_container_width=True, hide_index=True, disabled=True, key="vault_editor")
    else:
        st.info("Vault offline. Submit data to engage.")

# --- ACT 4: 24HR SIMULATION (120s RUNTIME + BLACK/GREEN TERMINAL) ---
with tabs[3]:
    st.subheader("ACT 4: 24-HOUR NATIONAL FISCAL LEDGER")
    if st.button("RUN 24HR FISCAL SIMULATION"):
        sim_log_window = st.empty()
        sim_stats = st.empty()
        sim_ledger = []
        
        for h in range(24):
            val = max(1000, 12000 * np.sin(np.pi * (h-6)/12)) * random.uniform(95, 105)
            st.session_state.total_kvu += val
            st.session_state.cat_metrics['inf'] += val * 0.4; st.session_state.cat_metrics['res'] += val * 0.5; st.session_state.cat_metrics['mem'] += val * 0.1
            
            sim_entry = {"Hour": f"{h:02d}:00", "Load": "National Grid", "KVUs": round(val, 0), "VAT Yield": round(val * 0.001 * 0.2, 2), "Hash": hashlib.sha256(str(h).encode()).hexdigest()[:10]}
            sim_ledger.insert(0, sim_entry)
            st.session_state.ledger.insert(0, sim_entry)
            
            update_all_metrics()
            sim_log_window.dataframe(sim_ledger, use_container_width=True, height=500)
            sim_stats.info(f"Simulating Hour {h+1}/24... 120s Fiscal Lock active.")
            time.sleep(5) # 2 minute runtime (24*5)
        st.success("Fiscal Projection Finalized.")