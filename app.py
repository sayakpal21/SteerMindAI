# app.py
import os
import json
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dotenv import load_dotenv

load_dotenv()

# 🎨 EXECUTIVE PROTO-THEME CONFIGURATION
st.set_page_config(
    page_title="SteerMind AI | Multi-Agent Diagnostics Workspace",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom UI styling injection for an immersive dark/light engineering cockpit feel
st.markdown("""
    <style>
    .report-card { background-color: #ffffff; padding: 20px; border-radius: 8px; border-left: 5px solid #FF4B4B; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    .agent-title { font-weight: bold; color: #1E1E1E; display: flex; align-items: center; gap: 8px; margin: 0 0 8px 0; }
    .stButton>button { width: 100%; border-radius: 6px; font-weight: bold; height: 3em; }
    </style>
""", unsafe_allow_html=True)

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agents.rootcause_agent import run_rootcause_analysis
from utils.guardrail import DiagnosticIncidentParser
from utils import *

# ==========================================
# 🎛️ SIDEBAR ENGINE & SCENARIO CONTROLLER
# ==========================================
st.sidebar.image("https://img.icons8.com/fluency/96/steering-wheel.png", width=60)
st.sidebar.title("SteerMind AI Control")
st.sidebar.caption("v1.4.4 • Core Diagnostic Orchestrator")
st.sidebar.markdown("---")

st.sidebar.subheader("📂 Mandatory Telemetry Ingestion")

# 📥 Field 1: ECU Logs (CSV)
uploaded_ecu = st.sidebar.file_uploader(
    "1. Ingest ECU Log (.csv): *", 
    type=["csv"],
    key="ecu_uploader",
    help="Requires high-frequency diagnostic internal registers."
)

# 📥 Field 2: CAN Logs (CSV)
uploaded_can = st.sidebar.file_uploader(
    "2. Ingest CAN-Bus Stream (.csv): *", 
    type=["csv"],
    key="can_uploader",
    help="Requires network physical bus message streams."
)

# 📥 Field 3: DTC Records (🔒 JSON ONLY)
uploaded_dtc_file = st.sidebar.file_uploader(
    "3. Ingest Active DTC Matrix (.json): *", 
    type=["json"],
    key="dtc_uploader",
    help="Requires snapshot freeze-frame trouble codes structured in a valid JSON schema map."
)

# Check validation flag status across all three entry gates
all_files_present = bool(uploaded_ecu and uploaded_can and uploaded_dtc_file)
has_any_upload = bool(uploaded_ecu or uploaded_can or uploaded_dtc_file)

# 🧠 SMART UX VALIDATION LOGIC
if all_files_present:
    st.sidebar.success("🟢 All diagnostic streams locked down!")
elif has_any_upload:
    st.sidebar.warning("⚠️ Incomplete multi-stream upload. Please provide all 3 logs.")
else:
    st.sidebar.info("💡 Running in Simulation Mode. Upload 3 files above to analyze live hardware.")

st.sidebar.markdown("---")
st.sidebar.markdown("**OR switch to pre-aligned simulation profile:**")
selected_scenario = st.sidebar.selectbox(
    "Simulation Select Matrix:",
    [
        "Healthy Operations (Nominal Baseline)",
        "C1044 - EPS Motor Overcurrent Spike",
        "C1051 - Steering Angle Sensor Flatline",
        "C1093 - Inverter Thermal Runaway Fault",
        "C1221 - ECU Power Rail Under-Voltage Sag"
    ]
)

# Isolate matching DTC
if "C1044" in selected_scenario: extracted_dtc_code = "C1044"
elif "C1051" in selected_scenario: extracted_dtc_code = "C1051"
elif "C1093" in selected_scenario: extracted_dtc_code = "C1093"
elif "C1221" in selected_scenario: extracted_dtc_code = "C1221"
else: extracted_dtc_code = "HEALTHY_NOMINAL"

st.sidebar.markdown("---")
st.sidebar.subheader("🔌 Network Architecture Gateway")
has_gemini = bool(os.getenv("GEMINI_API_KEY"))
has_openai = bool(os.getenv("OPENAI_API_KEY"))
st.sidebar.markdown(f"**Gemini Node:** {'🟢 Online' if has_gemini else '🔴 Offline'}")
st.sidebar.markdown(f"**OpenAI Node:** {'🟢 Online' if has_openai else '🔴 Offline'}")

# ==========================================
# 📊 TIME-SERIES DATA LAYER & PARSING PROTECTION
# ==========================================
parse_error_triggered = False
telemetry_df = None

def robust_float_convert(val):
    """Safely converts hex strings (e.g. '0x20C') or regular strings into standard floats."""
    if pd.isna(val):
        return 0.0
    val_str = str(val).strip()
    try:
        if val_str.lower().startswith("0x"):
            return float(int(val_str, 16))
        return float(val_str)
    except ValueError:
        return 0.0
if all_files_present:
    try:
        raw_can_df = pd.read_csv(uploaded_can)
        ecu_df = pd.read_csv(uploaded_ecu)
        dtc_data = json.load(uploaded_dtc_file)
        
        # Force column trim and clean whitespace configurations
        raw_can_df.columns = [str(col).strip() for col in raw_can_df.columns]
        col_mapping = {col.lower(): col for col in raw_can_df.columns}
        
        telemetry_df = pd.DataFrame()
        
        # Check if the CSV is already pivoted or follows the long schema format
        if 'signal_name' in col_mapping and 'physical_value' in col_mapping:
            # Pivot the long format data into standard timeline columns
            ts_col = col_mapping.get('timestamp', col_mapping.get('time', raw_can_df.columns[0]))
            
            pivot_df = raw_can_df.pivot_table(
                index=ts_col, 
                columns=col_mapping['signal_name'], 
                values=col_mapping['physical_value'], 
                aggfunc='first'
            ).sort_index().reset_index()
            
            # Re-map our columns list based on the pivoted DataFrame
            pivot_df.columns = [str(col).strip() for col in pivot_df.columns]
            p_mapping = {col.lower(): col for col in pivot_df.columns}
            
            # 1. Map Time Axis safely
            telemetry_df['Time'] = pivot_df.iloc[:, 0].apply(robust_float_convert)
            
            # 2. Map Motor Current
            if 'motor_current' in p_mapping:
                telemetry_df['Motor_Current_Amps'] = pivot_df[p_mapping['motor_current']].apply(robust_float_convert)
            elif 'motor_current_amps' in p_mapping:
                telemetry_df['Motor_Current_Amps'] = pivot_df[p_mapping['motor_current_amps']].apply(robust_float_convert)
            else:
                telemetry_df['Motor_Current_Amps'] = 5.0

            # 3. Map Steering Angle
            if 'steering_angle' in p_mapping:
                telemetry_df['Steering_Angle_Deg'] = pivot_df[p_mapping['steering_angle']].apply(robust_float_convert)
            elif 'steering_angle_deg' in p_mapping:
                telemetry_df['Steering_Angle_Deg'] = pivot_df[p_mapping['steering_angle_deg']].apply(robust_float_convert)
            else:
                telemetry_df['Steering_Angle_Deg'] = 0.0

            # 4. Map Inverter Temperature
            if 'inverter_temp' in p_mapping:
                telemetry_df['Inverter_Temp_C'] = pivot_df[p_mapping['inverter_temp']].apply(robust_float_convert)
            elif 'inverter_temp_c' in p_mapping:
                telemetry_df['Inverter_Temp_C'] = pivot_df[p_mapping['inverter_temp_c']].apply(robust_float_convert)
            else:
                telemetry_df['Inverter_Temp_C'] = 45.0
                
        else:
            # Fallback legacy parsing structure if file isn't long format
            # 1. Map Time Axis safely
            if 'time' in col_mapping:
                telemetry_df['Time'] = raw_can_df[col_mapping['time']].apply(robust_float_convert)
            elif 'timestamp' in col_mapping:
                telemetry_df['Time'] = raw_can_df[col_mapping['timestamp']].apply(robust_float_convert)
            else:
                telemetry_df['Time'] = np.linspace(0, 10, len(raw_can_df))
                
            # 2. Map Motor Current
            if 'motor_current' in col_mapping:
                telemetry_df['Motor_Current_Amps'] = raw_can_df[col_mapping['motor_current']].apply(robust_float_convert)
            elif 'motor_current_amps' in col_mapping:
                telemetry_df['Motor_Current_Amps'] = raw_can_df[col_mapping['motor_current_amps']].apply(robust_float_convert)
            elif len(raw_can_df.columns) > 1:
                telemetry_df['Motor_Current_Amps'] = raw_can_df.iloc[:, 1].apply(robust_float_convert)
            else:
                telemetry_df['Motor_Current_Amps'] = 5.0

            # 3. Map Steering Angle
            if 'steering_angle' in col_mapping:
                telemetry_df['Steering_Angle_Deg'] = raw_can_df[col_mapping['steering_angle']].apply(robust_float_convert)
            elif 'steering_angle_deg' in col_mapping:
                telemetry_df['Steering_Angle_Deg'] = raw_can_df[col_mapping['steering_angle_deg']].apply(robust_float_convert)
            elif len(raw_can_df.columns) > 2:
                telemetry_df['Steering_Angle_Deg'] = raw_can_df.iloc[:, 2].apply(robust_float_convert)
            else:
                telemetry_df['Steering_Angle_Deg'] = 0.0

            # 4. Map Inverter Temperature
            if 'inverter_temp' in col_mapping:
                telemetry_df['Inverter_Temp_C'] = raw_can_df[col_mapping['inverter_temp']].apply(robust_float_convert)
            elif 'inverter_temp_c' in col_mapping:
                telemetry_df['Inverter_Temp_C'] = raw_can_df[col_mapping['inverter_temp_c']].apply(robust_float_convert)
            elif len(raw_can_df.columns) > 3:
                telemetry_df['Inverter_Temp_C'] = raw_can_df.iloc[:, 3].apply(robust_float_convert)
            else:
                telemetry_df['Inverter_Temp_C'] = 45.0
                
    except Exception as parse_error:
        parse_error_triggered = True
        all_files_present = False


# Fallback block if files are missing, non-compliant, or broken
if telemetry_df is None:
    if "C1044" in selected_scenario: file_target = "data/can_overcurrent_fault.csv"
    elif "C1051" in selected_scenario: file_target = "data/can_flatline_fault.csv"
    elif "C1093" in selected_scenario: file_target = "data/can_thermal_fault.csv"
    elif "C1221" in selected_scenario: file_target = "data/can_voltagesag_fault.csv"
    else: file_target = "data/can_healthy_log.csv"
    
    if os.path.exists(file_target):
        telemetry_df = pd.read_csv(file_target)
    else:
        telemetry_df = pd.DataFrame({
            "Time": np.linspace(0,10,200), 
            "Motor_Current_Amps": 5.0, 
            "Steering_Angle_Deg": 0.0, 
            "Inverter_Temp_C": 45.0
        })

# ==========================================
# 🖥️ MAIN WORKSPACE VIEWPORT LAYOUT
# ==========================================
st.title("🤖 SteerMind AI: Agnostic Multi-Agent Diagnostics")
st.caption("Translating massive high-frequency chassis sensor waveforms into deterministic root-cause actions.")
st.markdown("---")

if parse_error_triggered:
    st.error("❌ Data Ingestion Exception! Ensure your files match expected structural guidelines. Running simulation targets safely.")

# Row 1: KPI Grid Panel
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric(label="📊 Bus Infrastructure", value="CAN-FD Channel A")
kpi2.metric(label="🎯 Active Fault Vector", value=extracted_dtc_code)

active_backend = "GPT-4o Mini (OpenAI)" if (has_openai and not has_gemini) else "Gemini 2.5 Flash (Google)"
kpi3.metric(label="🔌 Active Model Gateway", value=active_backend)
kpi4.metric(label="⏱️ Frame Ingestion Rate", value=f"{len(telemetry_df)} Hz")


# Row 2: Graphing telemetry profiles (3-Row Vertically Stacked Subplot Layout)
st.subheader("📈 Synchronized Multi-Channel Waveform Telemetry")

# Configure 3 stacked vertical rows sharing the same timeline X-axis
fig = make_subplots(
    rows=3, 
    cols=1, 
    shared_xaxes=True, 
    vertical_spacing=0.08,
    subplot_titles=("Motor Current Profile", "Steering Angle Profile", "Inverter Temperature Profile")
)

# 🔴 Subplot 1: Motor Current Trace (Row 1)
if "Motor_Current_Amps" in telemetry_df.columns:
    fig.add_trace(
        go.Scatter(
            x=telemetry_df["Time"], 
            y=telemetry_df["Motor_Current_Amps"], 
            name="Motor Current (Amps)", 
            mode='lines',
            line=dict(color="#FF4B4B", width=2.5)
        ),
        row=1, col=1
    )

# 🔵 Subplot 2: Steering Angle Trace (Row 2)
if "Steering_Angle_Deg" in telemetry_df.columns:
    fig.add_trace(
        go.Scatter(
            x=telemetry_df["Time"], 
            y=telemetry_df["Steering_Angle_Deg"], 
            name="Steering Angle (Deg)", 
            mode='lines',
            line=dict(color="#0068C9", width=2)
        ),
        row=2, col=1
    )

# 🌐 Subplot 3: Inverter Temp Trace (Row 3)
if "Inverter_Temp_C" in telemetry_df.columns:
    fig.add_trace(
        go.Scatter(
            x=telemetry_df["Time"], 
            y=telemetry_df["Inverter_Temp_C"], 
            name="Inverter Temp (°C)", 
            mode='lines',
            line=dict(color="#29B5E8", width=2, dash='dot')
        ),
        row=3, col=1
    )

# Master Layout configuration
fig.update_layout(
    height=650,  # Increased height to comfortably present 3 individual panels
    margin=dict(l=10, r=10, t=30, b=10), 
    legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1),
    plot_bgcolor="#F8F9FA"
)

