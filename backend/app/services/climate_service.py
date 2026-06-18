import os
import requests
from dotenv import load_dotenv

from app.services.supabase_service import (
    save_climate_reading,
    save_prediction
)

from app.services.prediction_service import calculate_prediction

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
AQICN_API_KEY = os.getenv("AQICN_API_KEY")


def get_weather(city: str):

    weather_url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}"
        f"&appid={OPENWEATHER_API_KEY}"
        f"&units=metric"
    )

    weather_response = requests.get(weather_url)

    if weather_response.status_code != 200:
        return {"error": "Weather API failed"}

    weather = weather_response.json()

    aqi_url = (
        f"https://api.waqi.info/feed/{city}/"
        f"?token={AQICN_API_KEY}"
    )

    aqi_response = requests.get(aqi_url)

    aqi = None
    pm25 = None
    pm10 = None

    if aqi_response.status_code == 200:

        aqi_data = aqi_response.json()

        if aqi_data["status"] == "ok":

            aqi = aqi_data["data"].get("aqi")

            iaqi = aqi_data["data"].get("iaqi", {})

            pm25 = iaqi.get("pm25", {}).get("v")
            pm10 = iaqi.get("pm10", {}).get("v")

    record = {
        "city": city,
        "aqi": aqi,
        "pm25": pm25,
        "pm10": pm10,
        "temperature": weather["main"]["temp"],
        "humidity": weather["main"]["humidity"],
        "rainfall": 0,
        "wind_speed": weather["wind"]["speed"]
    }

    # Save climate data
    save_climate_reading(record)

    # Calculate prediction
    prediction = calculate_prediction(record)

    prediction_record = {
        "user_id": None,
        "city": city,
        "risk_score": prediction["risk_score"],
        "risk_level": prediction["risk_level"],
        "esg_score": prediction["esg_score"]
    }

    # Save prediction
    save_prediction(prediction_record)

    # Return combined response
    return {
        **record,
        **prediction
    }