"""
Streamlit UI for the Legal Q&A Engine.

This module provides a browser-based frontend built with **Streamlit**
that communicates with the FastAPI backend via HTTP (``httpx``).

**Architecture – Presentation Layer:**
The UI is completely decoupled from business logic. It knows nothing
about ``DatasetBuilder``, ``LLMClient``, or any service class. It
simply sends JSON requests to the REST API and renders the responses.
This separation means:
    • The backend can be deployed independently.
    • The UI can be swapped for a React/Vue/CLI frontend without
      touching any backend code.

**SOLID – Dependency Inversion Principle (DIP) at the system level:**
The UI depends on the *API contract* (URL + JSON schemas), not on
concrete Python classes. This is DIP applied at the architectural
boundary between frontend and backend.

**Tabs layout:** The UI is organised into three tabs that mirror the
three core capabilities of the engine:
    1. Risk Analysis — scan a contract for risk clauses
    2. Ask           — ask a legal question with context
    3. Summarize     — condense a long document
"""
import streamlit as st
import httpx

# Base URL for the FastAPI backend (assumed to run locally on port 8002).
API_BASE = "http://localhost:8002/api/v1"

# Configure the Streamlit page metadata (appears in the browser tab).
st.set_page_config(page_title="Legal Q&A Engine", layout="wide")
st.title("⚖️ Legal Q&A Engine")

# Create three tabs — one for each core capability.
tab_analyze, tab_ask, tab_summarize = st.tabs(["Risk Analysis", "Ask", "Summarize"])

# ---------------------------------------------------------------------------
# Tab 1: Risk Analysis
# ---------------------------------------------------------------------------
with tab_analyze:
    st.subheader("Contract Risk Analysis")
    text = st.text_area("Paste contract text", height=200, key="risk_text")
    if st.button("Analyze Risk"):
        if text.strip():
            try:
                # Send the contract text to the /analyze-risk endpoint.
                resp = httpx.post(
                    f"{API_BASE}/analyze-risk",
                    json={"text": text},
                    timeout=60.0,
                )
                resp.raise_for_status()
                findings = resp.json()["findings"]
                if findings:
                    for f in findings:
                        # Visual indicator: red circle for high risk, yellow for medium.
                        color = "🔴" if f["risk_level"] == "high" else "🟡"
                        st.markdown(f"{color} **{f['risk_level'].upper()}**: {f['explanation']}")
                        st.caption(f["clause"])
                else:
                    st.success("No significant risks detected.")
            except httpx.HTTPError as exc:
                st.error(f"API error: {exc}")

# ---------------------------------------------------------------------------
# Tab 2: Legal Q&A
# ---------------------------------------------------------------------------
with tab_ask:
    st.subheader("Legal Q&A")
    context = st.text_area("Legal context", height=150, key="qa_context")
    question = st.text_input("Your question")
    if st.button("Ask"):
        if context.strip() and question.strip():
            try:
                # Send the question + context to the /ask endpoint.
                resp = httpx.post(
                    f"{API_BASE}/ask",
                    json={"question": question, "context": context},
                    timeout=60.0,
                )
                resp.raise_for_status()
                st.write(resp.json()["answer"])
            except httpx.HTTPError as exc:
                st.error(f"API error: {exc}")

# ---------------------------------------------------------------------------
# Tab 3: Document Summarization
# ---------------------------------------------------------------------------
with tab_summarize:
    st.subheader("Document Summarization")
    doc_text = st.text_area("Paste document text", height=200, key="sum_text")
    if st.button("Summarize"):
        if doc_text.strip():
            try:
                # Send the document text to the /summarize endpoint.
                resp = httpx.post(
                    f"{API_BASE}/summarize",
                    json={"text": doc_text},
                    timeout=60.0,
                )
                resp.raise_for_status()
                st.write(resp.json()["summary"])
            except httpx.HTTPError as exc:
                st.error(f"API error: {exc}")
