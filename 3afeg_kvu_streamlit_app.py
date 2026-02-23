import streamlit as st
import time, hashlib, json, random, io, zipfile
from datetime import datetime

# -----------------------------
# AFEG CORE LOGIC (INTEGRATED)
# -----------------------------
def calculate_complexity_kvu(query):
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
# SESSION STATE & UI CONFIG
# -----------------------------
st.set_page_config(page_title="AFEG v7 Online Gateway", layout="wide")

if "safe_ledger" not in st.session_state: st.session_state.safe_ledger = []
if "risk_ledger" not in st.session_state: st.session_state.risk_ledger = []
if "kvu_total" not in st.session_state: st.session_state.kvu_total = 0.0

# Sidebar controls
st.sidebar.title("AFEG v7 Control Panel")
text_size = st.sidebar.slider("UI Text Size", 12, 32, 18)
highlight_cat = st.sidebar.selectbox("Highlight Compute Tier", ["Inference", "Reasoning", "Memory", "None"])

st.markdown(f"""<style>
    html, body, [class*="st-"] {{ font-size: {text_size}px !important; }}
    .heat-high {{ background-color: rgba(255, 69, 0, 0.15); border: 2px solid #FF4500; padding: 20px; border-radius: 10px; animation: pulse 2s infinite; }}
    .heat-low {{ background-color: rgba(0, 255, 65, 0.1); border: 2px solid #00FF41; padding: 20px; border-radius: 10px; }}
    @keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(255, 69, 0, 0.4); }} 70% {{ box-shadow: 0 0 0 15px rgba(255, 69, 0, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(255, 69, 0, 0); }} }}
</style>""", unsafe_allow_html=True)

st.title("AFEG v7 // Online Governance Gateway")

# Top Level Financials
m1, m2, m3 = st.columns(3)
m1.metric("GROSS REVENUE", f"£{st.session_state.kvu_total * 0.001:,.2f}")
m2.metric("VAT CAPTURE (20%)", f"£{(st.session_state.kvu_total * 0.001 * 0.2):,.2f}")
m3.metric("VALIDATED KVUs", f"{st.session_state.kvu_total:,.0f}")

tabs = st.tabs(["ACT 1: GATEWAY", "ACT 2: SURGE", "ACT 3: LEDGER"])

with tabs[0]:
    st.subheader("ACT 1: LIVE GOVERNANCE AUDIT")
    user_query = st.text_input("Enter query to audit:")
    if st.button("RUN AUDIT") and user_query:
        # Integrated Logic Scan
        inf, res, mem, label, heat = calculate_complexity_kvu(user_query)
        total_kvu = inf + res + mem
        
        risky_keywords = ["hack", "bypass", "exploit", "illegal", "steal"]
        status = "approved"
        if any(word in user_query.lower() for word in risky_keywords):
            status, total_kvu = "blocked", 0.0

        st.session_state.kvu_total += total_kvu
        
        with st.container():
            st.markdown(f'<div class="heat-{heat}">', unsafe_allow_html=True)
            st.write(f"**INTENT ANALYSIS:** {label}")
            st.write(f"**EVIDENCE HASH:** `{hashlib.sha256(user_query.encode()).hexdigest()[:12]}`")
            st.markdown('</div>', unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("INF", inf, delta="Inference" if highlight_cat == "Inference" else None)
        c2.metric("RES", res, delta="Reasoning" if highlight_cat == "Reasoning" else None)
        c3.metric("MEM", mem, delta="Memory" if highlight_cat == "Memory" else None)
        
        entry = {"timestamp": datetime.now().isoformat(), "query": user_query, "kvu": total_kvu, "status": status}
        if status == "approved": st.session_state.safe_ledger.append(entry)
        else: st.session_state.risk_ledger.append(entry)

with tabs[1]:
    st.subheader("ACT 2: 60-SECOND NATIONAL SURGE")
    if st.button("EXECUTE LIVE SURGE"):
        prog = st.progress(0)
        status_text = st.empty()
        for i in range(30):
            batch_kvu = random.uniform(8000, 25000)
            st.session_state.kvu_total += batch_kvu
            prog.progress((i + 1) / 30)
            status_text.text(f"Auditing Batch {i+1}/30... Synchronizing Ledger.")
            time.sleep(2)
        st.rerun()

with tabs[2]:
    st.subheader("ACT 3: LEDGER VAULT")
    # Using the new stretch width parameter as requested by logs
    st.dataframe(st.session_state.safe_ledger + st.session_state.risk_ledger, width="stretch")

# Forecasting Sidebar
if st.session_state.kvu_total > 0:
    st.sidebar.divider()
    annual_est = (st.session_state.kvu_total * 0.001 * 365) * 1000 
    st.sidebar.subheader("Annual National Forecast")
    st.sidebar.metric("Est. Annual VAT", f"£{(annual_est * 0.2):,.0f}")