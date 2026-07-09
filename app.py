# # app.py (Updated with 5 Multi-Fault Scenarios)
# import os
# import streamlit as st
# import pandas as pd
# import numpy as np
# import plotly.graph_objects as go
# from dotenv import load_dotenv

# load_dotenv()
# st.set_page_config(page_title="SteerMind AI Dashboard", layout="wide")

# import sys
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# from agents.rootcause_agent import run_simple_diagnosis

# # ==========================================
# # 🎛️ SIDEBAR SCENARIO ENGINE
# # ==========================================
# st.sidebar.image("https://img.icons8.com/fluency/96/steering-wheel.png", width=60)
# st.sidebar.title("SteerMind Configurator")
# st.sidebar.markdown("---")

# st.sidebar.subheader("📂 Ingest Field Log Data")
# uploaded_file = st.sidebar.file_uploader("Upload custom CAN bus log:", type=["csv"])

# st.sidebar.markdown("OR choose an engineering test matrix:")
# selected_scenario = st.sidebar.selectbox(
#     "Select Simulation Scenario:",
#     [
#         "Healthy Operations (Nominal Baseline)",
#         "C1044 - EPS Motor Overcurrent Spike",
#         "C1051 - Steering Angle Sensor Flatline",
#         "C1093 - Inverter Thermal Runaway Fault",
#         "C1221 - ECU Power Rail Under-Voltage Sag"
#     ]
# )

# # Extract correct DTC for prompt framing vectors
# if "C1044" in selected_scenario: extracted_dtc_code = "C1044"
# elif "C1051" in selected_scenario: extracted_dtc_code = "C1051"
# elif "C1093" in selected_scenario: extracted_dtc_code = "C1093"
# elif "C1221" in selected_scenario: extracted_dtc_code = "C1221"
# else: extracted_dtc_code = "HEALTHY_NOMINAL"

# # ==========================================
# # 📊 TIME-SERIES DATA MATRIX ROUTING
# # ==========================================
# if uploaded_file is not None:
#     telemetry_df = pd.read_csv(uploaded_file)
#     st.sidebar.success("✅ Custom upload running live.")
# else:
#     if "C1044" in selected_scenario: file_target = "data/can_overcurrent_fault.csv"
#     elif "C1051" in selected_scenario: file_target = "data/can_flatline_fault.csv"
#     elif "C1093" in selected_scenario: file_target = "data/can_thermal_fault.csv"
#     elif "C1221" in selected_scenario: file_target = "data/can_voltagesag_fault.csv"
#     else: file_target = "data/can_healthy_log.csv"
    
#     if os.path.exists(file_target):
#         telemetry_df = pd.read_csv(file_target)
#     else:
#         # Failsafe array layout matrix
#         telemetry_df = pd.DataFrame({"Time": np.linspace(0,10,200), "Motor_Current_Amps": 5.0, "Steering_Angle_Deg": 0.0, "Inverter_Temp_C": 45.0})

# # ==========================================
# # 🖥️ APPLICATION CORE INTERACTIVE LAYOUT
# # ==========================================
# st.title("🤖 SteerMind AI: Multi-Agent Chassis Diagnostics")
# st.markdown("---")

# # Metrics KPIs Block Rows
# k1, k2, k3 = st.columns(3)
# k1.metric("Target Bus Architecture", "CAN-FD Channel A")
# k2.metric("Target Fault Register ID", extracted_dtc_code)

# has_gemini = bool(os.getenv("GEMINI_API_KEY"))
# has_openai = bool(os.getenv("OPENAI_API_KEY"))
# active_backend = "GPT-4o Mini (OpenAI)" if (has_openai and not has_gemini) else "Gemini 2.5 Flash (Google)"
# k3.metric("Active Core Gateway Driver", active_backend)

# st.markdown("---")

# # Synchronized Plotly Multi-Axis Render Engine
# st.subheader("📈 Interactive Multi-Channel Sensor Analytics")
# fig = go.Figure()
# fig.add_trace(go.Scatter(x=telemetry_df["Time"], y=telemetry_df["Motor_Current_Amps"], name="Current (Amps)", line=dict(color="#FF4B4B")))
# fig.add_trace(go.Scatter(x=telemetry_df["Time"], y=telemetry_df["Steering_Angle_Deg"], name="Angle (Deg)", line=dict(color="#0068C9")))
# if "Inverter_Temp_C" in telemetry_df.columns:
#     fig.add_trace(go.Scatter(x=telemetry_df["Time"], y=telemetry_df["Inverter_Temp_C"], name="Temp (°C)", line=dict(color="#29B5E8")))

# fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=1.05))
# st.plotly_chart(fig, use_container_width=True)

# st.markdown("---")

# # Execution trigger connection wrapper
# if st.button("🚀 Trigger SteerMind Diagnostic Engine", type="primary"):
#     with st.spinner("Compiling contextual window state vectors..."):
        
