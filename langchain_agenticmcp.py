import asyncio
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain_mcp_adapters.client import MultiServerMCPClient
from datetime import datetime

# Your existing system prompt
from system_prompt import SYSTEM_PROMPT

today = datetime.now()
system_prompt = SYSTEM_PROMPT.format(
    today=today.strftime("%Y-%m-%d"),
    weekday=today.strftime("%A"),
)

# Configure LLM (Ollama)
llm = ChatOllama(model="gemma4:e4b", temperature=0, request_timeout=120.0)

async def build_agent():
    """Build LangChain agent with MCP tools via streamable_http"""
    
    # Connect to your MCP server via streamable_http
    client = MultiServerMCPClient({
        "travel_mcp": {
            "url": "http://127.0.0.1:8000/mcp",  # Note: /mcp, not /sse
            "transport": "streamable_http",
        }
    })
    
    # Load tools from the MCP server
    tools = await client.get_tools()
    print(f"✅ Loaded {len(tools)} tools: {[t.name for t in tools]}")
    
    # Create the LangChain agent
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
    )
    
    return agent, client

async def main():
    # Build agent and keep client reference
    agent, client = await build_agent()
    
    print("\n🤖 Travel Agent ready! Ask me about flights, hotels, weather, or sightseeing.")
    print("Type 'exit' or 'quit' to stop.\n")
    
    # Chat loop
    while True:
        user_input = input("You: ").strip()
        if not user_input or user_input.lower() in ("exit", "quit"):
            break
        
        try:
            # Invoke the agent
            result = await agent.ainvoke({
                "messages": [{"role": "user", "content": user_input}]
            })
            
            # Display tool calls (optional)
            for msg in result["messages"]:
                tool_calls = getattr(msg, "tool_calls", None)
                if tool_calls:
                    for call in tool_calls:
                        print(f"🔧 Tool call: {call['name']}({call['args']})")
            
            # Display final answer
            print(f"\nAgent: {result['messages'][-1].content}\n")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())