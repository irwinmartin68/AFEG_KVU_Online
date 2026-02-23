import streamlit as st
import time, hashlib, json, random, io, zipfile
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from threading import Thread
import uvicorn
import requests

# -----------------------------
# FASTAPI BACKEND (THE ENGINE)
# -----------------------------
app = FastAPI(title="AFEG v7 Gateway API")

class QueryPayload(BaseModel):
    query: str
    mode: str = "live"

def calculate_complexity_kvu(query):
    """
    The 'Kitchen Logic' Engine: 
    Determines if compute is Inference-heavy or Reasoning-heavy.
    """
    base = 400.0 
    q = query.lower()
    label, heat = "Standard Processing", "low"
    
    # Why/How = Reasoning (High Value/High Compute)
    if any(w in q for w in ["why", "how", "explain", "audit"]):
        inf, res, mem = base * 0.8, base * 2.5, base * 0.5
        label, heat = "Deep Reasoning (High Compute)", "high"
    # What/Who/Where = Inference (Standard Value)
    elif any(w in q for w in ["what", "who", "where", "list"]):
        inf, res, mem = base * 1.2, base * 0.4, base * 0.3
    else:
        inf, res, mem = base, base * 0.2, base * 0.1
        
    return round(inf, 2), round(res, 2), round(mem, 2), label, heat

@app.post("/afeg-gateway")
def afeg_gateway(payload: QueryPayload):
    inf, res, mem, label, heat = calculate_complexity_kvu(payload.query)
    total_kvu = inf + res + mem
    
    # Semantic Firewall (Governance Layer)
    risky_keywords = ["hack", "bypass", "exploit", "illegal", "steal"]
    status = "approved"
    if any(word in payload.query.lower() for word in risky_keywords):
        status, total_kvu = "blocked", 0.0 # Rule: Zero revenue on risk

    return {
        "status": status,
        "kvu": total_kvu,
        "metrics": {"inf": inf, "res": res, "mem": mem},
        "complexity": label,
        "heat": heat,
        "hash": hashlib.sha256(f"{payload.query}{time.time()}".encode()).hexdigest()[:12]
    }

# Function to run the API in a separate thread
def run_api():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

if "api_thread_started" not in st.session_state:
    Thread(target=run_api, daemon=True).start()
    st.session_state.api_thread_started = True

# -----------------------------
# STREAMLIT UI (THE COCKPIT)
# -----------------------------
st.set_page_config(page_title="AFEG v7 Master Prototype", layout="wide")

if "safe_ledger" not in st.session_state: st.session_state.safe_ledger = []
if "risk_ledger" not in st.session_state: st.session_state.risk_ledger = []
if "kvu_total" not in st.session_state: st.session_state.kvu_total = 0.0

# Sidebar controls for the Demo
st.sidebar.title("AFEG v7 Control Panel")
text_size = st.sidebar.slider("UI Text Size", 12, 32, 18)
highlight_cat = st.sidebar.selectbox("Highlight Compute Tier", ["Inference", "Reasoning", "Memory", "None"])

st.markdown(f"""<style>
    html, body, [class*="st-"] {{ font-size: {text_size}px !important; }}
    .heat-high {{ background-color: rgba(255, 69, 0, 0.15); border: 2px solid #FF4500; padding: 20px; border-radius: 10px; animation: pulse 2s infinite; }}
    .heat-low {{ background-color: rgba(0, 255, 65, 0.1); border: 2px solid #00FF41; padding: 20px; border-radius: 10px; }}
    @keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(255, 69, 0, 0.4); }} 70% {{ box-shadow: 0 0 0 15px rgba(255, 69, 0, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(255, 69, 0, 0); }} }}
</style>""", unsafe_allow_html=True)

st.title("AFEG v7 // Unified Governance & Telemetry")

# Top Level Financials
m1, m2, m3 = st.columns(3)
m1.metric("GROSS REVENUE", f"£{st.session_state.kvu_total * 0.001:,.2f}")
m2.metric("VAT CAPTURE (20%)", f"£{(st.session_state.kvu_total * 0.001 * 0.2):,.2f}")
m3.metric("VALIDATED KVUs", f"{st.session_state.kvu_total:,.0f}")

tabs = st.tabs(["ACT 1: GATEWAY", "ACT 2: SURGE", "ACT 3: LEDGER"])

with tabs[0]:
    st.subheader("ACT 1: LIVE GOVERNANCE AUDIT")
    user_query = st.text_input("Enter query to audit (e.g., 'How do I audit AI'):")
    if st.button("RUN AUDIT") and user_query:
        try:
            r = requests.post("http://127.0.0.1:8000/afeg-gateway", json={"query": user_query}).json()
            st.session_state.kvu_total += r["kvu"]
            
            with st.container():
                st.markdown(f'<div class="heat-{r["heat"]}">', unsafe_allow_html=True)
                st.write(f"**INTENT ANALYSIS:** {r['complexity']}")
                st.write(f"**EVIDENCE HASH:** `{r['hash']}`")
                st.markdown('</div>', unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("INF", r['metrics']['inf'], delta="Inference" if highlight_cat == "Inference" else None)
            c2.metric("RES", r['metrics']['res'], delta="Reasoning" if highlight_cat == "Reasoning" else None)
            c3.metric("MEM", r['metrics']['mem'], delta="Memory" if highlight_cat == "Memory" else None)
            
            entry = {"timestamp": datetime.now().isoformat(), "query": user_query, "kvu": r["kvu"], "status": r["status"], "hash": r["hash"]}
            if r["status"] == "approved": st.session_state.safe_ledger.append(entry)
            else: st.session_state.risk_ledger.append(entry)
        except Exception as e:
            st.error(f"Gateway Error: {e}")

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
    st.subheader("ACT 3: LEDGER VAULT (AUDIT TICKETS)")
    st.dataframe(st.session_state.safe_ledger + st.session_state.risk_ledger, use_container_width=True)

# Forecasting Sidebar
if st.session_state.kvu_total > 0:
    st.sidebar.divider()
    annual_est = (st.session_state.kvu_total * 0.001 * 365) * 1000 
    st.sidebar.subheader("Annual National Forecast")
    st.sidebar.metric("Est. Annual VAT", f"£{(annual_est * 0.2):,.0f}")
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("SAFE_AUDIT.json", json.dumps(st.session_state.safe_ledger, indent=4))
        zf.writestr("RISK_AUDIT.json", json.dumps(st.session_state.risk_ledger, indent=4))
    st.sidebar.download_button("EXPORT AUDIT TICKETS", data=buf.getvalue(), file_name="AFEG_V7_AUDIT.zip")