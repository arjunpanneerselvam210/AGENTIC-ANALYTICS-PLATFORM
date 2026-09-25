from typing import List, Dict, Any, Optional
import httpx
from app.core.config import settings

class OllamaClient:
    """
    Client for interacting with local Ollama LLM models without Docker.
    Supports both general agent reasoning (llama3.1:8b) and SQL generation (qwen2.5-coder:7b).
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL

    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        timeout: float = 60.0
    ) -> str:
        """
        Sends chat messages to Ollama /api/chat endpoint.
        Returns the text response from the model.
        """
        chosen_model = model or settings.OLLAMA_AGENT_MODEL
        payload = {
            "model": chosen_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "").strip()
            except httpx.ConnectError:
                raise RuntimeError(
                    f"Could not connect to Ollama at {self.base_url}. Make sure Ollama is running ('ollama serve')."
                )
            except httpx.HTTPStatusError as e:
                raise RuntimeError(f"Ollama API returned HTTP error: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                raise RuntimeError(f"Ollama generation failed: {str(e)}")

    def generate_chat_sync(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        timeout: float = 60.0
    ) -> str:
        """
        Synchronous version of generate_chat.
        """
        chosen_model = model or settings.OLLAMA_AGENT_MODEL
        payload = {
            "model": chosen_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        with httpx.Client(timeout=timeout) as client:
            try:
                response = client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "").strip()
            except httpx.ConnectError:
                raise RuntimeError(
                    f"Could not connect to Ollama at {self.base_url}. Make sure Ollama is running ('ollama serve')."
                )
            except httpx.HTTPStatusError as e:
                raise RuntimeError(f"Ollama API returned HTTP error: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                raise RuntimeError(f"Ollama generation failed: {str(e)}")

ollama_client = OllamaClient()
