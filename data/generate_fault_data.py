# data/generate_fault_data.py
import os
import numpy as np
import pandas as pd

def build_extended_datasets():
    """Generates 5 realistic time-series CAN bus profiles for advanced app simulation."""
    os.makedirs("data", exist_ok=True)
    np.random.seed(42)
    time_steps = np.linspace(0, 10, 200)

    # 🟢 1. HEALTHY BASELINE
    pd.DataFrame({
        "Time": time_steps,
        "Motor_Current_Amps": np.random.normal(5.0, 0.2, 200),
        "Steering_Angle_Deg": np.sin(time_steps) * 30 + np.random.normal(0, 0.5, 200),
        "Inverter_Temp_C": np.linspace(40, 52, 200) + np.random.normal(0, 0.2, 200)
    }).to_csv("data/can_healthy_log.csv", index=False)

    # 🔴 2. OVERCURRENT SPARK (C1044) - Short Circuit
    current_spike = np.random.normal(5.0, 0.2, 200)
    current_spike[120:140] = np.random.normal(48.5, 0.8, 20) 
    pd.DataFrame({
        "Time": time_steps,
        "Motor_Current_Amps": current_spike,
        "Steering_Angle_Deg": np.sin(time_steps) * 20,
        "Inverter_Temp_C": np.linspace(40, 58, 200)
    }).to_csv("data/can_overcurrent_fault.csv", index=False)

    # 🟡 3. SENSOR SIGNAL LOSS (C1051) - Dead sensor
    angle_flatline = np.sin(time_steps) * 30
    angle_flatline[100:] = 0.0  # Physical freeze
    pd.DataFrame({
        "Time": time_steps,
        "Motor_Current_Amps": np.random.normal(4.2, 0.1, 200),
        "Steering_Angle_Deg": angle_flatline,
        "Inverter_Temp_C": np.linspace(38, 44, 200)
    }).to_csv("data/can_flatline_fault.csv", index=False)

    # 🟣 4. THERMAL RUNAWAY DEGRADATION (C1093) - Tight rack mechanical binding
    temp_runaway = np.linspace(45, 115, 200) + np.random.normal(0, 0.5, 200) # Exceeds safe threshold
    pd.DataFrame({
        "Time": time_steps,
        "Motor_Current_Amps": np.random.normal(12.0, 0.5, 200), # Constant heavy power draw
        "Steering_Angle_Deg": np.sin(time_steps) * 15,
        "Inverter_Temp_C": temp_runaway
    }).to_csv("data/can_thermal_fault.csv", index=False)

    # 🔲 5. UNDER-VOLTAGE DROPOUT SAG (C1221) - Battery terminal or alternator failure
    current_sag = np.random.normal(6.0, 0.2, 200)
    current_sag[80:130] = np.random.normal(1.1, 0.1, 50) # System drops power to enter fail-safe mode
    pd.DataFrame({
        "Time": time_steps,
        "Motor_Current_Amps": current_sag,
        "Steering_Angle_Deg": np.zeros(200), # Power loss locks control assist
        "Inverter_Temp_C": np.linspace(42, 45, 200)
    }).to_csv("data/can_voltagesag_fault.csv", index=False)

    print("📊 [SUCCESS] 5 Production-grade test matrix files written into './data/'")

if __name__ == "__main__":
    build_extended_datasets()