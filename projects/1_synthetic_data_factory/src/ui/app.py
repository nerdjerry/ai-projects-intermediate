"""Streamlit UI for the Synthetic Data Factory."""
import streamlit as st
import httpx
import pandas as pd

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Synthetic Data Factory", layout="wide")
st.title("🏭 Synthetic Data Factory")

tab_generate, tab_browse = st.tabs(["Generate", "Browse Datasets"])

with tab_generate:
    domain = st.text_input("Domain", value="science")
    num_samples = st.slider("Number of samples", 1, 50, 5)

    if st.button("Generate Dataset"):
        with st.spinner("Generating…"):
            try:
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
                st.error(f"API error: {exc}")

with tab_browse:
    try:
        resp = httpx.get(f"{API_BASE}/datasets", timeout=30.0)
        resp.raise_for_status()
        datasets = resp.json()
        if datasets:
            selected = st.selectbox(
                "Select domain",
                [d["domain"] for d in datasets],
            )
            if selected:
                detail = httpx.get(f"{API_BASE}/datasets/{selected}", timeout=30.0)
                detail.raise_for_status()
                df = pd.DataFrame(detail.json())
                st.dataframe(df, use_container_width=True)
        else:
            st.info("No datasets generated yet.")
    except httpx.HTTPError:
        st.warning("Could not connect to API. Is the server running?")
