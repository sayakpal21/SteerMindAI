# agents/learning_agent.py
import os
from utils.llm_gateway import MultiLLMManager
from agents.limit import *


def run_knowledge_caching(pipeline_summary: str) -> str:
    """Reads learning_prompt.txt to extract training features for MLOps staging workflows.
    Raises FileNotFoundError if the prompt file is missing.
    """
    prompt_path = "prompts/learning_prompt.txt"
    
    # 1. Enforce strict file checking (No fallback system_instruction allowed)
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"CRITICAL ERROR: Required prompt file missing at '{prompt_path}'")
        
    with open(prompt_path, "r", encoding="utf-8") as f:
        system_instruction = f.read()

    ai_hub = MultiLLMManager()

    # --- PROMPT CHAINING LAYER ---
    # Step 1: Extract raw training features and performance weights
    initial_payload = f"UNIFIED PIPELINE PERFORMANCE FOOTPRINT:\n{pipeline_summary}"
    raw_features = ai_hub.invoke_agent(
        system_instruction=system_instruction,
        user_payload=initial_payload,
        max_tokens=MAX_TOKENS
    )

    # Step 2: Chain the output into a second user prompt for definitive weight staging
    chained_user_payload = (
        f"Based on these raw extraction parameters:\n{raw_features}\n\n"
        f"Format this strictly as an optimized feature map weight configuration. "
        f"Consolidate structural logs under 50 tokens if possible, ensuring metrics are easily machine-parseable."
    )

    # Return the final chained output
    return ai_hub.invoke_agent(
        system_instruction="Role: Principal MLOps Platform Optimization Engineer.",
        user_payload=chained_user_payload,
        max_tokens=MAX_TOKENS
    )

if __name__ == "__main__":
    # 1. Create a fake pipeline summary to mimic real data
    mock_summary = "Epoch 10/10 - loss: 0.234 - val_loss: 0.251 - Staging: Success"
    
    print("Testing learning_agent with Chained Prompts...")
    
    try:
        # 2. Call the function and catch the chained response
        ai_response = run_knowledge_caching(mock_summary)
        print("\n--- Final Chained LLM Knowledge Staging Output ---")
        print(ai_response)
    except FileNotFoundError as e:
        print(f"\n❌ Error Caught Successfully:\n{e}")