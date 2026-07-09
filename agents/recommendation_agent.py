# agents/recommendation_agent.py
import os
from utils.llm_gateway import MultiLLMManager

def run_maintenance_advisory(root_cause_verdict: str) -> str:
    """Reads recommend_prompt.txt to issue high-precision field repair actions."""
    prompt_path = "prompts/recommend_prompt.txt"
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_instruction = f.read()
    else:
        system_instruction = "Role: Master Technician. Provide exactly 2 precise, numbered repair steps."

    user_payload = f"ENGINEERING ROOT CAUSE ANALYSIS VERDICT:\n{root_cause_verdict}"

    ai_hub = MultiLLMManager()
    return ai_hub.invoke_agent(
        system_instruction=system_instruction,
        user_payload=user_payload,
        max_tokens=200
    )