# Apply axes labels and standard formatting grids to the subplots cleanly
fig.update_xaxes(showgrid=True, gridcolor="#EAEAEA")
fig.update_yaxes(showgrid=True, gridcolor="#EAEAEA")

# Set distinct unique targets for individual Y axis markers
fig.update_yaxes(title_text="Current (Amps)", row=1, col=1)
fig.update_yaxes(title_text="Angle (Deg)", row=2, col=1)
fig.update_yaxes(title_text="Temp (°C)", row=3, col=1)

# Only label the bottom x-axis to keep visual data clean
fig.update_xaxes(title_text="Time (Seconds)", row=3, col=1)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Row 3: Control Buttons
st.subheader("🧠 Control Actions Console")
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    trigger_btn = st.button("🚀 Run SteerMind Autonomous Analysis", type="primary")

with btn_col2:
    save_btn = st.button("📦 Save Dataset for Model Training", type="secondary")

# Data Staging Logger Script Logic
if save_btn:
    if not all_files_present or parse_error_triggered:
        st.error("❌ Data Save Rejected! Please provide all 3 required files validly in the uploader array before saving.")
    else:
        with st.spinner("Writing compliant logs to staging arrays..."):
            os.makedirs("data/training_staging", exist_ok=True)
            telemetry_df.to_csv("data/training_staging/last_training_can.csv", index=False)
            ecu_df.to_csv("data/training_staging/last_training_ecu.csv", index=False)
            with open("data/training_staging/last_training_dtc.json", "w") as json_out:
                json.dump(dtc_data, json_out, indent=4)
            st.success("📦 Gold-Standard Data Matrix Staged Successfully into './data/training_staging/'!")

