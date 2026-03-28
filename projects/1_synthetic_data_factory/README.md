# Synthetic Data Factory

An automated data generation pipeline that creates high-quality synthetic Q&A datasets using LLMs.

## Architecture

Built with **SOLID** principles:

- **Single Responsibility** — DataGenerator, DataValidator, DatasetStore, and Trainer each own one concern.
- **Open/Closed** — Add new knowledge domains by extending `DOMAIN_TEMPLATES` without modifying the pipeline.
- **Liskov Substitution** — Swap LLM providers (OpenAI, Anthropic, local) via the `LLMClient` abstraction.
- **Interface Segregation** — `IDataGenerator` and `ITrainer` are separate interfaces so clients depend only on what they use.
- **Dependency Inversion** — All services depend on abstract `LLMClient`, not concrete implementations.

## Stack

| Layer | Technology |
|-------|-----------|
| API   | FastAPI   |
| UI    | Streamlit |
| LLM   | OpenAI    |
| Data  | JSONL / Hugging Face Datasets |

## Quick Start

```bash
pip install -r requirements.txt

# Start the API server
uvicorn src.api.app:app --reload

# In another terminal, start the UI
streamlit run src/ui/app.py
```

## Tests

```bash
pytest tests/ -v
```
