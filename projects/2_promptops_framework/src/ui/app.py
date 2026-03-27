"""Streamlit UI for the PromptOps Framework."""
import streamlit as st
import httpx
import pandas as pd

API_BASE = "http://localhost:8001/api/v1"

st.set_page_config(page_title="PromptOps Framework", layout="wide")
st.title("🔧 PromptOps Framework")

tab_eval, tab_versions = st.tabs(["Evaluate", "Prompt Versions"])

with tab_eval:
    st.subheader("Evaluate Predictions")
    predictions = st.text_area("Predictions (one per line)", height=100)
    references = st.text_area("References (one per line)", height=100)
    metrics = st.multiselect("Metrics", ["exact_match", "contains", "length_ratio"], default=["exact_match"])

    if st.button("Evaluate"):
        preds = [p.strip() for p in predictions.strip().split("\n") if p.strip()]
        refs = [r.strip() for r in references.strip().split("\n") if r.strip()]
        if len(preds) != len(refs):
            st.error("Number of predictions must match references")
        else:
            try:
                resp = httpx.post(
                    f"{API_BASE}/evaluate",
                    json={"predictions": preds, "references": refs, "metrics": metrics},
                    timeout=30.0,
                )
                resp.raise_for_status()
                st.json(resp.json()["scores"])
            except httpx.HTTPError as exc:
                st.error(f"API error: {exc}")

with tab_versions:
    st.subheader("Browse Prompt Versions")
    prompt_name = st.text_input("Prompt name")
    if prompt_name and st.button("Load Versions"):
        try:
            resp = httpx.get(f"{API_BASE}/prompts/{prompt_name}", timeout=30.0)
            resp.raise_for_status()
            df = pd.DataFrame(resp.json())
            st.dataframe(df, use_container_width=True)
        except httpx.HTTPError:
            st.warning("No versions found or API not running.")
