# AI Projects — Intermediate

Personal-scale, enterprise-design projects using **Python · FastAPI · Streamlit · OpenAI** with SOLID principles throughout.

## Projects

| # | Project | Description | Key Tech |
|---|---------|-------------|----------|
| 1 | [Synthetic Data Factory](projects/1_synthetic_data_factory/) | Automated Q&A dataset generation pipeline | FastAPI, OpenAI, Hugging Face |
| 2 | [PromptOps Framework](projects/2_promptops_framework/) | CI/CD for prompts — evaluate, version, optimize | FastAPI, pluggable metrics |
| 3 | [Legal Q&A Engine](projects/3_legal_qa_engine/) | Domain-specialized legal LLM — summarize, risk, Q&A | FastAPI, PyMuPDF, fine-tuning |
| 4 | [Personal Finance Agent](projects/4_personal_finance_agent/) | Stateful AI agent with short-term session memory | FastAPI, SQLAlchemy |
| 5 | [Meeting Transcription](projects/5_meeting_transcription/) | Prototype searchable meeting knowledge system (mock transcription/diarization, in-memory keyword search) | FastAPI, mock transcriber, in-memory search (Whisper, pgvector planned) |

## Stack Philosophy

- **Python 3.11+** everywhere
- **FastAPI** for APIs, **Streamlit** for UIs
- **OpenAI** as default LLM (swap-friendly via abstract `LLMClient`)
- **SOLID** design principles in every project

## Running a Project

```bash
cd projects/<project_name>
pip install -r requirements.txt

# Start the API
uvicorn src.api.app:app --reload --port 8000

# Start the UI (in a separate terminal)
streamlit run src/ui/app.py
```

## Running Tests

> **Important:** Each project uses the same top-level package name `src`.
> Always run tests from within a specific project directory to avoid
> `import src...` collisions between projects. Running `pytest` from the
> repo root will cause import conflicts.

```bash
cd projects/<project_name>
python -m pytest tests/ -v
```