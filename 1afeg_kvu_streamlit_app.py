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

# ------------------ STATE ------------------
if "ledger_compliant" not in st.session_state: st.session_state.ledger_compliant = []
if "ledger_intercept" not in st.session_state: st.session_state.ledger_intercept = []
if "session_rev" not in st.session_state: st.session_state.session_rev = 0.0
if "current" not in st.session_state: st.session_state.current = None

def commit_to_ledger(query, status, reason, action, inf, res, mem):
    total_kvu = inf + res + mem
    entry = {"query": query, "timestamp": datetime.now().strftime("%H:%M:%S"),
             "inf": inf, "res": res, "mem": mem, "kvu": total_kvu,
             "value": total_kvu * KVU_VALUE, "vat": (total_kvu * KVU_VALUE) * VAT_RATE,
             "status": status, "reason": reason, "action": action,
             "hash": hashlib.sha256(str(random.random()).encode()).hexdigest()}
    
    if status == "COMPLIANT":
        st.session_state.ledger_compliant.append(entry)
    else:
        st.session_state.ledger_intercept.append(entry)
    
    st.session_state.session_rev += entry["value"]
    st.session_state.current = entry
    return entry

# ------------------ UI ------------------
st.set_page_config(page_title="AFEG v7 Master Prototype", layout="wide")
st.sidebar.title("AFEG v7")
portal = st.sidebar.selectbox("PORTAL ACCESS", ["CEO Gateway", "Treasury Export Portal"])
gov_mode = st.sidebar.radio("Governance Mode", ["Demo", "Live"])

st.markdown("""<style>.terminal {background-color:#000; padding:15px; font-family:monospace; height:400px; overflow-y:scroll; border:1px solid #444;}</style>""", unsafe_allow_html=True)

