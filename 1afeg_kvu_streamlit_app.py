import streamlit as st
import time, hashlib, json, random
from datetime import datetime

# ------------------ NATIONAL SCALE CONFIG ------------------
KVU_VALUE = 0.001
VAT_RATE = 0.20
NATIONAL_DAILY_KVU = 975_000_000_000 
SIM_STEPS = 100 
ENDURANCE_STEPS = 150
TREASURY_KEY = "AFEG-V7-TREASURY-2026"

# ------------------ SESSION STATE ------------------
if "ledger" not in st.session_state:
    st.session_state.ledger = []
if "session_revenue" not in st.session_state:
    st.session_state.session_revenue = 0.0
if "act1_subtotal" not in st.session_state:
    st.session_state.act1_subtotal = 0.0
if "current_result" not in st.session_state:
    st.session_state.current_result = None

# ------------------ CORE ENGINE ------------------
def simulate_kvu(query:str, scale_factor=1.0):
    base = (400 + (len(query) * 10)) * scale_factor
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
st.set_page_config(page_title="AFEG National Auditor", layout="wide")

st.sidebar.title("AFEG KVU CONTROLS")
mode = st.sidebar.selectbox("ACCESS PORTAL", ["CEO Gateway", "Treasury Key Portal"])
text_size = st.sidebar.slider("TEXT SIZE", 10, 30, 14)

st.markdown(f"""
    <style>
    .terminal-box {{
        background-color: #000000;
        color: #00FF41;
        padding: 20px;
        font-family: monospace;
        height: 400px;
        overflow-y: scroll;
        white-space: pre-wrap;
        font-size: {text_size}px;
    }}
    </style>
    """, unsafe_allow_html=True)

if mode == "CEO Gateway":
    st.title("AFEG CEO COMMAND CENTER")
    
    m_cols = st.columns(3)
    m_rev = m_cols[0].empty()
    m_tax = m_cols[1].empty()
    m_kvu = m_cols[2].empty()

    def update_top_metrics():
        m_rev.metric("SESSION GROSS VALUE", f"£{st.session_state.session_revenue:,.2f}")
        m_tax.metric("VAT ACCRUED (20%)", f"£{(st.session_state.session_revenue * VAT_RATE):,.2f}")
        m_kvu.metric("TOTAL KVUs VALIDATED", f"{sum(e['raw_total'] for e in st.session_state.ledger):,.0f}")

    update_top_metrics()

    tab1, tab2, tab3, tab4 = st.tabs(["ACT 1: GATEWAY", "ACT 2: NATIONAL SURGE", "ACT 3: VAULT", "ACT 4: ENDURANCE"])

    with tab1:
        st.header("ACT 1: GATEWAY SEEDING")
        query = st.text_input("ENTER UK AI QUERY")
        if st.button("SUBMIT QUERY"):
            if query:
                result = simulate_kvu(query)
                add_to_ledger(query, result, is_act1=True)
                st.rerun()

        if st.session_state.current_result:
            res = st.session_state.current_result
            r1c1, r1c2, r1c3 = st.columns(3)
            r1c1.metric("INFERENCE", f"{res['inference']:,}")
            r1c2.metric("REASONING", f"{res['reasoning']:,}")
            r1c3.metric("MEMORY", f"{res['memory']:,}")
            r2c1, r2c2, r2c3 = st.columns(3)
            r2c1.metric("REVENUE CAPTURED", f"£{res['value']:,.4f}")
            r2c2.metric("VAT CAPTURED", f"£{res['vat']:,.4f}")
            r2c3.metric("ACT SUBTOTAL", f"£{st.session_state.act1_subtotal:,.4f}")

    with tab2:
        st.header("ACT 2: NATIONAL SIMULATION (975B KVU)")
        g1, g2, g3 = st.columns(3)
        ginf, gres, gmem = g1.empty(), g2.empty(), g3.empty()
        g4, g5, g6 = st.columns(3)
        grev, gvat, gtot = g4.empty(), g5.empty(), g6.empty()

        if st.button("EXECUTE NATIONAL SURGE"):
            window = st.empty()
            logs = []
            batch_size = NATIONAL_DAILY_KVU / SIM_STEPS
            for i in range(SIM_STEPS):
                res = simulate_kvu(f"NODE_UK_{i}", scale_factor=(batch_size/650))
                add_to_ledger(f"NODE_UK_{i}", res)
                
                ginf.metric("INFERENCE", f"{res['inference']:,.0f}")
                gres.metric("REASONING", f"{res['reasoning']:,.0f}")
                gmem.metric("MEMORY", f"{res['memory']:,.0f}")
                grev.metric("REVENUE CAPTURED", f"£{res['value']:,.2f}")
                gvat.metric("VAT CAPTURED", f"£{res['vat']:,.2f}")
                gtot.metric("UNIT TOTAL (RAW)", f"{res['raw_total']:,.0f}")
                
                update_top_metrics()
                
                logs.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] SYNC_OK | +{res['raw_total']:,.0f} KVU")
                window.markdown(f'<div class="terminal-box">{"<br>".join(logs[:50])}</div>', unsafe_allow_html=True)
                time.sleep(0.05)

    with tab3:
        st.header("ACT 3: IMMUTABLE VAULT")
        st.dataframe(st.session_state.ledger[::-1], use_container_width=True)

    with tab4:
        st.header("ACT 4: 24-HOUR ENDURANCE")
        if st.button("START ENDURANCE CYCLE"):
            window_4 = st.empty()
            logs_4 = []
            for i in range(ENDURANCE_STEPS):
                res = simulate_kvu(f"Endurance_{i}")
                add_to_ledger(f"Endurance_{i}", res)
                update_top_metrics()
                logs_4.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] STABLE | {res['raw_total']:,} KVU | £{res['value']:.4f}")
                window_4.markdown(f'<div class="terminal-box">{"<br>".join(logs_4[:50])}</div>', unsafe_allow_html=True)
                time.sleep(0.02)

else:
    st.title("HM TREASURY // REGULATORY OVERRIDE")
    auth_key = st.text_input("ENTER TREASURY ACCESS KEY:", type="password")
    if auth_key == TREASURY_KEY:
        st.success("AUDIT VAULT UNLOCKED")
        st.dataframe(st.session_state.ledger, use_container_width=True)