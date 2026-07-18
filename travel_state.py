# travle_state.py
from copy import deepcopy
from llama_index.core.workflow import Context
from tool_metadata import TOOL_METADATA   # direct import, no wrapper

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
#  Default trip (belongs to the state layer)
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
#  Public API – callers only need these two
# --------------------------------------------

async def update_trip_fields(ctx: Context, tool_name: str, kwargs: dict):
    """Extract mapped arguments from the tool call and store them in the trip state."""
    metadata = TOOL_METADATA.get(tool_name)
    if metadata is None:
        return

    arg_mapping = metadata["arg_mapping"]
    if not arg_mapping:
        return

    trip = await get_trip(ctx)

    for arg, path in arg_mapping.items():
        if arg in kwargs:
            set_nested_value(trip, path, kwargs[arg])

    await save_trip(ctx, trip)

async def update_result(ctx: Context, tool_name: str, value):
    """Store the tool's output in the trip's results using the configured key."""
    metadata = TOOL_METADATA.get(tool_name)
    if metadata is None:
        return

    result_key = metadata["result_key"]
    trip = await get_trip(ctx)
    trip["results"][result_key] = value
    await save_trip(ctx, trip)