# agents/learning_agent.py
import os
from utils.llm_gateway import MultiLLMManager

def run_knowledge_caching(pipeline_summary: str) -> str:
    """Reads learning_prompt.txt to extract training features for MLOps staging workflows."""
    prompt_path = "prompts/learning_prompt.txt"
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_instruction = f.read()
    else:
        system_instruction = "Role: MLOps Engineer. Output concise feature map weights under 50 tokens."

    user_payload = f"UNIFIED PIPELINE PERFORMANCE FOOTPRINT:\n{pipeline_summary}"

    ai_hub = MultiLLMManager()
    return ai_hub.invoke_agent(
        system_instruction=system_instruction,
        user_payload=user_payload,
        max_tokens=1000
    )

if __name__ == "__main__":
    # 1. Create a fake pipeline summary to mimic real data
    mock_summary = "Epoch 10/10 - loss: 0.234 - val_loss: 0.251 - Staging: Success"
    
    print("Testing learning_agent...")
    
    # 2. Call the function and catch the string response
    ai_response = run_knowledge_caching(mock_summary)
    
    # 3. Print the actual output to the terminal
    print("\n--- LLM Output Response ---")
    print(ai_response)