# agents/recommendation_agent.py
import os
from utils.llm_gateway import MultiLLMManager

def run_maintenance_advisory(root_cause_verdict: str) -> str:
    """Reads recommend_prompt.txt to issue high-precision field repair actions.
    Raises FileNotFoundError if the prompt file is missing.
    """
    prompt_path = "prompts/recommend_prompt.txt"
    
    # 1. Enforce strict file checking (No fallback system_instruction allowed)
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"CRITICAL ERROR: Required prompt file missing at '{prompt_path}'")
        
    with open(prompt_path, "r", encoding="utf-8") as f:
        system_instruction = f.read()

    ai_hub = MultiLLMManager()

    # --- PROMPT CHAINING LAYER ---
    # Step 1: Generate initial raw structural recommendations
    initial_payload = f"ENGINEERING ROOT CAUSE ANALYSIS VERDICT:\n{root_cause_verdict}"
    raw_recommendations = ai_hub.invoke_agent(
        system_instruction=system_instruction,
        user_payload=initial_payload,
        max_tokens=500
    )

    # Step 2: Chain the output into a second user prompt for final refinement
    chained_user_payload = (
        f"Based on these raw diagnostic steps:\n{raw_recommendations}\n\n"
        f"Format this strictly as an executive maintenance field manual advisory. "
        f"Ensure it highlights tool requirements and safety checks clearly."
    )

    # Return the final chained output
    return ai_hub.invoke_agent(
        system_instruction="Role: Senior MLOps & Quality Assurance Systems Inspector.",
        user_payload=chained_user_payload,
        max_tokens=1000
    )

if __name__ == "__main__":
    mock_verdict = "DTC P0301 detected: Cylinder 1 Misfire. Corroded spark plug thread or faulty ignition coil boot suspected."
    print("Testing recommendation_agent with Chained Prompts...")
    
    try:
        ai_response = run_maintenance_advisory(mock_verdict)
        print("\n--- Final Chained LLM Maintenance Advisory ---")
        print(ai_response)
    except FileNotFoundError as e:
        print(f"\n❌ Error Caught Successfully:\n{e}")