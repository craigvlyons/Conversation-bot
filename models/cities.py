import requests

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

# In-memory cache for cities
_city_cache = {}

def get_city(city_name):
    print(f"[get_city] Looking up city: {city_name}")
    city_name_lower = city_name.lower()
    if city_name_lower in _city_cache:
        print(f"[get_city] Found in cache: {city_name_lower}")
        return _city_cache[city_name_lower]
    # Fetch from Open-Meteo geocoding API
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}"
    print(f"[get_city] Fetching from API: {url}")
    response = requests.get(url)
    print(f"[get_city] API response status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        results = data.get("results")
        if results:
            city_data = results[0]
            print(f"[get_city] API result: {city_data}")
            city = City(
                name=city_data.get("name"),
                latitude=city_data.get("latitude"),
                longitude=city_data.get("longitude"),
                country=city_data.get("country")
            )
            _city_cache[city_name_lower] = city
            return city
        else:
            print(f"[get_city] No results for: {city_name}")
    else:
        print(f"[get_city] Failed to fetch city: {city_name}")
    return None
