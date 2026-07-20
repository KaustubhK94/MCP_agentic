# 🧠 Context-Aware Travel Agent using LlamaIndex + MCP

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



                 User
                  │
                  ▼
        LlamaIndex FunctionAgent
                  │
        stream_events()
                  │
      ┌───────────┴────────────┐
      ▼                        ▼
 ToolCall               ToolCallResult
      │                        │
      ▼                        ▼
update_trip_fields()   extract_payload()
      │                        │
      └───────────┬────────────┘
                  ▼
          Persistent Trip State
                  │
                  ▼
      Future Context Retrieval


## Context Engineering Pipeline

Instead of allowing the LLM to rely solely on conversation history,
every tool invocation becomes structured knowledge.

Each tool execution follows the pipeline below:

                    ```text
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


travel-agent/
│
├── llama_agent.py          # FunctionAgent orchestration
├── travel_state.py         # Persistent context management
├── tool_metadata.py        # State update definitions
├── tools/                  # MCP tool implementations
├── server.py               # MCP server
├── system_prompt.py
│
├── docs/
│   ├── context-engineering.md
│   ├── architecture.md
│   └── debugging-llamaindex.md
│
└── README.md


## Why this project is different

Most FunctionAgent examples simply execute tools and immediately return their
results to the language model.

This project treats every tool invocation as persistent knowledge.

Instead of asking:

> "What did the model remember?"

we ask:

> "What information should the system remember?"

That distinction is the foundation of Context Engineering.

User:
Compare flights to Bangkok and Phuket.

        ↓

search_flights(BKK)

        ↓

search_flights(HKT)

        ↓

results["flights"]

    ├── Bangkok Search
    └── Phuket Search

            ↓

User:
Which one was cheaper?

        ↓

Agent retrieves previous searches
without executing the tools again.



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