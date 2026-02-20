import streamlit as st
import time, hashlib, json, random, io, zipfile
from datetime import datetime

# ------------------ CONFIG & RESEARCH ------------------
DAU_UK, QUERIES_PER_USER = 4_000_000, 5
# Anchor: £2.6M VAT daily floor
NATIONAL_DAILY_KVU = (DAU_UK * QUERIES_PER_USER) * 650
KVU_VALUE, VAT_RATE = 0.001, 0.20

# ------------------ GOVERNANCE FILTERS ------------------
def pass1_input_scan(query):
    if any(x in query.lower() for x in ["hack", "exploit", "bypass", "malicious"]):
        return False, "Input Risk (Firewall)"
    return True, "Safe"

def pass2_output_scan(response):
    if any(x in response.lower() for x in ["unsafe", "leak", "pii", "private"]):
        return False, "Output Risk (Filter)"
    return True, "Safe"

# ------------------ STATE ------------------
if "ledger_compliant" not in st.session_state: st.session_state.ledger_compliant = []
if "ledger_intercept" not in st.session_state: st.session_state.ledger_intercept = []
if "session_rev" not in st.session_state: st.session_state.session_rev = 0.0
if "current" not in st.session_state: st.session_state.current = None

def commit_to_ledger(query, status, reason, action, kvu_amt):
    entry = {
        "query": query, "timestamp": datetime.now().strftime("%H:%M:%S"),
        "kvu": kvu_amt, "value": kvu_amt * KVU_VALUE, "vat": (kvu_amt * KVU_VALUE) * VAT_RATE,
        "status": status, "reason": reason, "action": action,
        "hash": hashlib.sha256(str(random.random()).encode()).hexdigest()
    }
    if status == "COMPLIANT":
        st.session_state.ledger_compliant.append(entry)
    else:
        st.session_state.ledger_intercept.append(entry)
    st.session_state.session_rev += entry["value"]
    st.session_state.current = entry

# ------------------ UI ------------------
st.set_page_config(page_title="AFEG v7 Auditor", layout="wide")
st.sidebar.title("AFEG v7")
portal = st.sidebar.selectbox("PORTAL ACCESS", ["CEO Gateway", "Treasury Export Portal"])
gov_mode = st.sidebar.radio("Governance Mode", ["Demo", "Live"])

st.markdown("""<style>.terminal {background-color:#000; padding:15px; font-family:monospace; height:400px; overflow-y:scroll; border:1px solid #444;}</style>""", unsafe_allow_html=True)

if portal == "CEO Gateway":
    st.title("AFEG v7 // Master Control")
    c1, c2, c3 = st.columns(3)
    total_kvu = sum(e['kvu'] for e in st.session_state.ledger_compliant + st.session_state.ledger_intercept)
    c1.metric("GROSS REVENUE", f"£{st.session_state.session_rev:,.2f}")
    c2.metric("VAT CAPTURE", f"£{(st.session_state.session_rev * VAT_RATE):,.2f}")
    c3.metric("VALIDATED KVUs", f"{total_kvu:,.0f}")

    tabs = st.tabs(["ACT 1: GATEWAY", "ACT 2: SURGE", "ACT 3: ARCHITECT", "ACT 4: 24H ENDURANCE"])

    with tabs[0]:
        st.header("ACT 1: GATEWAY (SEMANTIC FIREWALL)")
        q_in = st.text_input("AUDIT QUERY")
        if st.button("RUN AUDIT") and q_in:
            safe_in, r1 = pass1_input_scan(q_in)
            if not safe_in:
                commit_to_ledger(q_in, "INTERCEPT", r1, "Blocked", 0)
            else:
                kvu = 650 + (len(q_in) * 5)
                safe_out, r2 = pass2_output_scan("Simulated Response")
                status = "COMPLIANT" if safe_out else "INTERCEPT"
                action = "Delivered" if safe_out else ("Flagged" if gov_mode=="Demo" else "Blocked")
                commit_to_ledger(q_in, status, r2, action, kvu)
            st.rerun()
        if st.session_state.current: st.json(st.session_state.current)

    with tabs[1]:
        st.header("ACT 2: NATIONAL SURGE (30s LIVE)")
        if st.button("EXECUTE SURGE"):
            t_win, logs = st.empty(), []
            for i in range(15): # 15 steps * 2s = 30 seconds
                q = f"SURGE_NODE_{random.randint(100,999)}"
                is_breach = random.random() > 0.85
                status = "INTERCEPT" if is_breach else "COMPLIANT"
                color = "#FF4B4B" if status == "INTERCEPT" else "#00FF41"
                commit_to_ledger(q, status, "Surge Check", "Verified", 650 * 100)
                logs.insert(0, f"<span style='color:{color}'>[{datetime.now().strftime('%H:%M:%S')}] {q} | {status} | {650*100} KVU</span>")
                t_win.markdown(f'<div class="terminal">{"<br>".join(logs)}</div>', unsafe_allow_html=True)
                time.sleep(2.0)
            st.rerun()

    with tabs[2]:
        st.header("ACT 3: ARCHITECT'S GATE")
        if st.checkbox("Accept NDA for Core IP Access"):
            st.success("ACCESS GRANTED: KITCHEN LOGIC & TREASURY PIPE SCHEMATICS")

    with tabs[3]:
        st.header("ACT 4: 24H ENDURANCE (120s SIMULATION)")
        if st.button("START 2-MINUTE FORENSIC AUDIT"):
            e_win, e_logs = st.empty(), []
            hourly_load = NATIONAL_DAILY_KVU / 24
            # 24 hours / 5 seconds per hour = 120 seconds (2 minutes)
            for i in range(24):
                time_label = f"{i:02d}:00"
                commit_to_ledger(f"STRESS_{time_label}", "COMPLIANT", "Batch", "Audited", hourly_load)
                e_logs.insert(0, f"<span style='color:#00FF41'>[{time_label}] TEMPORAL_SYNC | AUDIT VALIDATED | VAT: £{hourly_load*KVU_VALUE*VAT_RATE:,.2f}</span>")
                e_win.markdown(f'<div class="terminal">{"<br>".join(e_logs)}</div>', unsafe_allow_html=True)
                time.sleep(5.0) 
            st.rerun()

else:
    st.title("HM TREASURY // AUDIT EXPORT")
    if st.session_state.ledger_compliant or st.session_state.ledger_intercept:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "x") as audit_zip:
            audit_zip.writestr("LEDGER_COMPLIANT.json", json.dumps(st.session_state.ledger_compliant, indent=4))
            audit_zip.writestr("LEDGER_INTERCEPTED.json", json.dumps(st.session_state.ledger_intercept, indent=4))
        st.download_button("EXPORT TREASURY ZIP", data=buf.getvalue(), file_name="AFEG_AUDIT.zip")