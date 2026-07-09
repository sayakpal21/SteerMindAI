# data/generate_healthy_can_logs.py
import os
import csv
import random
import numpy as np

# ==========================================
# 🌐 GLOBAL CONFIGURATION CONSTANTS
# ==========================================
DEFAULT_OUTPUT_PATH = "data/sample data/sample CAN logs/Sample_Healthy_CAN_logs.csv"
TOTAL_SECONDS = 3600      # 1 Hour simulation window
SAMPLE_RATE_HZ = 20       # 20 Hz frame broadcast rate
BUS_CHANNEL = "CAN_FD_1"

# Standard Schema Definition
CSV_HEADERS_FOR_CAN = ["Timestamp", "CAN_Id", "Message_Name", "Signal_Name", "Physical_Value", "Units", "Bus_Channel"]


# Component Messaging Properties
MSG_EPS_STATUS = {"id": "0x18F", "name": "EPS_Status_01"}
MSG_EPS_FEEDBACK = {"id": "0x20C", "name": "EPS_Feedback_02"}


def generate_healthy_can_log(output_path=DEFAULT_OUTPUT_PATH):
    """
    Generates a raw, sequential, completely healthy CAN bus log file 
    to serve as the nominal engineering baseline.
    """
    # Ensure the destination directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"⏳ Generating {TOTAL_SECONDS / 60:.1f} minutes of healthy CAN telemetry at {SAMPLE_RATE_HZ}Hz interval...")
    
    # Calculate time array sequence
    time_steps = np.arange(0, TOTAL_SECONDS, 1.0 / SAMPLE_RATE_HZ)
    
    with open(output_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(CSV_HEADERS)
        
        # Pre-compute a smooth steering angle wave to simulate normal highway steering corrections
        angle_wave = np.sin(time_steps * 0.05) * 15.0
        
        row_count = 0
        for idx, t in enumerate(time_steps):
            # Formulate baseline healthy metrics with minor white noise
            current = 5.0 + random.normalvariate(0, 0.15)
            temp = 42.0 + (t * 0.001) + random.normalvariate(0, 0.02)  # Normal operational warming trend
            angle = angle_wave[idx] + random.normalvariate(0, 0.2)
            voltage = 12.2 + random.normalvariate(0, 0.03)
            
            # 🔌 Frame A (0x18F) - EPS Power Status
            writer.writerow([f"{t:.6f}", MSG_EPS_STATUS["id"], MSG_EPS_STATUS["name"], "Motor_Current", f"{current:.2f}", "Amps", BUS_CHANNEL])
            writer.writerow([f"{t:.6f}", MSG_EPS_STATUS["id"], MSG_EPS_STATUS["name"], "Inverter_Temp", f"{temp:.2f}", "C", BUS_CHANNEL])
            
            # 🔌 Frame B (0x20C) - EPS Feedback Controls
            writer.writerow([f"{t:.6f}", MSG_EPS_FEEDBACK["id"], MSG_EPS_FEEDBACK["name"], "Steering_Angle", f"{angle:.2f}", "Deg", BUS_CHANNEL])
            writer.writerow([f"{t:.6f}", MSG_EPS_FEEDBACK["id"], MSG_EPS_FEEDBACK["name"], "System_Voltage", f"{voltage:.2f}", "V", BUS_CHANNEL])
            
            row_count += 4
            
            # Periodic progress tracker in console
            if idx % 15000 == 0 and idx > 0:
                print(f"   Progress: {int((t / TOTAL_SECONDS) * 100)}% complete ({row_count:,} lines written)...")

    print(f"\n✅ Success! Healthy baseline compiled and exported to: {output_path}")
    print(f"📊 Summary: Generated {row_count:,} independent signal row elements.")

if __name__ == "__main__":
    generate_healthy_can_log()