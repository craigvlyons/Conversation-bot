# agents/ollama_agent.py
import asyncio
import httpx

class LocalLLMAgent:
    def __init__(self, model="phi3:mini", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    async def get_city_from_text(self, prompt):
        # Use httpx for async HTTP requests to Ollama
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            # Ollama returns the result in 'response' or 'message'
            city = data.get("response") or data.get("message", "")
            return city.strip()