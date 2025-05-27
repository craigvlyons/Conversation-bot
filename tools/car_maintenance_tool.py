import json
from datetime import datetime

class CarMaintenanceTool:
    def __init__(self, storage_path="car_memory.json"):
        self.storage_path = storage_path
        self.data = self._load()

    def name(self):
        return "car_maintenance"
    
    def triggers(self):
        return ["car", "oil", "filter", "maintenance", "jeep", "subaru", "mileage", "air filter"]

    def _load(self):
        try:
            with open(self.storage_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save(self):
        with open(self.storage_path, "w") as f:
            json.dump(self.data, f, indent=2)

    async def run(self, user_input):
        # Very basic keyword logic. Replace with LLM extraction later
        if "changed" in user_input and "filter" in user_input:
            car = "jeep" if "jeep" in user_input.lower() else "subaru"
            mileage = self._extract_number(user_input)
            date = datetime.now().isoformat()
            record = {"item": "air filter", "mileage": mileage, "date": date}
            self.data.setdefault(car, {}).setdefault("air filter", []).append(record)
            self._save()
            return f"Logged air filter change for {car} at {mileage} miles."

        elif "when" in user_input.lower() and "air filter" in user_input.lower():
            car = "jeep" if "jeep" in user_input.lower() else "subaru"
            changes = self.data.get(car, {}).get("air filter", [])
            if changes:
                last = changes[-1]
                return f"Last {car} air filter change was at {last['mileage']} miles on {last['date']}."
            return f"No air filter history found for {car}."

        return "Sorry, I couldn't process that maintenance update."

    def _extract_number(self, text):
        import re
        match = re.search(r"\b(\d{3,6})\b", text)
        return int(match.group(1)) if match else None
