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

# --------------------------------------------
#  Main workflow
# --------------------------------------------

async def main():
    # Build agent and context
    agent = await build_agent()
    agent_context = Context(agent)

    # Ensure initial state exists and show it
    await get_trip(agent_context)
    await print_trip_state(agent_context, "INITIAL TRIP")

    # Main interaction loop
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in {"exit", "quit"}:
            break

        # Run agent
        handler = agent.run(
            user_input,
            ctx=agent_context,
        )

        # Process stream events
        async for event in handler.stream_events():
            if isinstance(event, ToolCall):
                print(f"\n🔧 Calling {event.tool_name}")
                print(event.tool_kwargs)
                # Update state from tool arguments
                await update_trip_fields(agent_context, event.tool_name, event.tool_kwargs)

            elif isinstance(event, ToolCallResult):
                print(f"\n✅ {event.tool_name}")
                print(event.tool_output)
                # Persist the tool result
                await handle_tool_result(agent_context, event)

        # Wait for final response and show updated state
        response = await handler
        await print_trip_state(agent_context, "TRIP STATE")
        print(f"\nAgent: {response}")

# --------------------------------------------
#  Entry point
# --------------------------------------------

if __name__ == "__main__":
    asyncio.run(main())