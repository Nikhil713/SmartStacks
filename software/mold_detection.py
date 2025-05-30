from weather_api import get_weather

def compute_mold_risk(temp, humidity):
    # Simple model: risk if humidity > 65% and temp between 15–30°C
    if temp is None or humidity is None:
        return "UNKNOWN"
    if humidity > 65 and 15 <= temp <= 30:
        return "HIGH"
    elif humidity > 55:
        return "MODERATE"
    else:
        return "LOW"

temp, humidity = get_weather()
risk = compute_mold_risk(temp, humidity)

print(f"Weather: {temp}°C, {humidity}% RH")
print(f"Mold Risk Level: {risk}")
