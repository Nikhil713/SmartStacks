# weather_api.py

import requests
from logger import log

# API configurations
API_KEY = "76e536f0e9933666a4713c1b5eb2f94a"
CITY = "Stuttgart"
LAT = "48.7758"  # Stuttgart latitude
LON = "9.1829"   # Stuttgart longitude
URL = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}"
COUNTRY = "XX"  # Country code like "IN", "GB", "US"

def get_weather():
    try:
        response = requests.get(URL)
        data = response.json()
        # print(f"Weather data for {CITY}: {data}")
        temp = data["main"]["temp"] - 273.15
        humidity = data["main"]["humidity"]
        return temp, humidity
    except Exception as e:
        print(f"Weather API error: {e}")
        log(f"Weather API error: {e}")
        return None, None

temp, humidity = get_weather()
print(f"Temperature: {temp}C, Humidity: {humidity}%")