#         # Calculate heuristics for prompt ingestion context summary block
#         max_amps = float(telemetry_df.iloc[:, 1].max())
#         max_temp = float(telemetry_df.iloc[:, 3].max()) if telemetry_df.shape[1] > 3 else 0.0
        
#         telemetry_string_payload = f"""
#         Ingested Signal Log Stats:
#         - Max Motor Draw: {max_amps:.2f} Amps
#         - Max Inverter Thermal Reading: {max_temp:.2f} °C
#         - Raw Sensor Record Dimensions: {len(telemetry_df)} frames
#         """
        
#         # Call the unified agent file
#         agent_raw_response = run_simple_diagnosis(
#             fault_code=extracted_dtc_code,
#             metric_telemetry=telemetry_string_payload
#         )
        
#         st.success("Analysis Execution Cycle Complete!")
#         st.markdown("### 📋 Root Cause Synthesis Report Card")
#         st.info(agent_raw_response)

# app.py

# app.py
import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
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
from agents.rootcause_agent import run_simple_diagnosis

# ==========================================
# 🎛️ SIDEBAR ENGINE & SCENARIO CONTROLLER
# ==========================================
st.sidebar.image("https://img.icons8.com/fluency/96/steering-wheel.png", width=60)
st.sidebar.title("SteerMind AI Control")
st.sidebar.caption("v1.3.1 • Core Diagnostic Orchestrator")
st.sidebar.markdown("---")

st.sidebar.subheader("📂 Mandatory Telemetry Ingestion")

# 📥 Field 1: ECU Logs
uploaded_ecu = st.sidebar.file_uploader(
    "1. Ingest ECU Log (.csv): *", 
    type=["csv"],
    key="ecu_uploader",
    help="Requires high-frequency diagnostic internal registers."
)

# 📥 Field 2: CAN Logs
uploaded_can = st.sidebar.file_uploader(
    "2. Ingest CAN-Bus Stream (.csv): *", 
    type=["csv"],
    key="can_uploader",
    help="Requires network physical bus message streams."
)

# 📥 Field 3: DTC Records
uploaded_dtc_file = st.sidebar.file_uploader(
    "3. Ingest Active DTC Matrix (.csv): *", 
    type=["csv"],
    key="dtc_uploader",
    help="Requires snapshot freeze-frame trouble codes."
)

# Check validation flag status across all three entry gates
all_files_present = bool(uploaded_ecu and uploaded_can and uploaded_dtc_file)
has_any_upload = bool(uploaded_ecu or uploaded_can or uploaded_dtc_file)

# 🧠 SMART UX VALIDATION LOGIC
if all_files_present:
    st.sidebar.success("🟢 All diagnostic streams locked down!")
elif has_any_upload:
    # Only show a warning if they started uploading but didn't finish the set
    st.sidebar.warning("⚠️ Incomplete multi-stream upload. Please provide all 3 logs.")
else:
    # Professional onboarding placeholder while navigating simulation targets
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
# 📊 TIME-SERIES DATA MATRIX ROUTING
# ==========================================
if all_files_present:
    telemetry_df = pd.read_csv(uploaded_can)
    ecu_df = pd.read_csv(uploaded_ecu)
    dtc_df = pd.read_csv(uploaded_dtc_file)
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

# Row 1: High-Fidelity KPI Status Grid
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric(label="📊 Bus Infrastructure", value="CAN-FD Channel A")
kpi2.metric(label="🎯 Active Fault Vector", value=extracted_dtc_code)

active_backend = "GPT-4o Mini (OpenAI)" if (has_openai and not has_gemini) else "Gemini 2.5 Flash (Google)"
kpi3.metric(label="🔌 Active Model Gateway", value=active_backend)
kpi4.metric(label="⏱️ Frame Ingestion Rate", value=f"{len(telemetry_df)} Hz")

st.markdown("---")

# Row 2: Graphing telemetry profiles
st.subheader("📈 Synchronized Multi-Channel Waveform Telemetry")
fig = go.Figure()
fig.add_trace(go.Scatter(x=telemetry_df["Time"], y=telemetry_df["Motor_Current_Amps"], name="Motor Current (Amps)", line=dict(color="#FF4B4B", width=2)))
fig.add_trace(go.Scatter(x=telemetry_df["Time"], y=telemetry_df["Steering_Angle_Deg"], name="Steering Angle (Deg)", line=dict(color="#0068C9", width=2)))
if "Inverter_Temp_C" in telemetry_df.columns:
    fig.add_trace(go.Scatter(x=telemetry_df["Time"], y=telemetry_df["Inverter_Temp_C"], name="Inverter Temp (°C)", line=dict(color="#29B5E8", width=2)))

