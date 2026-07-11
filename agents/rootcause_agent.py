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
    Uses only system + user prompt. Raises FileNotFoundError if missing.
    """
    # Strict file check
    if not os.path.exists(system_prompt_file):
        raise FileNotFoundError(f"CRITICAL ERROR: Required prompt file missing at '{system_prompt_file}'")

    # Load system prompt
    with open(system_prompt_file, "r", encoding="utf-8") as f:
        system_instruction = f.read()

    # Minimal user payload
    user_payload = f"{fault_code}"

    # Invoke agent directly
    ai_hub = MultiLLMManager()
    return ai_hub.invoke_agent(
        system_instruction=system_instruction,
        user_payload=user_payload,
        max_tokens=MAX_TOKENS
    )


if __name__ == "__main__":
    mock_code = "C1044"
    print("Testing rootcause_agent with minimal prompt...")

    try:
        ai_response = run_rootcause_analysis(mock_code)
        print("\n--- Final Root Cause Report ---")
        print(ai_response)
    except FileNotFoundError as e:
        print(f"\n❌ Error Caught Successfully:\n{e}")
