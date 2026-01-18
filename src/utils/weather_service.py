import requests

class WeatherService:
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"

    def get_current_weather(self, lat, lon):
        """
        Fetches current weather for the given coordinates.
        Returns a dictionary with temp, weather code, and description.
        """
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": "true"
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if "current_weather" in data:
                cw = data["current_weather"]
                return {
                    "temperature": cw["temperature"],
                    "weathercode": cw["weathercode"],
                    "description": self._get_weather_description(cw["weathercode"])
                }
            return None
            
        except requests.RequestException as e:
            print(f"Weather API error: {e}")
            return None

    def get_forecast(self, lat, lon):
        """
        Fetches 7-day forecast.
        """
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "timezone": "auto"
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if "daily" in data:
                return data["daily"]
            return None
        except Exception as e:
            print(f"Forecast error: {e}")
            return None

    def _get_weather_description(self, code):
        """
        Maps WMO Weather interpretation codes (WW) to emoji/text.
        """
        # Codes from Open-Meteo docs
        if code == 0: return "☀️ Clear sky"
        if code in [1, 2, 3]: return "⛅ Partly cloudy"
        if code in [45, 48]: return "🌫️ Fog"
        if code in [51, 53, 55]: return "🌧️ Drizzle"
        if code in [56, 57]: return "🌨️ Freezing Drizzle"
        if code in [61, 63, 65]: return "🌧️ Rain"
        if code in [66, 67]: return "🌨️ Freezing Rain"
        if code in [71, 73, 75]: return "❄️ Snow"
        if code == 77: return "❄️ Snow grains"
        if code in [80, 81, 82]: return "🌧️ Rain showers"
        if code in [85, 86]: return "❄️ Snow showers"
        if code == 95: return "⚡ Thunderstorm"
        if code in [96, 99]: return "⛈️ Thunderstorm with hail"
        
        return "Unknown"
