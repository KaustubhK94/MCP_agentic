#llama_agent.py

import asyncio
from datetime import datetime
from pprint import pprint

import nest_asyncio
nest_asyncio.apply()

from llama_index.core import Settings
from llama_index.core.agent.workflow import (FunctionAgent,ToolCall,ToolCallResult,)
from llama_index.core.workflow import Context
from llama_index.llms.ollama import Ollama
from llama_index.tools.mcp import (BasicMCPClient,McpToolSpec,)

from system_prompt import SYSTEM_PROMPT
from tool_result_handler import handle_tool_result
from travel_state import get_trip, update_trip_fields


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


async def main():

    mcp_client = BasicMCPClient(
        "http://127.0.0.1:8000/sse"
    )

    mcp_tool_spec = McpToolSpec(client=mcp_client)

    tools = await mcp_tool_spec.to_tool_list_async()

    print("Loaded tools:")
    print([t.metadata.name for t in tools])

    agent = FunctionAgent(
        name="TravelAgent",
        description="Travel planning agent using MCP tools.",
        tools=tools,
        llm=llm,
        system_prompt=system_prompt,)

    agent_context = Context(agent)

    
    await get_trip(agent_context)
    print("\n=========== INITIAL TRIP ===========")
    pprint(await get_trip(agent_context))
    print("====================================\n")

    while True:

        user_input = input("\nYou: ")
        if user_input.lower() in {"exit", "quit"}:
            break

        handler = agent.run(user_input,ctx=agent_context,)
        async for event in handler.stream_events():
            if isinstance(event, ToolCall):
                print(f"\n🔧 Calling {event.tool_name}")
                               
                print(event.tool_kwargs)
                await update_trip_fields(agent_context, event.tool_name, event.tool_kwargs)

            elif isinstance(event, ToolCallResult):

                print(f"\n✅ {event.tool_name}")
                print(event.tool_output)
                
                # Persist result into state
                await handle_tool_result(agent_context,event,)

        response = await handler
        print("\n=========== TRIP STATE ===========")
        pprint(await get_trip(agent_context))
        print("==================================")
        print(f"\nAgent: {response}")


if __name__ == "__main__":
    asyncio.run(main())