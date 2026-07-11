import numpy as np
import pandas as pd
from utils.parser import CANLogParser

def detect_short_circuit_fault(parsed_matrix):
    """
    Detect EPS short circuit fault from parsed CAN telemetry.

    Input:
        parsed_matrix:
            Output of CANLogParser.parse_csv()

    Required signals:
        Timestamp
        Motor_Current_Amps
        Steering_Angle_Deg
        Inverter_Temp_C

    Returns:
        diagnostic report string
    """

    # Convert parser output into DataFrame
    telemetry_df = pd.DataFrame(parsed_matrix)


    # Ensure required signals exist
    required_signals = [
        "Motor_Current",
        "Steering_Angle",
        "Inverter_Temp",
        "System_Voltage"
    ]

    missing = [
        sig for sig in required_signals
        if sig not in telemetry_df.columns
    ]

    if missing:
        return f"Missing telemetry signals: {missing}"


    # Extract signals

    time = telemetry_df["Timestamp"].values

    current = telemetry_df["Motor_Current"].astype(float).values

    angle = telemetry_df["Steering_Angle"].astype(float).values

    temp = telemetry_df["Inverter_Temp"].astype(float).values

    voltage = telemetry_df["System_Voltage"].astype(float).values



    # --------------------------------------------------
    # Fault indicators
    # --------------------------------------------------

    # Electrical overload
    current_fault = current > 22.0


    # Thermal protection limit
    temperature_fault = temp > 115.0


    # Steering actuator response degradation
    angle_rate = np.abs(np.gradient(angle))

    angle_fault = angle_rate > 0.5

    fault_condition = np.any(current_fault) & np.any(temperature_fault)

    if not fault_condition:
        return "System operating within normal parameters."

    # --------------------------------------------------
    # Short circuit signature
    # --------------------------------------------------
    #
    # Current rise is mandatory.
    # Confirmation:
    #   - thermal escalation OR
    #   - actuator response loss
    #

    fault_condition = (
        current_fault & temperature_fault
    )

    if fault_condition is False:
        return "No short circuit fault detected"

    # --------------------------------------------------
    # Persistence check
    # --------------------------------------------------

    persistence = 5

    count = 0
    fault_index = None


    for idx, condition in enumerate(fault_condition):

        if condition:
            count += 1

            if count >= persistence:
                fault_index = idx - persistence + 1
                break

        else:
            count = 0







    fault_timestamp = time[fault_index]


    # --------------------------------------------------
    # Extract before/after evidence
    # --------------------------------------------------

    window = 10

    before_start = max(0, fault_index-window)

    before_current = np.mean(
        current[before_start:fault_index]
    )

    after_current = np.mean(
        current[fault_index:fault_index+window]
    )


    before_temp = np.mean(
        temp[before_start:fault_index]
    )

    after_temp = np.mean(
        temp[fault_index:fault_index+window]
    )


    before_angle = np.mean(
        angle[before_start:fault_index]
    )

    after_angle = np.mean(
        angle[fault_index:fault_index+window]
    )



    report = f"""
SHORT CIRCUIT FAULT DETECTED

Fault Timestamp:
{fault_timestamp:.3f} sec


Signal Evidence:

Motor Current:
Before Fault : {before_current:.2f} A
After Fault  : {after_current:.2f} A
Increase     : {(after_current-before_current):.2f} A


Inverter Temperature:
Before Fault : {before_temp:.2f} C
After Fault  : {after_temp:.2f} C


Steering Angle:
Before Fault : {before_angle:.2f} deg
After Fault  : {after_angle:.2f} deg


Detection Criteria:

✓ Motor current exceeded 22A
✓ Thermal/actuator abnormality confirmed
✓ Fault persisted for {persistence} samples


Probable Failure Mode:

EPS motor winding short circuit or inverter power stage short circuit.

"""

    return report

if __name__ == "__main__":
    # Example usage
    #can_log_path = "data/sample data/sample CAN logs/Sample_Faulty_CAN_logs.csv"
    can_log_path = "data/sample data/sample CAN logs/Sample_Healthy_CAN_logs.csv"

    # 🏎️ Parse CAN Telemetry Logs
    print("Parsing CAN Logs...")

    parser = CANLogParser(
    target_signals=[
        "Motor_Current",
        "Steering_Angle",
        "Inverter_Temp",
        "System_Voltage"
    ])

    parsed_matrix, columns = parser.parse_csv(can_log_path)


    diagnosis = detect_short_circuit_fault(parsed_matrix)


    print(diagnosis)
