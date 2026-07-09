# utils/parser.py
import os
import pandas as pd
import json

class OEMConfigParser:
    """
    Parses dynamic diagnostic configuration profiles provided by automotive OEMs.
    Extracts metadata, trouble code registries, validation targets, and safety thresholds.
    """
    def __init__(self, file_path=None):
        # Initialize storage containers for JSON components
        self.config_data = {}
        self.oem_metadata = {}
        self.dtc_registry = {}
        
        # Automatically trigger parsing if a path is passed on instantiation
        if file_path:
            self.load_config(file_path)

    def load_config(self, file_path):
        """Validates, safely opens, and extracts structured data from the JSON config."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Not found: {file_path}")
            
        with open(file_path, 'r') as f:
            try:
                self.config_data = json.load(f)
                # Isolate higher-level OEM data vs specific code thresholds
                self.oem_metadata = self.config_data.get("OEM_Metadata", {})
                self.dtc_registry = self.config_data.get("DTC_Registry", {})
            except Exception as e:
                raise ValueError(f"Invalid JSON format: {e}")

    def get_supplier_name(self):
        """Retrieves the system supplier identity (e.g., Bosch, Nexteer)."""
        return self.oem_metadata.get("Supplier", "Unknown_OEM")

    def get_supported_dtcs(self):
        """Lists all Diagnostic Trouble Codes (DTCs) registered in this configuration."""
        return list(self.dtc_registry.keys())

    def get_dtc_details(self, dtc_code):
        """Retrieves the complete internal payload mapping for a specific trouble code."""
        return self.dtc_registry.get(dtc_code, {})

    def get_validation_signals(self, dtc_code):
        """Extracts the specific CAN signal names required to validate the given code."""
        return self.get_dtc_details(dtc_code).get("Telemetry_Validation_Signals", [])

    def get_critical_thresholds(self, dtc_code):
        """Extracts operating limit bounds used for evaluation checks on the target code."""
        return self.get_dtc_details(dtc_code).get("Critical_Thresholds", {})
        

class CANLogParser:
    """
    Parses raw sequential automotive CAN logs matching the specific schema,
    pivoting rows into aligned timeline events matching target tracking signals.
    """
    def __init__(self, target_signals=None):
        self.target_signals = set(target_signals) if target_signals else None

    def parse_csv(self, file_path):
        """Parses raw CAN frames, grouping row items sharing identical timestamps."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CAN log not found at: {file_path}")

        # 1. Read the CSV into a DataFrame
        df = pd.read_csv(file_path)

        # 2. Filter rows for target signals if specified
        if self.target_signals:
            df = df[df["Signal_Name"].isin(self.target_signals)]

        # 3. Handle data type conversions safely
        df["Timestamp"] = pd.to_numeric(df["Timestamp"])
        df["Physical_Value"] = pd.to_numeric(df["Physical_Value"], errors="coerce").fillna(df["Physical_Value"])

        # 4. Pivot the table to align timeline events
        # Index becomes 'Timestamp', Columns become unique 'Signal_Name' values
        pivot_df = df.pivot_table(
            index="Timestamp", 
            columns="Signal_Name", 
            values="Physical_Value", 
            aggfunc="first" # Handles duplicate timestamps for the same signal if they exist
        )

        # 5. Sort timestamps and reset index to make 'Timestamp' a regular column
        pivot_df = pivot_df.sort_index().reset_index()

        # 6. Extract dynamic column headers and the matrix payload to match original signature
        columns = pivot_df.columns.tolist()
        
        # Convert DataFrame back to a list of dictionaries (matching parsed_matrix)
        # to_dict('records') preserves float types for timestamps/values and uses None for NaNs
        parsed_matrix = pivot_df.where(pivot_df.notnull(), None).to_dict(orient="records")

        return parsed_matrix, columns


class EventLogParser:
    """
    Parses discrete vehicle system event and lifecycle status logs,
    mapping chronological system changes, alerts, and active trouble codes.
    """
    def __init__(self):
        # We will hold the parsed records as a list of dicts to preserve original API behavior
        self.events_list = []

    def parse_csv(self, file_path):
        """Parses the sequential state tracking logs into structured records."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Event log file not found at: {file_path}")

        # 1. Read only the columns we actually care about
        target_cols = ["Timestamp", "Event_Id", "Component", "Event_Type", "Description", "Severity", "Active_DTC"]
        df = pd.read_csv(file_path, usecols=target_cols)

        # 2. Reorder columns to guarantee they match the original order (in case CSV columns are shuffled)
        df = df[target_cols]

        # 3. Handle data type conversions and sort chronologically
        df["Timestamp"] = pd.to_numeric(df["Timestamp"])
        df = df.sort_values(by="Timestamp")

        # 4. Convert back to list of dicts and save to state
        # `.where(df.notnull(), None)` ensures empty CSV cells map to Python `None` instead of `NaN`
        self.events_list = df.where(df.notnull(), None).to_dict(orient="records")
        return self.events_list

    def filter_by_severity(self, target_severity):
        """Filters cached logs by severity."""
        return [ev for ev in self.events_list if ev["Severity"] == target_severity]

    def get_triggered_dtcs(self):
        """Returns a unique list of active Diagnostic Trouble Codes (DTCs) skipping 'NONE'."""
        return list({ev["Active_DTC"] for ev in self.events_list if ev["Active_DTC"] != "NONE" and ev["Active_DTC"] is not None})



if __name__ == "__main__":
    # 📁 File Paths
    config_path = "config/dtc_map_bosch.json"
    can_log_path = "data/sample data/sample CAN logs/Sample_Healthy_CAN_logs.csv"
    event_log_path = "data/sample data/sample Events logs/Sample_Healthy_Event_Logs.csv"
    
    # 🏎️ Parse CAN Telemetry Logs
    print("Parsing CAN Logs...")
    can_parser = CANLogParser(target_signals={"Motor_Current", "Vehicle_Speed"})
    can_data, headers = can_parser.parse_csv(can_log_path)
    print(f"Columns: {headers}\nFirst Row: {can_data[0] if can_data else 'Empty'}\n")

    # 📝 Parse System Event Logs
    print("Parsing Event Logs...")
    event_parser = EventLogParser()
    event_data = event_parser.parse_csv(event_log_path)
    print(f"Total Events: {len(event_data)}\nFirst Event: {event_data[0] if event_data else 'Empty'}")

    # 🔧 Parse OEM Configuration Map
    print("Parsing OEM Configuration...")
    try:
        config_parser = OEMConfigParser(config_path)
        print(f"Supplier: {config_parser.get_supplier_name()}")
        
        supported_dtcs = config_parser.get_supported_dtcs()
        print(f"Supported DTCs: {supported_dtcs}")
        
        if supported_dtcs:
            target_dtc = supported_dtcs[0]
            print(f"\nDetails for [{target_dtc}]:")
            print(f"  Signals: {config_parser.get_validation_signals(target_dtc)}")
            print(f"  Thresholds: {config_parser.get_critical_thresholds(target_dtc)}")
            
    except FileNotFoundError as e:
        print(e)