#travel_state.py

from copy import deepcopy
from llama_index.core.workflow import Context

# --------------------------------------------
#  Unified Tool Registry – single source of truth
# --------------------------------------------
TOOL_REGISTRY = {
    "search_flights": {
        "args": {                               # was "fields"
            "origin": ("itinerary", "origin", "airport"),
            "destination": ("itinerary", "destination", "airport"),
            "start_date": ("itinerary", "departure"),
            "end_date": ("itinerary", "return"),
        },
        "result": "flights",                    # was "result_key"
    },
    "search_hotels": {
        "args": {
            "location": ("itinerary", "destination", "city"),
            "adults": ("travellers", "adults"),
        },
        "result": "hotels",
    },
    "fetch_weather": {
        "args": {},
        "result": "weather",
    },
    "fetch_sightseeing": {
        "args": {},
        "result": "places",
    },
    "convert_currency": {
        "args": {
            "to_currency": ("budget", "currency"),
        },
        "result": "currency_conversion",
    },
}

# --------------------------------------------
#  State helpers (unchanged except for using the registry)
# --------------------------------------------

async def get_state(ctx: Context):
    return await ctx.store.get_state()

async def save_state(ctx: Context, state):
    await ctx.store.set_state(state)

async def get_trip(ctx: Context):
    state = await get_state(ctx)
    if "trip" not in state:
        state["trip"] = deepcopy(DEFAULT_TRIP)
        await save_state(ctx, state)
    return state["trip"]

async def save_trip(ctx: Context, trip):
    state = await get_state(ctx)
    state["trip"] = trip
    await save_state(ctx, state)

async def update_result(ctx: Context, key: str, value):
    trip = await get_trip(ctx)
    trip["results"][key] = value
    await save_trip(ctx, trip)

async def reset_trip(ctx: Context):
    state = await get_state(ctx)
    state["trip"] = deepcopy(DEFAULT_TRIP)
    await save_state(ctx, state)

# --------------------------------------------
#  Default trip structure (unchanged)
# --------------------------------------------

DEFAULT_TRIP = {
    "itinerary": {
        "origin": {"city": None, "airport": None},
        "destination": {"city": None, "airport": None},
        "departure": None,
        "return": None,
    },
    "travellers": {"adults": 2},
    "budget": {"amount": None, "currency": "USD"},
    "results": {
        "flights": None,
        "hotels": None,
        "weather": None,
        "places": None,
        "currency_conversion": None,
    },
}

# --------------------------------------------
#  Helper to set nested dict values (unchanged)
# --------------------------------------------

def set_nested_value(obj, path, value):
    current = obj
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = value

# --------------------------------------------
#  Core function that uses the registry
# --------------------------------------------

async def update_trip_fields(ctx: Context, tool_name: str, kwargs: dict):
    """Extract arguments from the tool call and update the trip state."""
    config = TOOL_REGISTRY.get(tool_name)
    if config is None:
        return  # or raise an error – up to you

    trip = await get_trip(ctx)
    for arg, state_path in config["args"].items():
        if arg in kwargs:
            set_nested_value(trip, state_path, kwargs[arg])

    await save_trip(ctx, trip)

# --------------------------------------------
#  New helpers for retrieving tool metadata
# --------------------------------------------

def get_tool_result_key(tool_name: str) -> str:
    """Return the result key (e.g., 'flights') for a given tool."""
    config = TOOL_REGISTRY.get(tool_name)
    if config is None:
        raise KeyError(f"Tool '{tool_name}' not found in registry")
    return config["result"]

def get_tool_args_map(tool_name: str) -> dict:
    """Return the argument mapping for a given tool."""
    config = TOOL_REGISTRY.get(tool_name)
    if config is None:
        raise KeyError(f"Tool '{tool_name}' not found in registry")
    return config["args"]