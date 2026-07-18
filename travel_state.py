from copy import deepcopy
from datetime import datetime
from llama_index.core.workflow import Context
from tool_metadata import TOOL_METADATA

# --------------------------------------------
#  Default trip – results are lists
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
        "flights": [],
        "hotels": [],
        "weather": [],
        "places": [],
        "currency_conversion": [],
    },
}

# --------------------------------------------
#  State helpers (unchanged)
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
#  Utility
# --------------------------------------------

def set_nested_value(obj, path, value):
    current = obj
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = value

# --------------------------------------------
#  Helper to extract raw result from ToolCallResult
# --------------------------------------------

def extract_tool_result(tool_output) -> any:
    """
    Extract the actual payload from a ToolCallResult's tool_output.
    Tries common attributes in order:
      - raw_output (MCP often has this)
      - structuredContent
      - content[0].text
    """
    if hasattr(tool_output, "raw_output"):
        return tool_output.raw_output
    if hasattr(tool_output, "structuredContent"):
        return tool_output.structuredContent
    if hasattr(tool_output, "content") and isinstance(tool_output.content, list) and len(tool_output.content) > 0:
        first = tool_output.content[0]
        if hasattr(first, "text"):
            return first.text
        if isinstance(first, dict) and "text" in first:
            return first["text"]
    # Fallback: return the whole object (but it's probably not ideal)
    return tool_output

# --------------------------------------------
#  Public API
# --------------------------------------------

async def update_trip_fields(ctx: Context, tool_name: str, kwargs: dict):
    """Update itinerary/traveller fields from tool arguments."""
    metadata = TOOL_METADATA.get(tool_name)
    if metadata is None:
        return
    state_updates = metadata["state_updates"]
    if not state_updates:
        return
    trip = await get_trip(ctx)
    for arg, path in state_updates.items():
        if arg in kwargs:
            set_nested_value(trip, path, kwargs[arg])
    await save_trip(ctx, trip)

async def update_result(ctx: Context, tool_name: str, query: dict, tool_output: any):
    """
    Append a record with timestamp, query, and extracted result.
    """
    metadata = TOOL_METADATA.get(tool_name)
    if metadata is None:
        return
    result_key = metadata["result_key"]
    trip = await get_trip(ctx)

    # Extract the actual payload
    result_payload = extract_tool_result(tool_output)

    # Ensure the list exists and append
    trip["results"].setdefault(result_key, []).append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "query": query,
        "result": result_payload,
    })
    await save_trip(ctx, trip)