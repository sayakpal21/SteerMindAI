# data/generate_healthy_event_logs.py
import os
import csv

# ==========================================
# 🌐 GLOBAL CONFIGURATION CONSTANTS
# ==========================================
DEFAULT_OUTPUT_PATH = "data/sample data/sample Events logs/Sample_Healthy_Event_Logs.csv"
TOTAL_DURATION_SEC = 3600  # 1 Hour simulation tracking mirror

# Standard Schema Definition
CSV_HEADERS = ["Timestamp", "Event_Id", "Component", "Event_Type", "Description", "Severity", "Active_DTC"]

# Severity Enums
SEV_INFO = "INFO"
SEV_WARN = "WARNING"

# Component System Strings
COMP_GATEWAY = "ECU_Gateway"
COMP_DRV_IN = "Driver_Inputs"
COMP_CHASSIS = "Chassis_Safety"
COMP_POWER   = "Power_Stage"

# Event Types
TYPE_STATE = "STATE_TRANSITION"
TYPE_USER  = "USER_ACTION"
TYPE_HEALTH = "HEARTBEAT"

def generate_healthy_event_log(output_path=DEFAULT_OUTPUT_PATH):
    """
    Generates a discrete, state-based event log file representing 
    a completely stable, nominal vehicle lifecycle run.
    """
    # Ensure the destination directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"⏳ Generating healthy event lifecycle logs for {TOTAL_DURATION_SEC / 60:.1f} minutes...")
    
    with open(output_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(CSV_HEADERS)
        
        # 1. 🚀 System Initialization Phase (Start of Drive)
        writer.writerow(["0.000000", "1001", COMP_GATEWAY, TYPE_STATE, "System initialization completed successfully", SEV_INFO, "NONE"])
        writer.writerow(["0.020000", "1022", COMP_DRV_IN, TYPE_USER, "Ignition terminal switched to RUN mode", SEV_INFO, "NONE"])
        writer.writerow(["0.150000", "3001", COMP_POWER, TYPE_STATE, "EPS Power inverter circuit calibration synchronized", SEV_INFO, "NONE"])
        
        # 2. 🛣️ Operational Phase Changes (Simulated events during travel)
        writer.writerow(["14.205000", "2045", COMP_CHASSIS, TYPE_STATE, "Automated Lane-Keep Assist system engaged by driver", SEV_INFO, "NONE"])
        writer.writerow(["840.650000", "2046", COMP_CHASSIS, TYPE_STATE, "Automated Lane-Keep Assist system disengaged - hands detected on wheel", SEV_INFO, "NONE"])
        
        # 3. 💓 Periodic Diagnostics (Hourly component health check check-ins)
        # Writes an automated internal health check every 15 minutes
        row_count = 5
        for t_check in [900.0, 1800.0, 2700.0]:
            writer.writerow([f"{t_check:.6f}", "9000", COMP_GATEWAY, TYPE_HEALTH, "Chassis bus component safety heartbeats nominal", SEV_INFO, "NONE"])
            row_count += 1
            
        # 4. 🏁 System Shutdown Phase (End of Drive)
        end_time = float(TOTAL_DURATION_SEC)
        writer.writerow([f"{end_time - 1.500000:.6f}", "2047", COMP_CHASSIS, TYPE_STATE, "All active driver assistance tracking modules safely disconnected", SEV_INFO, "NONE"])
        writer.writerow([f"{end_time - 0.050000:.6f}", "1023", COMP_DRV_IN, TYPE_USER, "Ignition terminal switched to OFF mode", SEV_INFO, "NONE"])
        writer.writerow([f"{end_time:.6f}", "1002", COMP_GATEWAY, TYPE_STATE, "Gateway enters micro-sleep power saving state", SEV_INFO, "NONE"])
        row_count += 3

    print(f"✅ Success! Healthy lifecycle events log saved to: {output_path}")
    print(f"📊 Summary: Compiled {row_count} discrete operational state records.")

if __name__ == "__main__":
    generate_healthy_event_log()