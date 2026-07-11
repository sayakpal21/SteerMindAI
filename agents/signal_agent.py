# agents/signal_agent.py
import os
from utils.llm_gateway import MultiLLMManager
from agents.limit import *


def run_signal_analysis(metric_telemetry: str) -> str:
    """Reads signal_prompt.txt and isolates sensor boundaries.
    Uses only system + user prompt. Raises FileNotFoundError if missing.
    """
    prompt_path = "prompts/signal_prompt.txt"

    # Strict file check
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"CRITICAL ERROR: Required prompt file missing at '{prompt_path}'")

    # Load system prompt
    with open(prompt_path, "r", encoding="utf-8") as f:
        system_instruction = f.read()

    # Minimal user payload
    user_payload = f"{metric_telemetry}"

    # Invoke agent directly
    ai_hub = MultiLLMManager()
    return ai_hub.invoke_agent(
        system_instruction=system_instruction,
        user_payload=user_payload,
        max_tokens=MAX_TOKENS
    )


if __name__ == "__main__":
    mock_telemetry = "Voltage levels fluctuating between 11.2V and 14.8V within 50ms windows. Current peak registered at 52A."
    print("Testing signal_agent with minimal prompt...")

    try:
        ai_response = run_signal_analysis(mock_telemetry)
        print("\n--- Final Signal Analysis Output ---")
        print(ai_response)
    except FileNotFoundError as e:
        print(f"\n❌ Error Caught Successfully:\n{e}")
