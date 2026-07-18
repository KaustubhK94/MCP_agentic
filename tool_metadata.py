# tool_metadata.py


TOOL_METADATA = {
    "search_flights": {
        "state_updates": {
            "origin": ("itinerary", "origin", "airport"),
            "destination": ("itinerary", "destination", "airport"),
            "start_date": ("itinerary", "departure"),
            "end_date": ("itinerary", "return"),
        },
        "result_key": "flights",
    },

    "search_hotels": {
        "state_updates": {
            "location": ("itinerary", "destination", "city"),
            "adults": ("travellers", "adults"),
        },
        "result_key": "hotels",
    },

    "fetch_weather": {
        "state_updates": {},
        "result_key": "weather",
    },

    "fetch_sightseeing": {
        "state_updates": {},
        "result_key": "places",
    },

    "convert_currency": {
        "state_updates": {
            "to_currency": ("budget", "currency"),
        },
        "result_key": "currency_conversion",
    },
}