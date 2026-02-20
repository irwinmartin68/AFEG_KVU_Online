import streamlit as st
import time, hashlib, json, random, io, zipfile
from datetime import datetime

# ------------------ CONFIG ------------------
DAU_UK = 4_000_000 
QUERIES_PER_USER = 5
NATIONAL_DAILY_QUERIES = DAU_UK * QUERIES_PER_USER 
AVG_KVU_PER_QUERY = 650
NATIONAL_DAILY_KVU = NATIONAL_DAILY_QUERIES * AVG_KVU_PER_QUERY 

KVU_VALUE = 0.001  # £0.001 per KVU
VAT_RATE = 0.20
HOURLY_STEPS = 24 

# ------------------ GOVERNANCE ------------------
GOVERNANCE_MODE = st.sidebar.selectbox("Governance Mode", ["Demo", "Live"])

def hash_query(query):
    return hashlib.sha256(query.encode()).hexdigest()

def pass1_input_scan(query):
    """Scan input for prompt injections / malicious intent"""
    if any(x in query.lower() for x in ["malicious", "hack", "exploit"]):
        return False, "Input Risk Detected"
    return True, "Safe"

def pass2_output_scan(response):
    """Scan output for bias, toxicity, PII"""
    if any(x in response.lower() for x in ["unsafe", "leak", "pii"]):
        return False, "Output Risk Detected"
    return True, "Safe"

# ------------------ KVU SIMULATION ------------------
def simulate_kvu(query:str):
    base = 400 + (len(query) * 10)
    q_low = query.lower()
    
    # Intent-based workload split
    if any(w in q_low for w in ["why", "how", "explain"]):
        inf, res, mem = base * 0.8, base * 1.2, base * 0.1
    else:
        inf, res, mem = base * 1.0, base * 0.1, base * 0.2
    
    total = inf + res + mem
    value = total * KVU_VALUE
    
    return {
        "inference": round(inf, 2),
        "reasoning": round(res, 2),
        "memory": round(mem, 2),
        "raw_total": round(total, 2),
        "value": round(value, 4),
        "vat": round(value * VAT_RATE, 4)
    }

# ------------------ STATE ------------------
if "ledger_compliant" not in st.session_state: st.session_state.ledger_compliant = []
if "ledger_intercept" not in st.session_state: st.session_state.ledger_intercept = []
if "session_rev" not in st.session_state: st.session_state.session_rev = 0.0
if "current" not in st.session_state: st.session_state.current = None

# ------------------ LEDGER COMMIT ------------------
def commit_to_ledger(query, result, status, reason, action, kvu_display=None):
    entry = result.copy()
    entry.update({
        "query": query,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "hash": hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest(),
        "status": status,
        "reason": reason,
        "action": action,
        "kvu_display": kvu_display
    })
    if status == "A":
        st.session_state.ledger_compliant.append(entry)
    else:
        st.session_state.ledger_intercept.append(entry)
    if kvu_display not in [None, "Nullified"]:
        st.session_state.session_rev += result["value"]
    st.session_state.current = entry

# ------------------ UI ------------------
st.set_page_config(page_title="AFEG v7 Auditor", layout="wide")
st.sidebar.title("AFEG v7")
portal = st.sidebar.selectbox("PORTAL ACCESS", ["CEO Gateway", "Treasury Export Portal"])

st.markdown("""<style>.terminal {background-color:#000; color:#00FF41; padding:15px; font-family:monospace; height:350px; overflow-y:scroll; border:1px solid #444;}</style>""", unsafe_allow_html=True)

