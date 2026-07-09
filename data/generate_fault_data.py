# data/generate_healthy_event_logs.py
from generate_healthy_can_logs import generate_healthy_can_log
from generate_healthy_event_logs import generate_healthy_event_log
import numpy as np

fault_time = np.random.randint(0, 3600)

DEFAULT_OUTPUT_PATH_OF_FAULTY_CAN = "data/sample data/sample CAN logs/Sample_Faulty_CAN_logs.csv"
DEFAULT_OUTPUT_PATH_OF_FAULTY_EVENTS = "data/sample data/sample Events logs/Sample_Faulty_Event_Logs.csv"

if __name__ == "__main__":
    generate_healthy_can_log(output_path=DEFAULT_OUTPUT_PATH_OF_FAULTY_CAN, faulty=True, fault_time=fault_time)
    generate_healthy_event_log(output_path=DEFAULT_OUTPUT_PATH_OF_FAULTY_EVENTS, faulty_time=fault_time, active_dtc="C10A4")