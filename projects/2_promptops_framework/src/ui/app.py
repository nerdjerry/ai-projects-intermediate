"""
Streamlit UI for the PromptOps Framework.

This module implements a lightweight graphical front-end that lets users
interact with the PromptOps REST API through their browser.  It is built
with `Streamlit <https://streamlit.io/>`_, a Python library that turns
simple scripts into shareable web applications.

Architecture notes
------------------
* The UI is a **thin client** — it contains no business logic.  Every action
  (evaluation, prompt retrieval) is delegated to the FastAPI back-end via
  HTTP calls.  This keeps the front-end and back-end independently
  deployable and testable.
* ``httpx`` is used instead of ``requests`` because it supports both sync and
  async usage and offers a modern, well-typed API.
* The module is *not* imported by the rest of the application.  It is
  launched as a standalone Streamlit app (``streamlit run src/ui/app.py``).

Tabs
----
1. **Evaluate** — paste predictions & references, pick metrics, and view
   scores.
2. **Prompt Versions** — browse stored versions of a named prompt template.
"""

import streamlit as st
import httpx
import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Base URL of the PromptOps REST API.  In production this would be read from
# an environment variable or config file.
API_BASE = "http://localhost:8001/api/v1"

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(page_title="PromptOps Framework", layout="wide")
st.title("🔧 PromptOps Framework")

# Create two top-level tabs — one for evaluation, one for version browsing.
tab_eval, tab_versions = st.tabs(["Evaluate", "Prompt Versions"])

# ---------------------------------------------------------------------------
# Tab 1 — Evaluate Predictions
# ---------------------------------------------------------------------------
with tab_eval:
    st.subheader("Evaluate Predictions")

    # Collect user inputs: predictions, references, and desired metrics.
    predictions = st.text_area("Predictions (one per line)", height=100)
    references = st.text_area("References (one per line)", height=100)
    metrics = st.multiselect(
        "Metrics",
        ["exact_match", "contains", "length_ratio"],
        default=["exact_match"],
    )

    if st.button("Evaluate"):
        # Parse multi-line text areas into lists, stripping empty lines.
        preds = [p.strip() for p in predictions.strip().split("\n") if p.strip()]
        refs = [r.strip() for r in references.strip().split("\n") if r.strip()]

        # Client-side validation: lengths must match before calling the API.
        if len(preds) != len(refs):
            st.error("Number of predictions must match references")
        else:
            try:
                # POST the evaluation request to the FastAPI back-end.
                resp = httpx.post(
                    f"{API_BASE}/evaluate",
                    json={"predictions": preds, "references": refs, "metrics": metrics},
                    timeout=30.0,
                )
                resp.raise_for_status()
                # Display the returned scores as formatted JSON.
                st.json(resp.json()["scores"])
            except httpx.HTTPError as exc:
                st.error(f"API error: {exc}")

# ---------------------------------------------------------------------------
# Tab 2 — Browse Prompt Versions
# ---------------------------------------------------------------------------
with tab_versions:
    st.subheader("Browse Prompt Versions")
    prompt_name = st.text_input("Prompt name")

    if prompt_name and st.button("Load Versions"):
        try:
            # GET all stored versions for the given prompt name.
            resp = httpx.get(f"{API_BASE}/prompts/{prompt_name}", timeout=30.0)
            resp.raise_for_status()
            # Render the versions as a Pandas DataFrame for easy browsing.
            df = pd.DataFrame(resp.json())
            st.dataframe(df, use_container_width=True)
        except httpx.HTTPError:
            st.warning("No versions found or API not running.")
