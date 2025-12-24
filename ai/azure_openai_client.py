import os
import logging
from openai import AzureOpenAI, OpenAI

logger = logging.getLogger(__name__)

class EngineeringAIClient:
    def __init__(self):
        self.client = None
        self.deployment_name = None
        self.is_azure = False
        
        # 1. Try Azure First
        azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        azure_key = os.environ.get("AZURE_OPENAI_API_KEY")
        self.deployment_name = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4") # Default deploy name
        
        if azure_endpoint and azure_key:
            logger.info("Initializing Azure OpenAI Client...")
            self.client = AzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_key=azure_key,
                api_version="2024-02-15-preview" # Update as needed
            )
            self.is_azure = True
        
        # 2. Fallback to Standard OpenAI
        elif os.environ.get("OPENAI_API_KEY"):
            logger.info("Initializing Standard OpenAI Client...")
            self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            self.is_azure = False
            # For standard OpenAI, the 'model' arg uses the name directly (e.g. gpt-4)
            # We reuse deployment_name var as the model name
            if not os.environ.get("AZURE_OPENAI_DEPLOYMENT"):
                self.deployment_name = "gpt-4-turbo-preview"
        
        else:
            logger.warning("No OpenAI credentials found (AZURE_OPENAI_API_KEY or OPENAI_API_KEY). AI features will fail.")

    def generate_chat_completion(self, system_prompt, user_prompt, temperature=0.0):
        """
        Generates a chat completion with JSON mode enforcement where possible.
        """
        if not self.client:
            raise ValueError("AI Client not initialized. Check credentials.")

        try:
            # Common params
            params = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature,
                "response_format": {"type": "json_object"}
            }
            
            if self.is_azure:
                params["model"] = self.deployment_name 
            else:
                params["model"] = self.deployment_name

            response = self.client.chat.completions.create(**params)
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"AI Generation Failed: {e}")
            raise
