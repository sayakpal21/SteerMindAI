# agents/rootcause_agent.py
import os
import json
from utils.llm_gateway import MultiLLMManager
from agents.limit import *

def run_rootcause_analysis(
    fault_code: str,  
    system_prompt_file: str = "prompts/rootcause_prompt.txt",
) -> str:
    """Reads rootcause_prompt.txt to deduce failure mechanics.
    Enforces a strict prompt chaining layer to isolate primary failure modes.
    Raises FileNotFoundError if the prompt file is missing.
    """
    # 1. Enforce strict file checking (No fallback system_instruction allowed)
    if not os.path.exists(system_prompt_file):
        raise FileNotFoundError(f"CRITICAL ERROR: Required prompt file missing at '{system_prompt_file}'")
        
    with open(system_prompt_file, "r", encoding="utf-8") as f:
        system_instruction = f.read()

    ai_hub = MultiLLMManager()

    # --- PROMPT CHAINING LAYER ---
    # Step 1: Perform raw forensic analysis of the target diagnostic trouble code
    initial_payload = f"TARGET FAULT VECTOR DTC: {fault_code}"
    
    print(f"🕵️‍♂️ [Root Cause] Analyzing active fault signature: {fault_code}...")
    
    raw_analysis = ai_hub.invoke_agent(
        system_instruction=system_instruction,
        user_payload=initial_payload,
        max_tokens=1000
    )

    # Step 2: Chain the output into a second user prompt for definitive engineering synthesis
    chained_user_payload = (
        f"Based on this structural engineering failure analysis context:\n{raw_analysis}\n\n"
        f"Refine this into a definitive, crisp, engineering-grade Root Cause Report. "
        f"Format explicitly with: \n"
        f"1. Primary Physical Mechanism of Failure\n"
        f"2. High-Probability Component Attributions (Max 2)"
    )

    # Return the final chained output
    return ai_hub.invoke_agent(
        system_instruction="Role: Chief Automotive Engineering & Fault Tree Isolation Specialist.",
        user_payload=chained_user_payload,
        max_tokens=1000
    )

if __name__ == "__main__":
    # 1. Create mock environment parameters for quick local verification testing
    mock_code = "C1044"
    print("Testing rootcause_agent with Chained Prompts...")
    
    # Quick creation of the prompt file if running a local test scaffold
    os.makedirs("prompts", exist_ok=True)
    with open("prompts/rootcause_prompt.txt", "w", encoding="utf-8") as f:
        f.write("Role: Automotive Functional Safety Engineer. Objective: Deduce hardware physics behind DTC codes.")

    try:
        # 2. Call the function and catch the chained response
        ai_response = run_rootcause_analysis(mock_code)
        print("\n--- Final Chained LLM Root Cause Report Output ---")
        print(ai_response)
    except FileNotFoundError as e:
        print(f"\n❌ Error Caught Successfully:\n{e}")