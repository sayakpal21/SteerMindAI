# utils/llm_gateway.py
import os
from dotenv import load_dotenv

# 🔍 Automatically find and load the .env file from the project root
load_dotenv()

class MultiLLMManager:
    def __init__(self):
        """
        Automatically detects which API key is active in the environment
        and selects the appropriate LLM provider.
        Priority:
            1. OpenAI
            2. Gemini
            3. Hugging Face
        """

        # Load API keys
        #self.openai_key = os.getenv("OPENAI_API_KEY")
        #self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")

        self.openai_key = None
        self.gemini_key = None
        self.hf_key = None

        #self.hf_key = os.getenv("HG_API_KEY")

        if self.openai_key:
            self.provider = "openai"
            #self.model_name = "gpt-4o-mini"
            #self.model_name = "gpt-5.3-codex"
            self.model_name = "gpt-5.2"
            self.api_key = self.openai_key
            print("🔌 Gateway: Auto-Switched to OPENAI Backend")

        elif self.gemini_key:
            self.provider = "gemini"
            self.model_name = "gemini-3.5-flash"
            self.api_key = self.gemini_key
            print("🔌 Gateway: Auto-Switched to GEMINI Backend")

        elif self.hf_key:
            self.provider = "huggingface"
            self.model_name = "Qwen/Qwen2.5-7B-Instruct"
            self.model_name = "meta-llama/Llama-3.1-8B-Instruct"
            #self.model_name = "mistralai/Mistral-7B-Instruct-v0.3"
            # Alternative models:
            # "mistralai/Mistral-7B-Instruct-v0.3"
            # "meta-llama/Llama-3.2-3B-Instruct"
            self.api_key = self.hf_key
            print("🔌 Gateway: Auto-Switched to HUGGING FACE Backend")
        
        elif self.groq_key:
            self.provider = "groq"
            self.model_name = "llama-3.3-70b-versatile"
            self.api_key = self.groq_key

            print("🔌 Gateway: Auto-Switched to GROQ Backend")


        else:
            raise RuntimeError(
                "No LLM API key found.\n"
                "Please set one of:\n"
                "  OPENAI_API_KEY\n"
                "  GEMINI_API_KEY\n"
                "  HUGGINGFACE_API_KEY or HF_TOKEN"
            )
        
        print('self.provider: ',self.provider)
        print('self.model_name: ',self.model_name)
    
    def invoke_agent(self, system_instruction: str, user_payload: str, max_tokens: int) -> str:
            """Routes the request to the selected LLM provider."""

            # ─── 🟢 GEMINI ──────────────────────────────────────────────────────────
            if self.provider == "gemini":
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=self.gemini_key)

                try:
                    response = client.models.generate_content(
                        model=self.model_name,
                        contents=user_payload,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.1,
                            max_output_tokens=max_tokens,
                        ),
                    )
                    return response.text

                except Exception as e:
                    return f"Gemini Error: {e}"

            # ─── 🔲 OPENAI ──────────────────────────────────────────────────────────
            elif self.provider == "openai":
                from openai import OpenAI

                client = OpenAI(api_key=self.openai_key)

                try:
                    response = client.chat.completions.create(
                        model=self.model_name,
                        temperature=0.1,
                        max_tokens=max_tokens,
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": user_payload},
                        ],
                    )

                    return response.choices[0].message.content

                except Exception as e:
                    return f"OpenAI Error: {e}"

            # ─── 🟠 HUGGING FACE ────────────────────────────────────────────────────
            elif self.provider == "huggingface":
                from huggingface_hub import InferenceClient

                client = InferenceClient(
                    provider="hf-inference",
                    api_key=self.api_key,
                )

                try:
                    response = client.chat.completions.create(
                        model=self.model_name,
                        temperature=0.1,
                        max_tokens=max_tokens,
                        messages=[
                            {
                                "role": "system",
                                "content": system_instruction,
                            },
                            {
                                "role": "user",
                                "content": user_payload,
                            },
                        ],
                    )

                    return response.choices[0].message.content

                except Exception as e:
                    return f"Hugging Face Error: {e}"
            
                        # ─── 🟣 GROQ ────────────────────────────────────────────────────────────
            elif self.provider == "groq":
                from groq import Groq

                client = Groq(
                    api_key=self.groq_key
                )

                try:
                    response = client.chat.completions.create(
                        model=self.model_name,
                        temperature=0.1,
                        max_tokens=max_tokens,
                        messages=[
                            {
                                "role": "system",
                                "content": system_instruction,
                            },
                            {
                                "role": "user",
                                "content": user_payload,
                            },
                        ],
                    )

                    return response.choices[0].message.content

                except Exception as e:
                    return f"Groq Error: {e}"

            return "Error: No valid provider configured."
    
    """
    def invoke_agent(self, system_instruction: str, user_payload: str, max_tokens: int) -> str:
        #Routes the request to whichever backend was automatically selected.
        
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
        """
        