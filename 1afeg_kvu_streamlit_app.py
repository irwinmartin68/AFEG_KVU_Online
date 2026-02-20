import streamlit as st
import time, hashlib, json, random, io, zipfile, psutil
from datetime import datetime

# ------------------ CONFIG & RESEARCH ------------------
DAU_UK, QUERIES_PER_USER = 4_000_000, 5
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

def get_hardware_throttle():
    cpu_usage = psutil.cpu_percent(interval=0.1)
    return 0.1 + (cpu_usage / 100)

# ------------------ STATE ------------------
if "ledger_compliant" not in st.session_state: st.session_state.ledger_compliant = []
if "ledger_intercept" not in st.session_state: st.session_state.ledger_intercept = []
if "session_rev" not in st.session_state: st.session_state.session_rev = 0.0
if "current" not in st.session_state: st.session_state.current = None

def commit_to_ledger(query, status, reason, action, kvu_amt):
    entry = {"query": query, "timestamp": datetime.now().strftime("%H:%M:%S"),
             "kvu": kvu_amt, "value": kvu_amt * KVU_VALUE, "vat": (kvu_amt * KVU_VALUE) * VAT_RATE,
             "status": status, "reason": reason, "action": action,
             "hash": hashlib.sha256(str(random.random()).encode()).hexdigest()}
    
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
    st.title("AFEG KVU – Governance, Regulatory Audit & Export")
    
    # MASTER TOP-LEVEL METRICS
    c1, c2, c3 = st.columns(3)
    total_kvu = sum(e['kvu'] for e in st.session_state.ledger_compliant + st.session_state.ledger_intercept)
    c1.metric("GROSS REVENUE", f"£{st.session_state.session_rev:,.2f}")
    c2.metric("VAT CAPTURE", f"£{(st.session_state.session_rev * VAT_RATE):,.2f}")
    c3.metric("VALIDATED KVUs", f"{total_kvu:,.0f}")

    tabs = st.tabs(["ACT 1: GATEWAY", "ACT 2: SURGE", "ACT 3: LEDGER VAULT", "ACT 4: 24H ENDURANCE"])

    with tabs[0]:
        st.header("ACT 1: GATEWAY (SEMANTIC FIREWALL)")
        q_in = st.text_input("AUDIT QUERY")
        if st.button("SUBMIT QUERY") and q_in:
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
        # ACT 2 SPECIFIC LIVE COUNTERS
        s1, s2, s3 = st.columns(3)
        surge_rev_metric = s1.empty()
        surge_vat_metric = s2.empty()
        surge_kvu_metric = s3.empty()
        
        # Initialize display
        surge_rev_metric.metric("SURGE REVENUE", "£0.00")
        surge_vat_metric.metric("SURGE VAT CAPTURED", "£0.00")
        surge_kvu_metric.metric("SURGE KVUs", "0")

        if st.button("EXECUTE SURGE"):
            t_win, logs = st.empty(), []
            running_surge_rev = 0.0
            running_surge_kvu = 0
            
            for i in range(15):
                q = f"SURGE_NODE_{random.randint(100,999)}"
                # High-volume batch for surge simulation
                batch_kvu = 85000 + random.randint(-10000, 10000)
                is_breach = random.random() > 0.9
                status = "INTERCEPT" if is_breach else "COMPLIANT"
                color = "#FF4B4B" if status == "INTERCEPT" else "#00FF41"
                
                commit_to_ledger(q, status, "Surge Integrity Check", "Verified", batch_kvu)
                
                # Increment Act 2 Local Counters
                batch_val = batch_kvu * KVU_VALUE
                running_surge_rev += batch_val
                running_surge_kvu += batch_kvu
                
                # Update UI in real-time
                surge_rev_metric.metric("SURGE REVENUE", f"£{running_surge_rev:,.2f}", delta=f"£{batch_val:,.2f}")
                surge_vat_metric.metric("SURGE VAT CAPTURED", f"£{(running_surge_rev * VAT_RATE):,.2f}", delta=f"£{(batch_val * VAT_RATE):,.2f}")
                surge_kvu_metric.metric("SURGE KVUs", f"{running_surge_kvu:,.0f}", delta=f"{batch_kvu:,.0f}")
                
                logs.insert(0, f"<span style='color:{color}'>[{datetime.now().strftime('%H:%M:%S')}] {q} | {status} | {batch_kvu:,.0f} KVU | VAT: £{(batch_val * VAT_RATE):,.2f}</span>")
                t_win.markdown(f'<div class="terminal">{"<br>".join(logs)}</div>', unsafe_allow_html=True)
                time.sleep(2.0) # Fixed pacing for 30s total
            st.rerun()

    with tabs[2]:
        st.header("ACT 3: LEDGER VAULT")
        search_query = st.text_input("Search Ledger by Query or Hash (Deep Diligence)", "")
        full_ledger = st.session_state.ledger_compliant + st.session_state.ledger_intercept
        
        if search_query:
            filtered_data = [e for e in full_ledger if search_query.lower() in e['query'].lower() or search_query.lower() in e['hash'].lower()]
            st.dataframe(filtered_data, use_container_width=True)
        else:
            st.dataframe(full_ledger, use_container_width=True)

    with tabs[3]:
        st.header("ACT 4: 24H ENDURANCE (HARDWARE-SYNC)")
        if st.button("START FORENSIC SCALING"):
            e_win, e_logs = st.empty(), []
            for i in range(24):
                throttle = get_hardware_throttle()
                time_label = f"{i:02d}:00"
                # Randomized national load curve
                hourly_kvu = (NATIONAL_DAILY_KVU / 24) * random.uniform(0.6, 1.4)
                commit_to_ledger(f"STRESS_{time_label}", "COMPLIANT", "Batch Load", "Audited", hourly_kvu)
                
                e_logs.insert(0, f"<span style='color:#00FF41'>[{time_label}] HARDWARE_SYNC: {100-psutil.cpu_percent()}% Idle | KVU: {hourly_kvu:,.0f} | Recovery: £{(hourly_kvu*KVU_VALUE*VAT_RATE):,.2f}</span>")
                e_win.markdown(f'<div class="terminal">{"<br>".join(e_logs)}</div>', unsafe_allow_html=True)
                time.sleep(throttle)
            st.rerun()

else:
    st.title("HM TREASURY // AUDIT EXPORT")
    # THE TREASURY ZIP EXPORT LOGIC
    if st.session_state.ledger_compliant or st.session_state.ledger_intercept:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "x") as audit_zip:
            audit_zip.writestr("LEDGER_COMPLIANT.json", json.dumps(st.session_state.ledger_compliant, indent=4))
            audit_zip.writestr("LEDGER_INTERCEPTED.json", json.dumps(st.session_state.ledger_intercept, indent=4))
        st.download_button("EXPORT TREASURY ZIP", data=buf.getvalue(), file_name="AFEG_AUDIT.zip")