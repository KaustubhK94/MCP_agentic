import time
import re
from datetime import datetime, timedelta

from typing import Optional, Dict, Any


def format_duration(iso_duration):
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?", iso_duration)
    if not match:
        return iso_duration
    hours = match.group(1) or "0"
    minutes = match.group(2) or "0"
    return f"{int(hours)}h {int(minutes)}m"

def format_time(iso_time):
    try:
        return datetime.fromisoformat(iso_time).strftime("%Y-%m-%d %H:%M")
    except:
        return iso_time

def format_segments(segments):
    legs = []
    for seg in segments:
        dep_airport = seg['departure']['iataCode']
        arr_airport = seg['arrival']['iataCode']
        dep_time = format_time(seg['departure']['at'])
        arr_time = format_time(seg['arrival']['at'])
        duration = format_duration(seg['duration'])
        legs.append(f"{dep_airport} ({dep_time}) → {arr_airport} ({arr_time}) [{duration}]")
    return legs



def _normalize_flight(flight: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a Google Flights result into a consistent schema."""

    legs = []

    for segment in flight.get("flights", []):

        legs.append(
            {
                "airline": segment.get("airline"),
                "flight_number": segment.get("flight_number"),
                "departure_airport": segment["departure_airport"]["id"],
                "departure_time": segment["departure_airport"]["time"],
                "arrival_airport": segment["arrival_airport"]["id"],
                "arrival_time": segment["arrival_airport"]["time"],
                "duration": segment.get("duration"),
                "airplane": segment.get("airplane"),
            }
        )

    return {
        "price": flight.get("price"),
        "total_duration": flight.get("total_duration"),
        "carbon_emissions": flight.get("carbon_emissions"),
        "layovers": flight.get("layovers", []),
        "legs": legs,
    }