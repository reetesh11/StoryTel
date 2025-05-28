# agents/crew/ollama_llm.py
from langchain.llms.base import LLM
from typing import Any, List, Optional, Dict
import requests
import os
from dotenv import load_dotenv
from langchain.callbacks.manager import CallbackManagerForLLMRun

from pydantic import Field

class OllamaLLM(LLM):

    # Define the fields that can be set
    base_url: str = Field(default="http://localhost:11434")
    model_name: str = Field(default="phi")

    def __init__(self, **kwargs):
        # Load environment variables
        load_dotenv()

        # Set default values from environment variables
        kwargs.setdefault('base_url', os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
        kwargs.setdefault('model_name', os.getenv("OLLAMA_MODEL", "phi"))

        
        super().__init__(**kwargs)
        
    def _call(self,
              prompt: str,
              stop: Optional[List[str]] = None,
              run_manager: Optional[CallbackManagerForLLMRun] = None,
              **kwargs: Any,
            ) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            print(f"Error calling Ollama: {str(e)}")
            return f"Error: {str(e)}"
            
    @property
    def _llm_type(self) -> str:
        return "ollama"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get the identifying parameters."""
        return {
            "base_url": self._base_url,
            "model_name": self._model_name
        }