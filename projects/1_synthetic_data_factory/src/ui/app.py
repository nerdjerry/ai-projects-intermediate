"""Streamlit UI for the Synthetic Data Factory.

This module provides a lightweight browser-based frontend that communicates
with the FastAPI backend over HTTP.  It is a thin presentation layer — all
business logic stays in the backend services, keeping the UI easy to
replace or redesign independently.

Design principles:
  - SRP (Single Responsibility Principle): The UI is only responsible for
    rendering widgets and forwarding user actions to the API.  It contains
    zero business logic (no validation, no file I/O, no LLM calls).
  - Separation of Concerns: The Streamlit app is a separate process from
    the FastAPI server.  This decoupling means you could swap Streamlit
    for a React frontend without touching the backend.

Architecture note:
  The UI talks to the backend via ``httpx`` HTTP calls.  This is the
  recommended pattern for Streamlit apps that front a REST API — it keeps
  the data flow explicit and testable.
"""
import streamlit as st
import httpx
import pandas as pd

# Base URL for the FastAPI backend.  In production this would come from an
# environment variable or a config file; hardcoded here for simplicity.
API_BASE = "http://localhost:8000/api/v1"

# --- Page configuration -------------------------------------------------------
st.set_page_config(page_title="Synthetic Data Factory", layout="wide")
st.title("🏭 Synthetic Data Factory")

# Two tabs keep the UI organised: one for generating new datasets, one for
# browsing existing ones.
tab_generate, tab_browse = st.tabs(["Generate", "Browse Datasets"])

# --- Generate tab --------------------------------------------------------------
with tab_generate:
    # Collect user inputs: which domain and how many samples.
    domain = st.text_input("Domain", value="science")
    num_samples = st.slider("Number of samples", 1, 50, 5)

    if st.button("Generate Dataset"):
        with st.spinner("Generating…"):
            try:
                # POST to the backend /generate endpoint.  A generous
                # timeout accounts for LLM response latency.
                resp = httpx.post(
                    f"{API_BASE}/generate",
                    json={"domain": domain, "num_samples": num_samples},
                    timeout=120.0,
                )
                resp.raise_for_status()
                data = resp.json()
                st.success(
                    f"Generated {data['generated']} → Validated {data['validated']} records"
                )
            except httpx.HTTPError as exc:
                # Surface API errors clearly so the user knows what went wrong.
                st.error(f"API error: {exc}")

# --- Browse tab ----------------------------------------------------------------
with tab_browse:
    try:
        # Fetch the list of available datasets from the API.
        resp = httpx.get(f"{API_BASE}/datasets", timeout=30.0)
        resp.raise_for_status()
        datasets = resp.json()
        if datasets:
            # Let the user pick a domain, then load and display its records.
            selected = st.selectbox(
                "Select domain",
                [d["domain"] for d in datasets],
            )
            if selected:
                detail = httpx.get(f"{API_BASE}/datasets/{selected}", timeout=30.0)
                detail.raise_for_status()
                # Convert JSON records to a DataFrame for a clean table view.
                df = pd.DataFrame(detail.json())
                st.dataframe(df, use_container_width=True)
        else:
            st.info("No datasets generated yet.")
    except httpx.HTTPError:
        # Gracefully handle the case where the backend isn't running.
        st.warning("Could not connect to API. Is the server running?")
