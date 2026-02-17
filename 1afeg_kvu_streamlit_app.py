import streamlit as st
import time, hashlib, json, random, io, zipfile
from datetime import datetime, timedelta

# ------------------ CONFIG ------------------
KVU_VALUE = 0.001
VAT_RATE = 0.20
NATIONAL_DAILY_KVU = 975_000_000_000 

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
    return {
        "inference": round(inf, 2), "reasoning": round(res, 2), "memory": round(mem, 2),
        "raw_total": round(raw_total, 2), "value": round(value, 4), "vat": round(value * VAT_RATE, 4)
    }

def add_to_ledger(query, result, is_act1=False):
    entry = result.copy()
    entry.update({
        "query": query, "timestamp": datetime.now().strftime("%H:%M:%S"),
        "hash": hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()
    })
    st.session_state.ledger.append(entry)
    st.session_state.session_revenue += entry["value"]
    if is_act1: st.session_state.act1_subtotal += entry["value"]
    st.session_state.current_result = entry

# ------------------ UI SETUP ------------------
st.set_page_config(page_title="AFEG National Auditor", layout="wide")
st.sidebar.title("AFEG KVU CONTROLS")
portal_mode = st.sidebar.selectbox("ACCESS PORTAL", ["CEO Gateway", "Treasury Export Portal"])
text_size = st.sidebar.slider("TEXT SIZE", 10, 30, 14)

st.markdown(f"<style>.terminal-box {{background-color:#000; color:#00FF41; padding:20px; font-family:monospace; height:500px; overflow-y:scroll; font-size:{text_size}px;}}</style>", unsafe_allow_html=True)

if portal_mode == "CEO Gateway":
    st.title("AFEG CEO COMMAND CENTER")
    
    m_cols = st.columns(3)
    m_rev, m_tax, m_kvu = m_cols[0].empty(), m_cols[1].empty(), m_cols[2].empty()

    def update_top_metrics():
        total_kvu = sum(e['raw_total'] for e in st.session_state.ledger)
        m_rev.metric("SESSION GROSS VALUE", f"£{st.session_state.session_revenue:,.2f}")
        m_tax.metric("VAT ACCRUED (20%)", f"£{(st.session_state.session_revenue * VAT_RATE):,.2f}")
        m_kvu.metric("TOTAL KVUs VALIDATED", f"{total_kvu:,.0f}")

    update_top_metrics()
    tabs = st.tabs(["ACT 1: GATEWAY", "ACT 2: NATIONAL SURGE", "ACT 3: VAULT", "ACT 4: 24H ENDURANCE"])

    with tabs[0]:
        st.header("ACT 1: GATEWAY SEEDING")
        q_in = st.text_input("ENTER UK AI QUERY")
        if st.button("SUBMIT QUERY"):
            if q_in:
                res = simulate_kvu(q_in)
                add_to_ledger(q_in, res, is_act1=True)
                st.rerun()
        if st.session_state.current_result:
            c = st.session_state.current_result
            r_cols = st.columns(3)
            r_cols[0].metric("INFERENCE", f"{c['inference']:,}")
            r_cols[1].metric("REASONING", f"{c['reasoning']:,}")
            r_cols[2].metric("MEMORY", f"{c['memory']:,}")

    with tabs[1]:
        st.header("ACT 2: NATIONAL SURGE")
        if st.button("EXECUTE NATIONAL SURGE"):
            log_win = st.empty()
            logs = []
            batch_size = NATIONAL_DAILY_KVU / 100
            for i in range(100):
                res = simulate_kvu(f"SURGE_NODE_{i}", scale_factor=(batch_size/650))
                add_to_ledger(f"SURGE_NODE_{i}", res)
                update_top_metrics()
                logs.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] SYNC_OK | +{res['raw_total']:,.0f} KVU")
                log_win.markdown(f'<div class="terminal-box">{"<br>".join(logs[:100])}</div>', unsafe_allow_html=True)
                time.sleep(0.05)

    with tabs[2]:
        st.header("ACT 3: IMMUTABLE VAULT")
        search = st.text_input("SEARCH LEDGER")
        if st.session_state.ledger:
            filt = [e for e in st.session_state.ledger if not search or search.lower() in str(e).lower()]
            st.dataframe(filt[::-1], use_container_width=True)

    with tabs[3]:
        st.header("ACT 4: 24-HOUR NATIONAL ENDURANCE")
        st.write("Stress-testing national infrastructure across a full 24-hour temporal cycle.")
        
        # ACT 4 INDEPENDENT COUNTERS
        e_cols = st.columns(2)
        e_metric_rev = e_cols[0].empty()
        e_metric_vat = e_cols[1].empty()
        
        e_metric_rev.metric("ACT 4 GROSS (LOCAL)", "£0.00")
        e_metric_vat.metric("ACT 4 VAT (LOCAL)", "£0.00")

        if st.button("START 24H TEMPORAL STRESS TEST"):
            e_win = st.empty()
            e_logs = []
            act4_revenue = 0.0
            
            # 144 steps = 1 step every 10 minutes of simulated time
            # 60 seconds total / 144 steps = approx 0.4s per step
            start_sim_time = datetime.strptime("00:00", "%H:%M")
            sustained_load = NATIONAL_DAILY_KVU / 144
            
            for i in range(144):
                # Update Simulated Clock
                current_sim_time = (start_sim_time + timedelta(minutes=i*10)).strftime("%H:%M")
                
                # Process Data
                res = simulate_kvu(f"TS_NODE_{i}", scale_factor=(sustained_load/650))
                
                # Add to Act 4 Local Totals
                act4_revenue += res['value']
                
                # Add to Master Ledger
                add_to_ledger(f"STRESS_TEST_{current_sim_time}", res)
                update_top_metrics()
                
                # Update Local UI
                e_metric_rev.metric("ACT 4 GROSS (LOCAL)", f"£{act4_revenue:,.2f}")
                e_metric_vat.metric("ACT 4 VAT (LOCAL)", f"£{(act4_revenue * 0.2):,.2f}")