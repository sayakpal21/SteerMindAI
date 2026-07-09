# agents/timeline_agent.py
import os
from utils.llm_gateway import MultiLLMManager
from limit import *

def run_timeline_sequencer(fault_code: str, signal_observations: str) -> str:
    """Reads timeline_prompt.txt to establish chronological failure stages.
    Raises FileNotFoundError if the prompt file is missing.
    """
    prompt_path = "prompts/timeline_prompt.txt"
    
    # 1. Enforce strict file checking (No fallback system_instruction allowed)
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"CRITICAL ERROR: Required prompt file missing at '{prompt_path}'")
        
    with open(prompt_path, "r", encoding="utf-8") as f:
        system_instruction = f.read()

    ai_hub = MultiLLMManager()

    # --- PROMPT CHAINING LAYER ---
    # Step 1: Establish raw chronological timeline and sequential events
    initial_payload = f"TARGET DTC: {fault_code}\nSIGNAL OBSERVATIONS:\n{signal_observations}"
    raw_timeline = ai_hub.invoke_agent(
        system_instruction=system_instruction,
        user_payload=initial_payload,
        max_tokens=MAX_TOKENS
    )

    # Step 2: Chain the output into a second user prompt for definitive lifecycle mapping
    chained_user_payload = (
        f"Based on this raw structural timeline events context:\n{raw_timeline}\n\n"
        f"Refine this into a strict 1-line forensic event map following this exact structure: "
        f"1. Baseline -> 2. Anomaly -> 3. Shutdown."
    )

    # Return the final chained output
    return ai_hub.invoke_agent(
        system_instruction="Role: Forensic Failure Sequencer & RCA Specialist.",
        user_payload=chained_user_payload,
        max_tokens=MAX_TOKENS
    )

if __name__ == "__main__":
    # 1. Create fake input telemetry logs to test the sequence architecture
    mock_code = "C1044"
    mock_signals = "Initial steady state readings at 12V. Sudden spike to 52A at T+12ms. Relays tripped out entirely at T+15ms."
    
    print("Testing timeline_agent with Chained Prompts...")
    
    try:
        # 2. Call the function and catch the chained response
        ai_response = run_timeline_sequencer(mock_code, mock_signals)
        print("\n--- Final Chained LLM Timeline Sequence Output ---")
        print(ai_response)
    except FileNotFoundError as e:
        print(f"\n❌ Error Caught Successfully:\n{e}")