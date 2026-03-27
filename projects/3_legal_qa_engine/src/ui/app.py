"""Streamlit UI for the Legal Q&A Engine."""
import streamlit as st
import httpx

API_BASE = "http://localhost:8002/api/v1"

st.set_page_config(page_title="Legal Q&A Engine", layout="wide")
st.title("⚖️ Legal Q&A Engine")

tab_analyze, tab_ask, tab_summarize = st.tabs(["Risk Analysis", "Ask", "Summarize"])

with tab_analyze:
    st.subheader("Contract Risk Analysis")
    text = st.text_area("Paste contract text", height=200, key="risk_text")
    if st.button("Analyze Risk"):
        if text.strip():
            try:
                resp = httpx.post(
                    f"{API_BASE}/analyze-risk",
                    json={"text": text},
                    timeout=60.0,
                )
                resp.raise_for_status()
                findings = resp.json()["findings"]
                if findings:
                    for f in findings:
                        color = "🔴" if f["risk_level"] == "high" else "🟡"
                        st.markdown(f"{color} **{f['risk_level'].upper()}**: {f['explanation']}")
                        st.caption(f["clause"])
                else:
                    st.success("No significant risks detected.")
            except httpx.HTTPError as exc:
                st.error(f"API error: {exc}")

with tab_ask:
    st.subheader("Legal Q&A")
    context = st.text_area("Legal context", height=150, key="qa_context")
    question = st.text_input("Your question")
    if st.button("Ask"):
        if context.strip() and question.strip():
            try:
                resp = httpx.post(
                    f"{API_BASE}/ask",
                    json={"question": question, "context": context},
                    timeout=60.0,
                )
                resp.raise_for_status()
                st.write(resp.json()["answer"])
            except httpx.HTTPError as exc:
                st.error(f"API error: {exc}")

with tab_summarize:
    st.subheader("Document Summarization")
    doc_text = st.text_area("Paste document text", height=200, key="sum_text")
    if st.button("Summarize"):
        if doc_text.strip():
            try:
                resp = httpx.post(
                    f"{API_BASE}/summarize",
                    json={"text": doc_text},
                    timeout=60.0,
                )
                resp.raise_for_status()
                st.write(resp.json()["summary"])
            except httpx.HTTPError as exc:
                st.error(f"API error: {exc}")
