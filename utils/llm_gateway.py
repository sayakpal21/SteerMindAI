# utils/llm_gateway.py
import os
from dotenv import load_dotenv

# 🔍 Automatically find and load the .env file from the project root
load_dotenv()

class MultiLLMManager:
    def __init__(self):
        """
        Automatically detects which API key is active in your environment
        and selects the appropriate provider.
        """
        # 1. Look for active environment variables
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")

        # 2. Automatically switch providers based on what key is available
        if self.openai_key and not self.gemini_key:
            self.provider = "openai"
            self.model_name = "gpt-4o-mini"  # Fast, affordable demo model
            print("🔌 Gateway: Auto-Switched to OPENAI Backend")
        else:
            self.provider = "gemini"
            self.model_name = "gemini-2.5-flash"
            print("🔌 Gateway: Auto-Switched to GEMINI Backend")

    def invoke_agent(self, system_instruction: str, user_payload: str, max_tokens: int) -> str:
        """Routes the request to whichever backend was automatically selected."""
        
        # ─── 🟢 OPTION A: GEMINI NATIVE ROUTE ───
        if self.provider == "gemini":
            from google import genai
            from google.genai import types
            
            # Use Gemini Key if available, fallback to OpenAI key slot if that's where your Gemini key lives
            key = self.gemini_key or self.openai_key
            client = genai.Client(api_key=key)
            try:
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=user_payload,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.1,
                        max_output_tokens=max_tokens
                    )
                )
                return response.text
            except Exception as e:
                return f"Gemini Error: {str(e)}"

        # ─── 🔲 OPTION B: OPENAI NATIVE ROUTE ───
        elif self.provider == "openai":
            from openai import OpenAI
            
            client = OpenAI(api_key=self.openai_key)
            try:
                response = client.chat.completions.create(
                    model=self.model_name,
                    max_tokens=max_tokens,
                    temperature=0.1,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_payload}
                    ]
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"OpenAI Error: {str(e)}"

        return "Error: No valid provider configured."