import os
from typing import Optional, Dict, Any

import serpapi
from config import SERPAPI_API_KEY

from utils.flight_formatter import _normalize_flight



if not SERPAPI_API_KEY:
    raise ValueError("SERPAPI_API_KEY not found in environment variables.")

client = serpapi.Client(api_key=SERPAPI_API_KEY)


TRAVEL_CLASS = {
    "ECONOMY": 1,
    "PREMIUM_ECONOMY": 2,
    "BUSINESS": 3,
    "FIRST": 4,
}



def search_flights(
    origin: str,
    destination: str,
    start_date: str,
    end_date: Optional[str] = None,
    currency: str = "USD",
    adults: int = 1,
    travel_class: str = "ECONOMY",
) -> Dict[str, Any]:
    """
    Search Google Flights using SerpAPI.
    """

    params = {
        "engine": "google_flights",
        "departure_id": origin,
        "arrival_id": destination,
        "outbound_date": start_date,
        "currency": currency,
        "adults": adults,
        "travel_class": TRAVEL_CLASS.get(travel_class.upper(), 1),
    }

    if end_date:
        params["return_date"] = end_date
        params["type"] = 1
    else:
        params["type"] = 2

    try:

        results = client.search(params)
        return {
            "best_flights": [
                _normalize_flight(f)
                for f in results.get("best_flights", [])],
            "other_flights": [
                _normalize_flight(f)
                for f in results.get("other_flights", [])],}

    except Exception as e:
        return {
            "error": str(e)}


if __name__ == "__main__":
    import json
    results = search_flights(
        origin="BOM",
        destination="BKK",
        start_date="2026-08-10",
        end_date="2026-08-17",
        currency="USD",)

    print(json.dumps(results, indent=2))