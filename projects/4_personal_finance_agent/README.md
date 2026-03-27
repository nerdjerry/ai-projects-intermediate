# Personal Finance Agent (Memory)

Stateful AI agent with short-term session memory for personal finance management.

## Features
- Ingest transactions via API (in-memory mock service, swappable for real DB via ISP)
- Short-term session memory for chat context (IMemoryReader/IMemoryWriter interfaces)
- Rule-based insight generation (spending alerts, category breakdowns)
- Agent tool system — add new tools via AgentTool ABC (OCP)
- Streamlit chat + dashboard UI

## Architecture

```
src/
├── interfaces/          # Abstract contracts (SOLID interfaces)
│   ├── agent_tool.py    # AgentTool ABC — add new tools without modifying agent (OCP)
│   ├── insight_generator.py  # IInsightGenerator — swap rule-based for LLM-based
│   ├── memory.py        # IMemoryReader / IMemoryWriter (ISP)
│   └── transaction_service.py  # ITransactionService (DIP)
├── services/            # Concrete implementations
│   ├── insight_generator.py   # SimpleInsightGenerator (rule-based)
│   ├── memory_manager.py      # SessionMemory (in-memory dict)
│   ├── tools.py               # SpendingSummaryTool, CategoryBreakdownTool
│   └── transaction_service.py # MockTransactionService (in-memory list)
├── api/                 # FastAPI with dependency injection
│   ├── app.py           # App setup with lifespan for service lifecycle
│   └── routes.py        # Endpoints: /transactions, /chat, /summary, /memory/search
└── ui/
    └── app.py           # Streamlit chat + dashboard
```

## Planned Enhancements
- PostgreSQL storage with SQLAlchemy (swap MockTransactionService)
- Plaid API integration for real bank transaction ingestion
- LLM-powered insight generation (swap SimpleInsightGenerator)
- Long-term persistent memory (swap SessionMemory for DB-backed store)
