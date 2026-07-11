# agents/recommendation_agent.py
import os
from utils.llm_gateway import MultiLLMManager
from agents.limit import *

def run_maintenance_advisory(root_cause_verdict: str) -> str:
    """Reads recommend_prompt.txt and issues concise field repair actions.
    Raises FileNotFoundError if the prompt file is missing.
    """
    prompt_path = "prompts/recommend_prompt.txt"

    # Strict file check
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"CRITICAL ERROR: Required prompt file missing at '{prompt_path}'")

    # Load system prompt
    with open(prompt_path, "r", encoding="utf-8") as f:
        system_instruction = f.read()

    # Build minimal user payload
    user_payload = f"{root_cause_verdict}"

    # Invoke agent with only system + user prompt
    ai_hub = MultiLLMManager()
    return ai_hub.invoke_agent(
        system_instruction=system_instruction,
        user_payload=user_payload,
        max_tokens=MAX_TOKENS
    )


if __name__ == "__main__":
    mock_verdict = "DTC P0301 detected: Cylinder 1 Misfire. Corroded spark plug thread or faulty ignition coil boot suspected."
    print("Testing recommendation_agent with minimal prompt...")
    
    try:
        ai_response = run_maintenance_advisory(mock_verdict)
        print("\n--- Final Maintenance Advisory ---")
        print(ai_response)
    except FileNotFoundError as e:
        print(f"\n❌ Error Caught Successfully:\n{e}")
