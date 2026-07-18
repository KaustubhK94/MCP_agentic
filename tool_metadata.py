# tool_metadata.py

TOOL_METADATA = {
    "search_flights": {
        "state_mapping": {          # tool arg → trip state path
            "origin": ("itinerary", "origin", "airport"),
            "destination": ("itinerary", "destination", "airport"),
            "start_date": ("itinerary", "departure"),
            "end_date": ("itinerary", "return"),
        },
        "result_key": "flights",    # where to store the tool output
    },
    "search_hotels": {
        "state_mapping": {
            "location": ("itinerary", "destination", "city"),
            "adults": ("travellers", "adults"),
        },
        "result_key": "hotels",
    },
    "fetch_weather": {
        "state_mapping": {},
        "result_key": "weather",
    },
    "fetch_sightseeing": {
        "state_mapping": {},
        "result_key": "places",
    },
    "convert_currency": {
        "state_mapping": {
            "to_currency": ("budget", "currency"),
        },
        "result_key": "currency_conversion",
    },
}