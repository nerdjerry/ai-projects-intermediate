"""
Streamlit front-end for the Meeting Transcription System.

This module builds a two-tab web UI that communicates with the FastAPI
backend to process meetings and search indexed transcripts.

Architecture Notes:
    - The UI is a *thin client* — all transcription, diarization, and
      indexing happen server-side.  The front-end only sends requests and
      renders results.
    - ``httpx`` provides HTTP communication with configurable timeouts;
      meeting processing may take a while, so the timeout is set higher
      (120 s) for the ``/process`` endpoint.
"""

import streamlit as st
import httpx

# Base URL of the FastAPI backend (must be started separately)
API_BASE = "http://localhost:8004/api/v1"

# --- Page configuration ---
st.set_page_config(page_title="Meeting Transcription", layout="wide")
st.title("🎙️ Meeting Transcription System")

# Two primary workflows: process a new meeting or search existing transcripts
tab_process, tab_search = st.tabs(["Process Meeting", "Search Transcripts"])

# ──────────────────────────────────────────────────────────────────────
# Tab 1: Process Meeting — upload and run the full pipeline
# ──────────────────────────────────────────────────────────────────────
with tab_process:
    st.subheader("Process Meeting Audio")
    audio_path = st.text_input("Audio file path", value="meeting.wav")
    if st.button("Process"):
        # Show a spinner because transcription can be slow
        with st.spinner("Processing…"):
            try:
                # POST the audio path to trigger the processing pipeline
                resp = httpx.post(
                    f"{API_BASE}/process",
                    json={"audio_path": audio_path},
                    timeout=120.0,
                )
                resp.raise_for_status()
                data = resp.json()

                # Show summary metrics
                st.success(f"Processed {len(data['segments'])} segments, indexed {data['indexed_count']} documents")

                # Render each transcribed segment with speaker and timestamp
                st.subheader("Transcript")
                for seg in data["segments"]:
                    st.markdown(f"**{seg['speaker']}** ({seg['start_time']:.1f}s): {seg['text']}")

                # Display extracted action items (if any)
                if data["action_items"]:
                    st.subheader("Action Items")
                    for item in data["action_items"]:
                        st.markdown(f"- [{item['speaker']}] {item['text']} ({item['timestamp']})")
            except httpx.HTTPError as exc:
                st.error(f"API error: {exc}")

# ──────────────────────────────────────────────────────────────────────
# Tab 2: Search — query previously indexed transcripts
# ──────────────────────────────────────────────────────────────────────
with tab_search:
    st.subheader("Search Transcripts")
    query = st.text_input("Search query")
    if query and st.button("Search"):
        try:
            # POST the search query to the backend's search endpoint
            resp = httpx.post(
                f"{API_BASE}/search",
                json={"query": query},
                timeout=30.0,
            )
            resp.raise_for_status()
            results = resp.json()["results"]
            if results:
                for r in results:
                    st.markdown(f"**{r.get('speaker', 'Unknown')}**: {r['text']}")
            else:
                st.info("No results found.")
        except httpx.HTTPError as exc:
            st.error(f"API error: {exc}")
