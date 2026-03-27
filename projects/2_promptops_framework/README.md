# PromptOps Framework

A CI/CD system for prompts with evaluation, testing, and optimization.

## Features

- **Prompt Versioning** — store and retrieve prompt templates with version history
- **Pluggable Metrics** — evaluate prompts with built-in or custom metrics (OCP)
- **REST API** — FastAPI endpoints for evaluation and prompt management
- **Streamlit UI** — visual interface for evaluation and version browsing
- **SOLID Design** — abstract LLM client, separated interfaces, composable metrics

## Quick Start

```bash
pip install -r requirements.txt

# Run API server
uvicorn src.api.app:app --port 8001

# Run Streamlit UI (in another terminal)
streamlit run src/ui/app.py

# Run tests
pytest tests/
```

## Architecture

| Principle | Implementation |
|-----------|---------------|
| **SRP** | Prompt, Evaluator, Optimizer each have a single responsibility |
| **OCP** | Add new metrics by subclassing `IMetric` |
| **LSP** | Swap DSPy / raw prompts via `IPromptRunner` |
| **ISP** | Separate testing (`IPromptRunner`) vs optimization (`IOptimizer`) interfaces |
| **DIP** | Abstract `LLMClient` — concrete `OpenAIClient` injected at runtime |
