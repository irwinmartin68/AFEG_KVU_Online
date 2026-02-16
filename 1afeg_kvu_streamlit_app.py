# AFEG KVU – Professional Online Dashboard (All-in-One)
# Save as: 1afeg_kvu_app.py
# Run: streamlit run 1afeg_kvu_app.py

import streamlit as st
import time, hashlib, json, io, zipfile, random
from datetime import datetime

# ------------------ CONFIG ------------------
KVU_VALUE = 0.001
NORMALIZATION_FACTOR = 0.01
VAT_RATE = 0.20
SIMULATION_STEPS = 50

# ------------------ SESSION STATE ------------------
for key, default in [("ledger", []), ("session_revenue", 0.0), ("latency", 0.0), 
                     ("view","All"), ("text_size",16)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ------------------ KVU SIMULATION ------------------
def simulate_kvu(query:str):
    base = max(len(query),10)
    inference = base * random.uniform(2.3,2.7)
    memory = base * random.uniform(1.7,1.9)
    reasoning = base * random.uniform(2.1,2.3)
    raw_total = inference+memory+reasoning
    normalized_total = raw_total*NORMALIZATION_FACTOR
    value = normalized_total*KVU_VALUE
    vat = value*VAT_RATE
    latency=random.uniform(0.1,0.5)
    return {
        "inference":round(inference,2),
        "memory":round(memory,2),
        "reasoning":round(reasoning,2),
        "raw_total":round(raw_total,2),
        "normalized_total":round(normalized_total,4),
        "value":round(value,4),
        "vat":round(vat,4),
        "latency":round(latency,3)
    }

# ------------------ LEDGER & HASH ------------------
def hash_entry(entry:dict):
    return hashlib.sha256(json.dumps(entry,sort_keys=True).encode()).hexdigest()

def add_to_ledger(query,result):
    entry = result.copy()
    entry.update({"query":query,"timestamp":datetime.now().isoformat(),"hash":hash_entry(result)})
    st.session_state.ledger.append(entry)
    st.session_state.session_revenue += entry["value"]
    st.session_state.latency += entry["latency"]

def generate_audit_zip():
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as zf:
        ledger_text="\n".join([json.dumps(e) for e in st.session_state.ledger])
        zf.writestr("AFEG_IMMUTABLE_AUDIT_LEDGER.txt",ledger_text)
    buf.seek(0)
    return buf

# ------------------ UI SETUP ------------------
st.set_page_config(page_title="AFEG KVU Dashboard",layout="wide")
st.title("AFEG KVU – Full Professional Online Simulation")
st.caption("Athena Fabric v4 Simulation | Live KVU Tracking")

# Sidebar controls
st.sidebar.title("Controls")
st.session_state.view = st.sidebar.radio("Metric View", ["All","Inference","Memory","Reasoning"])
st.session_state.text_size = st.sidebar.slider("Text Size",12,24,16)

# Tabs for Acts
tab1,tab2,tab3,tab4=st.tabs(["Act1: Query","Act2: Simulation","Act3: Ledger","Act4: Treasury"])

# ------------------ ACT1: QUERY ------------------
with tab1:
    st.header("Submit a Live Query")
    query = st.text_input("Enter your question for KVU calculation:")
    if st.button("Submit Query",key="submit"):
        if query:
            result=simulate_kvu(query)
            add_to_ledger(query,result)
            st.success("Query submitted!")
            st.json(result)

# ------------------ ACT2: SIMULATION ------------------
with tab2:
    st.header("Run Demo Simulation")
    if st.button("Run Simulation"):
        progress=st.progress(0)
        for i in range(SIMULATION_STEPS):
            demo_query=f"Demo Query {i+1}"
            result=simulate_kvu(demo_query)
            add_to_ledger(demo_query,result)
            progress.progress((i+1)/SIMULATION_STEPS)
            time.sleep(0.05)
        st.success(f"Simulation finished ({SIMULATION_STEPS} steps)")

    if st.session_state.ledger:
        st.subheader("Live Metrics")
        total_inference=sum(e["inference"] for e in st.session_state.ledger)
        total_memory=sum(e["memory"] for e in st.session_state.ledger)
        total_reasoning=sum(e["reasoning"] for e in st.session_state.ledger)
        total_kvus=sum(e["normalized_total"] for e in st.session_state.ledger)
        total_value=sum(e["value"] for e in st.session_state.ledger)
        total_vat=sum(e["vat"] for e in st.session_state.ledger)
        total_latency=sum(e["latency"] for e in st.session_state.ledger)

        if st.session_state.view in ["All","Inference"]:
            st.markdown(f"<p style='font-size:{st.session_state.text_size}px'>Inference KVU: {round(total_inference,2)}</p>",unsafe_allow_html=True)
        if st.session_state.view in ["All","Memory"]:
            st.markdown(f"<p style='font-size:{st.session_state.text_size}px'>Memory KVU: {round(total_memory,2)}</p>",unsafe_allow_html=True)
        if st.session_state.view in ["All","Reasoning"]:
            st.markdown(f"<p style='font-size:{st.session_state.text_size}px'>Reasoning KVU: {round(total_reasoning,2)}</p>",unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:{st.session_state.text_size}px'>Normalized KVUs: {round(total_kvus,4)}</p>",unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:{st.session_state.text_size}px'>Total Value (£): {round(total_value,4)}</p>",unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:{st.session_state.text_size}px'>VAT (£): {round(total_vat,4)}</p>",unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:{st.session_state.text_size}px'>Total Latency (s): {round(total_latency,3)}</p>",unsafe_allow_html=True)

# ------------------ ACT3: LEDGER ------------------
with tab3:
    st.header("Immutable Audit Ledger")
    if st.session_state.ledger:
        st.write("Last 10 entries")
        for e in st.session_state.ledger[-10:]:
            st.json(e)

# ------------------ ACT4: TREASURY ------------------
with tab4:
    st.header("Treasury Vault")
    if st.session_state.ledger:
        st.download_button(
            label="Download Secure Audit ZIP",
            data=generate_audit_zip(),
            file_name="AFEG_IMMUTABLE_AUDIT_LEDGER.zip",
            mime="application/zip"
        )