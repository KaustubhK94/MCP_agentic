# tool_metadata.py
from types import MappingProxyType

TOOL_METADATA = MappingProxyType({
    "search_flights": {
        "arg_mapping": {   # tool arg → trip state path
            "origin": ("itinerary", "origin", "airport"),
            "destination": ("itinerary", "destination", "airport"),
            "start_date": ("itinerary", "departure"),
            "end_date": ("itinerary", "return"),
        },
        "result_key": "flights",
    },
    "search_hotels": {
        "arg_mapping": {
            "location": ("itinerary", "destination", "city"),
            "adults": ("travellers", "adults"),
        },
        "result_key": "hotels",
    },
    "fetch_weather": {
        "arg_mapping": {},
        "result_key": "weather",
    },
    "fetch_sightseeing": {
        "arg_mapping": {},
        "result_key": "places",
    },
    "convert_currency": {
        "arg_mapping": {
            "to_currency": ("budget", "currency"),
        },
        "result_key": "currency_conversion",
    },
})