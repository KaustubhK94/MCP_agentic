# travel_state.py

from copy import deepcopy
from llama_index.core.workflow import Context
from tool_metadata import TOOL_METADATA

# --------------------------------------------
#  State helpers
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

async def reset_trip(ctx: Context):
    state = await get_state(ctx)
    state["trip"] = deepcopy(DEFAULT_TRIP)
    await save_state(ctx, state)

# --------------------------------------------
#  Default trip structure (stays here)
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
#  Utility
# --------------------------------------------

def set_nested_value(obj, path, value):
    current = obj
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = value

# --------------------------------------------
#  Public interface: get tool metadata
# --------------------------------------------

def get_tool_metadata(tool_name: str):
    """Return the full metadata dict for a tool, or None if not found."""
    return TOOL_METADATA.get(tool_name)

# --------------------------------------------
#  Core functions: update state from tool
# --------------------------------------------

async def update_trip_fields(ctx: Context, tool_name: str, kwargs: dict):
    """Extract tool arguments and store them in the trip state."""
    metadata = get_tool_metadata(tool_name)
    if metadata is None:
        return

    state_mapping = metadata["state_mapping"]
    if not state_mapping:
        return

    trip = await get_trip(ctx)

    for arg, path in state_mapping.items():
        if arg in kwargs:
            set_nested_value(trip, path, kwargs[arg])

    await save_trip(ctx, trip)

async def update_result(ctx: Context, tool_name: str, value):
    """Store the tool output in the trip's results, using the metadata to find the key."""
    metadata = get_tool_metadata(tool_name)
    if metadata is None:
        return

    result_key = metadata["result_key"]
    trip = await get_trip(ctx)
    trip["results"][result_key] = value
    await save_trip(ctx, trip)