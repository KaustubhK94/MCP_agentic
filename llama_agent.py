# llama_agent.py
import asyncio
from collections import deque
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
from llama_index.tools.mcp import (
    BasicMCPClient,
    McpToolSpec,
)

from system_prompt import SYSTEM_PROMPT
from travel_state import (
    get_trip,
    update_trip_fields,
    update_result,)

# ============================================================
# LLM Configuration
# ============================================================

today = datetime.now()

system_prompt = SYSTEM_PROMPT.format(
    today=today.strftime("%Y-%m-%d"),
    weekday=today.strftime("%A"),)

llm = Ollama(model="gemma4:e4b",
    request_timeout=120.0,)

Settings.llm = llm

# ============================================================
# Agent Builder
# ============================================================


async def build_agent() -> FunctionAgent:
    """
    Build the MCP-backed travel planning agent.
    """
    mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")
    tool_spec = McpToolSpec(client=mcp_client)
    tools = await tool_spec.to_tool_list_async()
    print("Loaded tools:")
    print([tool.metadata.name for tool in tools])
    return FunctionAgent(
        name="TravelAgent",
        description="Travel planning assistant powered by MCP tools.",
        tools=tools,
        llm=llm,
        system_prompt=system_prompt,)


# ============================================================
# Debug Helpers
# ============================================================


async def print_trip_state(
    ctx: Context,
    title: str = "TRIP STATE",):
    """
    Pretty-print the stored trip state.
    """
    trip = await get_trip(ctx)
    print(f"\n=========== {title} ===========")
    pprint(trip)
    print("=" * (24 + len(title)))


# ============================================================
# Main
# ============================================================

async def main():
    agent = await build_agent()
    ctx = Context(agent)
    # initialize state
    await get_trip(ctx)
    await print_trip_state(ctx,
        "INITIAL TRIP",)

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in {
            "quit",
            "exit",}:
            break
        handler = agent.run(
            user_input,
            ctx=ctx,)

        #
        # Tool queries are executed sequentially.
        #
        # Maintain a FIFO queue so that each ToolCallResult
        # can be paired with the ToolCall that generated it.
        #
        pending_queries = deque()
        async for event in handler.stream_events():
            #
            # -----------------------------
            # Tool Invocation
            # -----------------------------
            #
            if isinstance(event, ToolCall):
                print(f"\n🔧 Calling {event.tool_name}")
                pprint(event.tool_kwargs)
                pending_queries.append({"tool": event.tool_name,
                        "kwargs": event.tool_kwargs,})

                #
                # Update itinerary immediately from tool arguments.
                #
                await update_trip_fields(ctx,event.tool_name,
                    event.tool_kwargs,)

            #
            # -----------------------------
            # Tool Result
            # -----------------------------
            #
            elif isinstance(event, ToolCallResult):
                print(f"\n✅ {event.tool_name}")
                # print(event.tool_output)
                print("\n===== TOOL OUTPUT TYPE =====")
                print(type(event.tool_output))
                print("\n===== TOOL OUTPUT VARS =====")
                print(vars(event.tool_output))
                if hasattr(event.tool_output, "content"):
                    for item in event.tool_output.raw_output.content:
                        print(type(item))
                        print(item)
                        print(item.text)


                if pending_queries:
                    tool_call = pending_queries.popleft()
                    query = tool_call["kwargs"]
                else:
                    #
                    # Should never happen under sequential execution.
                    #
                    query = {}
                await update_result(ctx,event.tool_name,
                    query,event.tool_output,)
        #
        # Final response
        #
        response = await handler
        await print_trip_state(ctx)
        print(f"\nAgent: {response}")

# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())