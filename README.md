# 🧠 Context-Aware Travel Agent using LlamaIndex + MCP



## Cause similarity is not the same as relevance!

> An MCP-powered travel planning agent that persistently remembers user searches,
> separates exploration from decisions, and engineers context instead of relying
> solely on conversation history.

---

## Motivation

Most AI assistants answer a question and immediately forget how they arrived at
that answer.

For simple chatbots this is acceptable.

For agentic systems it quickly becomes a limitation.

Planning a trip requires remembering previous flight searches, hotel searches,
currency conversions, weather lookups and tourist attractions across multiple
reasoning steps.

This project explores **Context Engineering** — designing how information flows,
persists and is retrieved inside an AI agent.

Instead of treating the LLM prompt as memory, the agent maintains a structured
persistent state that evolves throughout the conversation.


## Features

- Persistent trip state across the entire conversation
- Event-driven architecture using LlamaIndex FunctionAgent
- MCP tool integration
- Query history for every tool invocation
- Separation of itinerary and search history
- Automatic context accumulation
- Extensible tool metadata system
- Modular travel planning architecture


```text
                                   ┌──────────────┐
                                   │     User     │
                                   └──────┬───────┘
                                          │
                                          ▼
                            ┌────────────────────────────────┐
                            │   LlamaIndex FunctionAgent     │
                            └──────────────┬─────────────────┘
                                           │
                                   stream_events()
                                          │
                            ┌─────────────┴─────────────┐
                            │                           │
                            ▼                           ▼
                     ┌──────────────┐          ┌────────────────┐
                     │   ToolCall   │          │ ToolCallResult │
                     └──────┬───────┘          └───────┬────────┘
                            │                          │
                            ▼                          ▼
                     Update Trip State          Extract Payload
                            │                          │
                            └─────────────┬────────────┘
                                          ▼
                            ┌────────────────────────────────┐
                            │     Persistent Trip State      │
                            └──────────────┬─────────────────┘
                                           │
                                           ▼
                                Future Context Retrieval
```


## Context Engineering Pipeline

Instead of allowing the LLM to rely solely on conversation history,
every tool invocation becomes structured knowledge.

Each tool execution follows the pipeline below:

                            ```
                               User Query
                                   │
                                   ▼
                             LLM chooses a Tool
                                   │
                                   ▼
                             ToolCall Event
                                   │
                                   ▼
                            Store Tool Arguments
                                   │
                                   ▼
                             Execute MCP Tool
                                   │
                                   ▼
                            ToolCallResult Event
                                   │
                                   ▼
                         Extract Structured Payload
                                   │    
                                   ▼
                             Persist Result
                            ```

This enables future reasoning to retrieve historical searches instead of
depending entirely on prompt history.


## Persistent Trip State

Unlike traditional chatbots, the agent maintains a structured state throughout
the conversation.

```python
trip = {
    "itinerary": {...},
    "travellers": {...},
    "budget": {...},
    "results": {
        "flights": [],
        "hotels": [],
        "weather": [],
        "places": [],
        "currency_conversion": []
    }
}
```

Every tool execution stores:

- Tool name
- Original query
- Timestamp
- Structured result

instead of simply returning a response to the LLM.

```text
travel-agent/
|
|-- llama_agent.py          # Main FunctionAgent orchestration
|-- travel_state.py         # Persistent trip state management
|-- tool_metadata.py        # Tool-to-state mapping
|-- system_prompt.py
|
|-- tools/
|   |-- flights.py
|   |-- hotels.py
|   |-- weather.py
|   |-- sightseeing.py
|   `-- currency.py
|
|-- mcp_server.py
|
|-- docs/
|   |-- context-engineering.md
|   |-- architecture.md
|   `-- debugging-llamaindex.md
|
`-- README.md
```


## Why this project is different

Most FunctionAgent examples simply execute tools and immediately return their
results to the language model.

This project treats every tool invocation as persistent knowledge.

Instead of asking:

> "What did the model remember?"

we ask:

> "What information should the system remember?"

That distinction is the foundation of Context Engineering.

### Example Workflow

```text
User
  │
  └── "Compare flights to Bangkok and Phuket"

Step 1
  └── search_flights(BKK)

Step 2
  └── search_flights(HKT)

Step 3
  └── Store both searches

      results["flights"]
      ├── Bangkok Search
      └── Phuket Search

Step 4
  └── User asks:
      "Which one was cheaper?"

Step 5
  └── Retrieve the stored searches
      instead of executing the tools again.
```



## Future Work

- Context retrieval policies
- Long-term memory
- Vector-based search history
- Tool result ranking
- Automatic itinerary confirmation
- Multi-agent orchestration

## Documentation

This repository contains detailed engineering notes describing the design
process.

- 📖 Context Engineering
- 🏗 Architecture
- 🔍 Runtime Object Introspection
- ⚙️ LlamaIndex Event Pipeline



## commands inspecting db from terminal 


SQLite CLI

First, locate your database (probably knowledge.db).

"""
ls
"""

You should see something like:

"""
knowledge.db
"""

Open it:

"""
sqlite3 knowledge.db
"""

Now list all tables:

"""
.tables
"""

You should see something like:

"""
tool_invocations
"""

View the schema:

"""
.schema tool_invocations
"""

View all rows:

"""
SELECT * FROM tool_invocations;
"""

A nicer formatted output:

"""
.mode column
.headers on
SELECT * FROM tool_invocations;
"""

Exit:

"""
.quit
"""