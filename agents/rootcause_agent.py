## agents/rootcause_agent.py
import json
from utils.llm_gateway import MultiLLMManager


def run_rootcause_analysis(
    fault_code: str,  
    system_prompt_file: str = "prompts/rootcause_prompt.txt",
) -> str:
    """
    Runs root cause analysis.

    Args:
        user_payload: Raw extracted DTC data (JSON string or plain text).
        system_prompt_file: Path to the system prompt text file.
    """

    with open(system_prompt_file, "r", encoding="utf-8") as f:
        system_instruction = f.read()

    ai_hub = MultiLLMManager()

    user_payload = json.dumps(fault_code, indent=2)

    response = ai_hub.invoke_agent(
        system_instruction=system_instruction,
        user_payload=user_payload,
        max_tokens=150,)

    print("System Instruction: ", system_instruction)
    print("fault_code: ", user_payload)
    print("🤖 Invoking root cause analysis agent response...", response)

    return response
