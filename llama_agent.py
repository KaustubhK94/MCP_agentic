import asyncio
from datetime import datetime
from pprint import pprint

import nest_asyncio
nest_asyncio.apply()

from llama_index.core import Settings
from llama_index.core.agent.workflow import (
    FunctionAgent,
    ToolCall,
    ToolCallResult,
)
from llama_index.core.workflow import Context
from llama_index.llms.ollama import Ollama
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec

from system_prompt import SYSTEM_PROMPT
from tool_result_handler import handle_tool_result
from travel_state import get_trip, update_trip_fields

# --------------------------------------------
#  Initialisation
# --------------------------------------------

today = datetime.now()
system_prompt = SYSTEM_PROMPT.format(
    today=today.strftime("%Y-%m-%d"),
    weekday=today.strftime("%A"),
)

llm = Ollama(
    model="gemma4:e4b",
    request_timeout=120.0,
)
Settings.llm = llm

# --------------------------------------------
#  Helper to pretty‑print trip state
# --------------------------------------------

async def print_trip_state(ctx: Context, title: str = "TRIP STATE"):
    """Print the current trip state with a centred title."""
    trip = await get_trip(ctx)
    print(f"\n=========== {title} ===========")
    pprint(trip)
    print("=" * (24 + len(title)))

# --------------------------------------------
#  Agent builder
# --------------------------------------------

async def build_agent() -> FunctionAgent:
    """Set up MCP client, load tools, and return the FunctionAgent."""
    mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")
    tool_spec = McpToolSpec(client=mcp_client)
    tools = await tool_spec.to_tool_list_async()

    print("Loaded tools:")
    print([t.metadata.name for t in tools])

    return FunctionAgent(
        name="TravelAgent",
        description="Travel planning agent using MCP tools.",
        tools=tools,
        llm=llm,
        system_prompt=system_prompt,
    )


async def main():
    agent = await build_agent()
    agent_context = Context(agent)

    await get_trip(agent_context)
    await print_trip_state(agent_context, "INITIAL TRIP")

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in {"exit", "quit"}:
            break

        handler = agent.run(user_input, ctx=agent_context)

        # Map call ID → tool kwargs (unique per tool call)
        pending_calls = {}

        async for event in handler.stream_events():
            if isinstance(event, ToolCall):
                print(f"\n🔧 Calling {event.tool_name}")
                print(event.tool_kwargs)

                # Use a unique ID. Try tool_call_id, fallback to id, else generate one.
                call_id = getattr(event, "tool_call_id", None)
                if call_id is None:
                    call_id = getattr(event, "id", None)
                if call_id is None:
                    # Fallback: not ideal but works for sequential execution
                    call_id = f"{event.tool_name}_{id(event)}"
                pending_calls[call_id] = event.tool_kwargs

                # Update trip state (itinerary)
                await update_trip_fields(agent_context, event.tool_name, event.tool_kwargs)

            elif isinstance(event, ToolCallResult):
                print(f"\n✅ {event.tool_name}")
                print(event.tool_output)

                # Retrieve the corresponding query
                call_id = getattr(event, "tool_call_id", None)
                if call_id is None:
                    call_id = getattr(event, "id", None)
                if call_id is None:
                    # Fallback: if no ID, we cannot match reliably; use tool_name as fallback (with warning)
                    call_id = event.tool_name
                    # If multiple calls to same tool, this will overwrite, but we log a warning.
                    import warnings
                    warnings.warn("No unique call ID; using tool_name as fallback. Parallel calls may mix queries.")

                query = pending_calls.pop(call_id, {})
                if not query:
                    # If not found, maybe we already popped? Use empty dict.
                    pass

                # Store the result with its query
                await update_result(agent_context, event.tool_name, query, event.tool_output)

        response = await handler
        await print_trip_state(agent_context, "TRIP STATE")
        print(f"\nAgent: {response}")


if __name__ == "__main__":
    asyncio.run(main())