# agents/rootcause_agent.py
import os
from utils.llm_gateway import MultiLLMManager

def run_simple_diagnosis(fault_code: str, metric_telemetry: str) -> str:
    """
    Loads a static prompt file and fires an evaluation request through
    the auto-switching LLM gateway.
    """
    # 1. Read the static prompt instructions from the text file
    prompt_path = "prompts/rootcause_prompt.txt"
    if os.path.exists(prompt_path):
        with open(prompt_path, "r") as f:
            system_instruction = f.read()
    else:
        # Simple fallback text if the file is missing
        system_instruction = "You are an automotive engineer. Explain the fault in 1 sentence."

    # 2. Package the variables into a clean user message
    user_payload = f"""
    ANALYSIS TARGET:
    - Active Fault Code: {fault_code}
    - Sensor Reading: {metric_telemetry}
    """

    # 3. Initialize the gateway (it auto-detects if you are using Gemini or OpenAI keys)
    ai_hub = MultiLLMManager()

    # 4. Invoke the model and pass back the result string
    response_text = ai_hub.invoke_agent(
        system_instruction=system_instruction,
        user_payload=user_payload,
        max_tokens=1000  # Low token limits keep it fast and cheap
    )
    
    return response_text

# =====================================================================
# 🏁 QUICK DEMO RUNNER
# =====================================================================
if __name__ == "__main__":
    print("🔬 Simulating a live diagnostic agent run...")
    
    # Example input data mapping a cascading electrical overload
    sample_code = "C1044"
    sample_metrics = "Motor current spiked to 46.5 Amps followed instantly by a voltage drop down to 10.8 Volts."
    
    # Run the function
    result_diagnosis = run_simple_diagnosis(sample_code, sample_metrics)
    
    print("\n📊 ──────── AGENT OUTPUT ────────")
    print(result_diagnosis)
    print("──────────────────────────────────")