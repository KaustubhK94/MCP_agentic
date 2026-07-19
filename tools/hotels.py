# tools/hotels.py

import requests
from dotenv import load_dotenv
import os
from config import SERPAPI_API_KEY


def search_hotels(
    destination_city: str,
    check_in_date: str,
    check_out_date: str,
    adults: int = 2
) -> list:
    """
    Search hotels via SerpAPI Google Hotels.
    Returns a list of hotel properties with name, price, rating, address, link.
    """
    params = {
        "engine": "google_hotels",
        "q": destination_city,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "adults": adults,
        "currency": "USD",
        "gl": "us",
        "hl": "en",
        "api_key": SERPAPI_API_KEY
    }

    resp = requests.get("https://serpapi.com/search", params=params)
    resp.raise_for_status()
    data = resp.json()

    hotels = []
    if "properties" in data:
        # Only take the first hotel for testing
        for h in data["properties"]:  
            hotels.append({
                "name": h.get("name"),
                "price": h.get("rate_per_night", {}).get("lowest"),
                "rating": h.get("overall_rating"),
                "address": h.get("address"),
                # "link": h.get("link")
            })
    return hotels