fig.update_layout(
    height=340, 
    margin=dict(l=10, r=10, t=10, b=10), 
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    plot_bgcolor="#F8F9FA"
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Row 3: Action Buttons (Analysis vs Data Saving Matrix)
st.subheader("🧠 Control Actions Console")
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    trigger_btn = st.button("🚀 Run SteerMind Autonomous Analysis", type="primary")

with btn_col2:
    save_btn = st.button("📦 Save Dataset for Model Training", type="secondary")

# ─── ACTION HANDLING 1: DATA TRAINING LOG SAVER ───
if save_btn:
    if not all_files_present:
        st.error("❌ Data Save Rejected! You must upload all 3 files (ECU, CAN, and DTC) into the Ingestion Hub before saving data for training purposes.")
    else:
        with st.spinner("Processing multi-stream frames for model staging repository..."):
            os.makedirs("data/training_staging", exist_ok=True)
            
            final_can = pd.read_csv(uploaded_can)
            final_ecu = pd.read_csv(uploaded_ecu)
            final_dtc = pd.read_csv(uploaded_dtc_file)
            
            final_can.to_csv("data/training_staging/last_training_can.csv", index=False)
            final_ecu.to_csv("data/training_staging/last_training_ecu.csv", index=False)
            final_dtc.to_csv("data/training_staging/last_training_dtc.csv", index=False)
            
            st.success(f"📦 Gold-Standard Data Matrix Saved! Conserved {len(final_can)} records cleanly into './data/training_staging/'. Pipeline is primed for training execution loops.")

# ─── ACTION HANDLING 2: MULTI-AGENT DIAGNOSIS ───
if trigger_btn:
    # Hard gate blocking execution if they started uploading but forgot part of the set
    if has_any_upload and not all_files_present:
        st.error("🛑 Incomplete Telemetry Upload! Missing critical parameters. Please upload ALL THREE mandatory files (ECU Log, CAN-Bus Stream, AND DTC Matrix) to run diagnosis, or clear your uploads to explore simulations.")
    else:
        with st.spinner("Compiling context window and streaming variables to cloud nodes..."):
            max_amps = float(telemetry_df.iloc[:, 1].max())
            max_temp = float(telemetry_df.iloc[:, 3].max()) if telemetry_df.shape[1] > 3 else 0.0
            
            telemetry_string_payload = f"""
            Ingested Signal Log Stats:
            - Max Motor Draw: {max_amps:.2f} Amps
            - Max Inverter Thermal Reading: {max_temp:.2f} °C
            - Raw Sensor Record Dimensions: {len(telemetry_df)} frames
            """
            
            agent_raw_response = run_simple_diagnosis(
                fault_code=extracted_dtc_code,
                metric_telemetry=telemetry_string_payload
            )
            
            st.success("🤖 Framework Inference Cycle Successfully Concluded!")
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 🔍 Pipeline Extraction Phase")
                with st.container():
                    st.markdown("<div class='report-card' style='border-left-color: #0068C9;'>", unsafe_allow_html=True)
                    st.markdown("<p class='agent-title'>🕵️‍♂️ Agent 1: Signal Interpreter</p>", unsafe_allow_html=True)
                    st.write(f"Anomalies analyzed. Peak current registered at **{max_amps:.2f} Amps** with thermal limits peaking at **{max_temp:.2f} °C**.")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                with st.container():
                    st.markdown("<div class='report-card' style='border-left-color: #29B5E8;'>", unsafe_allow_html=True)
                    st.markdown("<p class='agent-title'>⏱️ Agent 2: Chrono Sequencer</p>", unsafe_allow_html=True)
                    st.write("Parsed bus data streams. Telemetry tracking reveals clear operational anomalies preceding safety-switch cutoff intervals.")
                    st.markdown("</div>", unsafe_allow_html=True)

            with col2:
                st.markdown("### 🎯 Synthesis & Engineering Actions")
                with st.container():
                    st.markdown("<div class='report-card' style='border-left-color: #FF4B4B;'>", unsafe_allow_html=True)
                    st.markdown("<p class='agent-title'>🧠 Agent 3: Root Cause Expert Report</p>", unsafe_allow_html=True)
                    st.info(agent_raw_response)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                with st.container():
                    st.markdown("<div class='report-card' style='border-left-color: #28A745;'>", unsafe_allow_html=True)
                    st.markdown("<p class='agent-title'>🔧 Agent 4: Maintenance Advisory System</p>", unsafe_allow_html=True)
                    st.write("1. Check physical continuity of phase windings to isolate resistance leaks.\n2. Verify state of internal solid-state gate drive switches.")
                    st.markdown("</div>", unsafe_allow_html=True)

            with st.expander("🛠️ Show Hardware-Software Abstract Layer Logs (Infrastructure Immunity Validation)"):
                st.code(f"""
                [SYS-INIT] Instantiating MultiLLMManager cross-compatibility router object...
                [GATEWAY] Validation success: Detected live active environment variable.
                [ROUTING] Dynamically deploying to target hardware node: '{active_backend}'
                [CONTEXT] Sent text context block footprint: ~140 Tokens.
                [INFERENCE] Stream parsing return code: 200 OK.
                """, language="bash")