import streamlit as st
import time, hashlib, json, random, io, zipfile
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

def calculate_kvu_split(base_kvu, query):
    """Calculates the 3-way split of work."""
    q_low = query.lower()
    if any(w in q_low for w in ["why", "how", "explain"]):
        inf, res, mem = base_kvu * 0.4, base_kvu * 0.5, base_kvu * 0.1
    else:
        inf, res, mem = base_kvu * 0.7, base_kvu * 0.1, base_kvu * 0.2
    return round(inf, 2), round(res, 2), round(mem, 2)

# ------------------ STATE ------------------
if "ledger_compliant" not in st.session_state: st.session_state.ledger_compliant = []
if "ledger_intercept" not in st.session_state: st.session_state.ledger_intercept = []
if "session_rev" not in st.session_state: st.session_state.session_rev = 0.0
if "current" not in st.session_state: st.session_state.current = None

def commit_to_ledger(query, status, reason, action, kvu_amt, split):
    entry = {"query": query, "timestamp": datetime.now().strftime("%H:%M:%S"),
             "kvu": kvu_amt, "inference": split[0], "reasoning": split[1], "memory": split[2],
             "value": kvu_amt * KVU_VALUE, "vat": (kvu_amt * KVU_VALUE) * VAT_RATE,
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
    
    # Global Summary
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
                commit_to_ledger(q_in, "INTERCEPT", r1, "Blocked", 0, (0,0,0))
            else:
                kvu = 650 + (len(q_in) * 5)
                split = calculate_kvu_split(kvu, q_in)
                safe_out, r2 = pass2_output_scan("Simulated Response")
                status = "COMPLIANT" if safe_out else "INTERCEPT"
                action = "Delivered" if safe_out else ("Flagged" if gov_mode=="Demo" else "Blocked")
                commit_to_ledger(q_in, status, r2, action, kvu, split)
            st.rerun()
        
        if st.session_state.current:
            cur = st.session_state.current
            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("INFERENCE", f"{cur['inference']} KVU")
            sc2.metric("REASONING", f"{cur['reasoning']} KVU")
            sc3.metric("MEMORY", f"{cur['memory']} KVU")
            st.json(cur)

    with tabs[1]:
        st.header("ACT 2: NATIONAL SURGE (30s LIVE)")
        # Act 2 Specific Live Workload Counters
        s1, s2, s3 = st.columns(3)
        s_inf = s1.empty(); s_res = s2.empty(); s_mem = s3.empty()
        
        if st.button("EXECUTE SURGE"):
            t_win, logs = st.empty(), []
            r_inf, r_res, r_mem = 0, 0, 0
            for i in range(15):
                q = f"SURGE_NODE_{random.randint(100,999)}"
                batch_kvu = 65000 + random.randint(-5000, 5000)
                split = calculate_kvu_split(batch_kvu, "Complex surge reasoning")
                
                is_breach = random.random() > 0.85
                status = "INTERCEPT" if is_breach else "COMPLIANT"
                color = "#FF4B4B" if status == "INTERCEPT" else "#00FF41"
                
                commit_to_ledger(q, status, "Surge Check", "Verified", batch_kvu, split)
                
                # Update Act 2 Triple Counters
                r_inf += split[0]; r_res += split[1]; r_mem += split[2]
                s_inf.metric("INFERENCE (TOTAL)", f"{r_inf:,.0f}")
                s_res.metric("REASONING (TOTAL)", f"{r_res:,.0f}")
                s_mem.metric("MEMORY (TOTAL)", f"{r_mem:,.0f}")
                
                logs.insert(0, f"<span style='color:{color}'>[{datetime.now().strftime('%H:%M:%S')}] {q} | {status} | {batch_kvu:,.0f} KVU</span>")
                t_win.markdown(f'<div class="terminal">{"<br>".join(logs)}</div>', unsafe_allow_html=True)
                time.sleep(2.0)
            st.rerun()

    with tabs[2]:
        st.header("ACT 3: LEDGER VAULT")
        search_query = st.text_input("Search Ledger by Query or Hash", "")
        full_ledger = st.session_state.ledger_compliant + st.session_state.ledger_intercept
        if search_query:
            filtered_data = [e for e in full_ledger if search_query.lower() in e['query'].lower() or search_query.lower() in e['hash'].lower()]
            st.dataframe(filtered_data, use_container_width=True)
        else:
            st.dataframe(full_ledger, use_container_width=True)

    with tabs[3]:
        st.header("ACT 4: 24H ENDURANCE (2m FORENSIC SIMULATION)")
        e1, e2, e3 = st.columns(3)
        e_rev = e1.empty(); e_vat = e2.empty(); e_kvu = e3.empty()
        
        if st.button("START 24H AUDIT"):
            e_win, e_logs = st.empty(), []
            total_e_rev, total_e_kvu = 0.0, 0
            for i in range(24):
                time_label = f"{i:02d}:00"
                hourly_kvu = (NATIONAL_DAILY_KVU / 24) * random.uniform(0.7, 1.3)
                split = calculate_kvu_split(hourly_kvu, "Bulk audit")
                commit_to_ledger(f"STRESS_{time_label}", "COMPLIANT", "Batch", "Audited", hourly_kvu, split)
                
                total_e_rev += (hourly_kvu * KVU_VALUE)
                total_e_kvu += hourly_kvu
                e_rev.metric("AUDIT REVENUE", f"£{total_e_rev:,.2f}")
                e_vat.metric("AUDIT VAT", f"£{(total_e_rev * VAT_RATE):,.2f}")
                e_kvu.metric("AUDIT KVUs", f"{total_e_kvu:,.0f}")
                
                e_logs.insert(0, f"<span style='color:#00FF41'>[{time_label}] FORENSIC_SYNC | {hourly_kvu:,.0f} KVU | VAT: £{(hourly_kvu * KVU_VALUE * VAT_RATE):,.2f}</span>")
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