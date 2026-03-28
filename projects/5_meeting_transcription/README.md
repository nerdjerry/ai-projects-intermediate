# Meeting Transcription System

Prototype searchable meeting knowledge system with transcription, speaker diarization, action item extraction, and keyword search.

## Features
- Process audio files via path (transcribe → diarize → extract actions → index)
- Mock transcriber and diarizer for development (swappable via interfaces)
- Automatic action item extraction from transcripts (keyword-based)
- Keyword search across indexed meeting segments
- Streamlit UI for processing and search

## Architecture

```
src/
├── interfaces/          # Abstract contracts (SOLID interfaces)
│   ├── transcriber.py   # ITranscriber — swap mock for Whisper (LSP)
│   ├── diarizer.py      # IDiarizer — swap mock for pyannote (LSP)
│   ├── indexer.py        # IIndexer — swap in-memory for pgvector (LSP)
│   ├── retriever.py      # IRetriever — abstract document retrieval (DIP)
│   └── query_engine.py   # IQueryEngine — abstract RAG query (ISP)
├── services/             # Concrete implementations
│   ├── mock_transcriber.py   # MockTranscriber (placeholder segments)
│   ├── mock_diarizer.py      # MockDiarizer (placeholder speakers)
│   ├── in_memory_indexer.py  # InMemoryIndexer (keyword matching)
│   ├── action_extractor.py   # ActionExtractor (keyword-based extraction)
│   └── meeting_service.py    # MeetingService (orchestrates pipeline)
├── api/                  # FastAPI with dependency injection
│   ├── app.py            # App setup with lifespan for service lifecycle
│   └── routes.py         # Endpoints: /process, /search, /stats
└── ui/
    └── app.py            # Streamlit UI for processing and search
```

## Planned Enhancements
- Whisper integration for real audio transcription (swap MockTranscriber)
- pyannote.audio for real speaker diarization (swap MockDiarizer)
- pgvector for semantic search via embeddings (swap InMemoryIndexer)
- Audio file upload endpoint (currently accepts file paths)
- Chat over transcripts with RAG (use IQueryEngine interface)
