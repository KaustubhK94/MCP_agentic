from copy import deepcopy

from llama_index.core.workflow import Context

from tool_metadata import TOOL_METADATA


DEFAULT_TRIP = {

    "itinerary": {"origin": {"city": None,"airport": None,},
    
    "destination": {"city": None,"airport": None,},"departure": None,"return": None,},

    "travellers": {"adults": 2,},

    "budget": {"amount": None,"currency": "USD",},

    "results": {
        "flights": None,
        "hotels": None,
        "weather": None,
        "places": None,
        "currency_conversion": None,},}


# ------------------------------------------------------------------
# State helpers
# ------------------------------------------------------------------

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


# ------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------

def set_nested_value(obj, path, value):
    current = obj
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = value


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

async def update_trip_fields(
    ctx: Context,
    tool_name: str,
    kwargs: dict,):
    metadata = TOOL_METADATA.get(tool_name)
    if metadata is None:
        return
    state_updates = metadata["state_updates"]
    if not state_updates:
        return
    trip = await get_trip(ctx)
    for arg, path in state_updates.items():
        if arg not in kwargs:
            continue
        set_nested_value(
            trip,
            path,
            kwargs[arg],
        )
    await save_trip(ctx, trip)


async def update_result(
    ctx: Context,
    tool_name: str,
    value,):
    metadata = TOOL_METADATA.get(tool_name)
    if metadata is None:
        return
    result_key = metadata["result_key"]
    trip = await get_trip(ctx)
    trip["results"][result_key] = value
    await save_trip(ctx, trip)