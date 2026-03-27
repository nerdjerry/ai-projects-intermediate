"""Streamlit UI for the Meeting Transcription System."""
import streamlit as st
import httpx

API_BASE = "http://localhost:8004/api/v1"

st.set_page_config(page_title="Meeting Transcription", layout="wide")
st.title("🎙️ Meeting Transcription System")

tab_process, tab_search = st.tabs(["Process Meeting", "Search Transcripts"])

with tab_process:
    st.subheader("Process Meeting Audio")
    audio_path = st.text_input("Audio file path", value="meeting.wav")
    if st.button("Process"):
        with st.spinner("Processing…"):
            try:
                resp = httpx.post(
                    f"{API_BASE}/process",
                    json={"audio_path": audio_path},
                    timeout=120.0,
                )
                resp.raise_for_status()
                data = resp.json()

                st.success(f"Processed {len(data['segments'])} segments, indexed {data['indexed_count']} documents")

                st.subheader("Transcript")
                for seg in data["segments"]:
                    st.markdown(f"**{seg['speaker']}** ({seg['start_time']:.1f}s): {seg['text']}")

                if data["action_items"]:
                    st.subheader("Action Items")
                    for item in data["action_items"]:
                        st.markdown(f"- [{item['speaker']}] {item['text']} ({item['timestamp']})")
            except httpx.HTTPError as exc:
                st.error(f"API error: {exc}")

with tab_search:
    st.subheader("Search Transcripts")
    query = st.text_input("Search query")
    if query and st.button("Search"):
        try:
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
