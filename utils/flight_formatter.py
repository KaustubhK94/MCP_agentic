import time
import re
from datetime import datetime, timedelta

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