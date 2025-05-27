import os
import requests
import json
from .base_tool import BaseTool
from models.cities import get_city, City

class WeatherTool(BaseTool):
    def name(self):
        return "weather"
    
    def triggers(self):
        return ["weather", "forecast", "temperature"]

    async def run(self, user_input: str) -> str:
        city_name = await self.extract_location(user_input)
        return self.get_weather(city_name)

    def get_weather(self, location):
        if isinstance(location, City):
            city = location
        else:
            city = get_city(location)

        if not city:
            return f"City '{location}' not found."

        url = f"https://api.open-meteo.com/v1/forecast?latitude={city.latitude}&longitude={city.longitude}&current_weather=true"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            current = data.get("current_weather")
            if current:
                temp_c = current.get("temperature")
                temp_f = (temp_c * 9/5) + 32
                return f"The temperature in {city.name} is {temp_f:.1f}°F."
            else:
                return f"Weather data not available for {city.name}."
        else:
            return f"Failed to fetch weather data for {city.name}."

    async def extract_location(self, user_input):
        from pydantic_ai import Agent
        from pydantic_ai.models.gemini import GeminiModel

        api_key = os.getenv("GEMINI_KEY")
        model = GeminiModel(model_name="gemini-1.5-flash", api_key=api_key)
        agent = Agent(model)

        prompt = (
            f"Extract the city name from this sentence. "
            f"If no city is mentioned, return 'Colorado Springs'.\n"
            f"Sentence: '{user_input}'\nCity:"
        )
        response = await agent.run(prompt)
        city = response.data.strip()
        return city
