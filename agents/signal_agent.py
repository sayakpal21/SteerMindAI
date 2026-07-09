# agents/signal_agent.py
import os
from utils.llm_gateway import MultiLLMManager

def run_signal_analysis(metric_telemetry: str) -> str:
    """Reads signal_prompt.txt and isolates sensor boundaries.
    Raises FileNotFoundError if the prompt file is missing.
    """
    prompt_path = "prompts/signal_prompt.txt"
    
    # 1. Enforce strict file checking (No fallback system_instruction allowed)
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"CRITICAL ERROR: Required prompt file missing at '{prompt_path}'")
        
    with open(prompt_path, "r", encoding="utf-8") as f:
        system_instruction = f.read()

    ai_hub = MultiLLMManager()

    # --- PROMPT CHAINING LAYER ---
    # Step 1: Perform raw extraction of sensor spikes and boundary data
    initial_payload = f"INPUT TELEMETRY METRICS:\n{metric_telemetry}"
    raw_bounds = ai_hub.invoke_agent(
        system_instruction=system_instruction,
        user_payload=initial_payload,
        max_tokens=1000
    )

    # Step 2: Chain the output into a second user prompt for definitive anomaly synthesis
    chained_user_payload = (
        f"Based on these isolated sensor boundaries:\n{raw_bounds}\n\n"
        f"Format this strictly as an executive summary of numerical anomalies. "
        f"Identify and prioritize the 2 most severe points of deviation."
    )

    # Return the final chained output
    return ai_hub.invoke_agent(
        system_instruction="Role: Senior CAN Validation & Signal Processing Engineer.",
        user_payload=chained_user_payload,
        max_tokens=1000
    )

if __name__ == "__main__":
    # 1. Create a fake telemetry metrics feed to mimic CAN bus signals
    mock_telemetry = "Voltage levels fluctuating between 11.2V and 14.8V within 50ms windows. Current peak registered at 52A."
    
    print("Testing signal_agent with Chained Prompts...")
    
    try:
        # 2. Call the function and catch the chained response
        ai_response = run_signal_analysis(mock_telemetry)
        print("\n--- Final Chained LLM Signal Analysis Output ---")
        print(ai_response)
    except FileNotFoundError as e:
        print(f"\n❌ Error Caught Successfully:\n{e}")