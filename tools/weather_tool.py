"""
Weather Tool for Convo Bot Agent
This module provides a function to get the current weather for a given location using the Open-Meteo API.
"""

import requests
import json
from models.cities import get_city

def fetch_weather(location: str, city_lookup_func=get_city) -> str:
    print(f"[fetch_weather] Called with location: {location}")
    # If location is already a City object, use it directly
    from models.cities import City
    if isinstance(location, City):
        city = location
    else:
        if not location:
            print("[fetch_weather] No location provided.")
            return "Location is required."
        city = city_lookup_func(location)
    print(f"[fetch_weather] City lookup result: {city}")
    if not city:
        print(f"[fetch_weather] City '{location}' not found.")
        return f"City '{location}' not found."
    url = f"https://api.open-meteo.com/v1/forecast?latitude={city.latitude}&longitude={city.longitude}&current_weather=true"
    print(f"[fetch_weather] Fetching weather from: {url}")
    response = requests.get(url)
    print(f"[fetch_weather] Weather API response status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        current = data.get("current_weather")
        print(f"[fetch_weather] Current weather data: {current}")
        if current:
            weather = {
                "location": city.name,
                "country": city.country,
                "latitude": city.latitude,
                "longitude": city.longitude,
                "temperature": f"{current.get('temperature')}°C",
                "windspeed": f"{current.get('windspeed')} km/h",
                "weathercode": current.get('weathercode'),
                "time": current.get('time')
            }
            print(f"[fetch_weather] Returning weather: {weather}")
            return json.dumps(weather, ensure_ascii=False)
        else:
            print(f"[fetch_weather] Weather data not available for {location}.")
            return f"Weather data not available for {location}."
    else:
        print(f"[fetch_weather] Failed to fetch weather data for {location}.")
        return f"Failed to fetch weather data for {location}."

class WeatherTool:
    def name(self):
        return "weather"

    def get_weather(self, location, city_name):
        if location:
            # Use location object (has lat/lon)
            return fetch_weather(location)
        else:
            # Fallback: try to resolve city_name, or return a default/error
            city = get_city(city_name)
            if city:
                return fetch_weather(city)
            else:
                return f"City '{city_name}' not found."
