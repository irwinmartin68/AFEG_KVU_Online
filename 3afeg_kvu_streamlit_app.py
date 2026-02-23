import streamlit as st
import time, hashlib, json, random, io, zipfile
from datetime import datetime

# -----------------------------
# CORE AFEG V7 ENGINE (INTERNAL)
# -----------------------------
def calculate_complexity_kvu(query):
    """
    Law and Money Logic: 
    Detects intent to determine if compute is Inference or Reasoning.
    """
    base = 400.0 
    q = query.lower()
    label, heat = "Standard Processing", "low"
    
    if any(w in q for w in ["why", "how", "explain", "audit"]):
        inf, res, mem = base * 0.8, base * 2.5, base * 0.5
        label, heat = "Deep Reasoning (High Compute)", "high"
    elif any(w in q for w in ["what", "who", "where", "list"]):
        inf, res, mem = base * 1.2, base * 0.4, base * 0.3
    else:
        inf, res, mem = base, base * 0.2, base * 0.1
        
    return round(inf, 2), round(res, 2), round(mem, 2), label, heat

# -----------------------------
# PAGE CONFIG & THEME
# -----------------------------
st.set_page_config(page_title="AFEG v7 Gateway", layout="wide")

# Persistent State Management
if "kvu_total" not in st.session_state: st.session_state.kvu_total = 0.0
if "safe_ledger" not in st.session_state: st.session_state.safe_ledger = []
if "risk_ledger" not in st.session_state: st.session_state.risk_ledger = []

# Sidebar Controls
st.sidebar.title("AFEG v7 Control Panel")
text_size = st.sidebar.slider("UI Text Scaling (px)", 12, 32, 18)
highlight_cat = st.sidebar.selectbox("Highlight Category", ["Inference", "Reasoning", "Memory", "None"])

# Dynamic Styling for Heatmaps
st.markdown(f"""<style>
    html, body, [class*="st-"] {{ font-size: {text_size}px !important; }}
    .heat-high {{ background-color: rgba(255, 69, 0, 0.15); border: 2px solid #FF4500; padding: 20px; border-radius: 10px; animation: pulse 2s infinite; }}
    .heat-low {{ background-color: rgba(0, 255, 65, 0.1); border: 2px solid #00FF41; padding: 20px; border-radius: 10px; }}
    @keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(255, 69, 0, 0.4); }} 70% {{ box-shadow: 0 0 0 15px rgba(255, 69, 0, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(255, 69, 0, 0); }} }}
</style>""", unsafe_allow_html=True)

# -----------------------------
# DASHBOARD HEADER
# -----------------------------
st.title("AFEG v7 // Online Governance Gateway")
m1, m2, m3 = st.columns(3)
m1.metric("GROSS REVENUE", f"£{st.session_state.kvu_total * 0.001:,.2f}")
m2.metric("VAT CAPTURE (20%)", f"£{(st.session_state.kvu_total * 0.001 * 0.2):,.2f}")
m3.metric("VALIDATED KVUs", f"{st.session_state.kvu_total:,.0f}")

tabs = st.tabs(["ACT 1: GATEWAY", "ACT 2: SURGE", "ACT 3: LEDGER VAULT"])

with tabs[0]:
    st.subheader("ACT 1: LIVE GOVERNANCE AUDIT")
    user_query = st.text_input("Enter query to audit:", key="live_q_input")
    if st.button("RUN AUDIT") and user_query:
        # Internal Logic Processing
        inf, res, mem, label, heat = calculate_complexity_kvu(user_query)
        total_kvu = inf + res + mem
        
        # Security Firewall Scan
        risky_keywords = ["hack", "bypass", "exploit", "illegal", "steal"]
        status = "approved"
        if any(word in user_query.lower() for word in risky_keywords):
            status, total_kvu = "blocked", 0.0

        st.session_state.kvu_total += total_kvu
        
        # Visual Heatmap Feedback
        st.markdown(f'<div class="heat-{heat}"><b>INTENT ANALYSIS:</b> {label}<br><b>HASH:</b> {hashlib.sha256(user_query.encode()).hexdigest()[:12]}</div>', unsafe_allow_html=True)
        
        # Metric Breakdown
        c1, c2, c3 = st.columns(3)
        c1.metric("INF", inf, delta="Focused" if highlight_cat == "Inference" else None)
        c2.metric("RES", res, delta="Focused" if highlight_cat == "Reasoning" else None)
        c3.metric("MEM", mem, delta="Focused" if highlight_cat == "Memory" else None)
        
        entry = {"timestamp": datetime.now().strftime("%H:%M:%S"), "query": user_query, "kvu": total_kvu, "status": status}
        if status == "approved": st.session_state.safe_ledger.append(entry)
        else: st.session_state.risk_ledger.append(entry)

with tabs[1]:
    st.subheader("ACT 2: 60-SECOND NATIONAL SURGE")
    if st.button("EXECUTE SURGE"):
        prog = st.progress(0)
        for i in range(30):
            batch = random.uniform(10000, 35000)
            st.session_state.kvu_total += batch
            prog.progress((i + 1) / 30)
            time.sleep(2) # Real-time simulation
        st.rerun()

with tabs[2]:
    st.subheader("ACT 3: LEDGER VAULT")
    ledger_data = st.session_state.safe_ledger + st.session_state.risk_ledger
    if ledger_data:
        st.dataframe(ledger_data, width=1200)
        if st.button("CLEAR SYSTEM LEDGER"):
            st.session_state.safe_ledger = []
            st.session_state.risk_ledger = []
            st.session_state.kvu_total = 0.0
            st.rerun()

# -----------------------------
# FORECASTING SIDEBAR
# -----------------------------
if st.session_state.kvu_total > 0:
    st.sidebar.divider()
    annual_est = (st.session_state.kvu_total * 0.001 * 365) * 1000 
    st.sidebar.subheader("Annual National Projection")
    st.sidebar.metric("Est. Annual VAT Recovery", f"£{(annual_est * 0.2):,.0f}")