# agents/timeline_agent.py
import os
from utils.llm_gateway import MultiLLMManager

def run_timeline_sequencer(fault_code: str, signal_observations: str) -> str:
    """Reads timeline_prompt.txt to establish chronological failure stages."""
    prompt_path = "prompts/timeline_prompt.txt"
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_instruction = f.read()
    else:
        system_instruction = "Role: Forensic Sequencer. Map failure in 1 line: 1. Baseline -> 2. Anomaly -> 3. Shutdown."

    user_payload = f"TARGET DTC: {fault_code}\nSIGNAL OBSERVATIONS:\n{signal_observations}"

    ai_hub = MultiLLMManager()
    return ai_hub.invoke_agent(
        system_instruction=system_instruction,
        user_payload=user_payload,
        max_tokens=150
    )