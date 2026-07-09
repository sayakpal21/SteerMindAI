# agents/signal_agent.py
import os
from utils.llm_gateway import MultiLLMManager

def run_signal_analysis(metric_telemetry: str) -> str:
    """Reads signal_prompt.txt and isolates sensor boundaries."""
    prompt_path = "prompts/signal_prompt.txt"
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_instruction = f.read()
    else:
        system_instruction = "Role: CAN Validation Engineer. Identify numerical anomalies in 2 points."

    user_payload = f"INPUT TELEMETRY METRICS:\n{metric_telemetry}"

    ai_hub = MultiLLMManager()
    return ai_hub.invoke_agent(
        system_instruction=system_instruction,
        user_payload=user_payload,
        max_tokens=150
    )