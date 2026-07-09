import os
import pandas as pd
import parser

class DiagnosticIncidentParser:
    """
    Extracts high-frequency CAN telemetry sequences bounded within a 'before-and-after' 
    time window of active Diagnostic Trouble Code (DTC) occurrences.
    """
    def __init__(self, can_log_path, event_log_path, config_path):
        self.can_path = can_log_path
        self.event_path = event_log_path
        self.config_parser = parser.OEMConfigParser(config_path)

    def parse_incident_telemetry(self, time_buffer_seconds=5.0):
        """
        Locates active DTCs in the event logs and isolates matching timeline segments 
        from the CAN telemetry matrix, returning the result as a plain string block.
        """
        if not os.path.exists(self.can_path) or not os.path.exists(self.event_path):
            raise FileNotFoundError("One or both data log files are missing.")

        # --- 1. EXTRACT CRITICAL DTC WINDOWS FROM EVENT LOGS ---
        event_cols = ["Timestamp", "Active_DTC"]
        event_df = pd.read_csv(self.event_path, usecols=event_cols)
        event_df["Timestamp"] = pd.to_numeric(event_df["Timestamp"])
        
        active_dtc_df = event_df[
            event_df["Active_DTC"].notnull() & 
            (event_df["Active_DTC"] != "NONE") & 
            (event_df["Active_DTC"] != "")
        ]

        if active_dtc_df.empty:
            return ""

        # --- 2. STREAMLINE AND LOAD CAN LOG DATA ---
        can_cols = ["Timestamp", "Signal_Name", "Physical_Value"]
        can_df = pd.read_csv(self.can_path, usecols=can_cols)
        can_df["Timestamp"] = pd.to_numeric(can_df["Timestamp"])
        
        pivot_df = can_df.pivot_table(
            index="Timestamp", columns="Signal_Name", values="Physical_Value", aggfunc="first"
        ).sort_index().reset_index()

        # --- 3. FILTER TIMELINE USING BITWISE LOGICAL OR WINDOWS ---
        combined_window_mask = pd.Series(False, index=pivot_df.index)

        for _, row in active_dtc_df.iterrows():
            dtc_time = row["Timestamp"]
            start_window = dtc_time - time_buffer_seconds
            end_window = dtc_time + time_buffer_seconds
            
            current_incident_mask = (pivot_df["Timestamp"] >= start_window) & (pivot_df["Timestamp"] <= end_window)
            combined_window_mask |= current_incident_mask

        incident_df = pivot_df[combined_window_mask]

        if incident_df.empty:
            return ""

        # --- 4. FORMAT OUTPUT AS A PLAIN STRING PAYLOAD ---
        # First line: columns separated by comma
        header_line = ",".join(incident_df.columns.astype(str).tolist())
        
        # Subsequent lines: data values separated by comma
        data_lines = incident_df.to_csv(header=False, index=False, lineterminator="\n").strip()
        
        return f"{header_line}\n{data_lines}"
    
    def get_active_dtc_meaning(self):
        """
        Returns a dictionary mapping active DTCs to their human-readable descriptions
        using the OEM configuration parser.
        """
        event_cols = ["Active_DTC"]
        event_df = pd.read_csv(self.event_path, usecols=event_cols)
        
        active_dtcs = event_df[
            event_df["Active_DTC"].notnull() & 
            (event_df["Active_DTC"] != "NONE") & 
            (event_df["Active_DTC"] != "")
        ]["Active_DTC"].unique()

        dtc_meanings = {}
        for dtc in active_dtcs:
            meaning = self.config_parser.get_dtc_details(dtc)
            dtc_meanings[dtc] = meaning

        return dtc_meanings


if __name__ == "__main__":
    can_log = "data/sample data/sample CAN logs/Sample_Healthy_CAN_logs.csv"
    event_log = "data/sample data/sample Events logs/Sample_Healthy_Event_Logs.csv"
    config_path = "config/dtc_map_bosch.json"

    incident_parser = DiagnosticIncidentParser(can_log, event_log, config_path)
    
    # Receives plain string result
    plain_string_output = incident_parser.parse_incident_telemetry(time_buffer_seconds=1.0)
    active_dtc_meanings = incident_parser.get_active_dtc_meaning()
    
    # Verify exact layout structure
    if plain_string_output:
        print("--- [PLAIN STRING OUTPUT START] ---")
        print(plain_string_output)
        print("--- [PLAIN STRING OUTPUT END] ---")
    else:
        print("🟢 No active matching incident windows found.")
    
    # 2. Use .empty for the pandas DataFrame block
    if active_dtc_meanings:
        print("\n--- [ACTIVE DTC MEANINGS] ---")
        for dtc, meaning in active_dtc_meanings.items():
            print(f"{dtc}: {meaning}")
    else:
        print("🟢 No active DTC found.")
    