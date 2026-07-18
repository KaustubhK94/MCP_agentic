# tools/weather.py


import requests
from datetime import datetime

from dotenv import load_dotenv
import os

from config import OPENWEATHER_API_KEY

def fetch_weather(city: str, start_date: str, end_date: str) -> dict:
    """
    Fetch 3‑hourly weather forecast for a given city and date range.
    Returns a dict mapping date (YYYY-MM-DD) to list of readings.
    """
    params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"}
    data = requests.get("https://api.openweathermap.org/data/2.5/forecast", params=params).json()

    start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()

    filtered_forecast = {}
    for entry in data.get("list", []):
        entry_dt = datetime.strptime(entry["dt_txt"], "%Y-%m-%d %H:%M:%S")
        entry_date = entry_dt.date()

        if start_dt <= entry_date <= end_dt:
            day_str = entry_date.strftime("%Y-%m-%d")
            filtered_forecast.setdefault(day_str, []).append({
                "time": entry_dt.strftime("%H:%M"),
                "temp": round(entry["main"]["temp"], 1),
                "feels_like": round(entry["main"]["feels_like"], 1),
                "condition": entry["weather"][0]["description"].title(),
                "humidity": entry["main"]["humidity"],
                "wind_speed": entry["wind"]["speed"]
            })

    return filtered_forecast