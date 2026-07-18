# tools/sightseeing.py


import time
import googlemaps

from dotenv import load_dotenv
import os


from config import GOOGLE_MAPS_API_KEY


# Daily limit tracking – global variable (request-scoped if orchestrator re‑creates)
_calls_made = {"places": 0}
DAILY_LIMIT = 330

def fetch_sightseeing(location: str) -> list:
    global _calls_made

    if _calls_made["places"] >= DAILY_LIMIT:
        raise RuntimeError("Daily Places-API limit reached")

    _calls_made["places"] += 1
    time.sleep(0.1)

    results = (
        gmaps.places(
            query=f"tourist attractions in {location}"
        )
        .get("results", [])[:5]
    )

    return [
        {
            "name": p["name"],
            "address": p.get("formatted_address"),
            "rating": p.get("rating"),
        }
        for p in results
    ]