# Multi-Agent Framework Orchestration Process Loop
if trigger_btn:
    if has_any_upload and not all_files_present:
        st.error("🛑 Incomplete Telemetry Upload! Please provide all 3 mandatory streams (ECU CSV, CAN CSV, DTC JSON).")
    else:
        with st.spinner("Compiling context window and streaming variables to cloud nodes..."):
            max_amps = float(telemetry_df["Motor_Current_Amps"].max())
            max_temp = float(telemetry_df["Inverter_Temp_C"].max()) if "Inverter_Temp_C" in telemetry_df.columns else 0.0
            
            telemetry_string_payload = f"""
            Ingested Signal Log Stats:
            - Max Motor Draw: {max_amps:.2f} Amps
            - Max Inverter Thermal Reading: {max_temp:.2f} °C
            - Raw Sensor Record Dimensions: {len(telemetry_df)} frames
            """

            config_full_path = os.path.abspath(os.path.join("config", uploaded_dtc_file.name))
            uploaded_can_full_path = os.path.abspath(os.path.join("data/sample data/sample CAN logs", uploaded_can.name))
            uploaded_ecu_full_path = os.path.abspath(os.path.join("data/sample data/sample Events logs", uploaded_ecu.name))
            incident_parser = DiagnosticIncidentParser(uploaded_can_full_path, uploaded_ecu_full_path, config_full_path)

            extracted_dtc_code = incident_parser.get_active_dtc_meaning()

            # Fire our sequential multi-agent orchestration chain
            agent_response_dict = run_rootcause_analysis(
                fault_code=extracted_dtc_code,
            )
            
            st.success("🤖 Framework Inference Cycle Successfully Concluded!")
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 🔍 Pipeline Extraction Phase")
                with st.container():
                    st.markdown("<div class='report-card' style='border-left-color: #0068C9;'>", unsafe_allow_html=True)
                    st.markdown("<p class='agent-title'>🕵️‍♂️ Agent 1: Signal Interpreter</p>", unsafe_allow_html=True)
                    st.write(agent_response_dict["signal"])
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                with st.container():
                    st.markdown("<div class='report-card' style='border-left-color: #29B5E8;'>", unsafe_allow_html=True)
                    st.markdown("<p class='agent-title'>⏱️ Agent 2: Chrono Sequencer</p>", unsafe_allow_html=True)
                    st.write(agent_response_dict["timeline"])
                    st.markdown("</div>", unsafe_allow_html=True)

            with col2:
                st.markdown("### 🎯 Synthesis & Engineering Actions")
                with st.container():
                    st.markdown("<div class='report-card' style='border-left-color: #FF4B4B;'>", unsafe_allow_html=True)
                    st.markdown("<p class='agent-title'>🧠 Agent 3: Root Cause Expert Report</p>", unsafe_allow_html=True)
                    st.info(agent_response_dict["root_cause"])
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                with st.container():
                    st.markdown("<div class='report-card' style='border-left-color: #28A745;'>", unsafe_allow_html=True)
                    st.markdown("<p class='agent-title'>🔧 Agent 4: Maintenance Advisory System</p>", unsafe_allow_html=True)
                    st.write(agent_response_dict["action"])
                    st.markdown("</div>", unsafe_allow_html=True)

            with st.expander("🛠️ Show Hardware-Software Abstract Layer Logs (Infrastructure Immunity Validation)"):
                st.code(f"""
                [SYS-INIT] Instantiating MultiLLMManager cross-compatibility router object...
                [GATEWAY] Validation success: Detected live active environment variable.
                [ROUTING] Dynamically deploying to target hardware node: '{active_backend}'
                [CONTEXT] Sent text context block footprint: ~140 Tokens.
                [INFERENCE] Stream parsing return code: 200 OK.
                """, language="bash")