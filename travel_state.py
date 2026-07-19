# travel_state.py

from copy import deepcopy
from datetime import datetime, UTC
from typing import Any

from llama_index.core.workflow import Context

from tool_metadata import TOOL_METADATA
from pprint import pprint

# ============================================================
# Configuration
# ============================================================

MAX_HISTORY = 20

# ============================================================
# Default Trip State
# ============================================================

DEFAULT_TRIP = {
    "itinerary": {
        "origin": {
            "city": None,
            "airport": None,
        },
        "destination": {
            "city": None,
            "airport": None,
        },
        "departure": None,
        "return": None,
    },
    "travellers": {
        "adults": 2,
    },
    "budget": {
        "amount": None,
        "currency": "USD",
    },
    "results": {
        "flights": [],
        "hotels": [],
        "weather": [],
        "places": [],
        "currency_conversion": [],
    },
}

# ============================================================
# State Helpers
# ============================================================


async def get_state(ctx: Context):
    """Return the workflow state."""
    return await ctx.store.get_state()


async def save_state(ctx: Context, state):
    """Persist workflow state."""
    await ctx.store.set_state(state)


async def get_trip(ctx: Context):
    """
    Retrieve the trip object.

    Automatically initializes the default trip on first use.
    """
    state = await get_state(ctx)

    if "trip" not in state:
        state["trip"] = deepcopy(DEFAULT_TRIP)
        await save_state(ctx, state)

    return state["trip"]


async def save_trip(ctx: Context, trip):
    """Persist the trip object."""
    state = await get_state(ctx)
    state["trip"] = trip
    await save_state(ctx, state)


async def reset_trip(ctx: Context):
    """Reset the trip back to its initial state."""
    state = await get_state(ctx)
    state["trip"] = deepcopy(DEFAULT_TRIP)
    await save_state(ctx, state)


# ============================================================
# Utilities
# ============================================================


def set_nested_value(obj: dict, path: tuple | list, value: Any):
    """
    Set a nested dictionary value.

    Example:

        path = ("itinerary", "origin", "airport")
    """
    current = obj
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = value

import json


def extract_payload(tool_output):
    """
    Extract the payload from a ToolCallResult.
    """
    # Preferred:

    if getattr(tool_output, "structuredContent", None) is not None:
        return tool_output.structuredContent
    
    # MCP text response
    
    if hasattr(tool_output, "content"):
        payload = []
        for item in tool_output.content:
            text = getattr(item, "text", None)
            if text is None:
                continue
            try:
                payload.append(json.loads(text))
            except Exception:
                payload.append(text)
        return payload
    raise RuntimeError(
        f"Unknown tool output:\n{tool_output}")


# ============================================================
# Trip Updates
# ============================================================


async def update_trip_fields(
    ctx: Context,
    tool_name: str,
    kwargs: dict,):
    """
    Update itinerary / traveller information using tool arguments.

    Only non-None values overwrite existing state.
    """
    metadata = TOOL_METADATA.get(tool_name)
    if metadata is None:
        return
    state_updates = metadata.get("state_updates")
    if not state_updates:
        return
    trip = await get_trip(ctx)
    for arg, path in state_updates.items():
        value = kwargs.get(arg)
        if value is None:
            continue
        set_nested_value(trip, path, value)
    await save_trip(ctx, trip)


async def update_result(
    ctx: Context,
    tool_name: str,
    query: dict,
    tool_output: Any,):
    """
    Store a tool execution.
    Each result record contains:
    - tool
    - timestamp
    - query
    - result
    """

    metadata = TOOL_METADATA.get(tool_name)
    if metadata is None:
        return
    result_key = metadata.get("result_key")
    if result_key is None:
        return
    trip = await get_trip(ctx)
    payload = extract_payload(tool_output)
    print("\n===== EXTRACTED PAYLOAD =====")
    pprint(payload)
    print(type(payload))
    print("=============================\n")
    history = trip["results"].setdefault(result_key, [])
    history.append(
        {
            "tool": tool_name,
            "timestamp": datetime.now(UTC).isoformat(),
            "query": deepcopy(query),
            "result": payload,})

    # Keep only the latest N searches
    if len(history) > MAX_HISTORY:
        del history[:-MAX_HISTORY]
    await save_trip(ctx, trip)


# ============================================================
# Convenience Helpers
# ============================================================


async def get_latest_result(
    ctx: Context,
    result_key: str,):
    """
    Return the latest stored result for a category.

    Example:

        await get_latest_result(ctx, "flights")
    """
    trip = await get_trip(ctx)
    history = trip["results"].get(result_key, [])
    if not history:
        return None
    return history[-1]


async def get_results(
    ctx: Context,
    result_key: str,):
    """
    Return the complete history for a result category.

    Example:

        await get_results(ctx, "hotels")
    """
    trip = await get_trip(ctx)
    return trip["results"].get(result_key, [])


async def clear_results(
    ctx: Context,
    result_key: str | None = None,
):
    """
    Clear stored search history.

    clear_results(ctx)
        -> clears everything

    clear_results(ctx, "flights")
        -> clears only flight searches
    """

    trip = await get_trip(ctx)
    if result_key is None:
        for key in trip["results"]:
            trip["results"][key] = []
    else:
        if result_key in trip["results"]:
            trip["results"][result_key] = []

    await save_trip(ctx, trip)