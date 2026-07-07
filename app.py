# app.py (Updated with 5 Multi-Fault Scenarios)
import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="SteerMind AI Dashboard", layout="wide")

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agents.rootcause_agent import run_simple_diagnosis

# ==========================================
# 🎛️ SIDEBAR SCENARIO ENGINE
# ==========================================
st.sidebar.image("https://img.icons8.com/fluency/96/steering-wheel.png", width=60)
st.sidebar.title("SteerMind Configurator")
st.sidebar.markdown("---")

st.sidebar.subheader("📂 Ingest Field Log Data")
uploaded_file = st.sidebar.file_uploader("Upload custom CAN bus log:", type=["csv"])

st.sidebar.markdown("OR choose an engineering test matrix:")
selected_scenario = st.sidebar.selectbox(
    "Select Simulation Scenario:",
    [
        "Healthy Operations (Nominal Baseline)",
        "C1044 - EPS Motor Overcurrent Spike",
        "C1051 - Steering Angle Sensor Flatline",
        "C1093 - Inverter Thermal Runaway Fault",
        "C1221 - ECU Power Rail Under-Voltage Sag"
    ]
)

# Extract correct DTC for prompt framing vectors
if "C1044" in selected_scenario: extracted_dtc_code = "C1044"
elif "C1051" in selected_scenario: extracted_dtc_code = "C1051"
elif "C1093" in selected_scenario: extracted_dtc_code = "C1093"
elif "C1221" in selected_scenario: extracted_dtc_code = "C1221"
else: extracted_dtc_code = "HEALTHY_NOMINAL"

# ==========================================
# 📊 TIME-SERIES DATA MATRIX ROUTING
# ==========================================
if uploaded_file is not None:
    telemetry_df = pd.read_csv(uploaded_file)
    st.sidebar.success("✅ Custom upload running live.")
else:
    if "C1044" in selected_scenario: file_target = "data/can_overcurrent_fault.csv"
    elif "C1051" in selected_scenario: file_target = "data/can_flatline_fault.csv"
    elif "C1093" in selected_scenario: file_target = "data/can_thermal_fault.csv"
    elif "C1221" in selected_scenario: file_target = "data/can_voltagesag_fault.csv"
    else: file_target = "data/can_healthy_log.csv"
    
    if os.path.exists(file_target):
        telemetry_df = pd.read_csv(file_target)
    else:
        # Failsafe array layout matrix
        telemetry_df = pd.DataFrame({"Time": np.linspace(0,10,200), "Motor_Current_Amps": 5.0, "Steering_Angle_Deg": 0.0, "Inverter_Temp_C": 45.0})

# ==========================================
# 🖥️ APPLICATION CORE INTERACTIVE LAYOUT
# ==========================================
st.title("🤖 SteerMind AI: Multi-Agent Chassis Diagnostics")
st.markdown("---")

# Metrics KPIs Block Rows
k1, k2, k3 = st.columns(3)
k1.metric("Target Bus Architecture", "CAN-FD Channel A")
k2.metric("Target Fault Register ID", extracted_dtc_code)

has_gemini = bool(os.getenv("GEMINI_API_KEY"))
has_openai = bool(os.getenv("OPENAI_API_KEY"))
active_backend = "GPT-4o Mini (OpenAI)" if (has_openai and not has_gemini) else "Gemini 2.5 Flash (Google)"
k3.metric("Active Core Gateway Driver", active_backend)

st.markdown("---")

# Synchronized Plotly Multi-Axis Render Engine
st.subheader("📈 Interactive Multi-Channel Sensor Analytics")
fig = go.Figure()
fig.add_trace(go.Scatter(x=telemetry_df["Time"], y=telemetry_df["Motor_Current_Amps"], name="Current (Amps)", line=dict(color="#FF4B4B")))
fig.add_trace(go.Scatter(x=telemetry_df["Time"], y=telemetry_df["Steering_Angle_Deg"], name="Angle (Deg)", line=dict(color="#0068C9")))
if "Inverter_Temp_C" in telemetry_df.columns:
    fig.add_trace(go.Scatter(x=telemetry_df["Time"], y=telemetry_df["Inverter_Temp_C"], name="Temp (°C)", line=dict(color="#29B5E8")))

fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=1.05))
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Execution trigger connection wrapper
if st.button("🚀 Trigger SteerMind Diagnostic Engine", type="primary"):
    with st.spinner("Compiling contextual window state vectors..."):
        
        # Calculate heuristics for prompt ingestion context summary block
        max_amps = float(telemetry_df.iloc[:, 1].max())
        max_temp = float(telemetry_df.iloc[:, 3].max()) if telemetry_df.shape[1] > 3 else 0.0
        
        telemetry_string_payload = f"""
        Ingested Signal Log Stats:
        - Max Motor Draw: {max_amps:.2f} Amps
        - Max Inverter Thermal Reading: {max_temp:.2f} °C
        - Raw Sensor Record Dimensions: {len(telemetry_df)} frames
        """
        
        # Call the unified agent file
        agent_raw_response = run_simple_diagnosis(
            fault_code=extracted_dtc_code,
            metric_telemetry=telemetry_string_payload
        )
        
        st.success("Analysis Execution Cycle Complete!")
        st.markdown("### 📋 Root Cause Synthesis Report Card")
        st.info(agent_raw_response)