if portal == "CEO Gateway":
    st.title("AFEG KVU – Governance, Regulatory Audit & Export")
    
    # MASTER METRICS (Linked to Act 4)
    m1, m2, m3 = st.columns(3)
    def update_master_metrics():
        t_kvu = sum(e['kvu'] for e in st.session_state.ledger_compliant + st.session_state.ledger_intercept)
        m1.metric("GROSS REVENUE", f"£{st.session_state.session_rev:,.2f}")
        m2.metric("VAT CAPTURE", f"£{(st.session_state.session_rev * VAT_RATE):,.2f}")
        m3.metric("VALIDATED KVUs", f"{t_kvu:,.0f}")

    update_master_metrics()

    tabs = st.tabs(["ACT 1: GATEWAY", "ACT 2: SURGE", "ACT 3: LEDGER VAULT", "ACT 4: 24H ENDURANCE", "ACT 5: VALUATION ROI"])

    with tabs[0]:
        st.header("ACT 1: GATEWAY (SEMANTIC FIREWALL)")
        q_in = st.text_input("AUDIT QUERY")
        if st.button("SUBMIT QUERY") and q_in:
            safe_in, r1 = pass1_input_scan(q_in)
            if not safe_in:
                commit_to_ledger(q_in, "INTERCEPT", r1, "Blocked", 0, 0, 0)
            else:
                inf, res, mem = 400.0, 200.0, 50.0
                safe_out, r2 = pass2_output_scan("Simulated Response")
                status = "COMPLIANT" if safe_out else "INTERCEPT"
                action = "Delivered" if safe_out else ("Flagged" if gov_mode=="Demo" else "Blocked")
                commit_to_ledger(q_in, status, r2, action, inf, res, mem)
            st.rerun()
            
        if st.session_state.current:
            cur = st.session_state.current
            g1, g2, g3 = st.columns(3)
            g1.metric("INFERENCE", f"{cur['inf']:.0f} KVU")
            g2.metric("REASONING", f"{cur['res']:.0f} KVU")
            g3.metric("MEMORY", f"{cur['mem']:.0f} KVU")
            st.json(cur)

    with tabs[1]:
        st.header("ACT 2: NATIONAL SURGE (30s LIVE)")
        s1, s2, s3 = st.columns(3)
        inf_m = s1.empty(); res_m = s2.empty(); mem_m = s3.empty()
        
        if st.button("EXECUTE SURGE"):
            t_win, logs = st.empty(), []
            r_inf, r_res, r_mem = 0, 0, 0
            for i in range(15):
                q = f"SURGE_NODE_{random.randint(100,999)}"
                bi, br, bm = 50000, 25000, 10000
                commit_to_ledger(q, "COMPLIANT", "Surge", "Verified", bi, br, bm)
                r_inf += bi; r_res += br; r_mem += bm
                
                inf_m.metric("INFERENCE", f"{r_inf:,.0f} KVU")
                res_m.metric("REASONING", f"{r_res:,.0f} KVU")
                mem_m.metric("MEMORY", f"{r_mem:,.0f} KVU")
                update_master_metrics()
                
                logs.insert(0, f"<span style='color:#00FF41'>[{datetime.now().strftime('%H:%M:%S')}] {q} | COMPLIANT | +85k KVU</span>")
                t_win.markdown(f'<div class="terminal">{"<br>".join(logs)}</div>', unsafe_allow_html=True)
                time.sleep(2.0)
            st.rerun()

    with tabs[2]:
        st.header("ACT 3: LEDGER VAULT")
        search = st.text_input("Search Ledger (SHA-256 Integrity Check)")
        full = st.session_state.ledger_compliant + st.session_state.ledger_intercept
        if search:
            full = [e for e in full if search.lower() in e['query'].lower() or search.lower() in e['hash'].lower()]
        st.dataframe(full, use_container_width=True)

    with tabs[3]:
        st.header("ACT 4: 24H ENDURANCE (SYNCED SIMULATION)")
        if st.button("START FORENSIC SCALING"):
            e_win, e_logs = st.empty(), []
            for i in range(24):
                time_label = f"{i:02d}:00"
                h_kvu = (NATIONAL_DAILY_KVU / 24) * random.uniform(0.6, 1.4)
                # Split the randomized hourly load into categories
                commit_to_ledger(f"STRESS_{time_label}", "COMPLIANT", "Batch", "Audited", h_kvu/3, h_kvu/3, h_kvu/3)
                
                # Update top-level metrics in real-time during the loop
                update_master_metrics()
                
                e_logs.insert(0, f"<span style='color:#00FF41'>[{time_label}] SYNC | KVU: {h_kvu:,.0f} | VAT: £{(h_kvu*KVU_VALUE*VAT_RATE):,.2f}</span>")
                e_win.markdown(f'<div class="terminal">{"<br>".join(e_logs)}</div>', unsafe_allow_html=True)
                time.sleep(0.5)
            st.rerun()

    with tabs[4]:
        st.header("ACT 5: EXECUTIVE VALUATION ROI")
        v_col1, v_col2 = st.columns(2)
        with v_col1:
            st.subheader("Risk Mitigation Analysis")
            # Based on SHA-256 Evidence Integrity Logic
            dispute_risk = (sum(e['kvu'] for e in st.session_state.ledger_compliant) * 0.01) * 2.0
            st.metric("UNMITIGATED DISPUTE RISK", f"£{dispute_risk:,.2f}", delta="Critical", delta_color="inverse")
            st.write("Projected legal cost without Evidence Verification Engine (EV424).")
        with v_col2:
            st.subheader("AFEG Settlement Efficiency")
            savings = dispute_risk * 0.92
            st.metric("PROJECTED ANNUAL SAVINGS", f"£{savings:,.2f}", delta="AFEG SHIELD ACTIVE")
            st.write("Mitigation of legal exposure via SHA-256 Hashed Reproducibility.")

else:
    st.title("HM TREASURY // AUDIT EXPORT")
    if st.session_state.ledger_compliant or st.session_state.ledger_intercept:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "x") as audit_zip:
            audit_zip.writestr("LEDGER_COMPLIANT.json", json.dumps(st.session_state.ledger_compliant, indent=4))
            audit_zip.writestr("LEDGER_INTERCEPTED.json", json.dumps(st.session_state.ledger_intercept, indent=4))
        st.download_button("EXPORT TREASURY ZIP", data=buf.getvalue(), file_name="AFEG_AUDIT.zip")