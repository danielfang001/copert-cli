import requests

class WeatherTool:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.weatherapi.com/v1/current.json"

    def get_weather(self, city: str) -> str:
        params = {
            "key": self.api_key,
            "q": city,
            "aqi": "no"
        }
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            location = data.get("location", {})
            current = data.get("current", {})
            if location and current:
                location_name = location.get("name")
                region = location.get("region")
                temp_c = current.get("temp_c")
                condition = current.get("condition", {}).get("text")
                return f"Weather in {location_name}, {region}: {temp_c}°C, {condition}."
            else:
                return "Could not retrieve complete weather information."
        else:
            return f"Failed to get weather data: {response.status_code}"
