import streamlit as st
import hashlib, json, random, time, io, zipfile
from datetime import datetime

# -----------------------------
# CORE LOGIC (THE KITCHEN LOGIC ENGINE)
# -----------------------------
def calculate_complexity_kvu(query, mode):
    base = 400.0
    q = query.lower()
    # Categorical Split for IP Protection & Metering
    if any(w in q for w in ["why", "how", "explain", "audit"]):
        inf, res, mem = base * 0.8, base * 2.5, base * 0.5
        label, heat = "Deep Reasoning", "high"
    elif any(w in q for w in ["what", "who", "where", "list"]):
        inf, res, mem = base * 1.2, base * 0.4, base * 0.3
        label, heat = "Standard Inference", "low"
    else:
        inf, res, mem = base, base * 0.2, base * 0.1
        label, heat = "Basic System", "low"
    
    # Toggle Multiplier for Demo/Live Scaling
    multiplier = 2.5 if mode == "Demo Simulation" else 1.0
    return round(inf * multiplier, 2), round(res * multiplier, 2), round(mem * multiplier, 2), label, heat

# -----------------------------
# UI SETUP & PERSISTENT STATE
# -----------------------------
st.set_page_config(page_title="AFEG v7 Gateway", layout="wide")

if "total_kvu" not in st.session_state: st.session_state.total_kvu = 0.0
if "ledger" not in st.session_state: st.session_state.ledger = []
if "cat_metrics" not in st.session_state: st.session_state.cat_metrics = {"inf": 0.0, "res": 0.0, "mem": 0.0}

# -----------------------------
# DYNAMIC STYLING (THE HEATMAP)
# -----------------------------
st.markdown("""<style>
    .heat-high { background-color: rgba(255, 69, 0, 0.1); border: 2px solid #FF4500; padding: 20px; border-radius: 10px; animation: pulse 2s infinite; }
    .heat-low { background-color: rgba(0, 255, 65, 0.05); border: 2px solid #00FF41; padding: 20px; border-radius: 10px; }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(255, 69, 0, 0.4); } 70% { box-shadow: 0 0 0 10px rgba(255, 69, 0, 0); } 100% { box-shadow: 0 0 0 0 rgba(255, 69, 0, 0); } }
</style>""", unsafe_allow_html=True)

# -----------------------------
# PERSISTENT TELEMETRY (GRID COUNTERS)
# -----------------------------
st.sidebar.title("COMPUTE GRID COUNTERS")
s_inf = st.sidebar.empty()
s_res = st.sidebar.empty()
s_mem = st.sidebar.empty()

def update_all_metrics():
    # Update Top Financials
    gross_placeholder.metric("GROSS REVENUE", f"£{st.session_state.total_kvu * 0.001:,.2f}")
    vat_placeholder.metric("VAT CAPTURE", f"£{(st.session_state.total_kvu * 0.001 * 0.2):,.2f}")
    kvu_placeholder.metric("VALIDATED KVUs", f"{st.session_state.total_kvu:,.0f}")
    # Update Sidebar Grid Categories
    s_inf.metric("Inference Engine", f"{st.session_state.cat_metrics['inf']:,.1f}")
    s_res.metric("Reasoning Layer", f"{st.session_state.cat_metrics['res']:,.1f}")
    s_mem.metric("Memory Vault", f"{st.session_state.cat_metrics['mem']:,.1f}")

# -----------------------------
# MAIN DASHBOARD STRUCTURE
# -----------------------------
st.title("AFEG v7 // Unified Governance Gateway")
h1, h2, h3 = st.columns(3)
gross_placeholder = h1.empty()
vat_placeholder = h2.empty()
kvu_placeholder = h3.empty()

update_all_metrics()

tabs = st.tabs(["ACT 1: GATEWAY", "ACT 2: SURGE", "ACT 3: LEDGER VAULT", "ACT 4: ECONOMIC ENGINE"])

