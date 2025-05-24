import requests
from functools import lru_cache

class City:
    def __init__(self, name, latitude, longitude, country):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.country = country

    def to_dict(self):
        return {
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "country": self.country
        }

    def __repr__(self):
        return f"City(name={self.name}, lat={self.latitude}, lon={self.longitude}, country={self.country})"

@lru_cache(maxsize=100)
def get_city(city_name: str):
    city_name_clean = city_name.strip().lower()
    print(f"[get_city] Looking up city: {city_name_clean} (cached: {get_city.cache_info()})")

    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name_clean}"
    print(f"[get_city] Fetching from API: {url}")
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        results = data.get("results")
        if results:
            city_data = results[0]
            print(f"[get_city] API result: {city_data}")
            return City(
                name=city_data.get("name"),
                latitude=city_data.get("latitude"),
                longitude=city_data.get("longitude"),
                country=city_data.get("country")
            )
        else:
            print(f"[get_city] No results for: {city_name_clean}")
    else:
        print(f"[get_city] Failed to fetch city: {city_name_clean}")

    return None
