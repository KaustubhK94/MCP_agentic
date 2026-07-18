# # tools/flights.py


import os
from typing import Optional, List, Dict
from amadeus import Client
from utils.flight_formatter import format_segments

from dotenv import load_dotenv

load_dotenv()

# Load environment variables (or pass via settings)
AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")

amadeus = Client(
    client_id=AMADEUS_CLIENT_ID,
    client_secret=AMADEUS_CLIENT_SECRET
)

def search_flights(
    origin: str,
    destination: str,
    start_date: str,
    end_date: Optional[str] = None,
    currency: str = "USD"
) -> List[Dict]:
    """
    Search for flights using Amadeus API.
    Returns a list of flight offers with price, airline, and segment details.
    """
    try:
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": start_date,
            "adults": 1,
            "currencyCode": currency,
            "max": 1  # Changed from 5 to 1 for testing
        }
        if end_date:
            params["returnDate"] = end_date

        response = amadeus.shopping.flight_offers_search.get(**params)
        data = response.data

        results = []
        for offer in data:
            price = f"{offer['price']['total']} {offer['price']['currency']}"
            airline = offer["validatingAirlineCodes"][0]

            outbound_legs = format_segments(offer["itineraries"][0]["segments"])
            return_legs = format_segments(offer["itineraries"][1]["segments"]) if len(
                offer["itineraries"]) > 1 else []

            results.append({
                "price": price,
                "airline": airline,
                "outbound": outbound_legs,
                "return": return_legs
            })

        return results

    except Exception as e:
        return [{"error": str(e)}]