# --- ACT 1: GATEWAY AUDIT ---
with tabs[0]:
    st.subheader("AFEG KVU GOVERNANCE AUDIT TELEMETRY")
    gate_mode = st.radio("Gateway State:", ["Live Enforcement", "Demo Simulation"], horizontal=True)
    user_query = st.text_input("Enter Audit Query:", key="gate_input")
    
    # SUBMIT QUERY BUTTON
    if st.button("SUBMIT QUERY") and user_query:
        inf, res, mem, label, heat = calculate_complexity_kvu(user_query, gate_mode)
        total = inf + res + mem
        
        # Update System State
        st.session_state.total_kvu += total
        st.session_state.cat_metrics['inf'] += inf
        st.session_state.cat_metrics['res'] += res
        st.session_state.cat_metrics['mem'] += mem
        
        entry = {
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Origin": "Live Gateway",
            "Query": user_query,
            "KVU": total,
            "Type": label,
            "Hash": hashlib.sha256(user_query.encode()).hexdigest()[:12]
        }
        st.session_state.ledger.insert(0, entry) # Log to Vault
        update_all_metrics()
        
        st.markdown(f'<div class="heat-{heat}"><b>{label} detected.</b> Evidence Hash: <code>{entry["Hash"]}</code></div>', unsafe_allow_html=True)

# --- ACT 2: NATIONAL SURGE ---
with tabs[1]:
    st.subheader("ACT 2: NATIONAL SURGE SIMULATION")
    if st.button("EXECUTE 60s SURGE"):
        prog = st.progress(0)
        surge_status = st.empty()
        for i in range(30):
            # Batch Simulation Logic
            b_inf, b_res, b_mem = random.uniform(5000, 10000), random.uniform(8000, 15000), random.uniform(1000, 3000)
            batch_total = b_inf + b_res + b_mem
            
            st.session_state.total_kvu += batch_total
            st.session_state.cat_metrics['inf'] += b_inf
            st.session_state.cat_metrics['res'] += b_res
            st.session_state.cat_metrics['mem'] += b_mem
            
            st.session_state.ledger.insert(0, {
                "Time": datetime.now().strftime("%H:%M:%S"),
                "Origin": "National Surge",
                "Query": f"Batch Cluster #{i+1:02d}",
                "KVU": round(batch_total, 2),
                "Type": "Synthetic Aggregate",
                "Hash": hashlib.md5(str(i).encode()).hexdigest()[:12]
            })
            
            update_all_metrics()
            prog.progress((i + 1) / 30)
            surge_status.text(f"Batch {i+1}/30 Processing... Counters Jumping.")
            time.sleep(1)
        st.success("National Surge Logged to Vault.")

# --- ACT 3: SEARCHABLE LEDGER VAULT ---
with tabs[2]:
    st.subheader("ACT 3: SEARCHABLE LEDGER VAULT")
    if st.session_state.ledger:
        # Dataframe allows for the search bar and interactive filtering
        st.dataframe(st.session_state.ledger, use_container_width=True)
    else:
        st.info("Vault is empty. Submit a query or run surge to generate audit tickets.")

# --- ACT 4: THE ECONOMIC ENGINE ---
with tabs[3]:
    st.subheader("ACT 4: THE ECONOMIC ENGINE (ROI)")
    if st.session_state.total_kvu > 0:
        daily_capture = st.session_state.total_kvu * 0.001
        annual_projection = daily_capture * 365 * 1000 
        
        ec1, ec2 = st.columns(2)
        ec1.metric("Current Session Capture", f"£{daily_capture:,.2f}")
        ec2.metric("Annual National VAT Recovery", f"£{(annual_projection * 0.2):,.0f}")
        
        st.divider()
        st.write("### Regulatory Audit Export")
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("AFEG_V7_FULL_AUDIT.json", json.dumps(st.session_state.ledger, indent=4))
        st.download_button("DOWNLOAD ALL AUDIT TICKETS", data=buf.getvalue(), file_name="AFEG_V7_AUDIT.zip")