if portal == "CEO Gateway":
    st.title("AFEG v7 // Master Control")
    
    # Global Metrics
    c1, c2, c3 = st.columns(3)
    total_kvu = sum(e['raw_total'] for e in st.session_state.ledger_compliant) + \
                sum(e['raw_total'] for e in st.session_state.ledger_intercept if e['kvu_display'] != "Nullified")
    c1.metric("GROSS REVENUE", f"£{st.session_state.session_rev:,.2f}")
    c2.metric("VAT CAPTURE", f"£{(st.session_state.session_rev * VAT_RATE):,.2f}")
    c3.metric("VALIDATED KVUs", f"{total_kvu:,.0f}")

    tabs = st.tabs(["ACT 1: GATEWAY", "ACT 2: SURGE", "ACT 4: 24H ENDURANCE"])

    with tabs[0]:
        st.header("ACT 1: GATEWAY")
        q_in = st.text_input("AUDIT QUERY")
        if st.button("RUN AUDIT"):
            if q_in:
                # Pass 1 - Input Scan
                input_safe, input_reason = pass1_input_scan(q_in)
                if not input_safe:
                    kvu_display = "Nullified"
                    commit_to_ledger(q_in, simulate_kvu(q_in), "X", input_reason, "Blocked", kvu_display)
                else:
                    # LLM Simulation
                    response = f"Simulated LLM response for: {q_in}"
                    result = simulate_kvu(q_in)
                    # Pass 2 - Output Scan
                    output_safe, output_reason = pass2_output_scan(response)
                    if not output_safe:
                        kvu_display = f"{result['raw_total']} (Governed)"
                        action = "Blocked" if GOVERNANCE_MODE == "Live" else "Flagged"
                        commit_to_ledger(q_in, result, "B", output_reason, action, kvu_display)
                    else:
                        commit_to_ledger(q_in, result, "A", output_reason, "Delivered", result['raw_total'])
            st.rerun()

        if st.session_state.current:
            c = st.session_state.current
            if c['status'] == "X":
                st.error(f"Input Blocked: {c['reason']} | KVU Nullified")
            elif c['status'] == "B":
                st.warning(f"Response {c['action']}: {c['reason']} | KVU: {c['kvu_display']}")
            else:
                st.success(f"Response Delivered | KVU: {c['kvu_display']}")
            st.json(c)

    with tabs[1]:
        st.header("ACT 2: NATIONAL SURGE")
        if st.button("EXECUTE"):
            t_win = st.empty(); logs = []
            for i in range(10):
                query = f"SURGE_NODE_{i}"
                input_safe, _ = pass1_input_scan(query)
                response = f"Simulated LLM response for: {query}"
                result = simulate_kvu(query)
                if input_safe:
                    output_safe, _ = pass2_output_scan(response)
                    kvu_display = f"{result['raw_total']}" if output_safe else f"{result['raw_total']} (Governed)"
                    action = "Delivered" if output_safe else ("Flagged" if GOVERNANCE_MODE=="Demo" else "Blocked")
                    status = "A" if output_safe else "B"
                    commit_to_ledger(query, result, status, "N/A", action, kvu_display)
                    log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] NODE_{i} SYNC | KVU: {result['raw_total']}"
                    logs.insert(0, log_entry)
                    t_win.markdown(f'<div class="terminal">{"<br>".join(logs)}</div>', unsafe_allow_html=True)
                time.sleep(0.05)
            st.rerun()

    with tabs[2]:
        st.header("ACT 4: 24H ENDURANCE")
        if st.button("INITIALIZE TEST"):
            e_win = st.empty(); e_logs = []
            for i in range(HOURLY_STEPS):
                time_label = f"{i:02d}:00"
                query = f"TEMPORAL_{time_label}"
                input_safe, _ = pass1_input_scan(query)
                response = f"Simulated LLM response for: {query}"
                result = simulate_kvu(query)
                if input_safe:
                    output_safe, _ = pass2_output_scan(response)
                    kvu_display = f"{result['raw_total']}" if output_safe else f"{result['raw_total']} (Governed)"
                    action = "Delivered" if output_safe else ("Flagged" if GOVERNANCE_MODE=="Demo" else "Blocked")
                    status = "A" if output_safe else "B"
                    commit_to_ledger(query, result, status, "N/A", action, kvu_display)
                    e_logs.insert(0, f"[{time_label}] TEMPORAL_SYNC | KVU: {result['raw_total']} | VAT: £{result['vat']:,.2f}")
                    e_win.markdown(f'<div class="terminal">{"<br>".join(e_logs)}</div>', unsafe_allow_html=True)
                time.sleep(0.02)
            st.rerun()

else:
    st.title("HM TREASURY // AUDIT EXPORT")
    st.metric("NATIONAL VAT RECOVERY", f"£{(st.session_state.session_rev * VAT_RATE):,.2f}")
    if st.session_state.ledger_compliant or st.session_state.ledger_intercept:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "x") as audit_zip:
            audit_zip.writestr("TREASURY_LEDGER_COMPLIANT.json", json.dumps(st.session_state.ledger_compliant, indent=4))
            audit_zip.writestr("TREASURY_LEDGER_INTERCEPT.json", json.dumps(st.session_state.ledger_intercept, indent=4))
        st.download_button("EXPORT TREASURY ZIP", data=buf.getvalue(), file_name="AFEG_TREASURY_AUDIT.zip")