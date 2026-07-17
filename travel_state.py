# travel_state.py
from copy import deepcopy
from llama_index.core.workflow import Context




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



DEFAULT_TRIP = {

    "itinerary": {

        "origin": {
            "city": None,
            "airport": None,},

        "destination": {
            "city": None,
            "airport": None,},

        "departure": None,
        "return": None,},

    "travellers": {
        "adults": 2,},

    "budget": {
        "amount": None,
        "currency": "USD",},

    "results": {

        "flights": None,
        "hotels": None,
        "weather": None,
        "places": None,
        "currency_conversion": None,}}


TOOL_CONFIG = {

    "search_flights": {

        "fields": {

            "origin": ("itinerary", "origin", "airport"),
            "destination": ("itinerary", "destination", "airport"),
            "start_date": ("itinerary", "departure"),
            "end_date": ("itinerary", "return"),

        },

        "result_key": "flights",

    },

    "search_hotels": {

        "fields": {

            "location": ("itinerary", "destination", "city"),
            "adults": ("travellers", "adults"),

        },

        "result_key": "hotels",

    },

    "fetch_weather": {

        "fields": {},

        "result_key": "weather",

    },

    "fetch_sightseeing": {

        "fields": {},

        "result_key": "places",

    },

    "convert_currency": {

        "fields": {

            "to_currency": ("budget", "currency"),

        },

        "result_key": "currency_conversion",

    },

}

RESULT_MAP = {
    "search_flights": "flights",
    "search_hotels": "hotels",
    "fetch_weather": "weather",
    "fetch_sightseeing": "places",
    "convert_currency": "currency_conversion",
}


def set_nested_value(obj, path, value):
    current = obj
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = value


async def update_trip_fields(ctx, tool_name, kwargs):
    config = TOOL_CONFIG.get(tool_name)
    if config is None:
        return
    trip = await get_trip(ctx)

    for arg, state_path in config["fields"].items():
        if arg not in kwargs:
            continue
        set_nested_value(
            trip,
            state_path,
            kwargs[arg],)
    await save_trip(ctx, trip)